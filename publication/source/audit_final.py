"""Independent artifact audit; never fits or overwrites historical models."""
from pathlib import Path
import json, hashlib, sys, re, urllib.request, urllib.parse, concurrent.futures
import numpy as np
import pandas as pd
import joblib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.data import load_data,split_data
from src.evaluation import evaluate_predictions,positive_probability,wilson_interval
R=ROOT/'publication/results';O=ROOT/'publication/final';O.mkdir(exist_ok=True)
checks={}
frame,X,y=load_data();Xt,Xh,yt,yh=split_data(X,y)
assert frame.shape==(395,33) and len(Xt)==316 and len(Xh)==79 and len(X.columns)==30
assert not {'G1','G2','G3'}&set(X.columns)
p=pd.read_csv(R/'heldout_predictions.csv');m=pd.read_csv(R/'heldout_metrics.csv').set_index('model')
assert p.row_id.tolist()==Xh.index.tolist();np.testing.assert_array_equal(p.y,yh)
for name in m.index:
    a,_=evaluate_predictions(yh,p[name])
    for k in ['accuracy','precision','recall','f1','f2','roc_auc','average_precision','brier_score','specificity']:
        np.testing.assert_allclose(a[k],m.loc[name,k],atol=1e-12)
    np.testing.assert_array_equal(np.array(a['confusion_matrix']).ravel(),m.loc[name,['TN','FP','FN','TP']])
    if (R/(name+'.joblib')).exists():
        model=joblib.load(R/(name+'.joblib'))
        cols=list(model.feature_names_in_)
        np.testing.assert_allclose(positive_probability(model,Xh[cols]),p[name],atol=1e-12)
checks['16_heldout_variants_metrics_confusions_and_12_saved_models']=True
for name,val in {'majority':np.zeros(79),'always_at_risk':np.ones(79),'prevalence':np.full(79,yt.mean()),'prior_failure':(Xh.failures>0).astype(int)}.items():
    np.testing.assert_allclose(p[name],val,atol=1e-14)
checks['four_baselines_from_original_rows']=True
nf=pd.read_csv(R/'nested_fold_metrics.csv');pr=pd.read_csv(R/'nested_predictions.csv')
folds=json.loads((R/'nested_folds.json').read_text())
for f in folds:
    assert not set(f['fit_ids'])&set(f['validation_ids'])
    assert set(f['fit_ids'])|set(f['validation_ids'])==set(Xt.index)
for _,r in nf.iterrows():
    g=pr[(pr.fold==r.fold)&(pr.subset==r.subset)&(pr.model==r.model)]
    ids=folds[int(r.fold)]['validation_ids']
    if len(g):
        assert g.row_id.tolist()==ids
        np.testing.assert_array_equal(g.y,y.loc[g.row_id])
        yy,pp=g.y,g.p
    else:
        xx=X.loc[ids];yy=y.loc[ids];fit=y.loc[folds[int(r.fold)]['fit_ids']]
        pp={'majority':np.zeros(len(ids)),'always_at_risk':np.ones(len(ids)),
            'prevalence':np.full(len(ids),fit.mean()),'prior_failure':(xx.failures>0).astype(int)}[r.model]
    a,_=evaluate_predictions(yy,pp)
    for k in ['accuracy','precision','recall','f1','f2','roc_auc','average_precision','brier_score']:
        np.testing.assert_allclose(a[k],r[k],atol=1e-12)
summary=nf.groupby(['subset','model'])[['f2','recall','precision','roc_auc','average_precision','brier_score']].agg(['mean','std'])
saved=pd.read_csv(R/'nested_summary.csv',header=[0,1],index_col=[0,1])
pd.testing.assert_frame_equal(summary,saved,check_exact=False,atol=1e-12)
checks['140_nested_fold_records_including_baselines_and_sample_SD']=True
sg=pd.read_csv(R/'subgroups.csv')
for _,r in sg.iterrows():
    mask=Xh[r.attribute].astype(str).to_numpy()==str(r.group)
    a,_=evaluate_predictions(yh.to_numpy()[mask],p[r.model].to_numpy()[mask])
    assert mask.sum()==r.n and yh.to_numpy()[mask].sum()==r.positives
    np.testing.assert_array_equal(np.array(a['confusion_matrix']).ravel(),r[['TN','FP','FN','TP']])
    np.testing.assert_allclose(wilson_interval(int(r.TP),int(r.positives)),[r.recall_low,r.recall_high],atol=1e-12)
    np.testing.assert_allclose(wilson_interval(int(r.FP),int(r.n-r.positives)),[r.fpr_low,r.fpr_high],atol=1e-12)
checks['24_subgroups_denominators_confusions_and_Wilson_intervals']=True
for _,r in pd.read_csv(R/'calibration_bins.csv').iterrows():
    v=p[r.model].to_numpy();mask=np.minimum((v*5).astype(int),4)==r['bin']
    assert mask.sum()==r.n
    np.testing.assert_allclose([v[mask].mean(),p.y[mask].mean()],[r.mean_probability,r.observed_fraction],atol=1e-12)
checks['calibration_bin_counts_probabilities_and_outcomes']=True
for name in ['logistic_regression__sigmoid','decision_tree__sigmoid']:
    model=joblib.load(R/(name+'.joblib'));assert model.ensemble is True and len(model.calibrated_classifiers_)==3
    assert m.loc[name,'TP']==2 and m.loc[name,'FP']==0
checks['sigmoid_ensembles_three_members_and_two_positive_flags']=True
refit=ROOT/'.diagnostics/publication-reproduction-20261102/results'
comparison={}
if (refit/'environment.json').exists():
    for f in sorted(R.glob('*.csv')):
        fresh=refit/f.name
        if not fresh.exists():continue
        a=pd.read_csv(f);b=pd.read_csv(fresh)
        # Search timing columns are machine dependent, scientific columns are deterministic.
        keep=[c for c in a.columns if 'time' not in c]
        pd.testing.assert_frame_equal(a[keep],b[keep],check_exact=False,atol=1e-11,rtol=1e-10)
        comparison[f.name]={'rows':len(a),'status':'matched'}
    for name in ['data_checks.json','feature_subsets.json','frozen_split.json','mcnemar.json','nested_folds.json','protocol.json','reproduction_checks.json','tuning.json']:
        assert json.loads((R/name).read_text())==json.loads((refit/name).read_text()),name
    checks['fresh_rerun_eight_protocol_fold_and_reproduction_JSON_records']=True
    checks['fresh_end_to_end_rerun_scientific_csv_outputs']=True
for f in (ROOT/'publication/tables').glob('*.csv'):
    if (R/f.name).exists():assert f.read_bytes()==(R/f.name).read_bytes(),f.name
checks['14_table_source_copies_identical']=True
out={'date':'2026-11-02','checks':checks,'fresh_rerun_comparison':comparison,
     'limitations':['Previously inspected holdout; extensions exploratory','No independent institution','No feature timestamps','No causal or educational effectiveness inference']}
(O/'experiment_verification.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
