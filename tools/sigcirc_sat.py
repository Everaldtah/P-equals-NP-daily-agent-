# SAT search for a fan-in-2 AND/OR circuit over "signature" vectors (bit-parallel simulation on
# columns, with optional special AND rule for mark columns), as in the Fano L-meta-2348 family.
# usage: python3 sigcirc_sat.py G [comma list of output columns left free, e.g. 60,61 for a sanity check]
import sys, itertools, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc
L=[2594090156585648135,15270196031782968,58150373818816,94946423956573696,54820275478360064,3870282840506368,133412159488,1911954591369396745,218716039641305168,189725234880873600,156548607028504576,229736628137050114,270286071509155872,288160007408582916]
T=62; N=14
seed=[[(v>>b)&1 for b in range(T)] for v in L]
target=[1 if t<21 else 0 for t in range(T)]
G=int(sys.argv[1])
cnt=[0]
def new(): cnt[0]+=1; return cnt[0]
cl=[]
val={}
for i in range(N):
    for t in range(T): val[i,t]=seed[i][t]  # constants
def lit(w,t):
    return val[w,t]
for j in range(G):
    for t in range(T): val[N+j,t]=new()
op={j:new() for j in range(G)}  # true = AND
sel={}
for j in range(G):
    w=N+j
    pairs=[(a,b) for a in range(w) for b in range(a+1,w)]
    vs=[]
    for (a,b) in pairs:
        s=new(); sel[j,a,b]=s; vs.append(s)
    cl.append(vs)
    enc=CardEnc.atmost(vs,1,top_id=cnt[0],encoding=1); cnt[0]=max(cnt[0],enc.nv); cl.extend(enc.clauses)
cl.append([-op[0]])
def L_(x):  # literal helper: x int var, or constant 0/1
    return x
# constraints
def eq_clauses(s, out, expr_or, expr_and, o):
    pass
for j in range(G):
    w=N+j
    for a in range(w):
        for b in range(a+1,w):
            s=sel[j,a,b]
            for t in range(T):
                o=val[w,t]
                # OR case: o = A|B ; AND case per rule
                def terms_or(): return [(a,t),(b,t)]
                for isand in (0,1):
                    guard=[-s, (-op[j] if isand==0 else op[j])]
                    guard=[g for g in guard]
                    if isand==0 or t<60:
                        if isand==0: prods=[[(a,t)],[(b,t)]]
                        else: prods=[[(a,t),(b,t)]]
                    else:
                        m=t-2
                        prods=[[(a,m),(b,t)],[(a,t),(b,m)]]
                    # o <-> OR of ANDs of prods; build with aux vars where needed
                    def vlit(x):
                        return val[x]
                    plits=[]
                    for pr in prods:
                        ls=[vlit(x) for x in pr]
                        if any(l==0 for l in ls): continue
                        ls=[l for l in ls if l!=1]
                        if not ls: plits.append(True); continue
                        if len(ls)==1: plits.append(ls[0]); continue
                        p=new()
                        for l in ls: cl.append([-p,l])
                        cl.append([p]+[-l for l in ls])
                        plits.append(p)
                    if True in plits:
                        cl.append(guard+[o]); continue
                    if not plits:
                        cl.append(guard+[-o]); continue
                    cl.append(guard+[-o]+plits)
                    for p in plits: cl.append(guard+[o,-p])
# output = last gate
FREE=set(int(x) for x in (sys.argv[2].split(',') if len(sys.argv)>2 and sys.argv[2] else []))
for t in range(T):
    if t in FREE: continue
    cl.append([val[N+G-1,t]] if target[t] else [-val[N+G-1,t]])
# every gate used (non-final) - optional symmetry: each gate except last is an operand of a later gate
for j in range(G-1):
    w=N+j
    cl.append([sel[k,a,b] for k in range(j+1,G) for a in range(N+k) for b in range(a+1,N+k) if a==w or b==w])
print('vars',cnt[0],'clauses',len(cl),flush=True)
S=Cadical153(bootstrap_with=cl)
t0=time.time()
r=S.solve()
print('result',r,time.time()-t0,flush=True)
if r:
    m=set(x for x in S.get_model() if x>0)
    for j in range(G):
        for a in range(N+j):
            for b in range(a+1,N+j):
                if sel[j,a,b] in m: print(j, 'AND' if op[j] in m else 'OR', a, b)
