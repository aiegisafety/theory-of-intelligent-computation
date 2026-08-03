exec(open('experiment2.py').read().split("T,lab,Q,g=build()")[0])
import numpy as np
T,lab,Q,g=build()
part=np.array(g,dtype=int); rnd=0; mins=[]
while True:
    Bs=sorted(set(part)); R=np.array([[T[s][part==c].sum() for c in Bs] for s in range(N)])
    newlab={}; nxt=part.max()+1; new=part.copy(); changed=False; rnd_min=1e9
    for b in Bs:
        idx=np.where(part==b)[0]
        if len(idx)<2: continue
        reps=[idx[0]]; assign={idx[0]:0}
        for s in idx[1:]:
            hit=None
            for k,r in enumerate(reps):
                if 0.5*abs(R[s]-R[r]).sum()<1e-9: hit=k; break
            if hit is None:
                rnd_min=min(rnd_min,min(0.5*abs(R[s]-R[r]).sum() for r in reps))
                reps.append(s); assign[s]=len(reps)-1
            else: assign[s]=hit
        if len(reps)>1:
            changed=True
            for s in idx:
                if assign[s]>0: new[s]=nxt+assign[s]-1
            nxt+=len(reps)-1
    if not changed: break
    rnd+=1; mins.append(rnd_min); part=new
    print(f"  round {rnd}: blocks {len(set(part))}, smallest TV that had to be detected = {rnd_min:.4f}")
print(f"\n  effective detection threshold  Delta_eff = min over rounds = {min(mins):.4f}")
print(f"  naive gap w.r.t. the FINAL partition             = 0.2579")
print("  => the usable eps window is (noise, Delta_eff), NOT (noise, Delta_final).")
print("     eps=0.10 < Delta_eff : works.   eps=0.20 > Delta_eff : over-merges at every n. matches experiment.")
