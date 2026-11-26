# Search for small AND/OR/NOT fan-in-2 circuits for the "two-lit" function of a graph on n points.
# Usage: python3 twolit_search.py <n> <mask> <maxgates>
# Inputs are the vectors with points i,j lit (i<=j); target bit index n*min+max of mask.
import sys, itertools
n=int(sys.argv[1]); mask=int(sys.argv[2]); S=int(sys.argv[3])
pts=[(i,j) for i in range(n) for j in range(i,n)]
N=len(pts); FULL=(1<<N)-1
inp=[sum(1<<k for k,(i,j) in enumerate(pts) if v in (i,j)) for v in range(n)]
tgt=sum(1<<k for k,(i,j) in enumerate(pts) if (mask>>(n*i+j))&1)
print('target',bin(tgt),'inputs',N)
def dfs(wires,gates,depth):
    if wires[-1]==tgt and gates: return gates
    if tgt in wires and not gates: return []
    if depth==0: return None
    m=len(wires)
    seen=set(wires)
    cands=[]
    for a in range(m):
        v=FULL^wires[a]
        if v not in seen: cands.append((v,('not',a))); seen.add(v)
        for b in range(a+1,m):
            for op,v in (('and',wires[a]&wires[b]),('or',wires[a]|wires[b])):
                if v not in seen: cands.append((v,(op,a,b))); seen.add(v)
    # last gate must hit target
    if depth==1:
        for v,g in cands:
            if v==tgt: return gates+[g]
        return None
    for v,g in cands:
        r=dfs(wires+[v],gates+[g],depth-1)
        if r is not None: return r
    return None
for s in range(1,S+1):
    r=dfs(list(inp),[],s)
    print(s,r)
    if r is not None: break
