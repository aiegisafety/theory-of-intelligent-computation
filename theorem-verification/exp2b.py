exec(open('experiment1.py').read().split("P=lambda")[0])
P=lambda *a: print(*a,flush=True)
Q,h=make_chain(1.0)
P("EXPERIMENT 2b - agreement vs correctness (h_theta=1.0, C=2)")
P("   m   class-aware: agree/correct    naive: agree/correct")
for m in [1,2,4,8,16,32]:
    a1,c1,_=run(Q,2,m,"class-aware"); a2,c2,_=run(Q,2,m,"naive")
    P(f"  {m:3d}       {a1:5.3f} / {c1:5.3f}            {a2:5.3f} / {c2:5.3f}")
