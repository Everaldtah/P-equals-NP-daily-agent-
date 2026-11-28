import pickle,random,sys
from m20579_rows import R
rects=pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_rects.pkl'),'rb'))
N=[{j for j in range(32) if R[i]>>j&1} for i in range(32)]
NC=[{i for i in range(32) if R[i]>>j&1} for j in range(32)]
print('naive',sum(len(a)-1 for a,b in rects),sum(len(b)-1 for a,b in rects))
def paar_flex(targets,rng):
    # targets: list of (req set, allowed set) over 0..31 ; OR-circuit, returns cost
    lib=[frozenset([e]) for e in range(32)]; built=0
    def cov(r,a):
        c=[w for w in lib if w<=a and w&r]; left=set(r); out=[]
        while left:
            m=max(len(w&left) for w in c)
            b=rng.choice([w for w in c if len(w&left)==m]); out.append(b); left-=b
        return out
    while True:
        cs=[cov(r,a) for r,a in targets]
        cnt={}
        for c in cs:
            for x in range(len(c)):
                for y in range(x+1,len(c)):
                    u=c[x]|c[y]; cnt[u]=cnt.get(u,0)+1
        if not cnt or max(cnt.values())<2: break
        mx=max(cnt.values())
        lib.append(rng.choice([u for u in cnt if cnt[u]==mx])); built+=1
    cs=[cov(r,a) for r,a in targets]
    return built+sum(len(c)-1 for c in cs)
rng=random.Random(int(sys.argv[1]))
best=999
for it in range(int(sys.argv[2])):
    rt=[];ct=[]
    for a,b in rects:
        if rng.random()<0.5:
            ra={i for i in range(32) if b<=N[i]}; rt.append((a,ra)); 
            ca={j for j in range(32) if ra<=NC[j]} if rng.random()<0.5 else set(b)
            ct.append((b,ca))
        else:
            ca={j for j in range(32) if a<=NC[j]}; ct.append((b,ca))
            ra={i for i in range(32) if ca<=N[i]} if rng.random()<0.5 else set(a)
            rt.append((a,ra))
    c=paar_flex(rt,rng)+paar_flex(ct,rng)
    if c<best: best=c; print(it,c,c+61,flush=True)
