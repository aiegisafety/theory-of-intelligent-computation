import numpy as np, math
rng=np.random.default_rng(11)
def Hb(q):
    if q<=0 or q>=1: return 0.0
    return -(q*math.log2(q)+(1-q)*math.log2(1-q))

print("A) rescue-robot instance: goal = victim reached")
cands={"aggressive route":0.40,"cautious route":0.05,"do nothing":0.00}
for k,q in cands.items(): print(f"   {k:18s} P(goal)={q:.2f}   H_outcome={Hb(q):.3f} bits")
print("   argmax P(goal) =", max(cands,key=cands.get))
print("   argmin H        =", min(cands,key=lambda k:Hb(cands[k])), " <-- certain failure")

print("\nB) exact agreement condition:  argmin Hb == argmax q  iff  q_max + q_min >= 1")
bad=0; tot=0; agree=0
for t in range(300000):
    m=rng.integers(2,6); q=rng.random(m)
    i_max=int(np.argmax(q)); i_ent=int(np.argmin([Hb(x) for x in q]))
    pred = (q.max()+q.min()>=1.0)
    got  = (i_max==i_ent)
    tot+=1; agree+=got
    if pred!=got and abs(abs(q[i_max]-0.5)-abs(q[i_ent]-0.5))>1e-12: bad+=1
print(f"   violations of the condition: {bad}/{tot};  entropy-min happens to agree in {agree/tot:.1%} of random tasks")

print("\nC) how bad is it when it disagrees? (regret in goal probability)")
reg=[]
for t in range(200000):
    m=rng.integers(2,6); q=rng.random(m)
    i_ent=int(np.argmin([Hb(x) for x in q])); reg.append(q.max()-q[i_ent])
reg=np.array(reg)
print(f"   mean regret {reg.mean():.3f}   P(regret>0.3) {np.mean(reg>0.3):.3f}   max {reg.max():.3f}")

print("\nD) sub-1/2 regime: if every achievable q < 1/2, entropy-min ALWAYS picks the worst")
worst=0; n=0
for t in range(100000):
    m=rng.integers(2,6); q=rng.random(m)*0.5
    i_ent=int(np.argmin([Hb(x) for x in q])); n+=1
    worst += (i_ent==int(np.argmin(q)))
print(f"   picks the strictly worst candidate in {worst}/{n} = {worst/n:.1%} of cases")

print("\nE) predictive vs posterior reading — a measurement action")
# state in {0,1} unknown, prior 1/2. tau_m = measure (reveals), tau_i = ignore
# reading (i): predictive entropy of next state as seen ex ante
# reading (ii): expected posterior entropy after the step
print("   tau_measure : H(S_{t+1}|e_t)=1.000 bits (high)   E[H(S_{t+1}|e_{t+1})]=0.000 bits")
print("   tau_ignore  : H(S_{t+1}|e_t)=1.000 bits          E[H(S_{t+1}|e_{t+1})]=1.000 bits")
print("   -> reading (i) cannot distinguish them / penalises informative actions;")
print("      reading (ii) is correct here, and only here (epistemic goals).")
