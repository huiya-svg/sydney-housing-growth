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
- **Newer Power BI (Design tab):** **Design → Import theme**, then pick `<repo>\powerbi\sydney_theme.json` and click **Open**.
- **Older Power BI (View tab):** **View → Themes ▾ → Browse for themes**, then pick the same file.

Check it worked: select any visual, open the colour picker, and look at the top row. It should start with blue,
orange, grey.

**Fallback if the colours don't change:**
- *Newer Power BI:* **Design → Customize theme** opens a **Theme** pane on the right, inside Visualizations. Expand
  **Colors** and set the first three data colours to the hex codes above. Click a colour box → **More colors** → type
  the hex code.
- *Older Power BI:* **View → Themes ▾ → Customize current theme → Name and colors** → set Color 1–3 → **Apply**.

Note: a table visual (like the Cross-check page) doesn't use theme colours. Check the colours in the pane or on a
chart, not on the table.

*Why a file:* it's reproducible and version-controlled, like the rest of the repo. Anyone who clones the repo gets
the same colours.

### 0.2 Load the factor-test results (for page 3)
**Home → Get data → Text/CSV → `data\processed\factor_tests.csv` → Transform Data.** Set the types: `n` Whole Number;
`rho`, `p`, `p_holm`, `rho_rev`, `p_rev` Decimal Number; the rest Text. Delete `Columns=…` in the Advanced Editor
and use `RepoPath` as in T09 step 1.7. **Close & Apply.**
Model view → **Manage relationships → New relationship**:
- **From table:** `dim_dwelling`, click the `dwelling_type` column (the "one" side: 2 rows, each value once);
- **To table:** `factor_tests`, click `dwelling_type` (the "many" side: 5 rows per value);
- **Cardinality:** One to many (1:\*); **Cross-filter direction:** Single → **Save**.

