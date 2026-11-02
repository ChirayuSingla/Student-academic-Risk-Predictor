from pathlib import Path
import json,sys
import numpy as np,pandas as pd
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B.parent))
from src.evaluation import evaluate_predictions
R=B/'results';checks={}
sp=json.loads((R/'frozen_split.json').read_text());train=set(sp['train_row_ids']);test=set(sp['test_row_ids'])
assert len(train)==316 and len(test)==79 and not train&test
folds=json.loads((R/'nested_folds.json').read_text())
for f in folds:
    a,b=set(f['fit_ids']),set(f['validation_ids'])
    assert not a&b and a|b==train and not (a|b)&test
checks['split_and_outer_fold_isolation']=True
p=pd.read_csv(R/'heldout_predictions.csv');m=pd.read_csv(R/'heldout_metrics.csv').set_index('model')
assert p.row_id.tolist()==sp['test_row_ids']
for name in m.index:
    actual,pr=evaluate_predictions(p.y,p[name]);
    for k in ['accuracy','precision','recall','f1','f2','roc_auc','average_precision','brier_score','specificity']:
        assert np.isclose(actual[k],m.loc[name,k],atol=1e-12)
    assert np.array_equal(np.array(actual['confusion_matrix']).ravel(),m.loc[name,['TN','FP','FN','TP']].to_numpy())
checks['all_16_heldout_variants_recomputed']=True
n=pd.read_csv(R/'nested_predictions.csv');fm=pd.read_csv(R/'nested_fold_metrics.csv')
for (fold,subset,name),g in n.groupby(['fold','subset','model']):
    expected=set(folds[int(fold)]['validation_ids']);assert set(g.row_id)==expected
    q=fm[(fm.fold==fold)&(fm.subset==subset)&(fm.model==name)].iloc[0]
    actual,_=evaluate_predictions(g.y,g.p)
    for k in ['recall','f2','roc_auc','average_precision','brier_score']:assert np.isclose(actual[k],q[k],atol=1e-12)
for _,g in n.groupby(['subset','model','repeat']):assert len(g)==316 and g.row_id.nunique()==316
checks['all_100_nested_model_fold_outputs_recomputed']=True
groups=pd.read_csv(R/'subgroups.csv')
for _,r in groups.iterrows():
    assert r.TP+r.FN==r.positives and r.TP+r.FN+r.TN+r.FP==r.n
    assert 0<=r.recall_low<=r.recall<=r.recall_high<=1
checks['subgroup_denominators_and_rate_intervals']=True
sub=json.loads((R/'feature_subsets.json').read_text())
assert all(not set(cols)&{'G1','G2','G3'} for cols in sub.values())
assert len(sub['all'])==30 and len(sub['no_absences'])==29 and len(sub['no_failures'])==29 and len(sub['reduced_sensitive'])==15
checks['feature_exclusion_schemas']=True
ci=pd.read_csv(R/'bootstrap_intervals.csv');assert len(ci)==32 and np.isfinite(ci[['point','low','high']]).all().all()
checks['bootstrap_table_complete_and_finite']=True
assert json.loads((R/'reproduction_checks.json').read_text())['passed']
checks['original_reproduction']=True
(R/'output_verification.json').write_text(json.dumps({'status':'passed','checks':checks},indent=2))
print('Verified',len(checks),'scientific output groups')
