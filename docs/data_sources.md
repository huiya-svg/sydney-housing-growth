# Data sources and screening

Every candidate dataset is screened with four checks. Rejects stay in this table with the reason.

1. **Geography and time** — available by LGA, covering 2019 onwards?
2. **Varies between LGAs** — if identical everywhere (e.g. cash rate), it can only be a timeline overlay.
3. **Timing** — measured before / at the start of the period (plausible driver) or after (may be a result)?
4. **Licence and privacy** — licence noted; aggregated tables only in the repo.

| Dataset | Role | Source (URL) | Licence | Geography / time | 1 Geo+time | 2 Varies | 3 Timing | 4 Licence | Verdict | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Median sales price + number of sales, strata / non-strata | Core | [NSW DCJ Rent and Sales Report](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html), [issue archive](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/previous-rent-and-sales-reports.html) | [CC BY 4.0](https://dcj.nsw.gov.au/statements/copyright-and-disclaimer.html) | Published NSW LGA and aggregate rows, March 2019–March 2026 | Pass. All 29 quarters present. Wollondilly strata row absent in June 2019. | Yes | n/a | Pass. Licence recorded and only aggregate statistics retained. | Core | Issues 128–156. Latest sales quarter March 2026, issue 156. The release page was updated 18 August 2026. DCJ groups 34 LGAs under Greater Sydney. |
| Median weekly rent | Candidate | NSW DCJ Rent and Sales Report | | LGA, quarterly | | | | | TBD (T02) | |
| Population and population growth | Candidate | ABS Regional Population | | LGA, yearly | | | | | TBD (T02) | |
| Median household income | Candidate | ABS 2021 Census DataPacks | | LGA, 2021 | | | | | TBD (T02) | |
| Distance from Sydney CBD | Candidate | Calculated from LGA centroids | | LGA | | | | | TBD (T02) | |
| New dwelling supply | Candidate | NSW Housing Evidence Centre | | LGA | | | | | TBD (T02) | |
| RBA cash rate, CPI | Context only | RBA, ABS | | Australia | | No | | | Overlay / deflator only | |
| Individual property sales | Optional stretch | NSW Valuer General bulk sales | | One row per sale | | | | Address-level: never commit | TBD | |
