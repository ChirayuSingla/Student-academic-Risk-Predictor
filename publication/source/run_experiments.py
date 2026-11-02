"""Reproduce original experiment and execute exploratory publication extensions.
Run from the project root: .venv/Scripts/python.exe publication/source/run_experiments.py
Never writes the original models/results. No test-based model/threshold selection.
"""
from pathlib import Path
import sys, json, platform, hashlib, shutil, time
from importlib.metadata import version
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import joblib
from scipy.stats import binomtest
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, StratifiedKFold, RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import confusion_matrix
from src.config import FEATURES, NUMERIC, CATEGORICAL
from src.data import load_data, split_data
from src.training import model_specs, SCORING, refit_index, tune_models
from src.evaluation import evaluate_predictions, positive_probability, wilson_interval
from src.preprocessing import make_preprocessor

OUT = ROOT/'publication'
RES = OUT/'results'
RES.mkdir(exist_ok=True)
def js(path, value):
    path.write_text(json.dumps(value, indent=2, default=lambda x: x.item() if hasattr(x,'item') else str(x)), encoding='utf-8')
def flat(y,p,t=.5):
    m,_ = evaluate_predictions(y,p,t)
    return {k:v for k,v in m.items() if isinstance(v,(float,int))} | dict(zip(['TN','FP','FN','TP'], np.array(m['confusion_matrix']).ravel().astype(int))) | {'flags':int((p>=t).sum())}
def search(name, cols=FEATURES, seed=42):
    model, grid = specs[name]
    model=clone(model)
    if cols!=FEATURES:
        pre=model.named_steps['preprocess']
        pre.transformers=[(n,p,[c for c in cs if c in cols]) for n,p,cs in pre.transformers]
    return GridSearchCV(model,grid,scoring=SCORING,refit=refit_index,
        cv=StratifiedKFold(5,shuffle=True,random_state=seed),n_jobs=1,error_score='raise')

start=time.time()
frame,X,y=load_data()
Xt,Xh,yt,yh=split_data(X,y)
assert set(Xt.index).isdisjoint(Xh.index)
assert not set(['G1','G2','G3'])&set(X.columns)
split=json.loads((ROOT/'results/split_indices.json').read_text())
assert split['train_row_ids']==Xt.index.tolist() and split['test_row_ids']==Xh.index.tolist()
js(RES/'frozen_split.json',split)
rep=RES/'reproduction';rep.mkdir(exist_ok=True)
models,tuning,selected,_,_=tune_models(Xt,yt,rep)
checks={}
for name,m in models.items():
    old=pd.read_csv(ROOT/f'results/{name}_test_predictions.csv')
    p=positive_probability(m,Xh)
    np.testing.assert_allclose(p,old.probability_at_risk,atol=1e-12,rtol=1e-12)
    checks[name]={'max_probability_difference':float(np.max(np.abs(p-old.probability_at_risk))), 'best_params':tuning[name]['best_params']}
js(RES/'reproduction_checks.json',{'passed':True,'selected':selected,'checks':checks})
specs=model_specs()
specs['random_forest']=(Pipeline([('preprocess',make_preprocessor(False)),('classifier',RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=1))]),
    {'classifier__max_depth':[3,None],'classifier__min_samples_leaf':[10], 'classifier__class_weight':[None,'balanced']})
specs['gradient_boosting']=(Pipeline([('preprocess',make_preprocessor(False)),('classifier',GradientBoostingClassifier(n_estimators=100,min_samples_leaf=10,random_state=42))]),
    {'classifier__learning_rate':[.03,.1],'classifier__max_depth':[1,2]})
js(RES/'protocol.json', {'outer':'5-fold stratified, 2 repeats, seed 2026, on original 316 training records only','inner':'5-fold stratified shuffled seed 42, F2 then recall then ROC-AUC tie-break',
    'grids':{k:v[1] for k,v in specs.items()},'threshold':.5,'calibration':'sigmoid, ensemble=True, 3 stratified calibration folds seed 73; nested 5-fold hyperparameter searches within each fitting fold',
    'bootstrap':'2000 class-stratified paired resamples seed 2701; fixed fitted models; percentile 95% intervals','exploratory':True})
for name in ['random_forest','gradient_boosting']:
    s=search(name);s.fit(Xt,yt);models[name]=s.best_estimator_
    pd.DataFrame(s.cv_results_).to_csv(RES/f'{name}_search.csv',index=False)
    tuning[name]={'best_params':s.best_params_,'selection_f2':s.cv_results_['mean_test_f2'][s.best_index_]}
    print('Full training fit',name,s.best_params_,flush=True)

