# SAT search: fan-in-2 AND/OR/NOT circuit with S gates, correct on given promise points.
# Usage: python3 promise_sat.py rep <n> <m> <mask> <S>   (bipartite one-a-side, bit n?: 5*u+v style: m*u+v)
#        python3 promise_sat.py twolit <n> <mask> <S>
# Prints gate list as (op, a, b); wires 0..N-1 are inputs, gate k is wire N+k, output = last gate.
import sys, itertools, os
from pysat.solvers import Solver
import os
from pysat.card import CardEnc
mode=sys.argv[1]
if mode=='rep':
    n,m,mask,S=map(int,sys.argv[2:6]); N=n+m
    pts=[]; tv=[]
    for u in range(n):
        for v in range(m):
            pts.append([int(i==u) for i in range(n)]+[int(j==v) for j in range(m)]); tv.append((mask>>(m*u+v))&1)
else:
    n,mask,S=map(int,sys.argv[2:5]); N=n
    pts=[];tv=[]
    for i in range(n):
        for j in range(i,n):
            pts.append([int(k in (i,j)) for k in range(n)]); tv.append((mask>>(n*i+j))&1)
# DROPWIRE=k1,k2: treat points where any of these inputs is 1 as don't-care (e.g. a full column ORed in last).
_dw=[int(t) for t in os.environ.get('DROPWIRE','').split(',') if t]
if _dw:
    keep=[i for i in range(len(pts)) if not any(pts[i][k] for k in _dw)]
    pts=[pts[i] for i in keep]; tv=[tv[i] for i in keep]
P=len(pts)
cnt=[0]
def nv(): cnt[0]+=1; return cnt[0]
cl=[]
val={}
for w in range(N):
    for p in range(P): val[w,p]=None
const=lambda w,p: pts[p][w]
for g in range(S):
    w=N+g
    for p in range(P): val[w,p]=nv()
def lit(w,p):
    return val[w,p]
A={};B={};OP={}
for g in range(S):
    w=N+g
    A[g]=[nv() for i in range(w)]; B[g]=[nv() for i in range(w)]
    OP[g]=[nv(),nv(),nv()]  # and, or, not
    for sel in (A[g],B[g],OP[g]):
        enc=CardEnc.equals(lits=sel,bound=1,top_id=cnt[0]); cnt[0]=max(cnt[0],enc.nv); cl+=enc.clauses
    # symmetry: a<=b ; for not, b = a
    for i in range(w):
        for j in range(i): cl.append([-A[g][i],-B[g][j]])
        cl.append([-OP[g][2],-A[g][i],B[g][i]])
    for i in range(w):
        for j in range(i,w):
            for p in range(P):
                x=lambda q: q
                for o in range(3):
                    # compute output given input values
                    def V(k):
                        return ('c',pts[p][k]) if k<N else ('v',val[k,p])
                    vi,vj,vo=V(i),V(j),val[w,p]
                    base=[-A[g][i],-B[g][j],-OP[g][o]]
                    # enumerate assignments of variable inputs
                    vars_=[t for t in (vi,vj) if t[0]=='v']
                    for bits in itertools.product([0,1],repeat=2):
                        if vi[0]=='c' and bits[0]!=vi[1]: continue
                        if vj[0]=='c' and bits[1]!=vj[1]: continue
                        a_,b_=bits
                        if vj[0]=='c' and vi[0]=='v' and vi==vj: pass
                        r = (a_&b_) if o==0 else (a_|b_) if o==1 else 1-a_
                        c=list(base)
                        if vi[0]=='v': c.append(-vi[1] if a_ else vi[1])
                        if vj[0]=='v' and not (i==j):
                            c.append(-vj[1] if b_ else vj[1])
                        if i==j and a_!=b_: continue
                        c.append(vo if r else -vo)
                        cl.append(c)
out=N+S-1
import os
if os.environ.get('MONO'):
    for g in range(S): cl.append([-OP[g][2]])
for w_ in [int(t) for t in os.environ.get('FORBID','').split(',') if t]:
    for g in range(S): cl.append([-A[g][w_]]); cl.append([-B[g][w_]])
for p in range(P): cl.append([val[out,p] if tv[p] else -val[out,p]])
# every gate except last is used
for g in range(S-1):
    w=N+g
    cl.append([A[h][w] for h in range(g+1,S)]+[B[h][w] for h in range(g+1,S)])
# SYM=1: adjacent independent gates (not the output) are ordered by first operand.
if os.environ.get('SYM'):
    for g in range(S-2):
        w=N+g
        for i in range(w):
            for j in range(i):
                cl.append([-A[g][i],-A[g+1][j],A[g+1][w],B[g+1][w]])
print('vars',cnt[0],'clauses',len(cl),flush=True)
s=Solver(name=os.environ.get('SOLVER','cadical153'),bootstrap_with=cl)
if s.solve():
    M=set(x for x in s.get_model() if x>0)
    res=[]
    for g in range(S):
        a=[i for i,x in enumerate(A[g]) if x in M][0]; b=[i for i,x in enumerate(B[g]) if x in M][0]
        o=['and','or','not'][[k for k,x in enumerate(OP[g]) if x in M][0]]
        res.append((o,a,b))
    print('SAT',res)
    # verify
    ok=True
    for p in range(P):
        wv=list(pts[p])
        for o,a,b in res: wv.append(wv[a]&wv[b] if o=='and' else wv[a]|wv[b] if o=='or' else 1-wv[a])
        ok&=wv[-1]==tv[p]
    print('verified',ok)
else: print('UNSAT')
