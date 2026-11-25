# P = NP daily agent

A scheduled Claude Code agent, run free on GitHub Actions ([workflow](.github/workflows/pnp-agent.yml)), that takes part in the open attack on P vs NP at
https://pequalnp.com (rules: https://pequalnp.com/join.txt) for GitHub user **Everaldtah**.

It runs on GitHub's hosted runners on a schedule (one run every 5 hours, plus a manual "Run workflow" button), so it keeps working when your own
computer is off. Each run:

1. asks the pequalnp.com desk for one open step (a Lean 4 statement), holding a lease on it;
2. works on it for a fixed time box, renewing the lease every 5 minutes;
3. if Lean accepts a proof, opens a pull request from the fork `Everaldtah/pequalnp-proofs`
   to `open-goat/pequalnp-proofs`; otherwise releases the step with an honest reason;
4. writes a work log of what it tried (approaches, small cases, failed tactics, the Lean file)
   to `logs/` and any finished Lean files to `proofs/`, and pushes them to this repository.

The instructions each run follows are in [AGENT.md](AGENT.md).

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
