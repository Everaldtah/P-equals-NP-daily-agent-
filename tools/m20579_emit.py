# usage: python3 emit.py <pairs-json> <single-json> <seed>  -> writes L_meta_20579.lean if size<=170
import json,sys,random,re
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_pair.py')).read().split('rng=random.Random(int(sys.argv[1]))')[0])
def build(P,seed):
    rng=random.Random(seed)
    targets=[]
    for k,(A,B) in enumerate(P):
        sA,sB=sig(A),sig(B)
        if rng.random()<0.5:
            allA=frozenset(e for e in range(64) if (L[e]&sB)&~M==0); sAA=sig(allA)
            allB=frozenset(e for e in range(64) if (L[e]&sAA)&~M==0)
        else:
            allB=frozenset(e for e in range(64) if (L[e]&sA)&~M==0); sBB=sig(allB)
            allA=frozenset(e for e in range(64) if (L[e]&sBB)&~M==0)
        targets.append((A,allA)); targets.append((B,allB))
    lib=[frozenset([e]) for e in range(64)]; wire={frozenset([e]):e for e in range(64)}
    codes=[]
    def cover(req,allw):
        cands=[w for w in lib if w<=allw and w&req]
        left=set(req); cov=[]
        while left:
            best=max(cands,key=lambda w:(len(w&left),rng.random()))
            cov.append(best); left-=best
        return cov
    while True:
        covs=[cover(r,a) for r,a in targets]
        cnt={};par={}
        for t,c in enumerate(covs):
            for x in range(len(c)):
                for y in range(x+1,len(c)):
                    u=c[x]|c[y]; cnt[u]=cnt.get(u,0)+1; par.setdefault(u,(c[x],c[y]))
        if not cnt: break
        mx=max(cnt.values())
        if mx<2: break
        u=rng.choice([k for k,v in cnt.items() if v==mx])
        lib.append(u)
        a,b=par[u]
        if u not in wire:
            codes.append((1,wire[a],wire[b])); wire[u]=63+len(codes)
    covs=[cover(r,a) for r,a in targets]
    def chain(c):
        w=wire[c[0]]
        for x in c[1:]:
            codes.append((1,w,wire[x])); w=63+len(codes)
        return w
    tw=[chain(c) for c in covs]
    ands=[]
    for k in range(len(P)):
        codes.append((0,tw[2*k],tw[2*k+1])); ands.append(63+len(codes))
    w=ands[0]
    for a in ands[1:]:
        codes.append((1,w,a)); w=63+len(codes)
    return codes,w
def check(codes,out):
    Wv=list(L)
    for o,a,b in codes: Wv.append(Wv[a]|Wv[b] if o==1 else Wv[a]&Wv[b])
    return Wv[out]==M
if __name__=='__main__':
    pairs=[tuple(p) for p in json.loads(sys.argv[1])]; single=json.loads(sys.argv[2])
    P=mkprods(pairs,single)
    best=None
    for s in range(int(sys.argv[3]),int(sys.argv[4])):
        codes,out=build(P,s)
        if check(codes,out) and (best is None or len(codes)<len(best[0])): best=(codes,out); print(s,len(codes),flush=True)
    codes,out=best
    if len(codes)<=170:
        t=open('/home/runner/work/P-equals-NP-daily-agent-/pequalnp-proofs/lean/PEqualNP/Outside/L_meta_20578.lean').read()
        t=t.replace('L_meta_20578','L_meta_20579').replace('C.size ≤ 180','C.size ≤ 170')
        body=',\n    '.join(','.join('(%d,%d,%d)'%c for c in codes[i:i+9]) for i in range(0,len(codes),9))
        t=re.sub(r'let codes : List \(ℕ × ℕ × ℕ\) := \[.*?\]\n  let C','let codes : List (ℕ × ℕ × ℕ) := [\n    '+body+']\n  let C',t,flags=re.S)
        t=t.replace('.or, [a,b]⟩), 243⟩','.or, [a,b]⟩), %d⟩'%out)
        open('L_meta_20579.lean','w').write(t); print('written',len(codes),out)
