# T09 — Power BI model and DAX measures (Kang, on the Windows PC)

**Phase:** 4.1–4.2 · **Who:** Kang (hands-on) · **Guide and review:** Claude
**Tool:** Power BI Desktop (Windows, free, no sign-in needed to build and save reports)

You do this task yourself. It's the part interviewers will probe most. Claude explains each step and
reviews the result. Codex doesn't touch Power BI.

**Checkpoints.** Stop and send Claude screenshots at **Checkpoint A** (end of Part 2) and
**Checkpoint B** (end of Part 4). Don't rush past a checkpoint: a wrong relationship makes every measure wrong.

**Saving.** Press **Ctrl + S** often. Power BI has no autosave.

---

## Part 0 — One-time setup

### 0.1 On the Mac (done)
The repo is on GitHub: `huiya-svg/sydney-housing-growth`.

### 0.2 On the Windows PC: get the repo (done)
Cloned with GitHub Desktop. In the steps below, `<repo>` means your clone folder, e.g.
`C:\Users\<you>\Documents\GitHub\sydney-housing-growth`. In GitHub Desktop, **Repository → Show in Explorer**
opens it.

### Golden rule for two computers
**Before** you start on either machine, pull first. On Windows: GitHub Desktop → **Fetch origin**, then **Pull
origin** if it appears. On the Mac: `git pull`. **After** you finish, commit and push. Never edit the same file on
both machines without pulling in between.

### 0.3 Power BI settings (≈ 5 min)

1. Open Power BI Desktop. On the start screen, click **Blank report** (or **New**). Some settings only exist
   once a report is open.
2. **File → Options and settings → Options.** The window has two groups on the left: **GLOBAL** (all files)
   and **CURRENT FILE** (this report only).
3. **GLOBAL → Data Load.** Under *Time intelligence*, **untick "Auto date/time for new files"**.
4. **CURRENT FILE → Data Load.**
   - Under *Time intelligence*, **untick "Auto date/time"**.
   - Under *Relationships*, **untick "Autodetect new relationships after data is loaded"**. You'll create
     every relationship yourself in Part 2, so you know exactly why each one exists.
5. **CURRENT FILE → Regional Settings → Locale for import → English (Australia).**
6. Click **OK**.
7. **File → Save as →** `<repo>\powerbi\sydney_housing.pbix`. The `powerbi` folder already exists.

> **Interview point.** With Auto date/time on, Power BI builds a hidden date table for **every** date column.
> That makes the file bigger and the model harder to read. We have our own `dim_date`, so we turn it off.

---

## Part 1 — Load the four tables (≈ 30 min)

### 1.1 Load `fact_sales`

1. **Home → Get data → Text/CSV.** Browse to `<repo>\data\processed\fact_sales.csv` and click **Open**.
2. A preview window appears. Check that:
   - **File origin** is `65001: Unicode (UTF-8)`;
   - **Delimiter** is `Comma`;
   - **Data type detection** is `Based on first 200 rows`.
3. Click **Transform Data**, **not** Load. The **Power Query Editor** opens in a new window.

### 1.2 What you're looking at in Power Query

- **Left: Queries.** One per table. The name comes from the file name (`fact_sales`).
- **Middle: a data preview.** Each column header has a small **type icon** on its left:

  | Icon | Type |
  |---|---|
  | calendar | Date |
  | `123` | Whole Number |
  | `1.2` | Decimal Number |
  | `ABC` | Text |
  | ✓✗ (check/cross) | True/False |

- **Right: Applied Steps.** Power BI records each step, usually *Source → Promoted Headers → Changed Type*.
  These steps re-run every time you click Refresh. That's why we fix types here, not later.
- **Turn on column quality:** **View** tab → tick **Column quality**. Under each header you'll see
  *Valid / Error / Empty* percentages. **Error must be 0%.** Empty is fine: missing stays missing (rule 5).

### 1.3 Fix column types

Click the **type icon** in a column header and pick the right type. If Power BI asks *"Change Column Type:
Replace current or Add new step?"*, choose **Replace current**. That keeps a single *Changed Type* step.

Set every column as below. Most will already be correct; the ones marked ⚠ are often detected wrongly.

**fact_sales**

| Column | Type |
|---|---|
| `lga`, `dwelling_type`, `price_status`, `revised_source` | Text |
| `quarter_date` | Date |
| `median_price`, `sales_count`, `median_price_revised_est` | Whole Number |
| `low_sales_flag` | True/False |
| `yoy_change` | Decimal Number |

