import numpy as np, math
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]
    return float(-(p*np.log2(p)).sum())

# State: random walk on Z_m ; step uniform over q values -> entropy rate h = log2 q
# Observation: which of 2^C equal bins the state lies in -> at most C bits per step
def steady_state_U(m,q,C,T=4000):
    step=np.arange(q)                      # move +0..+q-1 mod m
    nbins=2**C
    binof=(np.arange(m)*nbins)//m          # bin index of each state
    b=np.ones(m)/m                         # belief over states
    rng=np.random.default_rng(1)
    s=rng.integers(m)
    Us=[]
    for t in range(T):
        # predict
        pred=np.zeros(m)
        for d in step: pred+=np.roll(b,d)/q
        s=(s+rng.choice(step))%m
        # observe: learn the bin
        y=binof[s]
        post=np.where(binof==y,pred,0.0); post/=post.sum()
        b=post
        if t>T//2: Us.append(H(b))
    return float(np.mean(Us))

print(" m   q   C |   h=log2 q   h-C(floor)   measured U_inf   floor respected")
for (m,q,C) in [(64,8,1),(64,8,2),(64,8,3),(64,4,1),(64,16,2),(128,16,1),(128,2,1),(64,8,4)]:
    h=math.log2(q); U=steady_state_U(m,q,C)
    print(f"{m:4d}{q:4d}{C:4d} |   {h:6.3f}      {h-C:7.3f}        {U:7.3f}        {'OK' if U>=h-C-1e-9 else 'VIOLATED'}")

# tightness check: when C >= h, floor is vacuous (<=0) and U can approach 0
print()
print("note: floor is informative only when C < h (channel slower than the world).")
