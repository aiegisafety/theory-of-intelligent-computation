import numpy as np, math
rng=np.random.default_rng(23)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def Hb(x):
    return 0.0 if x<=0 or x>=1 else -(x*math.log2(x)+(1-x)*math.log2(1-x))
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); pi=np.real(V[:,i]); return pi/pi.sum()

# ---- build a chain that is eps-lumpable w.r.t. a planted partition ----
def make(n,K,eps,rng):
    lab=np.array([i%K for i in range(n)])
    Q=rng.random((K,K)); Q/=Q.sum(1,keepdims=True)          # class-level kernel
    T=np.zeros((n,n))
    for s in range(n):
        base=np.array([Q[lab[s],lab[t]]/(lab==lab[t]).sum() for t in range(n)])
        pert=rng.random(n); pert/=pert.sum()
        T[s]=(1-eps)*base+eps*pert                          # perturbation => eps-lumpable-ish
        T[s]/=T[s].sum()
    return T,lab,Q

print("THEOREM 6.1  general floor needs NO lumpability:  H(B_{t+1}|S_t) <= H(B_{t+1}|B_t), gap = I(B;S|B)")
print("THEOREM 6.2  gap <= eps*log2(K-1) + Hb(eps)   [Fannes-Audenaert]")
print()
print("  eps    measured TV   H(B'|B)   H(B'|S)     gap    bound   bound holds")
for eps in [0.0,0.02,0.05,0.1,0.2,0.35]:
    gaps=[];bnds=[];tvs=[]
    for trial in range(12):
        n,K=48,6
        T,lab,Q=make(n,K,eps,rng)
        pi=stat(T)
        # class-transition row for each state
        R=np.zeros((n,K))
        for s in range(n):
            for c in range(K): R[s,c]=T[s][lab==c].sum()
        # block-average rows, and measured within-block TV
        tv=0.0; HBgivenB=0.0; HBgivenS=0.0
        for c in range(K):
            idx=np.where(lab==c)[0]; w=pi[idx]/pi[idx].sum()
            Rbar=(w[:,None]*R[idx]).sum(0)
            tv=max(tv,max(0.5*abs(R[s]-Rbar).sum() for s in idx))
            HBgivenB+=pi[idx].sum()*H(Rbar)
            HBgivenS+=sum(pi[s]*H(R[s]) for s in idx)
        gap=HBgivenB-HBgivenS
        e=tv
        bnd=e*math.log2(K-1)+Hb(e)
        gaps.append(gap);bnds.append(bnd);tvs.append(tv)
    print(f"  {eps:4.2f}     {np.mean(tvs):6.3f}   {HBgivenB:7.3f}  {HBgivenS:7.3f}  {np.mean(gaps):7.3f} {np.mean(bnds):7.3f}   "
          f"{'OK' if all(g<=b+1e-9 for g,b in zip(gaps,bnds)) else 'VIOLATED'}")

print()
print("  monotone: gap -> 0 as eps -> 0  (this is the continuity the bandwidth law needs)")