### 1.4 Load the other three tables

Stay in Power Query: **Home → New Source → Text/CSV**, choose the next file, then click **OK** in the preview
(inside Power Query there is no Transform button; it goes straight into the editor). Fix types the same way.

**dim_lga**

| Column | Type |
|---|---|
| `lga`, `geo_level`, `region` | Text |
| `lga_code_2025` ⚠ | **Text**. It's an ID code, not a quantity, so it must never be summed. |
| `distance_km`, `pop_growth_2016_19`, `rent_2019_house_weekly`, `rent_2019_unit_weekly` | Decimal Number |
| `income_2016_weekly`, `sort_order` | Whole Number |

**dim_date**

| Column | Type |
|---|---|
| `quarter_date` | Date |
| `year`, `q_index` | Whole Number |
| `quarter_label` | Text |
| `is_baseline_2019`, `is_latest_4q` | True/False |
| `cpi_sydney` (new in T07) | Decimal Number |

**lga_growth**

| Column | Type |
|---|---|
| `lga`, `geo_level`, `region`, `dwelling_type`, `growth_note` | Text |
| `baseline_quarters`, `latest_quarters`, `baseline_low_sales_quarters`, `latest_low_sales_quarters` | Whole Number |
| `price_2019`, `price_latest`, `price_2019_rev`, `price_latest_rev` | Decimal Number |
| `growth_pct`, `growth_annualised`, `growth_pct_rev`, `cpi_ratio`, `growth_pct_real` | Decimal Number |
| `growth_rank`, `growth_rank_rev`, `rank_change_rev` | Whole Number |

### 1.5 Check and apply

1. In the **Queries** list, the four names must be exactly `fact_sales`, `dim_lga`, `dim_date`, `lga_growth`.
   To rename one, right-click it → **Rename**.
2. Click through each query. Every column must show **Error 0%**.
3. **Home → Close & Apply.** Power BI loads the data, which takes a few seconds.
4. **Check the row counts.** Open **Table view** (left bar, second icon) and click each table. The row count is
   shown bottom-left. Expected: `fact_sales` **2,204**, `dim_lga` **38**, `dim_date` **29**, `lga_growth` **76**.

### 1.6 Add the dwelling-type table

1. **Home → Enter data.**
2. Double-click the header `Column1` and rename it `dwelling_type`. Click **+** to add a second column and name
   it `dwelling_label`.
3. Type two rows:

   | dwelling_type | dwelling_label |
   |---|---|
   | house | Houses |
   | unit | Units |

4. Bottom-left **Name:** `dim_dwelling` → **Load**.

**Why:** both fact tables have `dwelling_type`. A slicer on `dim_dwelling` filters **both** at once, and it shows
the nicer labels "Houses / Units".

### 1.7 Required: remove the fixed column count (and make the file portable)

Each CSV query's first step was written with a **fixed column count**, e.g. `Columns=10`. If a CSV later gains
columns (T08 will add some), Power BI would **silently ignore** them. Remove that count. While you're in the
same line, also swap the hard-coded Windows folder for a parameter, so the file refreshes on any computer.

1. Open Power Query: go to **Report view** (left bar, first icon) → **Home → Transform data**. If you can't see
   the button, widen the window or click the **<** arrow at the left end of the ribbon.