Now the dwelling slicer filters this table too. *Don't* link `factor_tests` to `lga_growth` or to `fact_sales`: neither
has each dwelling type only once, so Power BI refuses ("duplicate value 'house'"). Fact tables only link through
dimensions.

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
RETURN IF ( NOT ISBLANK ( [Fastest Growth] ), CONCATENATEX ( top1, dim_lga[lga], ", " ) )
```
*Why:* `TOPN` ranks the 34 LGAs by the growth measure and keeps the top one. `CONCATENATEX` turns that one-row table
into text, and would list both names if two LGAs tied. *Why the `IF`:* if there's no growth data at all, every LGA
"ties" on blank and `TOPN` returns all 34, so the card would list "Bayside, Blacktown, …". The guard shows blank
instead.

```DAX
Fastest Growth =
MAXX ( CALCULATETABLE ( VALUES ( dim_lga[lga] ), dim_lga[geo_level] = "lga" ), [Growth Since 2019] )
```

```DAX
Growth Rank =
IF (
    HASONEVALUE ( dim_lga[lga] ) && NOT ISBLANK ( [Growth Since 2019] ),
    RANKX (
        FILTER ( ALL ( dim_lga ), dim_lga[geo_level] = "lga" ),
        [Growth Since 2019], , DESC
    )
)
```
*Why `FILTER ( ALL ( dim_lga ), … )`:* RANKX needs the growth of **every** LGA to compare against. In the bar chart,
each bar is filtered to one LGA, and, because `lga` is **sorted by `sort_order`** (T09 step 2.3), also to that LGA's
`sort_order`. RANKX visits each row of its table and calculates `[Growth Since 2019]` for it (context transition). If
the table has only the `lga` column, visiting "Fairfield" replaces the `lga` filter, but the bar's `sort_order` filter
stays. "Fairfield AND Sydney's sort_order" matches nothing, so every other LGA is blank, and every bar ranks itself
1st. Iterating **whole rows** of `dim_lga` (`ALL ( dim_lga )`) sets every column, `sort_order` included, so each
visited LGA is calculated cleanly. `geo_level = "lga"` keeps only the 34 LGAs. The dwelling slicer still applies,
because it filters `dim_dwelling`, not `dim_lga`.
*Why `HASONEVALUE`:* a rank only makes sense for one LGA. Without it, a total row or a card would show a meaningless
rank.

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
2. **Open Format visual:** first click the slicer on the canvas so it has a border, which means it's selected. At
   the top of the **Visualizations** pane there are icons. The **second** one, a paintbrush over a chart, is
   **Format visual** (hover over it to see the name). If nothing is selected, the pane shows page or theme settings
   instead, so select the visual first.
   Then **Visual** tab → **Slicer settings → Options → Style: Tile**, and **Selection → Single select: On**.
   (Newer versions may say *Buttons* instead of *Tile*. Either is fine.)
   **Don't also put `dwelling_label` in the Filters pane.** A filter there plus the slicer means "Houses AND Units",
   which is nothing, so every visual goes blank. The slicer is the only dwelling filter.
3. Put it **top right**, about 250 × 60 px. You can drag the corners, or for exact numbers use Format visual →
   **General** tab → **Properties → Size** (Width 250, Height 60) and **Position** (on a 1280-wide page,
   Horizontal ≈ 1010, Vertical ≈ 10). Select **Houses**.

*Why single select:* every measure assumes one dwelling type (`Median Price` uses MAX). Houses and units must never
mix (D01).

### 2.2 Bar chart: growth by LGA
1. Visualizations → **Clustered bar chart**.
   - **Y-axis:** `dim_lga[lga]`.
   - **X-axis:** `[Growth Since 2019]`.
2. **Filters on this page:** `dim_lga[geo_level]` = `lga`.
3. Sort: click the bar chart, or just hover over it. A small row of icons appears at its **top-right corner**
   (sometimes just above the chart). The last icon, **…**, is **More options** → **Sort axis** → **Growth Since 2019**.
   Open **…** again → **Sort axis** → **Sort descending**. The biggest bar is now at the top.
4. Make it tall (left two-thirds of the page) so all 34 bars fit. If they don't, a scroll bar appears, and that's OK.
5. **Bar colour:** Format visual → **Bars → Color → fx** → Format style **Field value** → field `[Bar Colour]` → OK.
   The top 5 turn blue; the rest grey.
6. **Greater Sydney line:** select the bar chart, then find the constant line settings:
   - *Older versions:* the **Analytics** icon (a magnifier, third icon at the top of Visualizations) → **X-axis constant
     line** (or **Constant line**) → **Add line**.
   - *Newer versions (no magnifier icon):* **Format visual** → **Visual** tab → type `line` in the pane's **search box**
     → **Reference line** (or **X-axis constant line**) → **+ Add line** → type **Constant line**.

   Then set **Value → fx** → Format style **Field value** → `[Greater Sydney Growth]` → OK. Colour `#A54B16`,
   style dashed. **Label:** there is no free-text label box. Instead, rename the line itself to "Greater Sydney". In
   the line list, use the pencil/rename icon or the **Name** field; in the Analytics pane, double-click the line name.
   Then turn **Data label On** and set its **Style** (or **Text**) to **Both**, which shows the name and the value,
   e.g. "Greater Sydney 67.5%".
   The line should sit at **67.5%** for Houses and **18.1%** for Units.
7. Data labels: Format → **Data labels: On**, 1 decimal.

### 2.3 Three cards (right side, below the slicer)
Visualizations → **Card** (new card). One card each:
- `[Greater Sydney Growth]`, label "Greater Sydney, nominal";
- `[Greater Sydney Real Growth]`, label "Greater Sydney, after inflation";
- `[Fastest LGA]`, with `[Fastest Growth]` underneath (or two small cards).

