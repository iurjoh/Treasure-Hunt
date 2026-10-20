# Agent Guidelines

Rules for any agent (human or AI) working in this repository. Adopted from the owner's quality framework (Flow #663, 2026-10-20).

## Workflow
1. Work on a branch; open a draft PR. Never push directly to the default branch.
2. Independent QA reviews every PR and returns APROVADO/REPROVADO with evidence (real flows, inspected screenshots on mobile/tablet/desktop). The executor never certifies its own work.
3. Nothing merges without the owner's explicit OK. After merge, verify the published result against the exact merge commit.
4. Small, closed-scope diffs. One concern per PR.

## Adversarial lens (fixed, every change)
Check each change against three failure surfaces before asking for review:
1. **User input** (forms, uploads, URL params): injection, XSS, oversized or malformed input.
2. **AI-generated input** (model output that is rendered or executed): unsanitised HTML, invented data presented as fact.
3. **Public exposure** (what a stranger can see or enumerate): personal data, tokens, internal paths, unlisted-but-guessable URLs.

## Severity levels
- **A** - cosmetic/trivial: normal review.
- **B** - normal change: full checklist in DEFINITION_OF_DONE.md.
- **C** - **BLOCKING**: unauthorised cost, unauthorised disclosure, destructive action without approval, demonstrated serious defect, or conclusion without proof. Additionally, any auth/permission change is C. Requires a dry-run or preview plus the owner's explicit OK naming the action. When in doubt, treat as C.

## Falsifiable claims
Every claim in code comments, docs, READMEs and PR descriptions must be checkable. Numbers require source and date. "Works", "fast" or "secure" without evidence is not acceptable.

## Regression rule
Every bug fix ships with a test that fails without the fix and covers every path the bug touched. Search the whole repo for other occurrences of the same pattern and list what was checked in the PR.

## Hard rules
- No personal data in the repo: no personal emails, phone numbers, addresses, tokens or private keys - not in files, history, issues or PRs.
- Dependency updates only with green CI and a separate review.
- Diagnoses from scanners or other agents are acted on only after independent verification.

See also: GOTCHAS.md (project-specific pitfalls) and DEFINITION_OF_DONE.md (delivery checklist).
