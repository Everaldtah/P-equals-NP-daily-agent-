# Sweep small C4-free bipartite graphs with no star component; test whether a circuit with
# |E| + tau - 2 gates exists (a counterexample to L-meta-6390). Uses ao2_exact.py.
import itertools, subprocess, sys, os
from multiprocessing import Pool
here=os.path.dirname(os.path.abspath(__file__))
def comps(n1,n2,E):
    adj={}
    for i,j in E: adj.setdefault(('x',i),set()).add(('y',j)); adj.setdefault(('y',j),set()).add(('x',i))
    seen=set(); out=[]
    for v in adj:
        if v in seen: continue
        st=[v]; seen.add(v); c=[v]
        while st:
            u=st.pop()
            for w in adj[u]:
                if w not in seen: seen.add(w); st.append(w); c.append(w)
        out.append(c)
    return out,adj
def ok(n1,n2,E):
    for a,b in itertools.combinations(range(n1),2):
        if sum(1 for j in range(n2) if (a,j) in E and (b,j) in E)>1: return False
    cs,adj=comps(n1,n2,E)
    for c in cs:
        ec=sum(len(adj[v]) for v in c)//2
        if any(len(adj[v])==ec for v in c): return False   # star
    # no isolated vertices (keep graphs minimal)
    if len(adj)!=n1+n2: return False
    return True
def tau(n1,n2,E):
    for k in range(n1+n2+1):
        for X in itertools.combinations([('x',i) for i in range(n1)]+[('y',j) for j in range(n2)],k):
            Xs=set(X)
            if all(('x',i) in Xs or ('y',j) in Xs for i,j in E): return k
def canon(n1,n2,E):
    best=None
    for p in itertools.permutations(range(n1)):
        for q in itertools.permutations(range(n2)):
            t=tuple(sorted((p[i],q[j]) for i,j in E))
            if best is None or t<best: best=t
    return best
def run(job):
    n1,n2,E,S=job
    es=','.join(f'{i}-{j}' for i,j in E)
    try:
        r=subprocess.run([sys.executable,os.path.join(here,'ao2_exact.py'),str(n1),str(n2),es,str(S)],capture_output=True,text=True,timeout=int(os.environ.get('TO','300')))
        return job, r.stdout.strip().split('\n')[-1], r.stdout
    except subprocess.TimeoutExpired:
        return job,'TIMEOUT',''
if __name__=='__main__':
    maxN=int(sys.argv[1]); jobs=[]; seen=set()
    minN=int(sys.argv[2]) if len(sys.argv)>2 else 0
    for n1 in range(2,maxN):
        for n2 in range(n1,maxN-n1+1):
            if n1+n2<minN: continue
            pairs=[(i,j) for i in range(n1) for j in range(n2)]
            for m in range(3,len(pairs)+1):
                for E in itertools.combinations(pairs,m):
                    Es=set(E)
                    if not ok(n1,n2,Es): continue
                    c=(n1,n2,canon(n1,n2,E))
                    if c in seen: continue
                    seen.add(c); jobs.append((n1,n2,list(c[2]),m+tau(n1,n2,Es)-2))
    print(len(jobs),'graphs',flush=True)
    with Pool(4) as pool:
        for job,res,out in pool.imap_unordered(run,jobs):
            print(job,res,flush=True)
            if res=='SAT': print(out,flush=True)