**How to set a label:** a card shows the field's name as its label, so rename the field *for this visual only*.
Select the card → **Build visual** (first icon) → in the field well, **double-click** the measure name (or click its
**▾ → Rename for this visual**) → type the label → Enter. The measure itself keeps its name. If the label still
doesn't show: Format visual → **Visual** tab → **Callout values → Label** (newer card) or **Category label: On**
(older card).

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
   - **X-axis:** `dim_date[quarter_label]`, a text label like "2019 Q1" that's already sorted by `q_index`. It reads
     the same on any computer. A date axis would follow the PC's language, e.g. "2019年" on a Chinese-locale Windows.
   - **Y-axis:** `[Price Index]`.
   - **Legend:** `dim_lga[lga]`.
   - Format → **Lines → Interpolation type: Linear** (or turn **Smooth** off). Smoothed curves invent peaks and dips
     between quarters that aren't in the data.
3. **Area picker:** a second slicer `dim_lga[lga]` on the left, list style. Format → Slicer settings → Selection:
   **Single select Off** and **Multi-select with CTRL Off**, so a plain click ticks or unticks a box. Tick
   **Greater Sydney**, **Inner Ring**, **Middle Ring** and **Outer Ring**. Users can scroll down and tick any LGA
   to compare.
   *Test it:* untick Inner Ring and its line disappears; tick it again and it comes back. Switch Houses/Units, go to
   page 1, and page 1 shows the same dwelling type (synced). The area picker must **not** appear in View → **Sync
   slicers** for page 1, because the bar chart needs all LGAs.
4. Colours: select the chart → Format visual → **Lines**. At the top of the Lines card is a **Series** dropdown
   (sometimes "Apply settings to"). Pick one series, set its **Color** and **Stroke width**, then pick the next:
   Greater Sydney `#23578A`, 3 px; Inner / Middle / Outer Ring greys (e.g. `#BFC5CC`, `#8C959F`, `#5B6770`), 1.5 px.
   A series only appears in the dropdown while it's ticked in the area picker, so tick all four first.
   Greys are hard to tell apart in a legend, so turn on Format visual → **Series labels** (newer versions). Each line
   is then named at its right end.
   Chart title: Format visual → **General → Title → Text** "Price index by quarter (2019 average = 100)". Without
   this, Power BI builds a long automatic title from every field, tooltips included.
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
4. **Scatter 2: 2019 price.** Everything is the same as scatter 1 except the X-axis. Fastest way: select scatter 1 →
   Ctrl+C, Ctrl+V → move the copy → in Build visual, replace the X-axis field with `[Price 2019]`. The Values, Y-axis,
   marker colour, labels and page filter stay as they are. Then change only:
   - Format visual → **X-axis → Values → Display units: Millions**, so the axis reads $1.0M, $1.5M … instead of
     1,000,000;
   - X-axis title "2019 median price ($ m)"; visual title "2019 median price".
5. **Results table** (one row per factor test; the dwelling slicer picks the 5 rows for houses or units through the
   Part 0.2 relationship):
   1. **Number formats first (Table view).** Click `factor_tests` in the Data pane:
      - `rho`: Column tools → Format **Decimal number**, decimals **2**. Check that a negative shows as `-0.51`. If
        the minus sign is missing, the format is a custom one: set it back to plain Decimal number.
      - `p`, `p_holm`: Decimal number, decimals **3**.
      - `n`: Whole number.
      - Each numeric column: Column tools → **Summarization: Don't summarize**. This only sets the default for
        **new** drags; fields already in a visual keep "Sum", so set this before building the table.
   2. **Build the table (Report view).** Click an empty area → Visualizations → **Table**. Drag into **Columns**, in
      this order: `factor`, `family`, `n`, `rho`, `p`, `p_holm`, `verdict`.
   3. **Check the column headers.** If any header says "Sum of …", the field is being added up. In Build visual, click
      the **▾** next to that field in the Columns well → **Don't summarize**. Each row is one test, and totals of ρ or
      p are meaningless.
   4. **Turn off the total row:** Format visual → **Visual** → **Totals → Off**.
   5. **Friendly headers:** in the Columns well, double-click each field to rename it for this visual: Factor, Family,
      LGAs (n), Spearman ρ, p, Holm p, Verdict. (To type ρ, copy it from this guide.)
   6. **Sort:** click the **Family** header once (main before exploratory). Click again to reverse.
   7. **Check against the CSV (Houses):** price_2019 ρ **−0.44**, p 0.009, moderate negative; income ρ **−0.51**,
      Holm p 0.009; distance ρ 0.33, p 0.060, no clear relationship. Units: all five "no clear relationship".
   8. Title: Format visual → General → Title → "Spearman tests: growth vs each factor".
