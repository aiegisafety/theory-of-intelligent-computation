import numpy as np, itertools
P=lambda *a: print(*a,flush=True)
rng=np.random.default_rng(7)
M,q=4,3                       # M niches of q states each, plus 2 identity-loss states
N=M*q+2; DEATH={N-2,N-1}; ALIVE=set(range(M*q))
niche=lambda s: s//q
A=2
Pk=np.zeros((A,N,N))
for s in range(M*q):
    for a in range(A):
        stay,leak,die=(0.90,0.06,0.04) if a==0 else (0.55,0.40,0.05)
        row=np.zeros(N)
        own=[t for t in range(M*q) if niche(t)==niche(s)]
        oth=[t for t in range(M*q) if niche(t)!=niche(s)]
        for t in own: row[t]=stay/len(own)
        for t in oth: row[t]=leak/len(oth)
        for t in DEATH: row[t]=die/len(DEATH)
        Pk[a,s]=row/row.sum()
for s in DEATH:
    Pk[:,s,s]=1.0

def kernel(Om,delta):
    cur=set(Om)&ALIVE
    while True:
        nxt={s for s in cur if max(sum(Pk[a,s,t] for t in cur) for a in range(A))>=1-delta}
        if nxt==cur: return cur
        cur=nxt

P(f"THEOREM 13 - which identities are POSSIBLE?   world = {M} niches x {q} states + {len(DEATH)} death states\n")
P("   delta    |viability kernel|   equals ALIVE?")
for d in [0.02,0.04,0.06,0.10,0.20]:
    K=kernel(ALIVE,d); P(f"   {d:4.2f}         {len(K):3d}/{len(ALIVE)}            {K==ALIVE}")

d=0.06
P(f"\n  enumerate every subset that is viable at delta={d} (2^{len(ALIVE)} candidates):")
viable=[]
for r in range(1,len(ALIVE)+1):
    for S_ in itertools.combinations(sorted(ALIVE),r):
        if kernel(S_,d)==set(S_): viable.append(frozenset(S_))
P(f"   viable identities: {len(viable)}   (out of {2**len(ALIVE)} conceivable)")
unions={frozenset(sum([list(range(i*q,(i+1)*q)) for i in c],[]))
        for r in range(1,M+1) for c in itertools.combinations(range(M),r)}
P(f"   are they exactly the unions of niches?  {set(viable)==unions}   ({len(unions)} = 2^{M}-1)")
bad=sum(1 for X,Y in itertools.combinations(viable,2) if kernel(X|Y,d)!=set(X|Y))
P(f"   13.2 closure under union: violations {bad}/{len(viable)*(len(viable)-1)//2}")
P(f"   13.3 unique maximal element: |K| = {len(kernel(ALIVE,d))} = union of all niches")
P("\n  READ THIS ROW: the theory determines the LATTICE of possible identities exactly")
P("  (the niches and their unions). It does not determine WHICH niche an entity occupies.")
P("  That is the boundary.")
