-- Build the sales fact, geography and date dimensions, and growth summary.
-- Resolve all CSV paths from the repository root. The notebook handles export.

-- Read the accepted sales grid with explicit types for the window calculations.
CREATE OR REPLACE TABLE sales_input AS
SELECT geo_name AS lga, quarter_date, dwelling_type, median_price, sales_count,
       price_status, low_sales_flag, quarterly_change, annual_change
FROM read_csv('data/interim/sales_long.csv', header = true, columns = {
    'quarter_date': 'DATE', 'geo_level': 'VARCHAR', 'geo_name': 'VARCHAR',
    'region': 'VARCHAR', 'dwelling_type': 'VARCHAR', 'median_price': 'BIGINT',
    'sales_count': 'BIGINT', 'price_status': 'VARCHAR', 'count_status': 'VARCHAR',
    'low_sales_flag': 'BOOLEAN', 'source_file': 'VARCHAR', 'source_row': 'BIGINT',
    'quarterly_change': 'DOUBLE', 'annual_change': 'DOUBLE'
});

-- Check the full grid before using row offsets as calendar-quarter offsets.
WITH series_grid AS (
    -- Count the quarters and measure their span separately for each series.
    SELECT lga, dwelling_type,
           COUNT(*) AS row_count,
           COUNT(DISTINCT quarter_date) AS quarter_count,
           DATE_DIFF('quarter', MIN(quarter_date), MAX(quarter_date)) AS quarter_span,
           COUNT(*) FILTER (WHERE quarter_date = DATE_TRUNC('quarter', quarter_date)) AS quarter_starts
    FROM sales_input
    GROUP BY lga, dwelling_type
)
SELECT CASE
           WHEN COUNT(*) = 76
                AND (SELECT COUNT(DISTINCT quarter_date) FROM sales_input) = 29
                AND COUNT(*) FILTER (
                    WHERE row_count = 29 AND quarter_count = 29 AND quarter_span = 28 AND quarter_starts = 29
                ) = 76
           THEN true
           ELSE error('Expected 29 consecutive quarter starts for each of the 76 sales series')
       END AS grid_valid
FROM series_grid;

-- Preserve the published prices and attach YoY change and the D08 revised estimate.
CREATE OR REPLACE TABLE fact_sales AS
WITH quarter_neighbours AS (
    -- Bring in the prices and reported changes from the comparison quarters.
    SELECT *,
           LAG(median_price, 4) OVER by_quarter AS prior_year_price,
           LEAD(median_price, 4) OVER by_quarter AS next_year_price,
           LEAD(annual_change, 4) OVER by_quarter AS next_year_change,
           LEAD(median_price, 1) OVER by_quarter AS next_quarter_price,
           LEAD(quarterly_change, 1) OVER by_quarter AS next_quarter_change
    FROM sales_input
    WINDOW by_quarter AS (PARTITION BY lga, dwelling_type ORDER BY quarter_date)
),
revision_choices AS (
    -- Use the annual estimate first, then quarterly, then the original price.
    SELECT *,
           CASE
               WHEN next_year_price IS NOT NULL AND next_year_change IS NOT NULL THEN 'annual'
               WHEN next_quarter_price IS NOT NULL AND next_quarter_change IS NOT NULL THEN 'quarterly'
               WHEN median_price IS NOT NULL THEN 'first_published'
           END AS revised_source
    FROM quarter_neighbours
),
revision_values AS (
    -- Back-calculate the earlier median from the later median and its change.
    SELECT *,
           CASE revised_source
               WHEN 'annual' THEN next_year_price / (1 + next_year_change)
               WHEN 'quarterly' THEN next_quarter_price / (1 + next_quarter_change)
               WHEN 'first_published' THEN median_price
           END AS revised_price
    FROM revision_choices
)
SELECT lga, quarter_date, dwelling_type, median_price, sales_count, price_status, low_sales_flag,
       median_price / prior_year_price - 1 AS yoy_change,
       CAST(ROUND(revised_price, -3) AS BIGINT) AS median_price_revised_est,
       revised_source
FROM revision_values;

