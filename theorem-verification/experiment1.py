import numpy as np, math, sys
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); pi=np.real(V[:,i]); return pi/pi.sum()
K=12
def make_chain(h_target,seed=3):
    rng=np.random.default_rng(seed); L=rng.random((K,K))
    def rate(t):
        Q=np.exp(L/t); Q/=Q.sum(1,keepdims=True); pi=stat(Q)
        return float(sum(pi[b]*H(Q[b]) for b in range(K))),Q
    lo,hi=1e-3,60.0
    for _ in range(45):
        mid=math.sqrt(lo*hi)
        if rate(mid)[0]<h_target: lo=mid
        else: hi=mid
    return rate(math.sqrt(lo*hi))[1], rate(math.sqrt(lo*hi))[0]
def groups(w,G,perm):
    """C-bit code: greedy balanced split of belief mass in a per-agent random order
       (so two agents hold genuinely different C-bit channels, not the same one)"""
    order=perm
    mass=np.zeros(G); grp=np.empty(len(w),dtype=np.int64)
    for i in order:
        j=int(mass.argmin()); grp[i]=j; mass[j]+=w[i]
    return grp
def run(Q,C,m,encoder,T=1500,seed=7):
    rng=np.random.default_rng(seed); G=2**C
    perms=[rng.permutation(K*m if encoder=="naive" else K) for _ in range(2)]
    b=rng.integers(K); bel=[np.ones(K)/K for _ in range(2)]
    ag=[];co=[];hs=[]
    for t in range(T):
        b=rng.choice(K,p=Q[b]); u=rng.integers(m); est=[]
        for i in range(2):
            pred=bel[i]@Q
            if encoder=="class-aware":
                g=groups(pred,G,perms[i]); post=np.where(g==g[b],pred,0.0)
            else:
                w=np.repeat(pred/m,m); g=groups(w,G,perms[i])
                keep=(g==g[b*m+u]).reshape(K,m).sum(1)/m; post=pred*keep
            s=post.sum(); bel[i]=post/s if s>1e-12 else pred
            est.append(int(bel[i].argmax()))
        if t>T//3: ag.append(est[0]==est[1]); co.append(est[0]==b and est[1]==b); hs.append(H(bel[0]))
    return np.mean(ag),np.mean(co),np.mean(hs)
P=lambda *a: print(*a,flush=True)
P("EXPERIMENT 1 - prediction 4': cooperation collapses when capacity C < h_theta")
P(f"two agents, independent C-bit channels, K={K} operational classes; 'agree' = Theorem 3 condition\n")
chains={ht:make_chain(ht) for ht in [0.25,0.5,1.0,1.5,2.0,2.5,3.0]}
for C in [1,2,3]:
    P(f"  C = {C} bits/step")
    P("   h_theta   agree   both-correct   H_theta(meas)   Thm-2 floor   gap")
    for ht,(Q,h) in chains.items():
        a,c,hs=run(Q,C,1,"class-aware")
        P(f"    {h:5.2f}    {a:5.3f}      {c:5.3f}          {hs:6.3f}        {max(0,h-C):5.3f}      {hs-max(0,h-C):5.3f}")
    P("")
P("EXPERIMENT 2 - insensitivity to physical-state uncertainty (h_theta=1.0, C=2)")
P("  H_S = H_theta + log2(m);  m = physical sub-states per class")
P("   m   log2 m   agree: class-aware coder   agree: naive state coder")
Q,h=chains[1.0]
for m in [1,2,4,8,16,32]:
    a1,_,_=run(Q,2,m,"class-aware"); a2,_,_=run(Q,2,m,"naive")
    P(f"  {m:3d}  {math.log2(m):5.2f}         {a1:5.3f}                  {a2:5.3f}")
