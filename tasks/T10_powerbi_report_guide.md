# T10 — Power BI report pages, screenshots and PDF (Kang, on the Windows PC)

**Phase:** 4.3 · **Who:** Kang (hands-on) · **Guide and review:** Claude
**Before you start:** GitHub Desktop → **Fetch origin → Pull** (to get T07/T08 outputs and this guide). In Power
BI, **Home → Refresh**.

Four pages, one question each (project plan, Phase 4). Design rules for every page:
- the title **states the finding**;
- at most 2 colours plus grey;
- the dwelling-type slicer in the **same place** on pages 1–3.

**Checkpoints:** send Claude a screenshot after each page. Small fixes are cheaper one page at a time.

---

## Part 0 — Set-up (≈ 15 min)

### 0.1 Theme colours (the same as the Python charts)
The colours are saved in a small theme file in the repo, `powerbi/sydney_theme.json`:
- Color 1 = `#23578A` (blue, highlight);
- Color 2 = `#A54B16` (orange, benchmark or "bottom");
- Color 3 = `#BFC5CC` (grey, everyone else).

Load it:
1. Open the ribbon tab that shows the theme thumbnails. That's **View** in older versions and **Design** in newer ones.
2. Find the small **▾ arrow** at the right edge of the thumbnail row, and click it to open the full theme menu.
3. Click **Browse for themes**, pick `<repo>\powerbi\sydney_theme.json` and click **Open**. Power BI says
   "Theme imported successfully".

Check it worked: open **Customize current theme** in the same ▾ menu, or the colour picker of any visual. The first
three theme colours should be blue, orange and grey.

*Why a file:* it's reproducible and version-controlled, like the rest of the repo. Anyone who clones the repo gets
the same colours.

### 0.2 Load the factor-test results (for page 3)
**Home → Get data → Text/CSV → `data\processed\factor_tests.csv` → Transform Data.** Set the types: `n` Whole Number;
`rho`, `p`, `p_holm`, `rho_rev`, `p_rev` Decimal Number; the rest Text. Delete `Columns=…` in the Advanced Editor
and use `RepoPath` as in T09 step 1.7. **Close & Apply.**
Model view: relationship `dim_dwelling[dwelling_type]` → `factor_tests[dwelling_type]` (1 : \*, Single). Now the
dwelling slicer filters it too.

### 0.3 Hide the cross-check page
Right-click the **Cross-check** page tab → **Hide page**. It stays in the file as proof, but not in the report.

---

## Part 1 — New measures (type them; ≈ 30 min)

Same as T09: right-click `_Measures` → **New measure**. Read each "why" line first.

```DAX
CPI Ratio =
DIVIDE (
    CALCULATE ( AVERAGE ( dim_date[cpi_sydney] ), REMOVEFILTERS ( dim_date ), dim_date[is_latest_4q] = TRUE () ),
    CALCULATE ( AVERAGE ( dim_date[cpi_sydney] ), REMOVEFILTERS ( dim_date ), dim_date[is_baseline_2019] = TRUE () )
)
```
*Why:* average CPI of the latest four quarters ÷ average CPI of 2019, the same windows as the price growth. It
should show **1.241** (prices in general rose 24.1%).

```DAX
Real Growth Since 2019 =
IF (
    NOT ISBLANK ( [Growth Since 2019] ),
    DIVIDE ( 1 + [Growth Since 2019], [CPI Ratio] ) - 1
)
```
*Why the `IF`:* in DAX, `1 + BLANK()` is `1`, not blank. Without the guard, Wollondilly units (no 2019 price) would
show a made-up −19.4% instead of blank. Missing stays missing.

```DAX
Greater Sydney Real Growth =
CALCULATE ( [Real Growth Since 2019], REMOVEFILTERS ( dim_lga ), dim_lga[geo_level] = "greater_sydney" )
```

```DAX
Fastest LGA =
VAR lgas = CALCULATETABLE ( VALUES ( dim_lga[lga] ), dim_lga[geo_level] = "lga" )
VAR top1 = TOPN ( 1, lgas, [Growth Since 2019], DESC )
RETURN CONCATENATEX ( top1, dim_lga[lga], ", " )
```
*Why:* `TOPN` ranks the 34 LGAs by the growth measure and keeps the top one. `CONCATENATEX` turns that one-row table
into text, and would list both names if two LGAs tied.

```DAX
Fastest Growth =
MAXX ( CALCULATETABLE ( VALUES ( dim_lga[lga] ), dim_lga[geo_level] = "lga" ), [Growth Since 2019] )
```

```DAX
Growth Rank =
IF (
    NOT ISBLANK ( [Growth Since 2019] ),
    RANKX ( CALCULATETABLE ( VALUES ( dim_lga[lga] ), dim_lga[geo_level] = "lga" ), [Growth Since 2019], , DESC )
)
```