6. Title (text box):
   > **Fast-growing houses were mid-distance and cheaper in 2019. For units, no factor showed a clear link.**

   Small note under the scatters: "Spearman rank correlation, 34 LGAs (33 for units). Price, rent and income move
   together, so their effects can't be separated. Association, not cause."

### ✋ Checkpoint 3
Screenshots with Houses and Units.

---

## Part 5 — Page 4 "Notes" (≈ 45 min; write it in your own words)

This page is what a careful reader checks: where the numbers come from and what they can't tell you. Keep it short:
bullets, no paragraphs.

### 5.1 Set up the page
1. Click **+** at the bottom → new page → double-click the tab → rename to `Notes`.
2. Don't paste the dwelling slicer here. Nothing on this page depends on it.
3. Plan two columns: **left** for Question / Answer / Data sources, **right** for Method / Limitations / Quality
   check / Links. One text box per section is easiest to move and align.

### 5.2 Make one text box, then copy it
1. **Insert → Text box.** Drag it to about 600 × 150 px on the left.
2. Type the section heading, e.g. `Question`. Select the heading text → toolbar: **Segoe UI Semibold**, size **14**,
   colour `#23578A`.
3. Press **Enter** and type the body. Select the body → **Segoe UI**, size **11**, dark grey (`#333333`). For
   bullets, use the bullet-list button in the toolbar.
4. Press **Esc** to stop editing. (If the toolbar covers the text, see the tip in Part 4: move the box down while
   editing, then back.)
5. **Ctrl+C, Ctrl+V** this box for each next section, then replace the text. This keeps the fonts identical.
6. Turn off the box background if it looks like a card: Format text box → **Effects → Background: Off**.

### 5.3 What to write (facts to use, in your own words)

| Section | Content (facts checked against the repo) |
|---|---|
| **Question** | Which of Greater Sydney's 34 LGAs had the fastest median house and unit price growth since 2019, and what do the fastest-growing areas have in common? |
| **Answer** | Houses +67.5% (+34.9% after inflation), units +18.1% (−4.8% after inflation). Fastest: Fairfield houses (83.0%), Hawkesbury units (58.8%). Fast-growing house LGAs were mostly Middle Ring (7 of the top 10) and cheaper, lower-income areas in 2019; for units no tested factor showed a clear link. |
| **Data sources** | NSW DCJ Rent and Sales Report, sales tables, issues March 2019 to March 2026 (CC BY 4.0) · NSW DCJ rent tables 2019 (CC BY 4.0) · ABS Regional Population, ERP by LGA (CC BY 4.0) · ABS Census 2016, G02 (CC BY 2.5 AU) · ABS CPI, Sydney All groups, A2325806K (CC BY 4.0) · ABS ASGS 2025 LGA boundaries and Heritage NSW GPO location (CC BY 4.0). |
| **Method** | Growth = average median of 2019's four quarters → average of the latest four (Jun 2025 – Mar 2026). Houses (non-strata) and units (strata) always separate. Greater Sydney uses DCJ's own published figure, never an average of LGAs. Real growth deflated with Sydney CPI (ratio 1.241). Factors tested with Spearman rank correlation; the two exploratory factors with a Holm correction. |
| **Limitations** | First-published medians are later revised, usually slightly upward; Woollahra houses most affected (43.0% first-published vs 64.8% revised). Some windows rest on quarters with 30 or fewer sales (e.g. Hunters Hill houses and units, Burwood houses in 2019). Wollondilly units have no 2019 median, so they're not ranked. 34 LGAs is a small sample: associations, not causes. Distances use 2025 boundaries. |
| **Quality check** | Every Power BI growth figure was cross-checked against the Python/SQL pipeline (hidden Cross-check page): 0 differences. |
| **Links** | GitHub: `github.com/huiya-svg/sydney-housing-growth` · your LinkedIn URL · "Built by Kang Liang". |

