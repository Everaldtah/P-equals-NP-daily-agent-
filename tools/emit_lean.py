# Emit a Lean proof for an existential FanInTwo circuit statement.
# Usage: python3 emit_lean.py <unit id e.g. L_meta_20557> <statement file> "<gates python list>"
# Statement file: the skeleton (we keep its header and theorem line, replace sorry).
import sys, ast
uid, skel, gl = sys.argv[1], sys.argv[2], ast.literal_eval(sys.argv[3])
src=open(skel).read()
head=src[:src.index(':= by')+len(':= by')]
G='PEqualNP.CircuitLowerBounds.GateOp.'
gs=[]
for o,a,b in gl:
    ins=f'[{a}]' if o=='not' else f'[{a}, {b}]'
    gs.append('{ op := '+G+o+', inputs := '+ins+' }')
N=int(sys.argv[4]) if len(sys.argv)>4 else None
out=N+len(gl)-1
k=len(gl)
pat=' | '.join(['rfl']*k)
print(head)
print('  refine ⟨({ gates := ['+', '.join(gs)+f'], output := {out} }} : PEqualNP.CircuitLowerBounds.Circuit), ?_, by decide, ?_⟩')
print('  · intro g hg')
print('    simp only [List.mem_cons, List.not_mem_nil, or_false] at hg')
print(f'    rcases hg with {pat} <;> simp')
print('  · decide +kernel')