subsets={'all':FEATURES,'no_absences':[c for c in FEATURES if c!='absences'],
 'reduced_sensitive':[c for c in FEATURES if c not in ['sex','age','address','famsize','Pstatus','Medu','Fedu','Mjob','Fjob','guardian','internet','romantic','Dalc','Walc','health']],
 'no_failures':[c for c in FEATURES if c!='failures']}
js(RES/'feature_subsets.json',subsets)
records=[]; predictions=[]; stability=[]; coeffs=[]; folds=[]
outer=RepeatedStratifiedKFold(n_splits=5,n_repeats=2,random_state=2026)
for fold,(a,b) in enumerate(outer.split(Xt,yt)):
    xa,xb,ya,yb=Xt.iloc[a],Xt.iloc[b],yt.iloc[a],yt.iloc[b]
    folds.append({'fold':fold,'fit_ids':xa.index.tolist(),'validation_ids':xb.index.tolist()})
    for subset,cols in subsets.items():
        for name in (list(specs) if subset=='all' else ['logistic_regression','decision_tree']):
            s=search(name,cols);s.fit(xa[cols],ya)
            p=positive_probability(s,xb[cols])
            records.append({'fold':fold,'repeat':fold//5,'subset':subset,'model':name,**flat(yb,p),'params':json.dumps(s.best_params_)})
            predictions.extend({'fold':fold,'repeat':fold//5,'subset':subset,'model':name,'row_id':int(i),'y':int(v),'p':float(q)} for i,v,q in zip(xb.index,yb,p))
            if subset=='all' and name in ['logistic_regression','decision_tree']:
                imp=permutation_importance(s.best_estimator_,xb,yb,scoring='average_precision',n_repeats=10,random_state=100+fold,n_jobs=1)
                stability.extend({'fold':fold,'model':name,'feature':f,'mean_ap_decrease':float(v),'permutation_sd':float(w)} for f,v,w in zip(FEATURES,imp.importances_mean,imp.importances_std))
                if name=='logistic_regression':
                    fitted=s.best_estimator_
                    coeffs.extend({'fold':fold,'feature':f,'coefficient':float(v)} for f,v in zip(fitted['preprocess'].get_feature_names_out(),fitted['classifier'].coef_[0]))
    for name,p in [('majority',np.zeros(len(yb))),('always_at_risk',np.ones(len(yb))),('prevalence',np.full(len(yb),ya.mean())),('prior_failure', (xb.failures.to_numpy()>0).astype(float))]:
        records.append({'fold':fold,'repeat':fold//5,'subset':'all','model':name,**flat(yb,p),'params':'{}'})
    pd.DataFrame(records).to_csv(RES/'nested_fold_metrics.csv',index=False)
    print('Nested outer fold completed',fold+1,'of 10',round(time.time()-start,1),'s',flush=True)
js(RES/'nested_folds.json',folds)
pd.DataFrame(predictions).to_csv(RES/'nested_predictions.csv',index=False)
pd.DataFrame(stability).to_csv(RES/'permutation_stability.csv',index=False)
pd.DataFrame(coeffs).to_csv(RES/'coefficient_stability.csv',index=False)
nf=pd.DataFrame(records)
nf.groupby(['subset','model'])[['f2','recall','precision','roc_auc','average_precision','brier_score']].agg(['mean','std']).to_csv(RES/'nested_summary.csv')
for subset,cols in subsets.items():
    if subset=='all':continue
    for name in ['logistic_regression','decision_tree']:
        s=search(name,cols);s.fit(Xt[cols],yt)
        models[f'{name}__{subset}']=s.best_estimator_
for name in ['logistic_regression','decision_tree']:
    cal=CalibratedClassifierCV(search(name),method='sigmoid',cv=StratifiedKFold(3,shuffle=True,random_state=73),ensemble=True,n_jobs=1)
    cal.fit(Xt,yt);models[name+'__sigmoid']=cal
    print('Calibration fitted',name,flush=True)
prob={name:positive_probability(m,Xh) for name,m in models.items()}
prob.update({'majority':np.zeros(len(yh)),'always_at_risk':np.ones(len(yh)),'prevalence':np.full(len(yh),yt.mean()),'prior_failure':(Xh.failures.to_numpy()>0).astype(float)})
pd.DataFrame([{'model':n,**flat(yh,p)} for n,p in prob.items()]).to_csv(RES/'heldout_metrics.csv',index=False)
pd.DataFrame({'row_id':Xh.index,'y':yh,**prob}).to_csv(RES/'heldout_predictions.csv',index=False)
for name,m in models.items():joblib.dump(m,RES/(name+'.joblib'),compress=3)
js(RES/'tuning.json',tuning)

# Class-stratified bootstrap holds observed prevalence fixed and resamples paired students.
rng=np.random.default_rng(2701); yy=yh.to_numpy();ix=[np.flatnonzero(yy==v) for v in [0,1]]
boot={name:[] for name in ['logistic_regression','decision_tree','random_forest','gradient_boosting']}
for _ in range(2000):
    ii=np.r_[rng.choice(ix[0],len(ix[0]),True),rng.choice(ix[1],len(ix[1]),True)]
    for name in boot:boot[name].append(flat(yy[ii],prob[name][ii]))
ci=[]
for name,rows in boot.items():
    for metric in ['accuracy','precision','recall','f1','f2','roc_auc','average_precision','brier_score']:
        v=[r[metric] for r in rows]
        ci.append({'model':name,'metric':metric,'point':flat(yy,prob[name])[metric],'low':float(np.quantile(v,.025)),'high':float(np.quantile(v,.975))})
pd.DataFrame(ci).to_csv(RES/'bootstrap_intervals.csv',index=False)
diff=[]
for metric in ['f2','roc_auc','average_precision','brier_score']:
    v=np.array([r[metric] for r in boot['logistic_regression']])-np.array([r[metric] for r in boot['decision_tree']])
    diff.append({'metric':'LR minus DT '+metric,'point':flat(yy,prob['logistic_regression'])[metric]-flat(yy,prob['decision_tree'])[metric], 'low':float(np.quantile(v,.025)), 'high':float(np.quantile(v,.975))})
pd.DataFrame(diff).to_csv(RES/'paired_differences.csv',index=False)
c1=(prob['logistic_regression']>=.5)==yy;c2=(prob['decision_tree']>=.5)==yy
b=int((c1&~c2).sum());c=int((~c1&c2).sum())
js(RES/'mcnemar.json',{'LR_correct_DT_wrong':b,'DT_correct_LR_wrong':c,'exact_two_sided_p':float(binomtest(b,b+c,.5).pvalue) if b+c else 1.,'exploratory':True})
groups=[]
for name in ['logistic_regression','decision_tree','random_forest','gradient_boosting']:
    for attr in ['sex','address','school']:
        for group in sorted(Xh[attr].unique()):
            mask=(Xh[attr]==group).to_numpy();yyg=yy[mask];pg=prob[name][mask];m=flat(yyg,pg)
            lo,hi=wilson_interval(m['TP'],int(yyg.sum()))
            fl,fh=wilson_interval(m['FP'],int((yyg==0).sum()))
            groups.append({'model':name,'attribute':attr,'group':group,'n':int(mask.sum()),'positives':int(yyg.sum()), **m,'recall_low':lo,'recall_high':hi,'fpr':1-m['specificity'],'fpr_low':fl,'fpr_high':fh})
pd.DataFrame(groups).to_csv(RES/'subgroups.csv',index=False)
thresholds=[]
for name in ['logistic_regression','decision_tree','random_forest','gradient_boosting']:
    for t in np.arange(.1,1.,.1):thresholds.append({'model':name,**flat(yh,prob[name],t)})
pd.DataFrame(thresholds).to_csv(RES/'threshold_sensitivity.csv',index=False)
calrows=[]
for name in ['logistic_regression','decision_tree','logistic_regression__sigmoid','decision_tree__sigmoid']:
    p=prob[name]
    # Fixed uniform bins, preserve counts and uncertainty; tree ties stay together.
    bins=np.minimum((p*5).astype(int),4)
    for k in range(5):
        z=bins==k
        if not z.any():continue
        n=int(z.sum());succ=int(yy[z].sum());lo,hi=wilson_interval(succ,n)
        calrows.append({'model':name,'bin':k,'n':n,'mean_probability':float(p[z].mean()),'observed_fraction':succ/n,'low':lo,'high':hi})
pd.DataFrame(calrows).to_csv(RES/'calibration_bins.csv',index=False)
js(RES/'environment.json',{'python':sys.version,'platform':platform.platform(),'packages':{p:version(p) for p in ['numpy','pandas','scipy','scikit-learn','matplotlib','joblib']},'elapsed_seconds':time.time()-start})
js(RES/'data_checks.json',{'shape':frame.shape,'missing':int(frame.isna().sum().sum()),'exact_duplicate_rows':int(frame.duplicated().sum()),'G3_zero':int((frame.G3==0).sum()),'sha256':hashlib.sha256((ROOT/'data/student-mat.csv').read_bytes()).hexdigest()})
print('ALL EXPERIMENTS COMPLETE',round(time.time()-start,1),'seconds',flush=True)
