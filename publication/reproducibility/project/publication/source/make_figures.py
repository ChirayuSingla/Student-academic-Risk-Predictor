from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve,precision_recall_curve,ConfusionMatrixDisplay,confusion_matrix
B=Path(__file__).resolve().parents[1];R=B/'results';F=B/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
names={'logistic_regression':'LR','decision_tree':'DT','random_forest':'RF','gradient_boosting':'GB','always_at_risk':'Always risk','majority':'Majority','prevalence':'Prevalence','prior_failure':'Prior failure'}
colors=['#176b91','#c64b45','#258c70','#9663b6']
def save(fig,name):
    fig.tight_layout()
    for ext in ['png','pdf','svg']:fig.savefig(F/(name+'.'+ext),dpi=600,bbox_inches='tight')
    plt.close(fig)
p=pd.read_csv(R/'heldout_predictions.csv');y=p.y
fig,ax=plt.subplots(2,1,figsize=(3.35,4.8))
for a,n in zip(ax,['logistic_regression','decision_tree']):
    ConfusionMatrixDisplay(confusion_matrix(y,p[n]>=.5),display_labels=['Pass','Fail']).plot(ax=a,cmap='Blues',colorbar=False)
    a.set_title(names[n]);a.set_xlabel('Predicted');a.set_ylabel('Observed')
save(fig,'figure1_confusion')
fig,ax=plt.subplots(2,1,figsize=(3.35,4.8))
for n,c in zip(list(names)[:4],colors):
    a,b,_=roc_curve(y,p[n]);ax[0].plot(a,b,label=names[n],c=c)
    a,b,_=precision_recall_curve(y,p[n]);ax[1].step(b,a,label=names[n],where='post',c=c)
ax[0].plot([0,1],[0,1],'k--',lw=.6);ax[1].axhline(y.mean(),ls='--',c='gray',lw=.8)
ax[0].set(xlabel='False positive rate',ylabel='Recall',title='ROC');ax[1].set(xlabel='Recall',ylabel='Precision',title='Precision-recall')
for a in ax:a.legend(fontsize=8);a.set_xlim(0,1);a.set_ylim(0,1.02)
save(fig,'figure2_curves')
n=pd.read_csv(R/'nested_fold_metrics.csv');keep=['logistic_regression','decision_tree','random_forest','gradient_boosting','prior_failure','always_at_risk']
fig,ax=plt.subplots(figsize=(3.35,3.1))
for j,m in enumerate(keep):
    z=n[(n.model==m)&(n.subset=='all')].f2.to_numpy()
    ax.scatter(z,np.full(len(z),j)+np.linspace(-.12,.12,len(z)),s=18,c=colors[j%4],alpha=.65)
    ax.plot([z.mean()],[j],'k|',ms=18,mew=2)
ax.set(yticks=range(len(keep)),yticklabels=[names[m] for m in keep],xlabel='Outer-validation F2 at threshold 0.5',xlim=(0,1))
ax.invert_yaxis();save(fig,'figure3_nested')
cal=pd.read_csv(R/'calibration_bins.csv')
fig,ax=plt.subplots(2,1,figsize=(3.35,4.8))
for a,name in zip(ax,['logistic_regression','decision_tree']):
    for suffix,color,lab in [('',colors[0],'Raw'),('__sigmoid',colors[1],'Sigmoid')]:
        z=cal[cal.model==name+suffix]
        a.errorbar(z.mean_probability,z.observed_fraction,yerr=[z.observed_fraction-z.low,z.high-z.observed_fraction],fmt='o-',c=color,label=lab,ms=4,capsize=2)
    a.plot([0,1],[0,1],'k--',lw=.6);a.set(title=names[name],xlabel='Mean predicted probability',ylabel='Observed risk fraction',xlim=(0,1),ylim=(0,1));a.legend(fontsize=8)
save(fig,'figure4_calibration')
imp=pd.read_csv(R/'permutation_stability.csv')
fig,ax=plt.subplots(2,1,figsize=(3.35,5.2))
for a,m,c in zip(ax,['logistic_regression','decision_tree'],colors):
    z=imp[imp.model==m].groupby('feature').mean_ap_decrease.agg(['mean','std']).sort_values('mean').tail(8)
    a.barh(z.index,z['mean'],xerr=z['std'],color=c,capsize=2);a.axvline(0,c='k',lw=.6);a.set(title=names[m],xlabel='AP decrease after permutation')
save(fig,'figure5_importance')
t=pd.read_csv(R/'threshold_sensitivity.csv')
fig,ax=plt.subplots(2,1,figsize=(3.35,4.3))
for m,c in zip(['logistic_regression','decision_tree'],colors):
    z=t[t.model==m];ax[0].plot(z.threshold,z.recall,'o-',c=c,label=names[m]);ax[1].plot(z.threshold,z['flags'],'o-',c=c,label=names[m])
ax[0].set(xlabel='Threshold',ylabel='Recall',ylim=(0,1.05));ax[1].set(xlabel='Threshold',ylabel='Students flagged',ylim=(0,80))
for a in ax:a.legend()
save(fig,'figure6_thresholds')
g=pd.read_csv(R/'subgroups.csv');fig,ax=plt.subplots(figsize=(3.35,3.1))
for j,(m,c) in enumerate(zip(['logistic_regression','decision_tree'],colors)):
    z=g[(g.model==m)&(g.attribute=='sex')].sort_values('group')
    x=np.arange(len(z))+(j-.5)*.15
    ax.errorbar(x,z.recall,yerr=[z.recall-z.recall_low,z.recall_high-z.recall],fmt='o',c=c,capsize=4,label=names[m])
ax.set(xticks=[0,1],xticklabels=['Recorded F','Recorded M'],ylabel='Recall with 95% Wilson interval',ylim=(0,1.05));ax.legend()
save(fig,'figure7_subgroups')
print('Seven figures saved as 600 dpi PNG, vector SVG and PDF')
