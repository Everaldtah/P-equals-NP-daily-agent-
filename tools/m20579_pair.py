import pickle,random,sys
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_flex.py')).read().split('best=999')[0])
rects=pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'m20579_rects.pkl'),'rb'))
def compat(a,b): return not (rects[a][0]&rects[b][0]) and not (rects[a][1]&rects[b][1])
def mkprods(pairs,single):
    P=[]
    for a,b in pairs:
        (R1,C1),(R2,C2)=rects[a],rects[b]
        P.append((frozenset(R1)|frozenset(32+j for j in C2), frozenset(R2)|frozenset(32+j for j in C1)))
    for s in single:
        R1,C1=rects[s]; P.append((frozenset(R1),frozenset(32+j for j in C1)))
    return P
# recover original pairing
orig=[];single=[]
used=set()
for A,B in prods:
    Ar=frozenset(e for e in A if e<32);Bc=frozenset(e-32 for e in B if e>=32)
    Br=frozenset(e for e in B if e<32);Ac=frozenset(e-32 for e in A if e>=32)
    ids=[]
    for k,(r,c) in enumerate(rects):
        if (r==Ar and c==Bc) or (r==Br and c==Ac): ids.append(k)
    if len(ids)==2: orig.append(tuple(ids))
    else: single.append(ids[0])
g=globals()
def evalp(pairs,single,seeds):
    g['prods']=mkprods(pairs,single)
    return min(run(s)[0] for s in seeds)
rng=random.Random(int(sys.argv[1]))
cur=list(orig); curv=evalp(cur,single,range(3)); print('orig',curv,flush=True)
best=curv
while True:
    new=list(cur)
    i,j=rng.sample(range(len(new)),2)
    (a,b),(c,d)=new[i],new[j]
    if rng.random()<0.5: p1,p2=(a,c),(b,d)
    else: p1,p2=(a,d),(b,c)
    if not(compat(*p1) and compat(*p2)): continue
    new[i],new[j]=p1,p2
    v=evalp(new,single,range(2))
    if v<=curv+ (1 if rng.random()<0.1 else 0):
        cur,curv=new,v
        if v<best: best=v; print('best',v,cur,single,flush=True)
