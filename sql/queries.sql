
-- Query 1: Headline conversion metrics by test group
SELECT
    test_group,
    COUNT(*) AS users,
    SUM(CAST(converted AS INTEGER)) AS conversions,
    ROUND(AVG(CAST(converted AS REAL)) * 100, 3)
        AS conversion_rate_pct
FROM ads
GROUP BY test_group;


-- Query 2: Conversion rate by day and test group
SELECT
    most_ads_day,
    test_group,
    COUNT(*) AS users,
    SUM(CAST(converted AS INTEGER)) AS conversions,
    ROUND(AVG(CAST(converted AS REAL)) * 100, 3)
        AS conversion_rate_pct
FROM ads
GROUP BY most_ads_day, test_group
ORDER BY most_ads_day, test_group;


-- Query 3: CASE WHEN exposure buckets
SELECT
    CASE
        WHEN total_ads = 1 THEN '1'
        WHEN total_ads BETWEEN 2 AND 5 THEN '2-5'
        WHEN total_ads BETWEEN 6 AND 10 THEN '6-10'
        WHEN total_ads BETWEEN 11 AND 20 THEN '11-20'
        WHEN total_ads BETWEEN 21 AND 50 THEN '21-50'
        WHEN total_ads BETWEEN 51 AND 100 THEN '51-100'
        ELSE '101+'
    END AS exposure_bucket,
    test_group,
    COUNT(*) AS users,
    ROUND(AVG(CAST(converted AS REAL)) * 100, 3)
        AS conversion_rate_pct
FROM ads
GROUP BY exposure_bucket, test_group
ORDER BY MIN(total_ads), test_group;


-- Query 4: CTE to calculate conversions by hour
WITH hourly_metrics AS (
    SELECT
        most_ads_hour,
        test_group,
        COUNT(*) AS users,
        SUM(CAST(converted AS INTEGER)) AS conversions,
        AVG(CAST(converted AS REAL)) AS conversion_rate
    FROM ads
    GROUP BY most_ads_hour, test_group
)
SELECT
    most_ads_hour,
    test_group,
    users,
    conversions,
    ROUND(conversion_rate * 100, 3) AS conversion_rate_pct
FROM hourly_metrics
ORDER BY most_ads_hour, test_group;


-- Query 5: Rank days by conversion rate within each group
WITH daily_metrics AS (
    SELECT
        most_ads_day,
        test_group,
        COUNT(*) AS users,
        AVG(CAST(converted AS REAL)) AS conversion_rate
    FROM ads
    GROUP BY most_ads_day, test_group
)
SELECT
    most_ads_day,
    test_group,
    users,
    ROUND(conversion_rate * 100, 3) AS conversion_rate_pct,
    RANK() OVER (
        PARTITION BY test_group
        ORDER BY conversion_rate DESC
    ) AS conversion_rank
FROM daily_metrics
ORDER BY test_group, conversion_rank;
