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
fig,ax=plt.subplots(figsize=(6.8,1.8)); ax.axis('off'); ax.set_xlim(-3,103); ax.set_ylim(-1,21)
boxes=[('shop_sim.py\n9 visitor types,\n6,000 sessions',0),('access.log\n+ labels.csv\n(simulator)',20.5),('build_shop_\nfeatures.py\n16 features\nper session',41),('OptIForest\n(authors\' code)\n+ Isolation Forest',61.5),('AUC-ROC and\nAUC-PR, mean $\\pm$ SD\nover runs',82)]
for t,x in boxes:
    ax.add_patch(FancyBboxPatch((x+0.3,3.5),17.4,14,boxstyle='round,pad=0.3',fc='#eef3f8',ec='#4c78a8',lw=1))
    ax.text(x+9,10.5,t,ha='center',va='center',fontsize=5.8)
for x in [18.0,38.5,59.0,79.5]:
    ax.annotate('',xy=(x+2.3,10.5),xytext=(x,10.5),arrowprops=dict(arrowstyle='->',color='#444'))
ax.text(50,1.2,'labels kept separate from the features until evaluation',ha='center',fontsize=6.5,style='italic',color='#555')
plt.savefig('pipeline.pdf',bbox_inches='tight',pad_inches=0.1); plt.close()

# --- Fig C: schematic of binary vs multi-way isolation tree (illustration only)
import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,2,figsize=(3.3,1.9))
def node(ax,x,y,hl=False,leaf=False):
    ax.add_patch(plt.Circle((x,y),0.11,fc='#d62728' if hl and leaf else ('#f4b6b6' if hl else '#eef3f8'),ec='#4c78a8',lw=0.8,zorder=3))
def edge(ax,a,b,hl=False):
    ax.plot([a[0],b[0]],[a[1],b[1]],color='#d62728' if hl else '#888',lw=1.4 if hl else 0.8,zorder=1)
# binary: normal point goes deep (3 splits), anomaly isolated after 1 split
ax=axs[0]; ax.axis('off'); ax.set_xlim(-0.2,2.45); ax.set_ylim(-0.4,3.2)
P={'r':(1,3),'a':(0.3,2),'b':(1.7,2),'c':(1.3,1),'d':(2.1,1),'e':(1.0,0.0),'f':(1.6,0.0)}
for p,q,h in [('r','a',True),('r','b',False),('b','c',False),('b','d',False),('c','e',False),('c','f',False)]: edge(ax,P[p],P[q],h)
for k,(x,y) in P.items(): node(ax,x,y,hl=(k in 'ra'),leaf=(k=='a'))
ax.set_title('binary tree',fontsize=6.5)
ax=axs[1]; ax.axis('off'); ax.set_xlim(-0.2,2.45); ax.set_ylim(-0.4,3.2)
Q={'r':(1,3),'a':(0.2,2),'b':(1,2),'c':(1.8,2),'d':(1.5,1),'e':(2.1,1),'f':(1.2,1)}
for p,q,h in [('r','a',True),('r','b',False),('r','c',False),('c','d',False),('c','e',False),('c','f',False)]: edge(ax,Q[p],Q[q],h)
for k,(x,y) in Q.items(): node(ax,x,y,hl=(k in 'ra'),leaf=(k=='a'))
ax.set_title('multi-way tree',fontsize=6.5)
plt.tight_layout(pad=0.3); plt.savefig('method_trees.pdf'); plt.close()
