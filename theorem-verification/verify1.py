import numpy as np, itertools, math
rng=np.random.default_rng(0)
def H(p):
    p=np.asarray(p,dtype=float); p=p[p>0]
    return float(-(p*np.log2(p)).sum())
def Hb(p):
    if p<=0 or p>=1: return 0.0
    return -(p*math.log2(p)+(1-p)*math.log2(1-p))

# 1) exact identity  DeltaH = Hb(p) + p[H(P_B) - H(P_A)]
maxerr=0.0
for trial in range(200000):
    n=rng.integers(2,9)
    P=rng.random(n); P/=P.sum()
    k=rng.integers(1,n)           # remove k of n
    idx=rng.permutation(n); B=idx[:k]; A=idx[k:]
    p=P[B].sum()
    if p<=0 or p>=1: continue
    PA=P[A]/P[A].sum(); PB=P[B]/P[B].sum()
    lhs=H(P)-H(PA)
    rhs=Hb(p)+p*(H(PB)-H(PA))
    maxerr=max(maxerr,abs(lhs-rhs))
print("identity max error:", maxerr)

# 2) uniform corollary  DeltaH = -log2(1-p)
errs=[]
for n in range(2,60):
    for k in range(1,n):
        P=np.ones(n)/n; p=k/n
        PA=np.ones(n-k)/(n-k)
        errs.append(abs((H(P)-H(PA))-(-math.log2(1-p))))
print("uniform corollary max error:", max(errs))

# 3) entropy can INCREASE: remove the dominant candidate
P=np.array([0.98,0.01,0.01]); B=[0]; A=[1,2]
PA=P[A]/P[A].sum()
print("dominant-removal: H before=%.4f  after=%.4f  Delta=%.4f"%(H(P),H(PA),H(P)-H(PA)))

# 4) how often does pruning increase H_D? (random P, remove random subset)
inc=0; tot=0
for trial in range(200000):
    n=rng.integers(2,9); P=rng.random(n); P/=P.sum()
    k=rng.integers(1,n); idx=rng.permutation(n); B=idx[:k]; A=idx[k:]
    PA=P[A]/P[A].sum()
    d=H(P)-H(PA); tot+=1; inc+= (d< -1e-12)
print("fraction of prunings that RAISE H_D: %.4f"%(inc/tot))

# 5) single-candidate removal: exact threshold  Delta>0  <=>  H(P_A) < Hb(p)/p
bad=0
for trial in range(200000):
    n=rng.integers(2,9); P=rng.random(n); P/=P.sum()
    j=rng.integers(n); A=[i for i in range(n) if i!=j]; p=P[j]
    if p<=0 or p>=1: continue
    PA=P[A]/P[A].sum()
    d=H(P)-H(PA); pred=(H(PA) < Hb(p)/p)
    if (d>1e-12)!=pred and abs(d)>1e-12: bad+=1
print("threshold test violations:", bad)

# 6) cascade additivity in the uniform case
n=1000; ps=[0.5,0.25,0.4]
cur=n; tot=0.0
for p in ps:
    nxt=int(round(cur*(1-p))); tot+= (math.log2(cur)-math.log2(nxt)); cur=nxt
print("cascade: sum of steps=%.4f   -sum log2(1-p)=%.4f"%(tot, -sum(math.log2(1-p) for p in ps)))