-- Use one geography key for LGAs and the published Sydney and ring benchmarks.
CREATE OR REPLACE TABLE dim_lga AS
WITH lga_rows AS (
    -- Attach the four factors by ABS code and set alphabetical LGA display order.
    SELECT l.lga, 'lga' AS geo_level, l.region, l.lga_code_2025,
           f.distance_km, f.pop_growth_2016_19, f.income_2016_weekly,
           f.rent_2019_house_weekly, f.rent_2019_unit_weekly,
           4 + ROW_NUMBER() OVER (ORDER BY l.lga) AS sort_order
    FROM read_csv('data/reference/lga_lookup.csv', header = true, columns = {
        'lga': 'VARCHAR', 'region': 'VARCHAR', 'lga_code_2025': 'VARCHAR', 'abs_name_2025': 'VARCHAR'
    }) AS l
    LEFT JOIN read_csv('data/interim/lga_factors.csv', header = true, columns = {
        'lga': 'VARCHAR', 'lga_code_2025': 'VARCHAR', 'distance_km': 'DOUBLE',
        'pop_2016': 'BIGINT', 'pop_2019': 'BIGINT', 'pop_growth_2016_19': 'DOUBLE',
        'income_2016_weekly': 'BIGINT', 'rent_2019_house_weekly': 'DOUBLE',
        'rent_2019_unit_weekly': 'DOUBLE', 'rent_2019_quarters_used_house': 'BIGINT',
        'rent_2019_quarters_used_unit': 'BIGINT'
    }) AS f ON l.lga_code_2025 = f.lga_code_2025
),
benchmark_rows(lga, geo_level, region, sort_order) AS (
    -- Place the published benchmarks above the alphabetically ordered LGAs.
    VALUES ('Greater Sydney', 'greater_sydney', NULL, 1),
           ('Inner Ring', 'ring', 'Inner Ring', 2),
           ('Middle Ring', 'ring', 'Middle Ring', 3),
           ('Outer Ring', 'ring', 'Outer Ring', 4)
)
SELECT lga, geo_level, region, NULL AS lga_code_2025,
       NULL AS distance_km, NULL AS pop_growth_2016_19, NULL AS income_2016_weekly,
       NULL AS rent_2019_house_weekly, NULL AS rent_2019_unit_weekly, sort_order
FROM benchmark_rows
UNION ALL
SELECT lga, geo_level, region, lga_code_2025, distance_km, pop_growth_2016_19,
       income_2016_weekly, rent_2019_house_weekly, rent_2019_unit_weekly, sort_order
FROM lga_rows;

-- Date keys and window flags are shared by the fact and the growth summary.
CREATE OR REPLACE TABLE dim_date AS
WITH quarters AS (
    -- Take the quarter dates that exist in the validated sales grid.
    SELECT DISTINCT quarter_date
    FROM sales_input
),
numbered_quarters AS (
    -- Number quarters from the start and identify the four most recent.
    SELECT quarter_date, YEAR(quarter_date) AS year, QUARTER(quarter_date) AS quarter_number,
           ROW_NUMBER() OVER (ORDER BY quarter_date) AS q_index,
           ROW_NUMBER() OVER (ORDER BY quarter_date DESC) AS reverse_q_index
    FROM quarters
),
sydney_cpi AS (
    -- Read the quarter-start Sydney CPI series prepared by the cleaning notebook.
    SELECT quarter_date, cpi_sydney
    FROM read_csv('data/interim/cpi_sydney.csv', header = true, columns = {
        'quarter_date': 'DATE', 'cpi_sydney': 'DOUBLE'
    })
)
SELECT quarter_date, year, CONCAT(year, ' Q', quarter_number) AS quarter_label, q_index,
       year = 2019 AS is_baseline_2019,
       reverse_q_index <= 4 AS is_latest_4q,
       c.cpi_sydney
FROM numbered_quarters
LEFT JOIN sydney_cpi AS c USING (quarter_date);

