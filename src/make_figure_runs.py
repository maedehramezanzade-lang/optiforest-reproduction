import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':8,'font.family':'serif'})
roc=[.7691,.7720,.7693,.7664,.7687,.7703,.7702,.7674,.7632,.7793,.7791,.7792,.7745,.7845,.7716]
pr=[.3887,.4231,.4332,.3906,.4434,.4382,.4265,.3935,.3669,.4892,.4616,.4594,.4706,.5352,.4012]
fig,axs=plt.subplots(1,2,figsize=(3.2,2.0))
for ax,v,pm,ps,t in [(axs[0],roc,.774,.007,'AUC-ROC'),(axs[1],pr,.438,.031,'AUC-PR')]:
    x=np.arange(1,16)
    ax.axhspan(pm-ps,pm+ps,color='#f58518',alpha=.25,label='paper $\\pm$ SD')
    ax.axhline(pm,color='#f58518',lw=1)
    ax.plot(x,v,'o',ms=3,color='#4c78a8',label='my runs')
    ax.axhline(np.mean(v),color='#4c78a8',lw=1,ls='--',label='my mean')
    ax.set_title(t); ax.set_xlabel('run'); ax.set_xticks([1,5,10,15])
    ax.spines[['top','right']].set_visible(False); ax.grid(alpha=.3)
h,l=axs[0].get_legend_handles_labels()
fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=6.5,bbox_to_anchor=(0.5,-0.03))
plt.tight_layout(rect=(0,0.1,1,1)); plt.savefig('replication_runs.pdf'); plt.close()
