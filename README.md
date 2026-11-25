# P = NP daily agent

A scheduled Claude Code agent, run free on GitHub Actions ([workflow](.github/workflows/pnp-agent.yml)), that takes part in the open attack on P vs NP at
https://pequalnp.com (rules: https://pequalnp.com/join.txt) for GitHub user **Everaldtah**.

It runs on GitHub's hosted runners on a schedule (one run every 5 hours, plus a manual "Run workflow" button), so it keeps working when your own
computer is off. The schedule ticks every hour and a 10-second `gate` job lets a tick through only when the last run started
at least 4 h 40 min ago (`logs/LAST_RUN`): GitHub delays and sometimes drops scheduled runs, and this way a dropped tick costs
an hour instead of a whole 5-hour window. The skipped ticks show in the Actions tab as runs whose `run` job was skipped. Each run:

1. asks the pequalnp.com desk for one open step (a Lean 4 statement), holding a lease on it;
2. works on it for a fixed time box, renewing the lease every 5 minutes;
3. if Lean accepts a proof, opens a pull request from the fork `Everaldtah/pequalnp-proofs`
   to `open-goat/pequalnp-proofs`; otherwise releases the step with an honest reason;
4. writes a work log of what it tried (approaches, small cases, failed tactics, the Lean file)
   to `logs/` and any finished Lean files to `proofs/`, and pushes them to this repository.

The instructions each run follows are in [AGENT.md](AGENT.md). What earlier runs learned is in [NOTES.md](NOTES.md):
each run reads it first and updates it at the end (the runner is wiped after every job, so this file is the agent's memory).
If the agent stops before its time box is used, the workflow resumes the same conversation, up to three times.

## Usage budget

Claude has no setting for "use N% of my limit". Usage is capped by limiting each run instead:
one run per 5-hour window, with a work time box (see `TIME_BOX_MINUTES` in AGENT.md). Lower the
time box to use less, raise it to use more.

## What is public

Pull requests to `open-goat/pequalnp-proofs` show your GitHub handle, avatar and commit. Turn on
"Keep my email addresses private" in GitHub's email settings to keep your email out of commits.

## Setup

Two repository secrets (Settings → Secrets and variables → Actions):

- `CLAUDE_CODE_OAUTH_TOKEN`: from `claude setup-token`
- `PNP_GH_TOKEN`: a classic token with `public_repo` and `workflow` scopes (forks, pushes, opens the PR)

Each run's full transcript (the agent's reasoning and tool calls) is saved to `logs/transcripts/`.

## When something goes wrong

- **No scheduled runs at all:** GitHub registers a schedule when the workflow file is pushed to the default branch.
  Disable and re-enable the workflow (Actions tab → pnp-agent → ⋯), or push any change to the workflow file.
  Public repositories with no commits for 60 days have their schedules switched off; the log commits each run prevent that.
- **Red X with "No agent session finished successfully":** usually an expired `CLAUDE_CODE_OAUTH_TOKEN`. Run
  `claude setup-token` again and replace the secret.
- **"Configure git identity and gh" fails:** `PNP_GH_TOKEN` expired or lost a scope; make a new classic token.
- Each run's summary (sessions, turns, minutes, the agent's final report) is on the run page in the Actions tab.
