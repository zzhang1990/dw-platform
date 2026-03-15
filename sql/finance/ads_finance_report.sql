-- 财务报表 (ADS)
-- 聚合财务数据生成报表

INSERT INTO ads_finance_report
SELECT
    dt AS report_date,
    transaction_type,
    currency,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM dwd_finance_detail
WHERE dt = '{dt}'
GROUP BY dt, transaction_type, currency;