```DAX
Bar Colour =
IF ( NOT ISBLANK ( [Growth Rank] ) && [Growth Rank] <= 5, "#23578A", "#BFC5CC" )
```
*Why `NOT ISBLANK` again:* DAX treats blank as 0 in comparisons, so `BLANK() <= 5` is **true**. Without the guard, a
blank rank would be coloured as "top 5".

```DAX
Distance (km) = MAX ( dim_lga[distance_km] )
```

```DAX
Ring Colour = IF ( SELECTEDVALUE ( dim_lga[region] ) = "Middle Ring", "#23578A", "#BFC5CC" )
```

**Formats:** `Real Growth Since 2019`, `Greater Sydney Real Growth` and `Fastest Growth` → Percentage, 1 dp.
`CPI Ratio` → Decimal, 3 dp. `Distance (km)` → Decimal, 1 dp.

**Check with a quick table** (on the hidden Cross-check page is fine):

| Selection | Measure | Expected |
|---|---|---|
| Houses | Greater Sydney Real Growth | 34.9% |
| Units | Greater Sydney Real Growth | −4.8% |
| Houses | Fastest LGA / Fastest Growth | Fairfield / 83.0% |
| Units | Fastest LGA / Fastest Growth | Hawkesbury / 58.8% |

---

## Part 2 — Page 1 "The answer" (≈ 45 min)

Rename Page 1 → `The answer`.

### 2.1 Dwelling slicer (copy it to pages 2–3 later)
1. Click an empty part of the canvas → Visualizations → **Slicer** → field `dim_dwelling[dwelling_label]`.
2. Format visual → **Slicer settings → Options → Style: Tile**; **Selection → Single select: On**.
3. Put it **top right**, about 250 × 60 px. Select **Houses**.

*Why single select:* every measure assumes one dwelling type (`Median Price` uses MAX). Houses and units must never
mix (D01).

### 2.2 Bar chart: growth by LGA
1. Visualizations → **Clustered bar chart**.
   - **Y-axis:** `dim_lga[lga]`.
   - **X-axis:** `[Growth Since 2019]`.
2. **Filters on this page:** `dim_lga[geo_level]` = `lga`.
3. Sort: the visual's **… (More options) → Sort axis → Growth Since 2019**, then **Sort descending**.
4. Make it tall (left two-thirds of the page) so all 34 bars fit. If they don't, a scroll bar appears, and that's OK.
5. **Bar colour:** Format visual → **Bars → Color → fx** → Format style **Field value** → field `[Bar Colour]` → OK.
   The top 5 turn blue; the rest grey.
6. **Greater Sydney line:** Analytics pane (magnifier icon) → **Constant line → Add line → Value fx** →
   `[Greater Sydney Growth]`. Colour `#A54B16`, dashed, data label on, label text "Greater Sydney".
7. Data labels: Format → **Data labels: On**, 1 decimal.

### 2.3 Three cards (right side, below the slicer)
Visualizations → **Card** (new card). One card each:
- `[Greater Sydney Growth]`, label "Greater Sydney, nominal";
- `[Greater Sydney Real Growth]`, label "Greater Sydney, after inflation";
- `[Fastest LGA]`, with `[Fastest Growth]` underneath (or two small cards).

**No "slowest" card.** For houses it would say Woollahra, and Woollahra's first-published growth is understated
(revised: 64.8%, rank 17). Interview point: "I left it out on purpose because the sensitivity check showed it isn't robust."

### 2.4 Title
Insert → **Text box** at the top-left, large and bold:
> **Houses grew 67% since 2019 and units 18%. After inflation, units went backwards.**

Subtitle (smaller, grey): "Median sale price, 2019 average vs the four quarters to March 2026. Source: NSW DCJ Rent
and Sales Report."

*Stretch, a dynamic title:* a measure such as
`Page 1 Title = SELECTEDVALUE ( dim_dwelling[dwelling_label] ) & ": " & [Fastest LGA] & " grew fastest (" & FORMAT ( [Fastest Growth], "0%" ) & ")"`
used in a card or in Format visual → Title → **fx**.

### ✋ Checkpoint 1
Screenshot the page with **Houses**, then with **Units**, and send both to Claude.

---

## Part 3 — Page 2 "Trends" (≈ 30 min)

1. New page `Trends`. **Copy the slicer** from page 1 (Ctrl+C, Ctrl+V). When asked "Sync slicers?" choose **Sync**.
   It lands in the same position.
2. **Line chart:**
   - **X-axis:** `dim_date[quarter_date]`. Format → X-axis → Type **Continuous**.
   - **Y-axis:** `[Price Index]`.
   - **Legend:** `dim_lga[lga]`.