*Why your own words:* this page is where an interviewer asks "what would you do differently?". If you wrote it, you
can answer.

### 5.4 Make the links clickable
Select the link text inside the text box → toolbar **link** icon (chain) → paste the full URL (`https://…`) → Enter.
Links stay clickable in the exported PDF.

### 5.5 Page title
Same style as the other pages (copy the title text box from page 3 and change the text): **"Notes: data, method and
limitations"**.

### ✋ Checkpoint 4
Screenshot of the Notes page. Claude checks the facts and the wording.

---

## Part 6 — Export and commit (≈ 20 min)

### 6.1 Final tidy (every page)
1. Select **Houses** on the dwelling slicer. Because it's synced, all pages switch.
2. Page 2: area picker shows Greater Sydney and the three rings only.
3. Click an empty area on each page so no visual is selected (selected visuals show borders in screenshots).
4. Check that **Cross-check** is still hidden (eye-slash icon on its tab).
5. **Ctrl+S.**

### 6.2 Screenshots (PNG, for the README)
1. Close the side panes so the page is big: click **»** on Filters, Visualizations and Data.
2. Bottom right: **Fit to page** (the icon next to the zoom %).
3. Press **Win + Shift + S** → **Rectangle** → drag exactly around the white report page (not the ribbon or tabs).
4. A notification appears bottom right → click it → Snipping Tool opens → **Save** (disk icon, or Ctrl+S).
5. Save into `<repo>\powerbi\` with these names:

   | Page | File |
   |---|---|
   | The answer | `page1_answer.png` |
   | Trends | `page2_trends.png` |
   | Why? | `page3_why.png` |
   | Notes | `page4_notes.png` |

6. Optional: switch to **Units** and save `page1_answer_units.png` and `page3_why_units.png`, then switch back to
   Houses.

### 6.3 PDF
1. **File → Export → Export to PDF.** Power BI exports each visible page in its current state (Houses).
2. Wait for it to finish; it opens in your PDF reader. Check: 4 pages, no Cross-check page, titles readable.
3. Save it as `<repo>\powerbi\sydney_housing_report.pdf`.

### 6.4 Commit and push (GitHub Desktop on Windows)
1. **Fetch origin** first, then **Pull origin** if offered, so you have Claude's latest guide edits from the Mac.
2. Changed files should be: `powerbi/sydney_housing.pbix`, the 4 (or 6) PNGs and the PDF. Untick anything else.
3. Summary: `Add Power BI report pages, screenshots and PDF (T10)` → **Commit to main** → **Push origin**.
4. Tell Claude "T10 done". Claude pulls on the Mac and reviews the PNGs and the PDF.

*Privacy note:* the `.pbix` stores the `RepoPath` parameter value, which is your Windows folder path including your
user name. If you'd rather not publish that, set `RepoPath` to a neutral path such as `C:\repo\` before the final
save (the README will tell readers to change it to their own clone folder anyway).

## Interview checklist

- Why the slicer is single-select.
- Why there's no "slowest LGA" card.
- Why `Real Growth` needs `IF ( NOT ISBLANK … )`, and why `Bar Colour` does too.
- How `TOPN` / `RANKX` work over `VALUES ( dim_lga[lga] )`.
- What the page 3 table shows, and why price, rent and income can't be separated.
