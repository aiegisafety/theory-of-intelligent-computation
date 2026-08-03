exec(open('experiment2.py').read().split("T,lab,Q,g=build()")[0])
import numpy as np,math
T,lab,Q,g=build(); truth=refine(T,g,0.0); Bs=sorted(set(truth))
R=np.array([[T[s][truth==c].sum() for c in Bs] for s in range(N)])
gap=1e9; pair=None
for i in range(N):
    for j in range(i+1,N):
        if truth[i]!=truth[j]:
            tv=0.5*abs(R[i]-R[j]).sum()
            if tv<gap: gap=tv; pair=(i,j)
print(f"separation gap Delta (min TV between inequivalent states, over blocks) = {gap:.4f}  at {pair}")
for n in [20,50,100,300,1000,5000]:
    print(f"  n={n:5d}   estimation noise ~ 0.5*sqrt(2K/(pi n)) = {0.5*math.sqrt(2*len(Bs)/(math.pi*n)):.4f}"
          f"   -> usable eps window: ({0.5*math.sqrt(2*len(Bs)/(math.pi*n)):.3f}, {gap:.3f})"
          f" {'EMPTY' if 0.5*math.sqrt(2*len(Bs)/(math.pi*n))>=gap else 'ok'}")
