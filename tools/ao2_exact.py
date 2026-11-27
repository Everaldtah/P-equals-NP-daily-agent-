# Is there a fan-in-exactly-2 AND/OR circuit (no constants, no NOT) with S gates computing
# f_E(x,y) = OR over edges (i,j) of x_i & y_j EXACTLY on all 2^(n1+n2) inputs?
# Usage: python3 ao2_exact.py n1 n2 "i-j,i-j,..." S     (prints gates or UNSAT)
import sys, itertools, os
# env NOT=1: also allow NOT gates (reads its first operand, B forced = A), at most one in the circuit.
# Edge list may also be general-graph pairs on one vertex set: use n1=N, n2=0 and GRAPH=1.
ALLOWNOT=os.environ.get('NOT')=='1'
from pysat.solvers import Solver
from pysat.card import CardEnc
n1,n2=int(sys.argv[1]),int(sys.argv[2])
E=[tuple(map(int,e.split('-'))) for e in sys.argv[3].split(',')]
S=int(sys.argv[4]); N=n1+n2
pts=list(itertools.product((0,1),repeat=N))
tv=[int(any(p[i] and p[j] for i,j in E)) if os.environ.get('GRAPH')=='1' else int(any(p[i] and p[n1+j] for i,j in E)) for p in pts]
cnt=[0]
def nv(): cnt[0]+=1; return cnt[0]
cl=[]; val={}
for g in range(S):
    for k in range(len(pts)): val[N+g,k]=nv()
A={};B={};AND={};NOTg={}
for g in range(S):
    w=N+g
    A[g]=[nv() for _ in range(w)]; B[g]=[nv() for _ in range(w)]; AND[g]=nv(); NOTg[g]=nv()
    if not ALLOWNOT: cl.append([-NOTg[g]])
    for i in range(w): cl.append([-NOTg[g],-A[g][i],B[g][i]])
    for sel in (A[g],B[g]):
        enc=CardEnc.equals(lits=sel,bound=1,top_id=cnt[0]); cnt[0]=max(cnt[0],enc.nv); cl+=enc.clauses
    for i in range(w):
        for j in range(i): cl.append([-A[g][i],-B[g][j]])   # a <= b
    if g>0:  # gate g-1 is used later (no dead gates except output)
        pass
    for k,p in enumerate(pts):
        o=val[w,k]
        for i in range(w):
            for j in range(i,w):
                # if A=i,B=j: o = op(vi,vj)
                vi = p[i] if i<N else None; vj = p[j] if j<N else None
                li = val[i,k] if i>=N else None; lj = val[j,k] if j>=N else None
                sel=[-A[g][i],-B[g][j]]
                # AND case
                def lits(v,l,pos):
                    # returns (const or None, literal)
                    return v,l
                # encode generally with helper
                def enc(opsel, f):
                    # f: function over (a,b) ->o ; produce clauses for all combos
                    for a in (0,1):
                        if vi is not None and vi!=a: continue
                        for b in (0,1):
                            if vj is not None and vj!=b: continue
                            c=list(sel)+opsel
                            if li is not None: c.append(-li if a else li)
                            if lj is not None: c.append(-lj if b else lj)
                            r=f(a,b)
                            cl.append(c+[o if r else -o])
                enc([-AND[g],NOTg[g]], lambda a,b: a&b)
                enc([AND[g],NOTg[g]], lambda a,b: a|b)
                enc([-NOTg[g]], lambda a,b: 1-a)
out=N+S-1
for k in range(len(pts)):
    cl.append([val[out,k] if tv[k] else -val[out,k]])
# every gate except the last is read by some later gate
for g in range(S-1):
    w=N+g
    cl.append([A[h][w] for h in range(g+1,S)]+[B[h][w] for h in range(g+1,S)])
if ALLOWNOT:
    enc=CardEnc.atmost(lits=[NOTg[g] for g in range(S)],bound=1,top_id=cnt[0]); cnt[0]=max(cnt[0],enc.nv); cl+=enc.clauses
s=Solver(name='cadical153',bootstrap_with=cl)
if s.solve():
    m=set(x for x in s.get_model() if x>0)
    for g in range(S):
        a=[i for i in range(N+g) if A[g][i] in m][0]; b=[i for i in range(N+g) if B[g][i] in m][0]
        print(('NOT' if NOTg[g] in m else 'AND' if AND[g] in m else 'OR'),a,b)
    print('SAT')
else: print('UNSAT')
