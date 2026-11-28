import random,sys
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_flex.py')).read().split('def run(seed)')[0])
def mk_targets(rng):
    targets=[]
    for k,(A,B) in enumerate(prods):
        sA,sB=sig(A),sig(B)
        if rng.random()<0.5:
            allA=frozenset(e for e in range(64) if (L[e]&sB)&~M==0); sAA=sig(allA)
            allB=frozenset(e for e in range(64) if (L[e]&sAA)&~M==0)
        else:
            allB=frozenset(e for e in range(64) if (L[e]&sA)&~M==0); sBB=sig(allB)
            allA=frozenset(e for e in range(64) if (L[e]&sBB)&~M==0)
        targets.append((A,allA)); targets.append((B,allB))
    return targets
def run(seed,TOP=30):
    rng=random.Random(seed)
    targets=mk_targets(rng)
    lib=[frozenset([e]) for e in range(64)]
    built=[]
    def cover(req,allw,lib):
        cands=[w for w in lib if w<=allw and w&req]
        left=set(req); n=0
        while left:
            m=max(len(w&left) for w in cands)
            best=rng.choice([w for w in cands if len(w&left)==m])
            n+=1; left-=best; 
            if not hasattr(cover,'c'): pass
        return n
    def covlist(req,allw,lib):
        cands=[w for w in lib if w<=allw and w&req]
        left=set(req); cov=[]
        while left:
            best=max(cands,key=lambda w:(len(w&left),len(w)))
            cov.append(best); left-=best
        return cov
    def total(lib):
        return sum(len(covlist(r,a,lib))-1 for r,a in targets)
    cur=total(lib)
    while True:
        covs=[covlist(r,a,lib) for r,a in targets]
        cnt={}
        for t,c in enumerate(covs):
            for x in range(len(c)):
                for y in range(x+1,len(c)):
                    u=c[x]|c[y]; cnt[u]=cnt.get(u,0)+1
        if not cnt: break
        cand=sorted(cnt,key=lambda u:(-cnt[u],rng.random()))[:TOP]
        bestu=None;bv=cur-1
        for u in cand:
            v=total(lib+[u])
            if v<bv or (v==bv and bestu is not None and rng.random()<0.3): bv=v;bestu=u
        if bestu is None or bv>=cur-1: break
        lib.append(bestu); built.append(bestu); cur=bv
    cost=len(built)+cur+len(prods)*2-1
    return cost,targets,built
if __name__=='__main__':
    best=999
    for s in range(int(sys.argv[1]),int(sys.argv[2])):
        c=run(s)[0]
        if c<best: best=c; print(s,c,flush=True)
