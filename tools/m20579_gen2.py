import random,sys
src=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_flex2.py')).read()
exec(src.split("def mk_targets")[0])
pc=lambda x: bin(x).count('1')
def specs(rng):
    T=[]
    cov=[sig(A)&sig(B) for A,B in prods]
    own=[0]*len(prods)
    for p in range(1024):
        if M>>p&1:
            ks=[k for k in range(len(prods)) if cov[k]>>p&1]
            own[rng.choice(ks)]|=1<<p
    it=iter(own)  # (target_points, forbidden_mask)  wire w usable iff w & forb == 0 ; cover target points
    for A,B in prods:
        sA,sB=sig(A),sig(B)
        if rng.random()<0.5: A,B,sA,sB=B,A,sB,sA
        # A flexible: usable w: w & sB & ~M ==0 ; target sA & sB
        T.append((next(it), sB&~M&FULL))
        # B fixed exact
        T.append((sB, FULL&~sB))
    return T
def run(seed,NI=2000):
    rng=random.Random(seed)
    T=specs(rng)
    lib=list(L)
    def cover(t,f):
        cands=[w for w in lib if w&f==0 and w&t]
        left=t; cov=[]
        while left:
            best=max(cands,key=lambda w:(pc(w&left),-pc(w)))
            cov.append(best); left&=~best
        return cov
    built=0
    covs=[cover(t,f) for t,f in T]; cur=sum(len(c)-1 for c in covs)
    while True:
        cnt={}
        for c in covs:
            for x in range(len(c)):
                for y in range(x+1,len(c)):
                    u=c[x]|c[y]; cnt[u]=cnt.get(u,0)+1
        cand=sorted(cnt,key=lambda u:(-cnt[u],rng.random()))[:15]
        # intersections
        for _ in range(NI):
            a,b=rng.sample(lib,2); w=a&b
            if w: cand.append(w)
        # score each cand quickly: number of targets where w usable and covers >=2 cover elements' worth
        sc=[]
        for w in set(cand):
            s=0
            for (t,f),c in zip(T,covs):
                if w&f==0 and pc(w&t)>=2:
                    # how many cover elements become redundant: elements whose t-part subset of w
                    k=sum(1 for e in c if (e&t)&~w==0)
                    if k>=2: s+=k-1
            sc.append((s,rng.random(),w))
        sc.sort(reverse=True)
        bestw=None;bv=cur
        for s,_,w in sc[:12]:
            if s<2: break
            lib.append(w)
            nc=[cover(t,f) for t,f in T]; v=sum(len(c)-1 for c in nc)
            lib.pop()
            if v<bv: bv=v;bestw=w;bc=nc
        if bestw is None or bv+1>=cur: break
        lib.append(bestw); built+=1; cur=bv; covs=bc
    return built+cur+31, built, cur
if __name__=='__main__':
    best=999
    for s in range(int(sys.argv[1]),int(sys.argv[2])):
        r=run(s)
        if r[0]<best: best=r[0]; print(s,r,flush=True)
