# Workflow and task board

## The loop (one task at a time)

1. **Claude** writes the task spec `tasks/TNN_<slug>.md`.
2. **Kang** reads it, edits anything that should change, then starts Codex in the repo root and pastes:
   `Read AGENTS.md, then carry out tasks/TNN_<slug>.md exactly. Write your report to tasks/reports/TNN_report.md.`
3. **Codex** does the work and writes `tasks/reports/TNN_report.md`.
4. **Kang** tells Claude "TNN is done". **Claude** re-runs and checks everything and writes
   `tasks/reviews/TNN_review.md` with **Accept** or **Revise** (+ a ready-to-paste fix prompt).
5. **Kang** does the task's "Kang's part" (spot checks, decisions in `docs/decisions.md`), then commits.

Codex is started with network access (needed for downloads and package installs):

```bash
codex -c sandbox_workspace_write.network_access=true
```

## Task board

| ID | Task | Phase | Who | Status |
|---|---|---|---|---|
| P0 | Power BI account, GitHub account + repo, LinkedIn URL | 0 | Kang | To do |
| T01 | Python environment + core DCJ sales data: download and first look | 0–1 | Codex | Ready |
| T02 | Candidate "why" factors: find, download, screen (rent, population, income, distance, supply, CPI) | 1 | Codex | — |
| T03 | Greater Sydney LGA reference table + regions; reshape and clean core sales to long format | 2 | Codex | — |
| T04 | Clean the factors that passed screening; build `dim_lga` | 2 | Codex | — |
| T05 | `sql/transform.sql` (joins, CTE, window functions), `dim_date`, validation, export 4 CSVs | 2 | Codex | — |
| T06 | `docs/data_dictionary.md` for every column | 2 | Codex | — |
| T07 | Growth measurement: nominal + real, ranking, annualised rate (Phase 3A) | 3 | Codex | — |
| T08 | Factor tests: scatter, Spearman, correlation matrix, optional regression; draft findings | 3 | Codex + Kang | — |
| T09 | Power BI semantic model, star schema, DAX measures, cross-check vs Python | 4 | **Kang** (Claude guides) | — |
| T10 | Power BI report pages 1–4, screenshots, PDF export | 4 | **Kang** (Claude reviews) | — |
| T11 | README write-up, limitations, reproduce steps, final checklist | 5 | Kang + Codex | — |
| T12 | LinkedIn post draft | 5 | Kang | — |
