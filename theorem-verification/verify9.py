# Counterexample to State-Calculus-Axioms Theorem 5.2 / 5.3
# claim: R+(s1)=R+(s2) and R-(s1)=R-(s2)  =>  behavioural equivalence / safe to merge
S=['s1','s2','a','b']
E={'s1':['a','b'],'s2':['a'],'a':['b'],'b':[]}
def reach(x,E):
    seen=set(); st=[x]
    while st:
        u=st.pop()
        for v in E.get(u,[]):
            if v not in seen: seen.add(v); st.append(v)
    return seen
Einv={s:[] for s in S}
for u,vs in E.items():
    for v in vs: Einv[v].append(u)
print("R+(s1)=",sorted(reach('s1',E)), "  R+(s2)=",sorted(reach('s2',E)))
print("R-(s1)=",sorted(reach('s1',Einv)), "  R-(s2)=",sorted(reach('s2',Einv)))
print("Definition 5.2 satisfied:", reach('s1',E)==reach('s2',E) and reach('s1',Einv)==reach('s2',Einv))
print()
print("one-step successors: s1 ->",E['s1'],"   s2 ->",E['s2'])
print("=> from s1 you can reach b in ONE step; from s2 you cannot.")
print("=> not behaviourally equivalent; merging them CREATES a transition s2->b that did not exist.")
print()
print("Theorem 5.2's proof step 'every possible transition path from s1 exists from s2' does not follow")
print("from equality of reachable SETS. This is the classical trace-vs-bisimulation distinction.")
