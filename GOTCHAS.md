# Regression and gotcha register

Quality trial started 2026-10-20. Review friction around 2026-11-20. Pass counters below record new, independently evidenced runs only, not historical results.

## Regressions

No regression checks recorded yet. Entry format: - [YYYY-MM-DD] <bug> -> check: <deterministic re-run command> | consecutive passes: n/5. Do not record historical results as passes.

Five recorded consecutive passes make a check eligible for automation; adding CI is a separate code change. Record revision, environment and evidence before increasing a count. No automatic edits or release approval follow from a counter.

## Gotchas


- [2026-10-20] The "70/70 tests" claim dates from the revival QA run and needs a fresh re-run to stay true; keep the suite green | source: revival status record, 2026-10-08 | version: current | validity: re-verify on every change | projects: Treasure-Hunt.
- [2026-10-20] Dependency discipline: pure front-end; any new dependency needs a stated reason (zero-cost, no bloat) | source: owner standing rule (zero-cost services) | version: current | validity: permanent | projects: Treasure-Hunt (shared rule candidate: all projects).

## Check entry points

Python/JS project revived from Code Institute - inspect the repo's test tooling. Live on Cloudflare Pages. Report exactly what ran and where.

If a gotcha is independently observed in a second project, propose a shared rule with both sources.
