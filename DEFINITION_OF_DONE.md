# Definition of Done

A change is "done" only when ALL items pass, with evidence attached to the PR.

## Function
- [ ] The full user flow works end to end (not only the changed part).
- [ ] A regression test for the change fails without it and passes with it.

## Visual / UX
- [ ] Checked on mobile, tablet and desktop widths (inspected screenshots attached).
- [ ] No dead space, overflow or clipped content.
- [ ] Buttons look like buttons; touch targets >= 44px; contrast and keyboard navigation OK; form fields labelled.

## Content
- [ ] Every language of the site/app reviewed (no mixed or missing translations).
- [ ] Rendered content is complete (dates, times and counts fully shown).
- [ ] Every number displayed has a source and a date.

## Security & privacy
- [ ] No personal data exposed (the owner's or anyone else's).
- [ ] Security headers and basic security checks pass.
- [ ] Secrets only via environment/CI, never in the repo.

## Delivery
- [ ] QA verdict APROVADO with evidence (the executor never self-certifies).
- [ ] Owner's explicit OK recorded.
- [ ] After merge: the published result verified against the exact merge commit.
- [ ] Public launch: rolled out via preview first (preview -> owner OK -> production).
