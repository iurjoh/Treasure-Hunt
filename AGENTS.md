# AGENTS.md — Treasure-Hunt

- Treasure-Hunt — Code Institute project, revived (Python).
- Live: https://treasure-hunt-due.pages.dev · Public repo. Its value is rigour: tests and honest README.

> Working rules for any AI agent (or human) contributing to this repository. Complements the README; read GOTCHAS.md before editing.

## Non-negotiables
1. **No personal data.** Never commit real personal data — the owner's or anyone else's: names, e-mails, phones, addresses, financial exports, private photos or metadata. Tests and demos use fictitious data only.
2. **Zero cost.** Free-tier services only. No paid feature, trial or quota upgrade without the owner's explicit OK.
3. **Nothing reaches production without the owner's OK.** Work ships as branches + draft PRs. After any merge, verify the published result.
4. **Accessibility on every UI change.** Buttons look like buttons, touch targets, contrast, keyboard navigation, labels.
5. **Copyright-clean assets.** Own or freely licensed material only, credited.

## Severity levels
- **A — internal/cosmetic:** act, then report.
- **B — user-facing behaviour or public content:** propose first, act on approval.
- **C — money, third-party data, or destructive/irreversible action** (deletes, force-push, publishing a private repo, live data schema/rule changes, rotating keys): dry-run + explicit owner OK before executing. Blocking — never assume consent.

## Adversarial lens
Run on every change that touches user input, AI-generated output or public exposure:
- Input: injection, XSS, oversized payloads, path traversal, malformed files.
- AI output: prompt injection through user or content input; model output is never trusted as code without review.
- Exposure: what becomes visible once public — history, URLs, logs, error messages, bundled env vars.

## Definition of done
A change is "done" only when all pass, with evidence:
1. End-to-end flows work (desktop + mobile + tablet for UI).
2. No dead space; rendered content complete (no truncated dates, times or labels).
3. Texts and languages verified; bilingual UIs show one language at a time.
4. Tests green; every bug fix adds a regression test that fails without the fix, after searching all occurrences of the same pattern.
5. Independent QA verdict (APROVADO/REPROVADO) with evidence — the executor never self-certifies.

## Falsifiable claims
Every claim in the README, docs and comments must be checkable: how do we know it works? Which case breaks it? What is real vs. simulated? How is it undone? Numbers shown in the app carry source + date.

## Workflow
- Branch per change, draft PR, commits that read like a real developer's history (planning → steps → tests), never one giant "final" commit.
- README stays current: EN default with PT link, one live-demo link at the top.
- Deferred ideas become issues labelled `future`.
- Small adjustments logged with date and reason.
