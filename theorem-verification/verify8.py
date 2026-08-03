import numpy as np
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); v=np.real(V[:,i]); v=np.abs(v); return v/v.sum()
def hrate(T):
    pi=stat(T); return float(sum(pi[s]*H(T[s]) for s in range(len(T))))
rng=np.random.default_rng(5); N=36
T=rng.random((N,N))**3; T/=T.sum(1,keepdims=True)
lab=np.array([i%6 for i in range(N)])
P("Theorem 8 - identity as a transition constraint lowers the rate at which OTHERS must track you")
P("  lambda = probability of leaving one's identity manifold (1.0 = unconstrained)")
P("   lambda    h(agent) bits/step")
for lam in [1.0,0.7,0.5,0.3,0.2,0.1,0.05]:
    Tc=np.zeros_like(T)
    for s in range(N):
        inn=np.where(lab==lab[s],T[s],0.0); inn/=inn.sum()
        Tc[s]=(1-lam)*inn+lam*T[s]
    P(f"    {lam:4.2f}        {hrate(Tc):6.3f}")
P("\n  monotone: the tighter the identity, the fewer bits/step a partner needs (Theorem 6.1).")
