import math,sys,numpy as np
sys.path.insert(0,'.')
from test_asym import build
ref={(4,0.3):(0.05,0.45,2.707,1.612,2.726),(4,0.6):(0.05,0.45,1.916,1.909,3.180),(6,0.15):(0.05,0.45,2.989,1.424,2.459),(6,0.55):(0.02,0.60,2.084,1.856,3.105)}
keys=[tuple(map(float,a.split(','))) for a in sys.argv[1:]]
for k in keys:
    m,dg=int(k[0]),k[1]; lo,hi,h0,s0,w0=ref[(m,dg)]
    env,P,mu,nb,ht,sg,shapes=build(m,lo,hi,0.15,dg)
    v=[];w=[]
    for i in range(nb):
        for j in range(nb):
            if P[i,j]>1e-14: v.append(-math.log2(P[i,j])); w.append(mu[i]*P[i,j])
    v=np.array(v);w=np.array(w);w/=w.sum();o=np.argsort(v);v,w=v[o],w[o];cw=np.cumsum(w)
    W=float(np.interp(0.8,cw,v)-np.interp(0.2,cw,v))
    ok=abs(ht-h0)<1e-3 and abs(sg-s0)<1e-3 and abs(W-w0)<1e-3
    print('m=%d drag=%.2f blocks=%d shapes=%d h_th=%.3f(was %.3f) sigma=%.3f(was %.3f) W=%.3f(was %.3f) %s'%(m,dg,nb,shapes,ht,h0,sg,s0,W,w0,'UNCHANGED' if ok else '*** CHANGED ***'),flush=True)
