import numpy as np, math
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); v=np.abs(np.real(V[:,i])); return v/v.sum()
def rate(T):
    pi=stat(T); return float(sum(pi[s]*H(T[s]) for s in range(len(T))))
def tune(Kd,target,seed):
    rng=np.random.default_rng(seed); L=rng.random((Kd,Kd))
    lo,hi=1e-3,60.0
    for _ in range(40):
        mid=math.sqrt(lo*hi); Q=np.exp(L/mid); Q/=Q.sum(1,keepdims=True)
        if rate(Q)<target: lo=mid
        else: hi=mid
    Q=np.exp(L/math.sqrt(lo*hi)); Q/=Q.sum(1,keepdims=True); return Q,rate(Q)

K,M=8,4                      # K operational classes, M ontology regimes
def run(h_theta,h_A,C,T=1200,seed=4):
    QA,hA=tune(M,h_A,seed)                                  # regime (ontology) chain
    QB=[tune(K,h_theta,seed+10+r)[0] for r in range(M)]     # class kernel depends on regime
    hB=np.mean([rate(q) for q in QB])
    rng=np.random.default_rng(seed+99); G=2**C
    r,b=rng.integers(M),rng.integers(K)
    bel=np.ones((M,K))/(M*K)                                # joint belief over (regime,class)
    ok=[]
    for t in range(T):
        r=rng.choice(M,p=QA[r]); b=rng.choice(K,p=QB[r][b])
        pred=np.zeros((M,K))                                # predict
        for rr in range(M):
            for r2 in range(M): pred[r2]+=bel[rr].sum()*QA[rr,r2]*(bel[rr]@QB[rr])/max(bel[rr].sum(),1e-12)
        pred/=pred.sum()
        w=pred.ravel(); order=rng.permutation(len(w))       # C-bit balanced code
        mass=np.zeros(G); grp=np.empty(len(w),dtype=int)
        for i in order:
            j=int(mass.argmin()); grp[i]=j; mass[j]+=w[i]
        obs=grp[r*K+b]
        post=np.where(grp==obs,w,0.0); s=post.sum()
        bel=(post/s).reshape(M,K) if s>1e-12 else pred
        if t>T//3: ok.append(int(bel.sum(0).argmax())==b)    # class estimate correct?
    return hA,hB,np.mean(ok)

P("EXPERIMENT 3 - Theorem 11: capacity must cover BOTH levels,  C >= h_theta + h_A")
P("  h_theta = rate of the operational state;  h_A = rate at which the world changes the ontology\n")
for C in [2,3,4]:
    P(f"  C = {C} bits/step   (h_theta fixed at 1.5)")
    P("    h_A    h_theta+h_A    class-correct")
    for hA in [0.1,0.5,1.0,1.5,2.0,2.5]:
        a,b,acc=run(1.5,hA,C)
        flag="   <-- exceeds C" if b+a>C else ""
        P(f"   {a:5.2f}     {b+a:6.2f}         {acc:5.3f}{flag}")
    P("")
