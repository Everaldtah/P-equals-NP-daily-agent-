import random,sys
from m20579_rows import R
def T(R):
    return [sum(((R[i]>>j)&1)<<i for i in range(32)) for j in range(32)]
def paar(targets,rng):
    # targets: list of sets (as lists of base indices) ; base 0..31 singletons
    reps=[set(i for i in range(32) if t>>i&1) for t in targets]
    nb=32; gates=[]
    while True:
        cnt={}
        for r in reps:
            l=sorted(r)
            for a in range(len(l)):
                for b in range(a+1,len(l)):
                    cnt[(l[a],l[b])]=cnt.get((l[a],l[b]),0)+1
        if not cnt: break
        mx=max(cnt.values())
        if mx<2:
            # remaining: each rep needs len-1 gates
            gates.append(sum(len(r)-1 for r in reps if len(r)>1)); break
        best=[p for p,c in cnt.items() if c==mx]
        a,b=rng.choice(best)
        new=nb; nb+=1; gates.append(1)
        for r in reps:
            if a in r and b in r: r.discard(a); r.discard(b); r.add(new)
    return sum(gates)
rng=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 0)
best=10**9
for it in range(int(sys.argv[2]) if len(sys.argv)>2 else 50):
    for tr in (0,1):
        rows=R if tr==0 else T(R)
        thr=rng.choice([14,15,16,17,18,32])
        tg=[];nc=0
        for r in rows:
            if bin(r).count('1')>thr: tg.append(r^0xffffffff); nc+=1
            else: tg.append(r)
        c=paar(tg,rng)+nc+63
        if c<best: best=c; print(it,tr,thr,c,flush=True)
