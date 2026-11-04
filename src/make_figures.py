import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.size':8,'font.family':'serif'})
# --- Fig A: results chart
ds=['AD (replication)','Web shop','HDFS']
raw=[(.772,.006,.435,.043),(.889,.004,.387,.024),(.762,.007,.167,.020)]
std=[None,(.962,.0015,.834,.011),(.745,.0085,.186,.0141)]
isf=[(.683,.018,.378,.058),(.959,.003,.790,.019),(.792,.005,.540,.005)]
series=[('OptIForest, raw features',raw,'#4c78a8',''),('OptIForest, standardised',std,'#f58518','//'),('Isolation Forest',isf,'#54a24b','..')]
fig,axs=plt.subplots(1,2,figsize=(6.8,2.5),sharey=True)
for ax,(k,name) in zip(axs,[(0,'AUC-ROC'),(2,'AUC-PR')]):
    w=0.26
    for j,(lab,dat,c,h) in enumerate(series):
        for i,d in enumerate(dat):
            if d is None:
                ax.text(i+(j-1)*w,0.03,'n/a',ha='center',fontsize=6,color='gray'); continue
            ax.bar(i+(j-1)*w,d[k],w*0.95,yerr=d[k+1],color=c,hatch=h,edgecolor='white',capsize=2,label=lab if i==0 or (i==1 and j==1) else None)
    ax.set_xticks(range(3)); ax.set_xticklabels(ds); ax.set_title(name); ax.set_ylim(0,1.05)
    ax.spines[['top','right']].set_visible(False); ax.grid(axis='y',alpha=.3)
h,l=axs[0].get_legend_handles_labels(); u=dict(zip(l,h))
fig.legend(u.values(),u.keys(),loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(0.5,-0.04))
axs[0].set_ylabel('score (mean $\\pm$ SD)')
plt.tight_layout(rect=(0,0.08,1,1)); plt.savefig('results_chart.pdf'); plt.close()
# --- Fig B: pipeline
fig,ax=plt.subplots(figsize=(6.8,1.5)); ax.axis('off'); ax.set_xlim(0,100); ax.set_ylim(0,20)
boxes=[('shop_sim.py\n9 visitor types,\n6,000 sessions',0),('access.log\n+ labels.csv\n(simulator)',20),('build_shop_features.py\n16 features per\nsession',40),('OptIForest\n(authors\' code)\n+ Isolation Forest',62),('AUC-ROC, AUC-PR\nmean $\\pm$ SD\nover runs',82)]
for t,x in boxes:
    ax.add_patch(FancyBboxPatch((x,4),17,12,boxstyle='round,pad=0.4',fc='#eef3f8',ec='#4c78a8'))
    ax.text(x+8.5,10,t,ha='center',va='center',fontsize=7)
for x in [17.9,37.9,57.9,79.9]:
    ax.annotate('',xy=(x+2.1,10),xytext=(x,10),arrowprops=dict(arrowstyle='->',color='#444'))
ax.text(29,1,'labels kept separate from the features until evaluation',ha='center',fontsize=6.5,style='italic',color='#555')
plt.savefig('pipeline.pdf',bbox_inches='tight'); plt.close()