2. **Create the parameter:** in Power Query, **Home → Manage Parameters → New Parameter**. Name `RepoPath`,
   Type **Text**, Current value = your clone folder **ending with a backslash**, e.g.
   `C:\Users\<you>\Documents\GitHub\sydney-housing-growth\` → **OK**.
3. **Edit one query:** in the **Queries** list on the left, **right-click `fact_sales` → Advanced Editor**.
   A window with code opens. The `Source = ...` line looks like this:
   ```text
   Source = Csv.Document(File.Contents("C:\Users\...\data\processed\fact_sales.csv"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
   ```
   Change it to:
   ```text
   Source = Csv.Document(File.Contents(RepoPath & "data\processed\fact_sales.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
   ```
   That's two edits: the path becomes `RepoPath & "data\processed\fact_sales.csv"`, and `Columns=10, ` is
   deleted. Click **Done**. If a yellow error bar appears, check the quotes and commas.
4. Do the same for `dim_lga`, `dim_date` and `lga_growth`. Each has its own file name and its own `Columns=` number.
5. **Home → Close & Apply.** Check that the row counts are unchanged (2,204 / 38 / 29 / 76).

---

## Part 2 — Model view: relationships (≈ 30 min)

### 2.1 Open Model view

On the left bar, the icons are **Report**, **Table**, **Model** (three linked boxes) and sometimes **DAX query**.
Click **Model**. You'll see five table cards. Drag them into a star layout: `fact_sales` in the centre, with
`dim_lga` on the left, `dim_date` at the top and `dim_dwelling` at the bottom. Put `lga_growth` anywhere it sits
close to both `dim_lga` and `dim_dwelling`, e.g. below `dim_lga`. The exact layout doesn't matter; readable lines do.

Because you turned off autodetect, there should be **no lines yet**. If you see any, click the line → **Delete**.

### 2.2 Create the five relationships

**How:** drag a column from the **dimension** card (the "1" side) and drop it **on the same column** in the fact
card (the "many" side). A **New relationship** window opens. For each one, check:
- the two columns shown are the right ones;
- **Cardinality: One to many (1:\*)**;
- **Cross filter direction: Single**;
- **Make this relationship active**: ticked.

Then click **OK** (or **Save**).

| # | From (one side) | To (many side) |
|---|---|---|
| 1 | `dim_lga[lga]` | `fact_sales[lga]` |
| 2 | `dim_date[quarter_date]` | `fact_sales[quarter_date]` |
| 3 | `dim_dwelling[dwelling_type]` | `fact_sales[dwelling_type]` |
| 4 | `dim_lga[lga]` | `lga_growth[lga]` |
| 5 | `dim_dwelling[dwelling_type]` | `lga_growth[dwelling_type]` |

Dragging can be fiddly. The alternative is **Home → Manage relationships → New**, where you choose both tables and
click the column in each.

**Stop and tell Claude if:**
- Power BI suggests **Many to many** or **One to one** for any of these. That means a key isn't unique where it
  should be.
- It refuses because of a **type mismatch**: e.g. `quarter_date` is Date on one side and Text on the other.
  Go back to Part 1.3.

There's no relationship between `dim_date` and `lga_growth`. That's correct: `lga_growth` is a summary over
fixed windows and has no quarter column.

**What you should see:** five lines, each with a **1** at the dimension end, a **\*** at the fact end and an
arrow pointing toward the fact table. That arrow is the filter direction.

### 2.3 Sort orders (Table view)

1. **Table view** → open the **Data** pane on the right → click table `dim_lga` → click the column `lga`.
2. Ribbon **Column tools → Sort by column → `sort_order`**. Greater Sydney and the rings now come first in
   visuals, then the LGAs alphabetically.
3. Table `dim_date` → column `quarter_label` → **Sort by column → `q_index`**. Without this, "2019 Q1, 2019 Q2,
   …" still sorts correctly by luck, but the explicit sort is the professional habit.

### 2.4 Stop Power BI from summing things it shouldn't

Power BI puts a **Σ** next to numeric columns and **sums** them by default when you drag them into a visual.
Summing medians, ranks or years is meaningless.

For each column below: select it → **Column tools → Summarization → Don't summarize**.
- `fact_sales`: `median_price`, `median_price_revised_est`, `yoy_change`
- `dim_date`: `year`, `q_index`, `cpi_sydney`
- `dim_lga`: `sort_order`, `distance_km`, `pop_growth_2016_19`, `income_2016_weekly`, both rents
- `lga_growth`: every numeric column

Leave `fact_sales[sales_count]` as **Sum**, because summing sales counts is meaningful.

> **Interview point.** "You can't add up medians. The median of a group isn't the sum or the average of the
> sub-group medians. So I turned off default summarisation and used explicit measures."

### 2.5 Hide technical columns

In **Model view**, right-click **each** column listed below → **Hide in report view** (all of them, both groups). Hidden columns show greyed out. They still
work in relationships and DAX; report users just don't see them.
- Fact-side keys: `fact_sales[lga]`, `fact_sales[quarter_date]`, `fact_sales[dwelling_type]`, `lga_growth[lga]`,
  `lga_growth[dwelling_type]`. Users should slice by the dimension tables.
- Helpers: `dim_lga[sort_order]`, `dim_lga[lga_code_2025]`, `dim_date[q_index]`,
  `fact_sales[revised_source]`, `fact_sales[price_status]`.

### 2.6 Number formats

Go to **Table view** (left bar, second icon). The **Column tools** ribbon only appears there, after you click
a column. Select a column → **Column tools → Format**:
- **Dates:** `dim_date[quarter_date]` → Format → **Custom**, `yyyy-mm-dd`. If your Windows language is Chinese,
  dates otherwise show as `2019年1月1日`, and recruiters would see that in the report.
- **Percentage, 1 decimal:** `yoy_change`, `growth_pct`, `growth_annualised`, `growth_pct_rev`,
  `growth_pct_real`, `pop_growth_2016_19`.
- **Currency, 0 decimals** ($ English (Australia)): `median_price`, `median_price_revised_est`, `price_2019`,
  `price_latest`, `price_2019_rev`, `price_latest_rev`, both rents, `income_2016_weekly`.
- **Decimal, 3 decimals:** `cpi_ratio`.

### 2.7 Screenshot and save

1. **Ctrl + S.**
2. In Model view, arrange the cards so all five lines are visible. Press **Win + Shift + S**, drag over the
   diagram, then click the notification → **Save** as `<repo>\powerbi\model_view.png`.

### ✋ Checkpoint A: send Claude
- `model_view.png`;
- one screenshot of **Home → Manage relationships** (the list of five);
- the four row counts from step 1.5.4.

---

## Part 3 — Measures (type them yourself; ≈ 45 min)

### 3.1 A home for measures
1. **Home → Enter data** → leave the default column empty → Name `_Measures` → **Load**.
2. In the **Data** pane, right-click `_Measures` → **New measure**. The formula bar opens above the canvas.
3. Type the measure and press **Enter**. If there's an error, a yellow bar explains it.
4. After your first measure, right-click `_Measures[Column1]` → **Delete** (or Hide). The table icon becomes a
   calculator, and the table moves to the top of the Data pane.

Before you type each measure, read its "why" line. After typing it, test it on a card or in a table.

```DAX
Median Price = MAX ( fact_sales[median_price] )
```
*Why MAX:* with one LGA, one quarter and one dwelling type selected there's exactly one row, and MAX returns it.
If several rows are in context (e.g. no dwelling type selected), MAX gives a wrong number, so visuals must always
have a dwelling type selected.

```DAX
Price 2019 =
CALCULATE (
    AVERAGE ( fact_sales[median_price] ),
    REMOVEFILTERS ( dim_date ),
    dim_date[is_baseline_2019] = TRUE ()
)
```
*Why `REMOVEFILTERS(dim_date)`:* this fixes a bug in the original plan. In a line chart, each point already filters
one quarter (e.g. 2023 Q1). Without removing that filter, "2023 Q1 **and** baseline 2019" matches nothing, and the
price-index line goes blank. Expect an interview question on this.

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
*Why:* the benchmark must be DCJ's **published** Greater Sydney median, never an average of the 34 LGA medians
(pitfall #1). This measure gives the same value on every row, so you can use it as a reference line.

```DAX
YoY Change =
VAR cur = [Median Price]
VAR qi = MAX ( dim_date[q_index] )
VAR prev =
    CALCULATE ( [Median Price], FILTER ( ALL ( dim_date ), dim_date[q_index] = qi - 4 ) )
RETURN DIVIDE ( cur - prev, prev )
```

```DAX
Price Index = DIVIDE ( [Median Price], [Price 2019] ) * 100
```
*Name:* a measure name can't contain `=`. The formula bar treats the first `=` as the end of the name. Put
"2019 = 100" in the chart's axis title instead.

Format: select each measure → **Measure tools → Format**. `Growth Since 2019`, `Greater Sydney Growth` and
`YoY Change` → Percentage (1 dp). Prices → Currency (0 dp). Price Index → Decimal (1 dp).

---

## Part 4 — Cross-check against Python (the rigour step, ≈ 20 min)

**Goal:** one table showing, for every LGA, the growth **Power BI calculates** (`[Growth Since 2019]`) next to
the growth **Python/SQL calculated** (`lga_growth[growth_pct]`). If the two columns are equal, your DAX is proven
correct.

**Two things to know first**
- **Filters don't need to be in the visual.** You can filter a table by `geo_level` or dwelling type without showing
  those columns. You drag them into the **Filters pane** instead.
- **The panes on the right** (Report view): **Filters**, **Visualizations** and **Data**. If one is collapsed to a
  thin strip, click its name or the `<<` arrow to open it. If one is missing, open the **View** tab and click it on.

### 4.1 Make a page and a table
1. **Report view** (left bar, first icon, the bar chart).
2. At the bottom, click **+** to add a page. Double-click its tab and rename it `Cross-check`.
3. Click on an **empty** part of the white canvas, so no visual is selected.
4. **Visualizations** pane → **Build visual** tab → click the **Table** icon (a small grid; hover over the icons and
   the tooltip says "Table"). An empty table frame appears on the canvas.
   *Shortcut:* with nothing selected, tick a **text** column in the Data pane and Power BI makes a table by itself.
5. Drag the frame's corner to make it large (most of the page).

### 4.2 Put three fields in the table

First make a measure for the Python/SQL value: right-click `_Measures` → **New measure**:
```DAX
Growth (Python) = MAX ( lga_growth[growth_pct] )
```
*Why a measure and not the raw `growth_pct` column:* the table groups rows by `dim_lga[lga]`. A raw column from
another table (`lga_growth[growth_pct]`) becomes a **second grouping column**, and Power BI then pairs every LGA with
every growth value it finds (many rows per LGA). As a measure, it's calculated **inside** each LGA's row, after
the relationships have filtered `lga_growth` to that LGA and dwelling type, which leaves exactly one row, so MAX
returns it. Rule of thumb: **put dimension columns in rows and measures in values.**

With the table selected (it has a border), tick these in the **Data** pane:
1. `dim_lga` → `lga`
2. `_Measures` → `Growth Since 2019`
3. `_Measures` → `Growth (Python)`

### 4.3 Add the two filters (Filters pane)
1. Open the **Filters** pane. It has sections **Filters on this visual**, **Filters on this page** and
   **Filters on all pages**.
2. Drag `dim_lga` → `geo_level` from the Data pane into **Filters on this visual** ("Add data fields here").
   The filter card opens: choose **Basic filtering** and tick **lga** and **greater_sydney**. Rings drop out.
3. Drag `dim_dwelling` → `dwelling_label` into **Filters on this visual**. Tick **Houses** only.

You should now see 35 rows: 34 LGAs and Greater Sydney. Greater Sydney sorts first because of the `sort_order`
you set in Part 2.3.

### 4.4 Show two decimals and remove the total row
1. In the Data pane click the measure `Growth Since 2019` → ribbon **Measure tools** → click the **%** button
   (so it shows 67.47%, not 0.67) → decimal places **2**.
2. Do the same for the measure `Growth (Python)`.
3. Select the table → Visualizations pane → **Format visual** (paintbrush) → **Visual** → **Totals** → **Off**.
   The total row would show a growth "averaged" over all LGAs' medians, which is exactly the meaningless number
   pitfall #1 warns about.

### 4.5 Check
| Row | Expected growth (both columns) |
|---|---|
| Blacktown, houses | 72.66% |
| Greater Sydney, houses | 67.47% |
| Sydney, units (in the filter card, untick Houses and tick **Units**) | 6.89% |

Scan the whole table. The two growth columns must be equal on **every** row. In Units, Wollondilly is blank in
both columns, which is correct (D05).

### 4.6 Screenshot
Set the filter back to **Houses**, press **Win + Shift + S**, select the table, then click the notification →
**Save** as `<repo>\powerbi\crosscheck.png`. **Ctrl + S** to save the report.

If a number differs, don't change the data. Note the LGA and both numbers and send them to Claude.

### ✋ Checkpoint B: send Claude
`crosscheck.png`, and a screenshot of the Data pane with `_Measures` expanded.

---

## Part 5 — Save and commit

1. **Ctrl + S** (`<repo>\powerbi\sydney_housing.pbix`).
2. GitHub Desktop → **Changes** tab: you'll see the `.pbix` and PNGs. Summary:
   `Add Power BI model, measures and cross-check (T09)` → **Commit to main** → **Push origin**.
3. On the Mac afterwards: `git pull` before your next commit.

## When the CSVs change later (e.g. new columns from T08)

Pull in GitHub Desktop, then in Power BI click **Home → Refresh**. Your relationships, measures and formats stay.
New columns appear at the end of each table; set their type in Power Query if needed.

## Interview checklist (be able to say each in 1–2 sentences)

- Why a star schema, and why `dim_lga` contains Greater Sydney and the rings.
- Why Auto date/time is off and summarisation is set to "Don't summarize".
- Why `Median Price` uses MAX, and when that would give a wrong answer.
- Why `REMOVEFILTERS(dim_date)` is needed in `Price 2019`.
- Why `DIVIDE` instead of `/`.
- DAX `AVERAGE` skips blanks, but the SQL rule needs all 4 quarters. Why do they still agree here? (Only
  Wollondilly units have a gap, and they have 0 of 4 quarters, so both give blank.)
- How you proved the Power BI numbers match the Python/SQL numbers.
