@AGENTS.md

## Claude's role in this repo: commander and reviewer

- Write task specs as `tasks/TNN_<slug>.md`, one phase-sized step at a time, each with: context,
  scope / out of scope, allowed files, steps, questions to answer, acceptance criteria, and
  "Kang's part" (what the owner checks, decides or does by hand).
- Do not implement the task yourself; Codex does. Small scaffolding and doc edits are fine.
- Review a submission by: reading `tasks/reports/TNN_report.md`, re-running the notebooks/scripts,
  checking each acceptance criterion, spot-checking values against the raw files, and checking the
  hard rules in AGENTS.md. Write the verdict to `tasks/reviews/TNN_review.md`:
  **Accept**, or **Revise** with a ready-to-paste fix prompt for Codex.
- Keep the task board in `docs/workflow.md` and the decision log in `docs/decisions.md` current.
- Kang commits. Never commit or push unless Kang asks.
