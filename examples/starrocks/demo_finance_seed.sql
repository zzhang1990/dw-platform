-- Sanitized seed data for the public demo finance chain.
-- Run this only against the demo_ods databases created by demo_finance_chain.sql.

INSERT INTO demo_ods.ods_demo_project (
    project_id,
    project_code,
    project_name,
    customer_id,
    project_status,
    created_at,
    updated_at
)
VALUES
    (101, 'DEMO-PROJECT-A', 'Demo Project Alpha', 1001, 'ACTIVE', '2026-05-01 09:00:00', '2026-05-01 09:00:00'),
    (102, 'DEMO-PROJECT-B', 'Demo Project Beta', 1002, 'ACTIVE', '2026-05-02 09:00:00', '2026-05-02 09:00:00');

INSERT INTO demo_ods.ods_demo_order_receivable (
    receivable_id,
    tenant_id,
    order_no,
    customer_id,
    project_id,
    receivable_amount,
    discount_amount,
    receivable_status,
    created_at,
    updated_at
)
VALUES
    (10001, 1, 'DEMO-ORDER-001', 1001, 101, 120.00, 10.00, 'CONFIRMED', '2026-05-10 10:00:00', '2026-05-10 10:00:00'),
    (10002, 1, 'DEMO-ORDER-002', 1001, 101, 80.00, 0.00, 'CONFIRMED', '2026-05-11 11:00:00', '2026-05-11 11:00:00'),
    (10003, 1, 'DEMO-ORDER-003', 1002, 102, 200.00, 20.00, 'CONFIRMED', '2026-05-12 12:00:00', '2026-05-12 12:00:00'),
    (10004, 1, 'DEMO-ORDER-004', 1002, 102, 50.00, 0.00, 'CANCELLED', '2026-05-13 13:00:00', '2026-05-13 13:00:00');
