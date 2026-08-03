import numpy as np, itertools, math
from functools import lru_cache
rng=np.random.default_rng(7)

# ---------- machinery ----------
def blocks_of(part):            # part: array label per state
    return [np.where(part==b)[0] for b in sorted(set(part))]
def canon(part):                # canonical relabel
    m={}; out=[]
    for x in part:
        if x not in m: m[x]=len(m)
        out.append(m[x])
    return tuple(out)

def adequate(part,P,g):
    """(G) blocks agree on goal/constraint label g ; (D) block-transition probs agree, for every action"""
    part=np.asarray(part)
    for B in blocks_of(part):
        if len(set(g[B]))>1: return False           # (G)
        for a in range(P.shape[0]):
            rows=[]
            for s in B:
                rows.append([P[a,s][part==c].sum() for c in sorted(set(part))])
            rows=np.array(rows)
            if np.abs(rows-rows[0]).max()>1e-9: return False   # (D)
    return True

def refine(P,g):
    """partition refinement from the goal partition until (D) holds -> coarsest adequate"""
    part=np.array(g,dtype=int)
    while True:
        sig={}
        for s in range(len(part)):
            key=(part[s],)+tuple(round(P[a,s][part==c].sum(),9)
                                 for a in range(P.shape[0]) for c in sorted(set(part)))
            sig.setdefault(key,len(sig))
        new=np.array([sig[(part[s],)+tuple(round(P[a,s][part==c].sum(),9)
                    for a in range(P.shape[0]) for c in sorted(set(part)))] for s in range(len(part))])
        if len(set(new))==len(set(part)): return canon(new)
        part=new

def join(p1,p2):                # coarsest common coarsening (transitive closure of union)
    n=len(p1); par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    def uni(a,b):
        a,b=find(a),find(b)
        if a!=b: par[a]=b
    for i in range(n):
        for j in range(i+1,n):
            if p1[i]==p1[j] or p2[i]==p2[j]: uni(i,j)
    return canon([find(i) for i in range(n)])

def all_partitions(n):
    def helper(i,cur,k):
        if i==n: yield tuple(cur); return
        for b in range(k):
            cur.append(b); yield from helper(i+1,cur,k); cur.pop()
        cur.append(k); yield from helper(i+1,cur,k+1); cur.pop()
    yield from helper(0,[],0)

def is_coarser(p,q):            # p coarser-or-equal than q  (every q-block inside a p-block)
    return all(len(set(np.array(p)[np.array(q)==b]))==1 for b in set(q))

# ---------- Test 1: exhaustive check that the coarsest adequate partition exists, is unique, = refine() ----------
print("TEST 1  exhaustive (n=6 states, 2 actions), 300 random MDPs with planted symmetry")
bad=0; nontrivial=0
for trial in range(300):
    n,A=6,2
    K=rng.integers(2,4)                                  # planted quotient blocks
    lab=np.sort(rng.integers(0,K,n)); lab[0]=0; lab[-1]=K-1
    Q=rng.random((A,K,K)); Q/=Q.sum(axis=2,keepdims=True)
    P=np.zeros((A,n,n))
    for a in range(A):
        for s in range(n):
            for t in range(n):
                P[a,s,t]=Q[a,lab[s],lab[t]]/ (lab==lab[t]).sum()
    g=(lab==K-1).astype(int)                             # goal = last planted block
    ad=[p for p in all_partitions(n) if adequate(p,P,g)]
    # unique maximum under coarsening?
    maxes=[p for p in ad if all(is_coarser(p,q) or not is_coarser(q,p) for q in ad)]
    tops=[p for p in ad if all(not (is_coarser(q,p) and canon(q)!=canon(p)) for q in ad)]
    coarsest=[p for p in ad if all(is_coarser(p,q) for q in ad)]
    r=refine(P,g)
    ok = (len(coarsest)==1) and canon(coarsest[0])==canon(r)
    if len(set(r))<n: nontrivial+=1
    if not ok: bad+=1
print(f"  unique coarsest adequate partition = refine() in {300-bad}/300 MDPs; "
      f"non-trivial abstraction found in {nontrivial}/300")

# ---------- Test 2: join-closure (the lattice property the proof rests on) ----------
print("TEST 2  join of two adequate partitions is adequate")
bad=0; tot=0
for trial in range(2000):
    n,A=8,2; K=rng.integers(2,5)
    lab=rng.integers(0,K,n)
    if len(set(lab))<2: continue
    Q=rng.random((A,K,K)); Q/=Q.sum(axis=2,keepdims=True)
    P=np.zeros((A,n,n))
    for a in range(A):
        for s in range(n):
            for t in range(n): P[a,s,t]=Q[a,lab[s],lab[t]]/(lab==lab[t]).sum()
    g=(lab==0).astype(int)
    # random adequate partitions: merge only within planted blocks, respecting g
    def rand_adeq():
        p=np.arange(n)
        for b in set(lab):
            idx=np.where(lab==b)[0]
            for i in idx[1:]:
                if rng.random()<0.6: p[i]=p[idx[0]]
        return canon(p)
    p1,p2=rand_adeq(),rand_adeq()
    if not(adequate(p1,P,g) and adequate(p2,P,g)): continue
    tot+=1
    if not adequate(join(p1,p2),P,g): bad+=1
print(f"  violations: {bad}/{tot}")

# ---------- Test 3: intrinsic task bandwidth  h_theta <= h ----------
print("TEST 3  entropy rate of quotient vs ground chain")
def entropy_rate(T):
    ev,evec=np.linalg.eig(T.T); i=np.argmin(np.abs(ev-1))
    pi=np.real(evec[:,i]); pi/=pi.sum()
    return float(sum(pi[s]*(-(T[s][T[s]>0]*np.log2(T[s][T[s]>0])).sum()) for s in range(len(pi))))
for trial in range(5):
    n=12; K=3
    lab=np.array([i%K for i in range(n)])
    Q=rng.random((K,K)); Q/=Q.sum(axis=1,keepdims=True)
    T=np.zeros((n,n))
    for s in range(n):
        for t in range(n): T[s,t]=Q[lab[s],lab[t]]/(lab==lab[t]).sum()
    print(f"  h(ground)={entropy_rate(T):.3f} bits/step   h_theta(quotient)={entropy_rate(Q):.3f} bits/step")
