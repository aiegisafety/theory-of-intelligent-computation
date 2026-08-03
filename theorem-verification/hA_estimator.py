import numpy as np, math
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def Hcond(a,b):
    a=np.asarray(a); b=np.asarray(b); n=len(a); out=0.0
    for bv in set(b):
        idx=np.where(b==bv)[0]
        _,c=np.unique(a[idx],return_counts=True); out+=(len(idx)/n)*H(c/c.sum())
    return out
N,K=12,3
rng0=np.random.default_rng(2); Q=rng0.random((K,K))**2; Q/=Q.sum(1,keepdims=True)
def kernel_of(lab):
    T=np.array([[Q[lab[s],lab[t]]/max((lab==lab[t]).sum(),1) for t in range(N)] for s in range(N)])
    return T/T.sum(1,keepdims=True)
def refine(Tk,eps):
    """agglomerative: start from singletons, merge blocks whose block-transition rows agree
       within eps in TV; iterate to a fixed point (no goal seed needed)"""
    part=np.arange(N)
    while True:
        Bs=sorted(set(part))
        R=np.array([[Tk[np.array(part)==b].mean(0)[np.array(part)==c].sum() for c in Bs] for b in Bs])
        merged={}; reps=[]
        for i,b in enumerate(Bs):
            hit=None
            for k,r in enumerate(reps):
                if 0.5*np.abs(R[i]-R[r]).sum()<=eps: hit=k; break
            if hit is None: reps.append(i); merged[b]=len(reps)-1
            else: merged[b]=hit
        new=np.array([merged[x] for x in part])
        if len(set(new))==len(set(part)): break
        part=new
    m={};o=[]
    for x in part:
        if x not in m: m[x]=len(m)
        o.append(m[x])
    return np.array(o)

def run(p_drift,n_per_state,eps=0.15,windows=25,seed=1):
    rng=np.random.default_rng(seed)
    lab=np.array([i%K for i in range(N)]); prev=None; tr=[]; es=[]; blocks=[]
    W=n_per_state*N                                   # world-steps consumed per window
    for _ in range(windows):
        old=lab.copy(); cnt=np.zeros((N,N)); T=kernel_of(lab)
        for i in range(W):
            if rng.random()<p_drift:
                j=rng.integers(N); lab=lab.copy(); lab[j]=rng.integers(K); T=kernel_of(lab)
            s=i%N; cnt[s,rng.choice(N,p=T[s])]+=1
        tr.append(Hcond(lab,old)/W)
        hat=refine(cnt/np.maximum(cnt.sum(1,keepdims=True),1),eps); blocks.append(len(set(hat)))
        if prev is not None: es.append(Hcond(hat,prev)/W)
        prev=hat
    return np.mean(tr),np.mean(es),np.mean(blocks)

P("MAKING h_A MEASURABLE — estimator = sliding-window abstraction learning (Thm 7)")
P("  + conditional entropy between consecutive learned partitions / window length\n")
P(f"  world: N={N} states, K={K} true classes; noise floor ~0.5*sqrt(2K/(pi*n)) must be < eps=0.15\n")
n=200
P(f"  n={n} samples/state per window (noise {0.5*math.sqrt(2*K/(math.pi*n)):.3f} < eps) — VALID REGIME")
P("   p_drift    true h_A     estimated h_A     blocks found")
for p in [0.0,0.0002,0.0005,0.0010,0.0020]:
    t,e,b=run(p,n)
    P(f"   {p:6.4f}   {t:9.6f}    {e:9.6f}        {b:4.1f}")
P("\n  sample budget per window (p_drift fixed at 0.0005):")
P("   n/state   noise    true h_A     estimated h_A    regime")
for n2 in [30,60,120,200,400]:
    t,e,b=run(0.0005,n2)
    noise=0.5*math.sqrt(2*K/(math.pi*n2))
    reg = "noise > eps: unusable" if noise>0.15 else "usable"
    P(f"   {n2:5d}   {noise:6.3f}  {t:9.6f}    {e:9.6f}     {reg}")
