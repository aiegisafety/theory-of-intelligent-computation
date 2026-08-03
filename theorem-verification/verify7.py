import numpy as np, math, itertools
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); return np.real(V[:,i])/np.real(V[:,i]).sum()
def h_of(part,T):
    pi=stat(T); Bs=sorted(set(part)); out=0.0
    for b in Bs:
        idx=np.where(np.array(part)==b)[0]; w=pi[idx]/pi[idx].sum()
        M=np.array([[T[s][np.array(part)==c].sum() for c in Bs] for s in idx])
        out+=pi[idx].sum()*H((w[:,None]*M).sum(0))
    return out
def meet(*ps):   # common refinement: blocks are intersections
    keys={}; out=[]
    for t in zip(*ps):
        if t not in keys: keys[t]=len(keys)
        out.append(keys[t])
    return out

rng=np.random.default_rng(5); N=36
T=rng.random((N,N))**3; T/=T.sum(1,keepdims=True)
P("C6 / Theorem 10 - a shared state serving several tasks pays the COMMON REFINEMENT rate")
P("  N=36 physical states;  h(physical) = %.3f bits/step\n"%h_of(list(range(N)),T))
P("   tasks   |blocks of refinement|   h(common refinement)   max_i h(theta_i)")
parts=[]
for k in range(1,7):
    parts.append(list(rng.integers(0,3,N)))          # each task: a 3-way partition
    cr=meet(*parts)
    P(f"     {k}            {len(set(cr)):3d}                 {h_of(cr,T):7.3f}            {max(h_of(p,T) for p in parts):7.3f}")
P("\n  -> serving k tasks costs the refinement's rate, which climbs toward the physical rate.")
P("     General-purpose state sharing is expensive BY THEOREM; task-specific channels are cheap.")

P("\nC7 / Theorem 8 - identity constraints make an entity cheaper for others to track")
lab=np.array([i%6 for i in range(N)])
free=h_of(list(range(N)),T)
Tc=T.copy()                                            # identity constraint: forbid leaving one's own class
for s in range(N):
    Tc[s]=np.where(lab==lab[s],T[s],0.0); Tc[s]/= Tc[s].sum()
P(f"   unconstrained agent  h = {free:.3f} bits/step")
P(f"   identity-constrained h = {h_of(list(range(N)),Tc):.3f} bits/step   (conditioning reduces entropy)")
