# SAT search v2: fan-in-2 AND/OR circuit over 62-column signatures (Fano family, L-meta-2348 cut).
# Operand selectors are one-hot per operand (O(G*W*T) clauses). Columns 60/61 are marks with the
# special AND rule mark = A[t-2]&B[t] | A[t]&B[t-2].  Last gate = target, every gate used later.
# Does NOT encode the signature-count condition of L-meta-6899 (check any model by hand).
# usage: python3 -I sigcirc_sat2.py G [free output columns, e.g. 60,61 for a sanity check]
import sys, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc
L=[2594090156585648135,15270196031782968,58150373818816,94946423956573696,54820275478360064,3870282840506368,133412159488,1911954591369396745,218716039641305168,189725234880873600,156548607028504576,229736628137050114,270286071509155872,288160007408582916]
T=62; N=14
seed=[[(v>>b)&1 for b in range(T)] for v in L]
target=[1 if t<21 else 0 for t in range(T)]
G=int(sys.argv[1]); FREE=set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv)>2 else set()
nv=[0]
def new(): nv[0]+=1; return nv[0]
cl=[]
TRUE=new(); cl.append([TRUE])
val={}
for i in range(N):
    for t in range(T): val[i,t]=TRUE if seed[i][t] else -TRUE
for j in range(G):
    for t in range(T): val[N+j,t]=new()
op=[new() for j in range(G)]; cl.append([-op[0]])
SA={};SB={}
for j in range(G):
    W=N+j
    a=[new() for w in range(W)]; b=[new() for w in range(W)]
    SA[j]=a; SB[j]=b
    for X in (a,b):
        e=CardEnc.equals(X,1,top_id=nv[0],encoding=1); nv[0]=max(nv[0],e.nv); cl.extend(e.clauses)
    for w in range(W):
        cl.append([-a[w]]+[b[u] for u in range(w+1,W)])
    A={};B={}
    for t in range(T):
        A[t]=new(); B[t]=new()
        for w in range(W):
            for S,V in ((a,A[t]),(b,B[t])):
                cl.append([-S[w],-val[w,t],V]); cl.append([-S[w],val[w,t],-V])
    for t in range(T):
        o=val[N+j,t]
        cl += [[op[j],-o,A[t],B[t]],[op[j],o,-A[t]],[op[j],o,-B[t]]]
        if t<60:
            cl += [[-op[j],-o,A[t]],[-op[j],-o,B[t]],[-op[j],o,-A[t],-B[t]]]
        else:
            m=t-2
            p=new(); q=new()
            cl += [[-p,A[m]],[-p,B[t]],[p,-A[m],-B[t]],[-q,A[t]],[-q,B[m]],[q,-A[t],-B[m]]]
            cl += [[-op[j],-o,p,q],[-op[j],o,-p],[-op[j],o,-q]]
for t in range(T):
    if t in FREE: continue
    cl.append([val[N+G-1,t]] if target[t] else [-val[N+G-1,t]])
for j in range(G-1):
    w=N+j
    cl.append([SA[k][w] for k in range(j+1,G)]+[SB[k][w] for k in range(j+1,G)])
print('vars',nv[0],'clauses',len(cl),flush=True)
S=Cadical153(bootstrap_with=cl); t0=time.time(); r=S.solve()
print('result',r,round(time.time()-t0,1),flush=True)
if r:
    m=set(x for x in S.get_model() if x>0)
    for j in range(G):
        print(j,'AND' if op[j] in m else 'OR',[w for w in range(N+j) if SA[j][w] in m],[w for w in range(N+j) if SB[j][w] in m])
