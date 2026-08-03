exec(open('experiment2.py').read().split("T,lab,Q,g=build()")[0])
import numpy as np
P=lambda *a: print(*a,flush=True)
T,lab,Q,g=build(); truth=refine(T,g,0.0)
P("epsilon sweep at n=5000 (estimation noise ~0.014) - where does over-merging begin?")
P("   eps    blocks   over-merge   over-split   h_theta(learned)")
for eps in [0.01,0.02,0.04,0.06,0.08,0.10,0.12,0.15,0.18,0.20,0.25]:
    oms=[];oss=[];hts=[];blks=[]
    for r in range(12):
        rng=np.random.default_rng(500+r)
        p=refine(sample_kernel(T,5000,rng),g,eps)
        om,os=pair_stats(p,truth); oms.append(om);oss.append(os);hts.append(h_theta(p,T));blks.append(len(set(p)))
    P(f"  {eps:5.2f}    {np.mean(blks):5.1f}     {np.mean(oms):7.3f}      {np.mean(oss):7.3f}        {np.mean(hts):7.3f}")
P("\n  target: 6 blocks, over-merge 0.000, h_theta* = 2.067")
