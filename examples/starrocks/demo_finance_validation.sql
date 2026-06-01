-- Validation queries for the sanitized public demo finance chain.

SELECT
    tenant_id,
    stat_month,
    customer_id,
    project_id,
    project_name,
    order_count,
    receivable_amount,
    discount_amount,
    net_receivable_amount,
    average_order_receivable_amount
FROM demo_ads.ads_demo_project_monthly_finance
ORDER BY tenant_id, stat_month, customer_id, project_id;

-- Expected result after running the 2026-05-31 chain:
-- Project Alpha: 2 orders, 200.00 receivable, 10.00 discount, 190.00 net.
-- Project Beta:  1 order,  200.00 receivable, 20.00 discount, 180.00 net.

SELECT
    tenant_id,
    stat_month,
    customer_id,
    project_id,
    COUNT(*) AS duplicate_rows
FROM demo_ads.ads_demo_project_monthly_finance
GROUP BY tenant_id, stat_month, customer_id, project_id
HAVING COUNT(*) > 1;
