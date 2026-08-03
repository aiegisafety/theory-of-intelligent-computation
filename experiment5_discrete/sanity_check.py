"""
Anti-trap rule #2: prove the refiner is not degenerate BEFORE trusting it.

Three checks, in increasing strength:

  CHECK 1  A 6-state MDP whose quotient I compute by hand  -> expect 3 blocks.
  CHECK 2  Same MDP + one extra state that must split off  -> expect 4 blocks,
           with the extra state alone in its own block.  (Guards against a
           refiner that just returns the goal partition, and against one that
           over-merges.)
  CHECK 3  The REAL torus environment, where the correct answer is known
           analytically but is NOT given to the refiner: for zone modulus m the
           canonical quotient must be exactly m^2 blocks (x1 mod m, x2 mod m),
           with y1, y2 and the weather variable fully collapsed.  Run for
           m = 2, 3, 6 and K = 1, 4.

CHECK 3 is the one that matters: it is an analytic prediction about a 10^3-10^4
state kernel that the algorithm has no way to shortcut.
"""

import numpy as np
from refine import refine, entropy_rates
from env import RendezvousTorus


def _mk_trans(edges, num_states, num_actions):
    """edges[a] = list of (src, dst, prob)."""
    def trans_fn(a):
        src = np.array([e[0] for e in edges[a]], dtype=np.int64)
        dst = np.array([e[1] for e in edges[a]], dtype=np.int64)
        pr = np.array([e[2] for e in edges[a]], dtype=np.float64)
        return src, dst, pr
    return trans_fn


def check1():
    print("CHECK 1: 6-state hand-computed MDP")
    print("  labels: {0,1}=L0  {2,3}=L1  {4,5}=L2")
    print("  0->2(.7),4(.3) | 1->3(.7),5(.3) | 2->0(1) | 3->1(1)"
          " | 4->4(.5),5(.5) | 5->4(.5),5(.5)")
    print("  BY HAND: 0 and 1 both send (L1=.7, L2=.3) -> stay merged")
    print("           2 and 3 both send (L0=1.0)       -> stay merged")
    print("           4 and 5 both send (L2=1.0)       -> stay merged")
    print("  => fixed point is the goal partition itself: 3 blocks")
    labels = np.array([0, 0, 1, 1, 2, 2], dtype=np.int64)
    edges = {0: [(0, 2, .7), (0, 4, .3), (1, 3, .7), (1, 5, .3),
                 (2, 0, 1.0), (3, 1, 1.0),
                 (4, 4, .5), (4, 5, .5), (5, 4, .5), (5, 5, .5)]}
    s2b, nb = refine(6, 1, labels, _mk_trans(edges, 6, 1))
    print(f"  ALGORITHM: {nb} blocks, map = {s2b.tolist()}")
    ok = (nb == 3 and s2b[0] == s2b[1] and s2b[2] == s2b[3] and s2b[4] == s2b[5])
    print("  -> PASS" if ok else "  -> FAIL")
    return ok


def check2():
    print("\nCHECK 2: same + state 6 (label L0) with 6->2(1.0)")
    print("  BY HAND: state 6 sends (L1=1.0); states 0,1 send (L1=.7,L2=.3).")
    print("           Different signature inside block L0 -> 6 must split off.")
    print("  => 4 blocks, state 6 alone")
    labels = np.array([0, 0, 1, 1, 2, 2, 0], dtype=np.int64)
    edges = {0: [(0, 2, .7), (0, 4, .3), (1, 3, .7), (1, 5, .3),
                 (2, 0, 1.0), (3, 1, 1.0),
                 (4, 4, .5), (4, 5, .5), (5, 4, .5), (5, 5, .5),
                 (6, 2, 1.0)]}
    s2b, nb = refine(7, 1, labels, _mk_trans(edges, 7, 1))
    print(f"  ALGORITHM: {nb} blocks, map = {s2b.tolist()}")
    alone = sum(1 for i in range(7) if s2b[i] == s2b[6]) == 1
    ok = (nb == 4 and alone and s2b[0] == s2b[1])
    print("  -> PASS" if ok else "  -> FAIL")
    return ok


def check3():
    print("\nCHECK 3: real torus kernel, analytic prediction |S/~| = m^2")
    all_ok = True
    for (N, m, K) in [(6, 2, 1), (6, 3, 1), (6, 6, 1), (6, 2, 4), (6, 3, 4)]:
        env = RendezvousTorus(grid_size=N, m=m, K=K)
        s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                         env.transitions_for_action)
        pred = m * m
        ok = (nb == pred)
        all_ok &= ok
        # additionally verify the block is a function of the RELATIVE offset
        # ((x1-x2) mod m, (y1-y2) mod m) only -- absolute position must collapse
        sig = ((env.x1_of - env.x2_of) % m) * m + ((env.y1_of - env.y2_of) % m)
        consistent = len(np.unique(sig * 10**6 + s2b)) == len(np.unique(sig))
        all_ok &= consistent
        print(f"  N={N} m={m} K={K}: |S|={env.num_states:6d}  "
              f"blocks={nb:3d}  predicted={pred:3d}  "
              f"{'PASS' if ok else 'FAIL'}  "
              f"block==f(x1%m,x2%m): {'yes' if consistent else 'NO'}")
    return all_ok


if __name__ == "__main__":
    r = [check1(), check2(), check3()]
    print("\n" + ("ALL SANITY CHECKS PASSED" if all(r) else "SANITY CHECK FAILED"))
