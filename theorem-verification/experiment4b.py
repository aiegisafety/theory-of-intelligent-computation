import numpy as np, math
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); v=np.abs(np.real(V[:,i])); return v/v.sum()
def h_of(part,T):
    pi=stat(T); part=np.array(part); Bs=sorted(set(part)); out=0.0
    for b in Bs:
        idx=np.where(part==b)[0]; w=pi[idx]/pi[idx].sum()
        M=np.array([[T[s][part==c].sum() for c in Bs] for s in idx])
        out+=pi[idx].sum()*H((w[:,None]*M).sum(0))
    return out
def refine(T,g,eps=0.0):
    N=len(T); part=np.array(g,dtype=int)
    for _ in range(N):
        new=part.copy(); nxt=part.max()+1; changed=False
        for b in sorted(set(part)):
            idx=np.where(part==b)[0]
            if len(idx)<2: continue
            R=np.array([[T[s][part==c].sum() for c in sorted(set(part))] for s in idx])
            reps=[0]; asg={0:0}
            for j in range(1,len(idx)):
                hit=None
                for k,r in enumerate(reps):
                    if 0.5*np.abs(R[j]-R[r]).sum()<=eps: hit=k; break
                if hit is None: reps.append(j); asg[j]=len(reps)-1
                else: asg[j]=hit
            if len(reps)>1:
                changed=True
                for j,s in enumerate(idx):
                    if asg[j]>0: new[s]=nxt+asg[j]-1
                nxt+=len(reps)-1
        part=new
        if not changed: break
    m={};o=[]
    for x in part:
        if x not in m: m[x]=len(m)
        o.append(m[x])
    return np.array(o)

P("THEOREM 12.1 revisited - when does the viability goal generate a real abstraction?\n")
rng=np.random.default_rng(11)

P("A) STRUCTURED world (states group into 5 behavioural kinds, 6 copies each, N=30)")
N,Kt,m=30,5,6
lab=np.repeat(np.arange(Kt),m)
Q=rng.random((Kt,Kt))**2; Q/=Q.sum(1,keepdims=True)
Ts=np.array([[Q[lab[s],lab[t]]/m for t in range(N)] for s in range(N)])
hp=h_of(list(range(N)),Ts)
for frac in [0.2,0.4,0.6]:
    viable=np.zeros(N,dtype=int)
    viable[rng.choice(N,int(N*frac),replace=False)]=1
    p=refine(Ts,viable)
    P(f"   |Omega_D|/|S|={frac:.1f}  ->  {len(set(p)):2d} blocks of {N},  h_theta={h_of(p,Ts):.3f}  (h_phys={hp:.3f})")

P("\nB) UNSTRUCTURED world (generic dense random kernel, N=30) - exact refinement")
Tu=rng.random((N,N))**3; Tu/=Tu.sum(1,keepdims=True)
hpu=h_of(list(range(N)),Tu)
viable=np.zeros(N,dtype=int); viable[rng.choice(N,12,replace=False)]=1
p=refine(Tu,viable)
P(f"   -> {len(set(p))} blocks of {N},  h_theta={h_of(p,Tu):.3f}  (h_phys={hpu:.3f})   NO COMPRESSION")

P("\nC) UNSTRUCTURED world - eps-refinement (accepting approximate adequacy)")
for eps in [0.05,0.10,0.20,0.30]:
    p=refine(Tu,viable,eps)
    P(f"   eps={eps:.2f}  ->  {len(set(p)):2d} blocks,  h_theta={h_of(p,Tu):.3f}  (h_phys={hpu:.3f})")
P("\n  Conclusion: viability generates an ontology only if the world HAS one.")
P("  In a structureless world the free goal buys nothing exactly, and buys compression")
P("  only by accepting approximation - i.e. by paying the Theorem 6 error term.")
