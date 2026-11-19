# Repository Scope and Publication Controls

## Only deliverable

The portfolio is the central GitHub repository and its agreed folders. Do not add a separate portfolio website or homepage, custom domain, hosting configuration, GitHub Pages site, or web deployment.

Interactive projects may contain local HTML, CSS, JavaScript, and local server code when that is part of the demonstration. Their run instructions must bind to loopback where a local server is used. A local demo is not a hosted portfolio.

## Client information

- Use synthetic or specifically authorized data only.
- Do not publish client names, logos, identifiers, source documents, screenshots, operational baselines, personal information, confidential commercial details, or testimonials without explicit authorization.
- Where authorization for attribution or source details is absent, omit those details from the public tree.
- A client-confirmed workflow is not automatically approved for public disclosure.
- Do not invent client engagements, outcomes, metrics, or testimonials.

## Project status labels

Every project README must use exactly one of: `CONCEPT`, `DEMO`, `PROTOTYPE`, or `IMPLEMENTED`. The label describes the current artifact maturity and does not imply production readiness or client approval.

## Automated guard

`scripts/validate_public_repository.py` checks the current repository tree for known web-deployment workflow markers, root hosting manifests, the six category indexes, a maturity label in every demo README, and basic anonymized case-study publication requirements. Its checks are intentionally conservative and do not scan historical Git objects or prove legal authorization.
