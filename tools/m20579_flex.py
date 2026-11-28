import pickle,random,sys
from m20579_rows import R
codes=pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_c180.pkl'),'rb'))
FULL=(1<<1024)-1
def line(e): 
    if e<32: return sum(1<<(32*e+j) for j in range(32))
    j=e-32; return sum(1<<(32*i+j) for i in range(32))
L=[line(e) for e in range(64)]
M=sum(((R[i]>>j)&1)<<(32*i+j) for i in range(32) for j in range(32))
W=list(L)
for o,a,b in codes: W.append(W[a]|W[b] if o==1 else W[a]&W[b])
def dec(w): return frozenset(e for e in range(64) if W[w]&L[e]==L[e])
prods=[(dec(a),dec(b)) for o,a,b in codes if o==0]
def sig(S):
    s=0
    for e in S: s|=L[e]
    return s
def run(seed):
    rng=random.Random(seed)
    targets=[]  # (required, allowed)
    order=list(range(len(prods))); 
    for k,(A,B) in enumerate(prods):
        sA,sB=sig(A),sig(B)
        if rng.random()<0.5:
            allA=frozenset(e for e in range(64) if (L[e]&sB)&~M==0)
            sAA=sig(allA)
            allB=frozenset(e for e in range(64) if (L[e]&sAA)&~M==0)
        else:
            allB=frozenset(e for e in range(64) if (L[e]&sA)&~M==0)
            sBB=sig(allB)
            allA=frozenset(e for e in range(64) if (L[e]&sBB)&~M==0)
        targets.append((A,allA)); targets.append((B,allB))
    lib=[frozenset([e]) for e in range(64)]
    built=[]
    def cover(req,allw):
        cands=[w for w in lib if w<=allw and w&req]
        left=set(req); cov=[]
        while left:
            best=max(cands,key=lambda w:(len(w&left),rng.random()))
            cov.append(best); left-=best
        return cov
    while True:
        covs=[cover(r,a) for r,a in targets]
        cnt={}
        for t,c in enumerate(covs):
            for x in range(len(c)):
                for y in range(x+1,len(c)):
                    u=c[x]|c[y]
                    cnt[u]=cnt.get(u,0)+1
        if not cnt: break
        mx=max(cnt.values())
        if mx<2: break
        u=rng.choice([k for k,v in cnt.items() if v==mx])
        lib.append(u); built.append(u)
    covs=[cover(r,a) for r,a in targets]
    cost=len(built)+sum(len(c)-1 for c in covs)+len(prods)*2-1
    return cost,targets,covs,built
best=999
for s in range(int(sys.argv[1]),int(sys.argv[2])):
    c=run(s)[0]
    if c<best: best=c; print(s,c,flush=True)
