# Numerically test L-pcx-416: rank over Q of Z(P,Q) equals prod of component factors.
import itertools, sys
from fractions import Fraction
import random

def rank_mod(M, p):
    M=[[x%p for x in r] for r in M]; r=0; cols=len(M[0]) if M else 0
    for c in range(cols):
        piv=None
        for i in range(r,len(M)):
            if M[i][c]: piv=i;break
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]; inv=pow(M[r][c],p-2,p)
        M[r]=[x*inv%p for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                f=M[i][c]; M[i]=[(a-f*b)%p for a,b in zip(M[i],M[r])]
        r+=1
    return r

def test(n, sigma, tau, A, z, p=1000003):
    V=[(b,i) for b in (0,1) for i in range(n)]
    def arc(u,v):
        return u[0]==0 and v[0]==1 and ((u[1] in A) != (v[1] in A)) and sigma[u[1]]!=tau[u[1]] and (v[1]==sigma[u[1]] or v[1]==tau[u[1]])
    adj={u:[v for v in V if arc(u,v) or arc(v,u)] for u in V}
    seen=set(); prod=1
    for u in V:
        if u in seen: continue
        comp=[u]; seen.add(u); k=0
        while k<len(comp):
            for w in adj[comp[k]]:
                if w not in seen: seen.add(w); comp.append(w)
            k+=1
        if all(len(adj[x])==2 for x in comp):
            e=len(comp)//2-2
            f=3*2**e if e>=0 else Fraction(3,2**(-e))
        else: f=2**(len(comp)//2)
        prod*=f
    # z as num/den mod p : z^energy
    zn,zd=z
    zz=zn*pow(zd,p-2,p)%p
    # Z(P,Q) depends only on P∩{(0,i): i in A} and Q∩{(1,j): j notin A}
    pinsP=[b*n+i for b in (0,1) for i in range(n) if i in A]
    pinsQ=[b*n+j for b in (0,1) for j in range(n) if j not in A]
    ys=list(itertools.product((0,1),repeat=2*n))
    def energy(y):
        a=y[:n]; b=y[n:]
        return sum(a[i]!=b[i] for i in range(n))+sum(a[i]!=b[sigma[i]] for i in range(n))+sum(a[i]==b[tau[i]] for i in range(n))
    en=[energy(y) for y in ys]
    rows=[]
    for Ps in itertools.chain.from_iterable(itertools.combinations(pinsP,k) for k in range(len(pinsP)+1)):
        row=[]
        for Qs in itertools.chain.from_iterable(itertools.combinations(pinsQ,k) for k in range(len(pinsQ)+1)):
            s=0
            for y,e in zip(ys,en):
                if all(y[i]==0 for i in Ps) and all(y[j]==0 for j in Qs):
                    s+=pow(zz,e,p)
            row.append(s%p)
        rows.append(row)
    return rank_mod(rows,p), prod

if __name__=='__main__':
    nmax=int(sys.argv[1]); zs=[(2,1),(1,2),(3,1),(5,3),(7,2)]
    bad=0; cnt=0
    for n in range(1,nmax+1):
        perms=list(itertools.permutations(range(n)))
        for s in perms:
          for t in perms:
            for k in range(n+1):
              for A in itertools.combinations(range(n),k):
                for z in zs:
                    r,pr=test(n,s,t,set(A),z); cnt+=1
                    if r!=pr:
                        bad+=1
                        if bad<15: print('MISMATCH n',n,'sigma',s,'tau',t,'A',A,'z',z,'rank',r,'claim',pr)
    print('tested',cnt,'mismatches',bad)
