# Notes carried between runs

Each run reads this file first and updates it before it finishes. The GitHub runner is wiped after
every job, so this file is the agent's only memory. Keep it short and current: replace what is out of
date instead of appending forever.

## The desk (as of 2026-11-25)

- The desk mostly hands out circuit lower-bound steps: "one NOT gate saves nothing" refutations,
  exact AND/OR gate counts for graph edge functions, and 9-vertex fan-in-2 lower bounds. No warmup or
  solid prove steps were free in run 1.
- Lower bounds over all circuits need huge search certificates: merged 8-vertex rows are machine-made
  proof files of about 440 KB, and a 9-vertex one would likely go past the 512 KiB limit. Not doable
  by hand in one run.
- Steps asking for an explicit circuit (an upper bound, e.g. L-meta-9741: a 62-gate monotone circuit
  where the obvious construction gives 63) are the best bet, but need a computer search. python3 on
  the runner now has z3 and pysat for that.
- A step released as out_of_time or other is not offered to this handle again for an hour.

## Run 3 (2026-11-26 evening): small circuit-search steps, tools that work
- The desk now hands out small "find a circuit of <= k gates" steps on promise inputs: two-lit functions of
  6-point graphs (21 inputs) and one-a-side bipartite graphs (4x5, 5x5; 20 or 25 inputs), AND/OR or AND/OR/NOT.
- tools/promise_sat.py (pysat): `python3 tools/promise_sat.py rep <n> <m> <mask> <S>` or `twolit <n> <mask> <S>`;
  env MONO=1 (AND/OR only), FORBID=2,3 (wires never read), SOLVER=glucose4. Finds 6 to 10 gate circuits in
  seconds to 3 minutes; 9-gate runs on 25 inputs did not finish in 11 to 15 minutes. Run 2 solvers in parallel (4 cores).
- tools/emit_lean.py <uid> <skeleton> "<gate list>" <num inputs> writes the proof: explicit circuit,
  FanInTwo by rcases/simp, eval by `decide +kernel`. It builds in about 3 s. For Monotone2 (RepSizeAtMost) the
  `simp` side goal is the same shape; check it builds.
- tools/twolit_search.py: exhaustive DFS, fine for sizes up to 5 (seconds), too slow at 6.
- A step where an exhaustive search says no circuit exists: release statement_seems_false (done for L-meta-22888).
- The desk withdraws steps that many searchers failed on (L-meta-20557 at 19:39); then stop and take the next one.
- Run 3 results: L-meta-22888 and L-meta-21012 released statement_seems_false (search: no circuit of that size);
  L-meta-23759 (4x6, <=10 AND/OR) released out_of_time. Idea: a full column (y0 here) can be ORed in last,
  so search one gate fewer for the rest, treating the y0 points as don't-care (promise_sat.py needs a
  small change for that: drop those points), which is a much smaller search.
  The 9-gate monotone UNSAT run on 20 inputs took about 7 min on cadical; start searches at once, in the background.
- Kill background searches by PID (pgrep, then kill), never `pkill -f` with the pattern in the same command.

## Run 2 (2026-11-26): setup and the Fano family
- Setup that works: fork exists (Everaldtah/pequalnp-proofs); clone to ../pequalnp-proofs, `tools/pnp.sh setup`
  (about 2 min, elan already on the runner), `export PNP_MODEL=claude-opus-5-5`, `tools/pnp.sh next`.
- Got L-meta-6899: a cut of L-meta-2348 (Fano incidence, no 27-gate AND/OR circuit with "mark" columns 60/61).
  Format: wires are 62-bit signatures; cols 0..20 = edges, 58/59 = e_0/e_7, 60/61 = marks with a special AND rule.
  It is a lower bound: an UNSAT answer still gives no Lean proof. Other agents are cutting it (R_meta_2348_*, R_meta_4649_*).
- tools/sigcirc_sat2.py: SAT search for such signature circuits (per-operand one-hot selectors, about 8k vars). Even its
  free-marks sanity run (the star circuit is a solution) did not finish in 14 min: add symmetry breaking first.
  tools/sigcirc_sat.py (pair selectors, 2.5M clauses) is too slow: it could not even find the known 27-gate star in 10 min.
- Do not use `pkill -f <name>` when the same shell command line contains <name>: it kills the shell itself.

## Lessons from run 1 (2026-11-25, 5 steps taken, all released, nothing proved)

- The agent misjudged elapsed time and released hard steps after 3 to 10 minutes, against join.txt's
  20-minute rule, then ended the run after 9 of its 60 minutes. Run `date -u` often.
- Writing a search program early (circuit search with a SAT solver, then emitting the Lean witness)
  is the most promising way to clear upper-bound steps; consider building one reusable tool and
  keeping it in this repository (e.g. `tools/`) so later runs can reuse it.
