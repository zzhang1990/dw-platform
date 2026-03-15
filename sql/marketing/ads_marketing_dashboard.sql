-- 营销仪表盘数据 (ADS)
-- 聚合用户行为数据生成营销指标

INSERT INTO ads_marketing_dashboard
SELECT
    dt AS report_date,
    action_type,
    device_type,
    platform,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(*) AS action_count,
    COUNT(DISTINCT session_id) AS session_count
FROM dwd_user_behavior
WHERE dt = '{dt}'
GROUP BY dt, action_type, device_type, platform;