-- Compare complete four-quarter windows for each geography and dwelling type.
CREATE OR REPLACE TABLE lga_growth AS
WITH window_parameters AS (
    -- Use the quarter indexes for elapsed time and the same two windows for inflation.
    SELECT (
        AVG(q_index) FILTER (WHERE is_latest_4q) - AVG(q_index) FILTER (WHERE is_baseline_2019)
    ) / 4.0 AS years,
    AVG(cpi_sydney) FILTER (WHERE is_latest_4q)
        / AVG(cpi_sydney) FILTER (WHERE is_baseline_2019) AS cpi_ratio
    FROM dim_date
),
window_prices AS (
    -- Count first-published prices and keep an average only for a complete window.
    SELECT s.lga, s.dwelling_type,
           COUNT(s.median_price) FILTER (WHERE d.is_baseline_2019) AS baseline_quarters,
           COUNT(s.median_price) FILTER (WHERE d.is_latest_4q) AS latest_quarters,
           COUNT(s.median_price) FILTER (WHERE d.is_baseline_2019 AND s.low_sales_flag) AS baseline_low_sales_quarters,
           COUNT(s.median_price) FILTER (WHERE d.is_latest_4q AND s.low_sales_flag) AS latest_low_sales_quarters,
           CASE WHEN COUNT(s.median_price) FILTER (WHERE d.is_baseline_2019) = 4
                THEN AVG(s.median_price) FILTER (WHERE d.is_baseline_2019) END AS price_2019,
           CASE WHEN COUNT(s.median_price) FILTER (WHERE d.is_latest_4q) = 4
                THEN AVG(s.median_price) FILTER (WHERE d.is_latest_4q) END AS price_latest,
           CASE WHEN COUNT(s.median_price_revised_est) FILTER (WHERE d.is_baseline_2019) = 4
                THEN AVG(s.median_price_revised_est) FILTER (WHERE d.is_baseline_2019) END AS price_2019_rev,
           CASE WHEN COUNT(s.median_price_revised_est) FILTER (WHERE d.is_latest_4q) = 4
                THEN AVG(s.median_price_revised_est) FILTER (WHERE d.is_latest_4q) END AS price_latest_rev
    FROM fact_sales AS s
    JOIN dim_date AS d USING (quarter_date)
    GROUP BY s.lga, s.dwelling_type
),
window_growth AS (
    -- The price ratios remain null when a window is incomplete.
    SELECT *,
           price_latest / price_2019 - 1 AS growth_pct,
           price_latest_rev / price_2019_rev - 1 AS growth_pct_rev
    FROM window_prices
),
nominal_ranks AS (
    -- Rank only LGAs with a first-published growth figure within each dwelling type.
    SELECT w.lga, w.dwelling_type,
           RANK() OVER (PARTITION BY w.dwelling_type ORDER BY w.growth_pct DESC) AS growth_rank
    FROM window_growth AS w
    JOIN dim_lga AS g USING (lga)
    WHERE g.geo_level = 'lga' AND w.growth_pct IS NOT NULL
),
revised_ranks AS (
    -- Apply the same ranking rule to the available revised estimates.
    SELECT w.lga, w.dwelling_type,
           RANK() OVER (PARTITION BY w.dwelling_type ORDER BY w.growth_pct_rev DESC) AS growth_rank_rev
    FROM window_growth AS w
    JOIN dim_lga AS g USING (lga)
    WHERE g.geo_level = 'lga' AND w.growth_pct_rev IS NOT NULL
)
SELECT w.lga, g.geo_level, g.region, w.dwelling_type, w.baseline_quarters, w.latest_quarters,
       w.baseline_low_sales_quarters, w.latest_low_sales_quarters, w.price_2019, w.price_latest,
       w.growth_pct, POWER(1 + w.growth_pct, 1.0 / t.years) - 1 AS growth_annualised,
       w.price_2019_rev, w.price_latest_rev, w.growth_pct_rev,
       NULLIF(CONCAT_WS(' / ',
           CASE WHEN w.baseline_quarters < 4 THEN CONCAT('baseline: ', w.baseline_quarters, ' of 4 quarters published') END,
           CASE WHEN w.latest_quarters < 4 THEN CONCAT('latest: ', w.latest_quarters, ' of 4 quarters published') END
       ), '') AS growth_note,
       t.cpi_ratio,
       (1 + w.growth_pct) / t.cpi_ratio - 1 AS growth_pct_real,
       n.growth_rank,
       r.growth_rank_rev,
       r.growth_rank_rev - n.growth_rank AS rank_change_rev
FROM window_growth AS w
JOIN dim_lga AS g USING (lga)
CROSS JOIN window_parameters AS t
LEFT JOIN nominal_ranks AS n USING (lga, dwelling_type)
LEFT JOIN revised_ranks AS r USING (lga, dwelling_type);
