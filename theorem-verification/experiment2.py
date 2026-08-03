import numpy as np, math, itertools
P=lambda *a: print(*a,flush=True)
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); pi=np.real(V[:,i]); pi=np.real(pi); return pi/pi.sum()

K,m=6,4; N=K*m
def build(seed=1):
    rng=np.random.default_rng(seed)
    lab=np.repeat(np.arange(K),m)                    # planted classes
    Q=rng.random((K,K))**2; Q/=Q.sum(1,keepdims=True)
    T=np.zeros((N,N))
    for s in range(N):
        for t in range(N): T[s,t]=Q[lab[s],lab[t]]/m
    g=(lab==0).astype(int)                            # goal label seeds the refinement
    return T,lab,Q,g

def refine(Tk,g,eps):
    """eps-refinement: split a block only if two states' block-transition rows differ by TV > eps"""
    part=np.array(g,dtype=int)
    for _ in range(N):
        new=part.copy(); nxt=part.max()+1; changed=False
        for b in sorted(set(part)):
            idx=np.where(part==b)[0]
            if len(idx)<2: continue
            R=np.array([[Tk[s][part==c].sum() for c in sorted(set(part))] for s in idx])
            reps=[0]; assign={idx[0]:0}
            for j in range(1,len(idx)):
                placed=False
                for r_i,r in enumerate(reps):
                    if 0.5*np.abs(R[j]-R[r]).sum()<=eps: assign[idx[j]]=r_i; placed=True; break
                if not placed: reps.append(j); assign[idx[j]]=len(reps)-1
            if len(reps)>1:
                changed=True
                for s in idx:
                    if assign[s]>0: new[s]=nxt+assign[s]-1
                nxt+=len(reps)-1
        part=new
        if not changed: break
    # relabel
    mp={}; out=[]
    for x in part:
        if x not in mp: mp[x]=len(mp)
        out.append(mp[x])
    return np.array(out)

def pair_stats(part,truth):
    om=os=0; tot_ne=tot_e=0
    for i in range(N):
        for j in range(i+1,N):
            same_t=(truth[i]==truth[j]); same_p=(part[i]==part[j])
            if same_t: tot_e+=1; os+= (not same_p)
            else: tot_ne+=1; om+= same_p
    return om/max(tot_ne,1), os/max(tot_e,1)

def h_theta(part,T):
    pi=stat(T); Bs=sorted(set(part)); out=0.0
    for b in Bs:
        idx=np.where(part==b)[0]; w=pi[idx]/pi[idx].sum()
        row=np.array([ (w[:,None]*np.array([[T[s][part==c].sum() for c in Bs] for s in idx])).sum(0)])[0]
        out+=pi[idx].sum()*H(row)
    return out

def sample_kernel(T,n,rng):
    Tk=np.zeros_like(T)
    for s in range(N):
        c=rng.multinomial(n,T[s]); Tk[s]=c/n
    return Tk

T,lab,Q,g=build()
truth=refine(T,g,0.0)                                   # exact canonical abstraction from the true kernel
P(f"ground truth: planted classes K={K}, canonical abstraction has {len(set(truth))} blocks, "
  f"h_theta*={h_theta(truth,T):.3f} bits/step,  h(ground)={h_theta(np.arange(N),T):.3f}")
P("")
P("EXPERIMENT 2 - learning the abstraction from n samples per state")
P("  over-merge = fraction of inequivalent pairs wrongly merged  (UNSAFE: admissibility conflicts)")
P("  over-split = fraction of equivalent pairs wrongly separated (SAFE but costs bandwidth)")
P("  h_theta(learned) = bandwidth the learned abstraction actually needs")
P("  both-safe = P(two independently-trained agents BOTH avoid over-merging)")
P("")
for eps in [0.02,0.05,0.10,0.20]:
    P(f"  eps = {eps:.2f}")
    P("     n     blocks   over-merge   over-split   h_theta(learned)   both-safe")
    for n in [20,50,100,300,1000,5000]:
        rows=[];bm=0;R=25
        oms=[];oss=[];hts=[];blks=[]
        for r in range(R):
            rng=np.random.default_rng(1000*r+n)
            p1=refine(sample_kernel(T,n,rng),g,eps)
            p2=refine(sample_kernel(T,n,rng),g,eps)
            om1,os1=pair_stats(p1,truth); om2,_=pair_stats(p2,truth)
            oms.append(om1);oss.append(os1);hts.append(h_theta(p1,T));blks.append(len(set(p1)))
            bm+= (om1==0 and om2==0)
        P(f"   {n:5d}    {np.mean(blks):5.1f}     {np.mean(oms):7.3f}      {np.mean(oss):7.3f}         {np.mean(hts):7.3f}        {bm/R:5.2f}")
    P("")
