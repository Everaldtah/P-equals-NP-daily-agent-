# Checker search for step H1 of Erdos1052 R2.H2.R3.H1.R1, case c = 1.
# With c = 1: b = 2^a, u = 2^a + 1, and the balance is (2^a+1) * prod(1+p) = 2^(a+1) * prod(p), p in S,
# i.e. N = 2^a * prod(S) is a unitary perfect number with squarefree odd part.
# Every odd prime of 2^a+1 must be in S, so the filtered count equals omega(2^a+1).
# Exhaustive DFS for 5 <= a <= AMAX over S within the statement's own range S subset [3, u].
import sys, math
from fractions import Fraction
AMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 20

def factor(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1; n //= d
        d += 1 if d == 2 else 2
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for b in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(b, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def solve(a):
    u = 2 ** a + 1
    sols = []
    nodes = [0]
    def dfs(S, Lf):
        # Lf: factorization of L = u * prod(1+p) as a dict
        nodes[0] += 1
        if nodes[0] > 2_000_000: raise RuntimeError('node limit')
        # prune: exponents
        if Lf.get(2, 0) > a + 1: return
        for q, e in Lf.items():
            if q != 2 and e > 1: return
        # forced primes: odd primes of L not in S
        forced = [q for q in Lf if q != 2 and q not in S]
        if forced:
            q = min(forced)
            if q > u: return
            nf = dict(Lf)
            for r, e in factor(q + 1).items(): nf[r] = nf.get(r, 0) + e
            dfs(S | {q}, nf); return
        # ratio L/R must stay <= 1
        L = u; R = 2 ** (a + 1)
        for p in S: L *= p + 1; R *= p
        if L == R:
            sols.append(sorted(S)); return
        if L > R: return
        # deficit: smallest prime of S not yet in L (2-adic deficit only: add r with odd part of r+1 inside S)
        miss = sorted(p for p in S if p not in Lf)
        budget = a + 1 - Lf.get(2, 0)
        if budget <= 0: return
        if miss:
            q = miss[0]
            # r + 1 = 2^j * q * t, t odd, r prime, r <= u, r not in S
            for j in range(1, budget + 1):
                base = 2 ** j * q
                t = 1
                while base * t - 1 <= u:
                    r = base * t - 1
                    if r not in S and is_prime(r):
                        nf = dict(Lf)
                        for s, e in factor(r + 1).items(): nf[s] = nf.get(s, 0) + e
                        dfs(S | {r}, nf)
                    t += 2
        else:
            # Only the power of 2 is short (R/L = 2^budget) and every odd prime is balanced. New primes T must have
            # prod(1+1/r) = 2^budget with sum v2(r+1) = budget, so |T| <= budget, but (4/3)^|T| < 2^budget: impossible.
            return
    dfs(frozenset(), factor(u))
    return sols, nodes[0]

import time
for a in range(int(sys.argv[2]) if len(sys.argv)>2 else 5, AMAX + 1):
    t0=time.time()
    try:
        sols, n = solve(a)
        res = [(s, sum(1 for p in s if (2 ** a + 1) % p == 0)) for s in sols if len(s) >= 4]
        print(a, 'omega(2^a+1)=%d' % len(factor(2 ** a + 1)), 'nodes', n, 'solutions(|S|>=4):', res, '%.1fs'%(time.time()-t0), flush=True)
    except RuntimeError as e:
        print(a, 'stopped:', e, flush=True)
