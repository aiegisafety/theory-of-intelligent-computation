"""Table 8.2 (V2, Theorem 8.8): requirement of the common refinement of several tasks.

Computes H(B_meet' | S), the true requirement of Theorem 6.4, for the common refinement of
k = 1..6 random three-class tasks on a random 36-state chain, together with the largest single-task
requirement. The bracketed column is the quotient proxy H(B'|B) used in the first version, shown
for comparison only.
"""
import numpy as np
def H(p):
    p=np.asarray(p,float); p=p[p>1e-15]; return float(-(p*np.log2(p)).sum())
def stat(T):
    ev,V=np.linalg.eig(T.T); i=np.argmin(abs(ev-1)); v=np.abs(np.real(V[:,i])); return v/v.sum()
def h_true(part,T):     # H(B'|S): the requirement of Theorem 6.4
    pi=stat(T); part=np.array(part); Bs=sorted(set(part)); out=0.0
    for s in range(len(T)):
        out+=pi[s]*H([T[s][part==c].sum() for c in Bs])
    return out
def h_proxy(part,T):    # H(B'|B): quotient proxy (as in verify7)
    pi=stat(T); part=np.array(part); Bs=sorted(set(part)); out=0.0
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
rng=np.random.default_rng(5); N=36
T=rng.random((N,N))**3; T/=T.sum(1,keepdims=True)
print('h (physical) = %.3f'%h_true(list(range(N)),T))
parts=[]
print(' k  blocks  H(B_meet|S)  max_i H(B_i|S)   [proxy H(B|B) as in earlier notes]')
for k in range(1,7):
    parts.append(list(rng.integers(0,3,N)))
    cr=meet(*parts)
    print('%2d   %3d     %6.3f       %6.3f          [%6.3f]'%(k,len(set(cr)),h_true(cr,T),max(h_true(p,T) for p in parts),h_proxy(cr,T)))
