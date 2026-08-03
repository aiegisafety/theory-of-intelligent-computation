import numpy as np, math
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]
    return float(-(p*np.log2(p)).sum())

# ---- Corollary: bandwidth is set by the QUOTIENT (operational) state, not the physical state
# physical: Z_m random walk, step uniform over q  -> h = log2 q
# task theta: only the coarse block matters (m/K states per block)
def run(m,q,C,K,T=4000):
    nbins=2**C; binof=(np.arange(m)*nbins)//m
    blockof=(np.arange(m)*K)//m
    b=np.ones(m)/m; rng=np.random.default_rng(2); s=rng.integers(m)
    Hs=[];Hth=[];contained=[]
    for t in range(T):
        pred=np.zeros(m)
        for d in range(q): pred+=np.roll(b,d)/q
        s=(s+rng.integers(q))%m
        y=binof[s]; post=np.where(binof==y,pred,0.0); post/=post.sum(); b=post
        if t>T//2:
            Hs.append(H(b))
            cls=np.array([b[blockof==k].sum() for k in range(K)])
            Hth.append(H(cls))
            # is the whole possibility set inside ONE class?
            contained.append(cls.max()>1-1e-9)
    return np.mean(Hs), np.mean(Hth), np.mean(contained)

print("m=64 q=8 (h=3.0 bits/step). K = number of task-relevant classes")
print(" C  K |  H_S(physical)  H_theta(operational)  P[Omega(e) inside one class]")
for C in [1,2,3,4]:
    for K in [64,8,2]:
        hs,ht,ct=run(64,8,C,K)
        print(f" {C}{K:4d} |     {hs:6.3f}            {ht:6.3f}                 {ct:5.2f}")

# ---- Theorem 3 demo: class agreement => identical admissible sets
# operational classes over CPU load; admissible transitions defined per class
cls=lambda x: 0 if x<50 else (1 if x<80 else 2)
A={0:{"idle","noop"},1:{"noop","rebalance"},2:{"scale_out","shed_load"}}
pairs=[(78.0,79.0),(78.0,81.0),(49.9,50.1),(20.0,45.0)]
print("\n  S_A    S_B  | same class? admissible sets equal?  numeric gap")
for a,b in pairs:
    print(f" {a:5.1f} {b:5.1f} |     {str(cls(a)==cls(b)):5s}          {str(A[cls(a)]==A[cls(b)]):5s}        {abs(a-b):4.1f}")
