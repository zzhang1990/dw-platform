-- 用户行为明细表 (DWD)
-- 数据来源: ODS 层用户行为日志

INSERT INTO dwd_user_behavior
SELECT
    user_id,
    session_id,
    action_type,
    action_time,
    page_url,
    referrer_url,
    device_type,
    platform,
    created_at
FROM ods_user_log
WHERE dt = '{dt}'
  AND user_id IS NOT NULL
  AND action_time IS NOT NULL;