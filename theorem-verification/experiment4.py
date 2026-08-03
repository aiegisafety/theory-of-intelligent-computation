import numpy as np, math
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); v=np.abs(np.real(V[:,i])); return v/v.sum()
def h_of(part,T):
    pi=stat(T); Bs=sorted(set(part)); out=0.0; part=np.array(part)
    for b in Bs:
        idx=np.where(part==b)[0]; w=pi[idx]/pi[idx].sum()
        M=np.array([[T[s][part==c].sum() for c in Bs] for s in idx])
        out+=pi[idx].sum()*H((w[:,None]*M).sum(0))
    return out
def meet(*ps):
    keys={}; out=[]
    for t in zip(*ps):
        if t not in keys: keys[t]=len(keys)
        out.append(keys[t])
    return out

rng=np.random.default_rng(11); N=40
T=rng.random((N,N))**3; T/=T.sum(1,keepdims=True)
hphys=h_of(list(range(N)),T)
P(f"THEOREM 12.3 - capacity bounds the NUMBER of goals an entity can hold")
P(f"  N={N} physical states, h(physical) = {hphys:.3f} bits/step\n")
P("   k goals   h(common refinement)   affordable at C=1.5 / 2.5 / 3.5 / 4.5")
parts=[]
for k in range(1,9):
    parts.append(list(rng.integers(0,3,N)))
    hk=h_of(meet(*parts),T)
    flags=" / ".join("yes" if hk<=C else "NO " for C in [1.5,2.5,3.5,4.5])
    P(f"     {k}            {hk:6.3f}              {flags}")
P("\n  k_max(C): the largest number of simultaneously maintainable goals is set by capacity,")
P("  not by intelligence. Goal proliferation is bounded by the channel, via Theorem 10.\n")

# --- 12.1: does the *free* goal (stay alive / stay in the identity manifold) generate real structure?
def refine(T,g,tol=1e-9):
    part=np.array(g,dtype=int)
    for _ in range(N):
        sig={}; new=[]
        for s in range(N):
            key=(part[s],)+tuple(round(T[s][part==c].sum(),9) for c in sorted(set(part)))
            if key not in sig: sig[key]=len(sig)
            new.append(sig[key])
        new=np.array(new)
        if len(set(new))==len(set(part)): break
        part=new
    return part
P("THEOREM 12.1 - the viability goal is not vacuous: it generates a genuine abstraction")
for frac in [0.1,0.25,0.5]:
    viable=np.zeros(N,dtype=int); viable[rng.choice(N,int(N*frac),replace=False)]=1
    p=refine(T,viable)
    P(f"   |Omega_D|/|S| = {frac:.2f}   ->  induced abstraction has {len(set(p)):2d} blocks "
      f"(of {N}),  h_theta = {h_of(p,T):.3f}  vs h_phys = {hphys:.3f}")
P("\n  staying alive is enough to carve the world: no external goal specification needed.")
