-- Measure straight-line distance from each LGA's geometric centroid to the Sydney GPO.
WITH boundaries AS (
    -- Read the ABS LGA 2025 polygons.
    SELECT lga_code_2025, geom
    FROM ST_Read($boundaries_path)
),
centroids AS (
    -- Find centroids in Australian Albers and transform them back to longitude and latitude.
    SELECT lga_code_2025,
           ST_Transform(
               ST_Centroid(ST_Transform(geom, 'EPSG:4326', 'EPSG:9473', always_xy := true)),
               'EPSG:9473', 'EPSG:4326', always_xy := true
           ) AS centre
    FROM boundaries
),
gpo AS (
    -- Read the GPO point from the NSW State Heritage Register export.
    SELECT geom AS gpo_point
    FROM ST_Read($gpo_path)
)
SELECT c.lga_code_2025,
       ROUND(ST_Y(c.centre), 6) AS centroid_lat,
       ROUND(ST_X(c.centre), 6) AS centroid_lon,
       ROUND(ST_Distance_Spheroid(c.centre, g.gpo_point) / 1000, 2) AS distance_km
FROM centroids AS c
CROSS JOIN gpo AS g
ORDER BY c.lga_code_2025;
