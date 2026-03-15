-- 财务账单明细表 (DWD)
-- 数据来源: ODS 层财务账单原始数据

INSERT INTO dwd_finance_detail
SELECT
    bill_id,
    account_id,
    account_name,
    amount,
    currency,
    transaction_type,
    transaction_time,
    created_at,
    updated_at
FROM ods_finance_bill
WHERE dt = '{dt}'
  AND amount IS NOT NULL
  AND transaction_time IS NOT NULL;