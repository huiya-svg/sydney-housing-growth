# T09 — Power BI model and DAX measures (Kang, on the Windows PC)

**Phase:** 4.1–4.2 · **Who:** Kang (hands-on) · **Guide and review:** Claude
**Tool:** Power BI Desktop (Windows, free, no sign-in needed to build and save reports)

You do this task yourself. It's the part interviewers will probe most. Claude explains each step and
reviews the result. Codex doesn't touch Power BI.

---

## Part 0 — One-time setup (≈ 30 min)

### 0.1 On the Mac: put the repo on GitHub (once)

The repo isn't on GitHub yet. The Windows PC will get the files from there.

1. Commit T05 on the Mac as usual (see Claude's message).
2. Install **GitHub Desktop** for Mac (desktop.github.com) and sign in with your GitHub account.
3. **File → Add Local Repository…** and choose the `Sydney Housing Price` folder.
4. **Repository → Repository Settings… → Remote.** Paste
   `https://github.com/huiya-svg/sydney-housing-growth.git` and **Save**.
5. Click **Push origin** (top bar). Refresh the GitHub page in your browser. Your files and commit history
   should be there.

### 0.2 On the Windows PC: get the repo

1. Install **GitHub Desktop** for Windows and sign in.
2. **File → Options → Git**. Set Name `Kang Liang` and Email = your `…@users.noreply.github.com` address
   (the same one as on the Mac, so your Windows commits stay private too).
3. **File → Clone repository… → GitHub.com tab** → `huiya-svg/sydney-housing-growth` → Local path e.g.
   `C:\Users\<you>\Documents\sydney-housing-growth` → **Clone**.

### 0.3 Power BI Desktop settings (once)

**File → Options and settings → Options**:
- **Global → Data Load:** untick **Auto date/time** for new files. (Power BI otherwise builds hidden date
  tables for every date column. We have our own `dim_date`. Good interview point.)
- **Current File → Regional Settings:** Locale for import = **English (Australia)**.

### Golden rule for two computers

Before you start working on either machine: **pull first**. On Windows: GitHub Desktop → **Fetch origin →
Pull**. On the Mac: `git pull` in the project folder. After you finish: **commit and push**. Never edit the
same file on both machines without pulling in between.

---

## Part 1 — Load the four tables (≈ 20 min)

1. **Home → Get data → Text/CSV** → `data\processed\fact_sales.csv` → **Transform Data** (not Load).
2. In Power Query, check each column's type icon (top-left of the column header) and fix any wrong ones:

| Table | Column | Type |
|---|---|---|
| fact_sales | `quarter_date` | Date |
| fact_sales | `median_price`, `sales_count`, `median_price_revised_est` | Whole Number |
| fact_sales | `yoy_change` | Decimal Number |
| fact_sales | `low_sales_flag` | True/False |
| dim_date | `quarter_date` | Date; `q_index`, `year` Whole Number; `is_baseline_2019`, `is_latest_4q` True/False |
| dim_lga | `distance_km`, `pop_growth_2016_19`, rents | Decimal Number; `income_2016_weekly`, `sort_order` Whole Number; `lga_code_2025` **Text** |
| lga_growth | all `price_*`, `growth_*` | Decimal Number; `*_quarters` Whole Number |

3. **Home → New Source → Text/CSV** for `dim_lga.csv`, `dim_date.csv`, `lga_growth.csv`. Check types the same way.
4. Make sure each query is named exactly `fact_sales`, `dim_lga`, `dim_date`, `lga_growth` (right panel → Name).
5. **Close & Apply.**
6. **Stretch (recommended):** **Home → Manage Parameters → New**: `RepoPath` (Text) = your clone folder
   ending with `\`. In each query's first step (**Source**), replace the hard-coded folder with `RepoPath`. Now
   the report works on any computer by changing one parameter.

### Add a small dwelling-type table

**Home → Enter data**, table name `dim_dwelling`:

| dwelling_type | dwelling_label |
|---|---|
| house | Houses |
| unit | Units |

One slicer on this table then filters **both** fact tables.

---

## Part 2 — Model view: relationships (≈ 20 min)

Open **Model view** (left bar, third icon). Delete any relationship Power BI guessed that isn't in this list,
then create these (drag the column from the "1" side to the "many" side):

| From (one side) | To (many side) | Cardinality | Cross-filter |
|---|---|---|---|
| `dim_lga[lga]` | `fact_sales[lga]` | 1 : * | Single |
| `dim_date[quarter_date]` | `fact_sales[quarter_date]` | 1 : * | Single |
| `dim_dwelling[dwelling_type]` | `fact_sales[dwelling_type]` | 1 : * | Single |
| `dim_lga[lga]` | `lga_growth[lga]` | 1 : * | Single |
| `dim_dwelling[dwelling_type]` | `lga_growth[dwelling_type]` | 1 : * | Single |

This is a **star schema** with two fact tables sharing dimensions (sometimes called a constellation schema).
Use that wording in the README.

Then, in **Table view / Column tools**:
- `dim_lga[lga]` → **Sort by column** → `sort_order`. `dim_date[quarter_label]` → **Sort by column** → `q_index`.
- **Hide** (right-click → Hide in report view): `q_index`, `sort_order`, `lga_code_2025`, `revised_source`,
  `price_status`, and the key columns on the fact side (`fact_sales[lga]`, `fact_sales[quarter_date]`,
  `fact_sales[dwelling_type]`, `lga_growth[lga]`, `lga_growth[dwelling_type]`). Report users should slice by the
  dimension tables.
- Formats: growth columns → **Percentage**, 1 decimal; prices → **Currency**, 0 decimals.

Take a screenshot of the Model view → save as `powerbi\model_view.png`.

---

## Part 3 — Measures (type them yourself; ≈ 45 min)

**Home → Enter data** → empty table named `_Measures` (a home for measures). Select it, then
**Home → New measure** for each one below. Before you type each one, read the "why" line. After typing it,
put it in a card or table and check that the number makes sense.

```DAX
Median Price = MAX ( fact_sales[median_price] )
```
*Why MAX:* with one LGA, one quarter and one dwelling type selected there is exactly one row, and MAX returns
it. If several rows are in context (e.g. no dwelling type selected), MAX gives a wrong number, so visuals must
always have a dwelling type selected.

```DAX
Price 2019 =
CALCULATE (
    AVERAGE ( fact_sales[median_price] ),
    REMOVEFILTERS ( dim_date ),
    dim_date[is_baseline_2019] = TRUE ()
)
```
*Why `REMOVEFILTERS(dim_date)`:* this fixes a bug in the original plan. In a line chart, each point already
filters one quarter (e.g. 2023 Q1). Without removing that filter, "2023 Q1 **and** baseline 2019" matches
nothing, and the price index line goes blank. Expect an interview question on this.

```DAX
Price Latest 4Q =
CALCULATE (
    AVERAGE ( fact_sales[median_price] ),
    REMOVEFILTERS ( dim_date ),
    dim_date[is_latest_4q] = TRUE ()
)
```

```DAX
Growth Since 2019 = DIVIDE ( [Price Latest 4Q] - [Price 2019], [Price 2019] )
```
*Why `DIVIDE`:* it returns blank instead of an error when the 2019 price is blank (Wollondilly units, D05).

```DAX
Greater Sydney Growth =
CALCULATE (
    [Growth Since 2019],
    REMOVEFILTERS ( dim_lga ),
    dim_lga[geo_level] = "greater_sydney"
)
```
*Why:* the benchmark must be DCJ's **published** Greater Sydney median, never an average of the 34 LGA
medians (pitfall #1). This measure gives the same value on every row, so you can use it as a reference line.

```DAX
YoY Change =
VAR cur = [Median Price]
VAR qi = MAX ( dim_date[q_index] )
VAR prev =
    CALCULATE ( [Median Price], FILTER ( ALL ( dim_date ), dim_date[q_index] = qi - 4 ) )
RETURN DIVIDE ( cur - prev, prev )
```

```DAX
Price Index (2019 = 100) = DIVIDE ( [Median Price], [Price 2019] ) * 100
```

Format `Growth Since 2019`, `Greater Sydney Growth` and `YoY Change` as Percentage (1 dp), and the prices as
Currency (0 dp).

---

## Part 4 — Cross-check against Python (the rigour step, ≈ 15 min)

1. New page → **Table** visual with `dim_lga[lga]`, `[Growth Since 2019]` and `lga_growth[growth_pct]`.
2. Filters pane: `dim_lga[geo_level]` = `lga` and `greater_sydney`; slicer or filter `dim_dwelling` = **Houses**.
3. Check these three. All must match `lga_growth.csv` to the decimal:

| Row | Expected growth |
|---|---|
| Blacktown, houses | 72.66% |
| Greater Sydney, houses | 67.47% |
| Sydney, units (switch the filter to Units) | 6.89% |

4. Screenshot the table → `powerbi\crosscheck.png`. The README will mention this check.

If a number differs, don't change the data. Note the LGA and both numbers and send them to Claude.

---

## Part 5 — Save and commit

1. **File → Save As** → `powerbi\sydney_housing.pbix` inside the cloned repo.
2. GitHub Desktop → you'll see the `.pbix` and PNGs → summary e.g. `Add Power BI model, measures and cross-check (T09)`
   → **Commit to main** → **Push origin**.
3. On the Mac afterwards: `git pull` before your next commit.

## What to send Claude for review

- Screenshots: Model view, the cross-check table, and the Measures list (Data pane, `_Measures` expanded).
- Anything that confused you, with the step number.

## Interview checklist (be able to say each in 1–2 sentences)

- Why a star schema, and why `dim_lga` contains Greater Sydney and the rings.
- Why `Median Price` uses MAX, and when that would give a wrong answer.
- Why `REMOVEFILTERS(dim_date)` is needed in `Price 2019`.
- Why `DIVIDE` instead of `/`.
- How you proved the Power BI numbers match the Python/SQL numbers.
