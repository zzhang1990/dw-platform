-- Sanitized StarRocks DDL for the public demo finance chain.
-- The names and fields are intentionally generic and do not mirror a private system.

CREATE DATABASE IF NOT EXISTS demo_ods;
CREATE DATABASE IF NOT EXISTS demo_dim;
CREATE DATABASE IF NOT EXISTS demo_dwd;
CREATE DATABASE IF NOT EXISTS demo_dws;
CREATE DATABASE IF NOT EXISTS demo_ads;

CREATE TABLE IF NOT EXISTS demo_ods.ods_demo_project (
    project_id BIGINT NOT NULL,
    project_code VARCHAR(64) NOT NULL,
    project_name VARCHAR(128) NOT NULL,
    customer_id BIGINT NOT NULL,
    project_status VARCHAR(32) NOT NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL
)
ENGINE=OLAP
DUPLICATE KEY(project_id)
DISTRIBUTED BY HASH(project_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS demo_ods.ods_demo_order_receivable (
    receivable_id BIGINT NOT NULL,
    tenant_id BIGINT NOT NULL,
    order_no VARCHAR(64) NOT NULL,
    customer_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    discount_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    receivable_status VARCHAR(32) NOT NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL
)
ENGINE=OLAP
DUPLICATE KEY(receivable_id)
DISTRIBUTED BY HASH(receivable_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS demo_dim.dim_demo_project (
    project_id BIGINT NOT NULL,
    project_code VARCHAR(64) NOT NULL,
    project_name VARCHAR(128) NOT NULL,
    customer_id BIGINT NOT NULL,
    project_status VARCHAR(32) NOT NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL
)
ENGINE=OLAP
DUPLICATE KEY(project_id)
DISTRIBUTED BY HASH(project_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS demo_dwd.dwd_demo_order_receivable (
    receivable_id BIGINT NOT NULL,
    tenant_id BIGINT NOT NULL,
    order_no VARCHAR(64) NOT NULL,
    customer_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    project_code VARCHAR(64) NOT NULL,
    project_name VARCHAR(128) NOT NULL,
    receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    discount_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    net_receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    receivable_status VARCHAR(32) NOT NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL
)
ENGINE=OLAP
DUPLICATE KEY(receivable_id)
DISTRIBUTED BY HASH(receivable_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS demo_dws.dws_demo_project_monthly_receivable (
    tenant_id BIGINT NOT NULL,
    stat_month VARCHAR(7) NOT NULL,
    customer_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    project_name VARCHAR(128) NOT NULL,
    order_count BIGINT NOT NULL DEFAULT "0",
    receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    discount_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    net_receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    etl_time DATETIME NOT NULL
)
ENGINE=OLAP
DUPLICATE KEY(tenant_id, stat_month, customer_id, project_id)
DISTRIBUTED BY HASH(project_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS demo_ads.ads_demo_project_monthly_finance (
    tenant_id BIGINT NOT NULL,
    stat_month VARCHAR(7) NOT NULL,
    customer_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    project_name VARCHAR(128) NOT NULL,
    order_count BIGINT NOT NULL DEFAULT "0",
    receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    discount_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    net_receivable_amount DECIMAL(18, 2) NOT NULL DEFAULT "0",
    average_order_receivable_amount DECIMAL(18, 2) NULL,
    etl_time DATETIME NOT NULL
)
ENGINE=OLAP
DUPLICATE KEY(tenant_id, stat_month, customer_id, project_id)
DISTRIBUTED BY HASH(project_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");