3. **Area picker:** a second slicer `dim_lga[lga]` on the left, list style, multi-select. Select **Greater Sydney**,
   **Inner Ring**, **Middle Ring** and **Outer Ring**. Users can tick any LGA to compare.
4. Colours (Format → Lines → Colors): Greater Sydney `#23578A` (thick, 3 px); the rings in greys; any picked
   LGA `#A54B16`.
5. Analytics → **Constant line** at **100**, light grey, label "2019 average".
6. **Tooltips:** drag `[Median Price]` and `[YoY Change]` into the **Tooltips** well. Hovering a point shows the
   actual price and the year-on-year change.
7. Y-axis title: "Price index (2019 average = 100)". This is where the "2019 = 100" from the old measure name goes.
8. Title (text box). Claude checked this against the Greater Sydney data, and it's true for both houses and units:
   > **Prices surged in 2021, fell through 2022, then climbed to new highs by 2024.**

   The detail: houses peaked at index 152 (2021 Q4), fell to 135 (2023 Q1), and passed the old peak in 2023 Q4.
   Units peaked at 113, fell to 105, and passed the old peak in 2024 Q4.

### ✋ Checkpoint 2
Screenshot with Houses, and send it.

---

## Part 4 — Page 3 "Why?" (≈ 45 min)

1. New page `Why`. Paste the synced slicer.
2. **Filters on this page:** `dim_lga[geo_level]` = `lga`.
3. **Scatter 1: distance.**
   - **Values:** `dim_lga[lga]`.
   - **X-axis:** `[Distance (km)]`.
   - **Y-axis:** `[Growth Since 2019]`.
   - Format → **Markers → Color → fx → Field value → `[Ring Colour]`**. Middle-ring LGAs turn blue.
   - Format → **Category label: On** (shows LGA names; turn it off if it's too cluttered).
   - Title: "Distance to CBD (km)". Axis titles with units.
4. **Scatter 2: 2019 price.** The same, with X-axis `[Price 2019]` (Currency, $ m). Title "2019 median price".
5. **Results table:**
   - **Table** visual with `factor_tests[factor]`, `family`, `n`, `rho`, `p`, `p_holm` and `verdict`.
   - Format `rho` to 2 dp and `p`, `p_holm` to 3 dp. Set each to **Don't summarize** (Columns well → arrow).
   - The dwelling slicer filters it through the relationship from Part 0.2.
6. Title (text box):
   > **Fast-growing houses were mid-distance and cheaper in 2019. For units, no factor showed a clear link.**

   Small note under the scatters: "Spearman rank correlation, 34 LGAs (33 for units). Price, rent and income move
   together, so their effects can't be separated. Association, not cause."

### ✋ Checkpoint 3
Screenshots with Houses and Units.

---

## Part 5 — Page 4 "Notes" (≈ 30 min; write it in your own words)

New page `Notes`, using text boxes only. Write these sections as short bullets:
- **Question and answer** (1 sentence each).
- **Data sources:**
  - NSW DCJ Rent and Sales Report (CC BY 4.0), March 2026 quarter issue;
  - ABS Regional Population, Census 2016 G02, CPI (A2325806K) and ASGS 2025 boundaries (CC BY 4.0 / 2.5 AU).
- **Method (4–5 bullets):**
  - the growth definition (D02);
  - houses and units separate;
  - the published Greater Sydney figure, never averaged;
  - real growth with Sydney CPI;
  - Spearman with Holm for the exploratory factors.
- **Limitations:**
  - first-published medians run slightly low (Woollahra houses most affected);
  - low-sales quarters (Burwood houses, Hawkesbury and Hunters Hill units);
  - Wollondilly units have no 2019 baseline;
  - 34 LGAs is a small sample: associations, not causes;
  - distances are measured on 2025 boundaries.
- **Quality check:** "Every Power BI growth figure matches the Python/SQL pipeline (cross-check page)."
- **Links:** GitHub repo URL; your name and LinkedIn.

---

## Part 6 — Export and commit (≈ 15 min)

1. On each page, use **Houses** for the screenshot (Units for page 3 too, if you like).
   **Win + Shift + S** → save as:
   - `powerbi\page1_answer.png`
   - `powerbi\page2_trends.png`
   - `powerbi\page3_why.png`
   - `powerbi\page4_notes.png`
2. **File → Export → Export to PDF** → `powerbi\sydney_housing_report.pdf`.
3. **Ctrl + S.** GitHub Desktop → summary `Add Power BI report pages, screenshots and PDF (T10)` → Commit →
   **Push origin**.

## Interview checklist

- Why the slicer is single-select.
- Why there's no "slowest LGA" card.
- Why `Real Growth` needs `IF ( NOT ISBLANK … )`, and why `Bar Colour` does too.
- How `TOPN` / `RANKX` work over `VALUES ( dim_lga[lga] )`.
- What the page 3 table shows, and why price, rent and income can't be separated.
