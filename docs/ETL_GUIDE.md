# ETL Development Guide

## Runnable Sanitized Example

The repository includes a sanitized vertical finance chain with StarRocks DDL, seed data,
validation queries, dry-run support, and shadow-table `SWAP` publishing:

- [Demo finance chain guide](etl/demo-finance-chain.md)
- [StarRocks DDL](../examples/starrocks/demo_finance_chain.sql)
- [Seed data](../examples/starrocks/demo_finance_seed.sql)
- [Validation queries](../examples/starrocks/demo_finance_validation.sql)

## Data Warehouse Architecture Overview
In this section, we will explore the overall architecture of our data warehouse, including the various layers and components that constitute the system.

## Layer Specifications
- **ODS (Operational Data Store)**: This layer holds operational data from various sources before it is transformed and moved to the data warehouse.  
- **DIM (Dimension Tables)**: These tables contain attributes related to the dimensions of the business, such as customers, products, etc. 
- **DWD (Data Warehouse Detail)**: This layer includes detailed, raw data that is subject to various transformations before it becomes available for analysis.  
- **DWS (Data Warehouse Summary)**: Summary tables offering aggregated views of data to facilitate quicker queries and reporting.
- **ADS (Analytics Data Store)**: This is a specialized layer tailored for analytics purposes, containing refined data for data science and business intelligence operations.

## SQL Coding Standards
- Use meaningful table and column names. 
- Always include comments for complex queries. 
- Use consistent formatting to enhance readability.

## Python Function Naming Conventions
- Function names should be written in snake_case. 
- Use descriptive names that convey the purpose of the function.

## ETL Task Templates
- Use templates for common ETL tasks to ensure consistency and efficiency. Each template should include:
  - Input specifications
  - Transformation logic
  - Output definitions
- Example of an ETL task template: 
```
1. Extract data from source
2. Transform the data
3. Load data into target
```

## Data Validation Requirements
- Define validation rules for data accuracy and integrity. 
- Validate data at each stage of the ETL process.

## Best Practices for Creating New ETL Jobs
- Always start with a defined scope and requirements. 
- Keep jobs modular to ensure maintainability. 
- Regularly review and update ETL processes to adapt to new requirements and technologies.

## Conclusion
This ETL development guide provides an overview of the key components and standards required for effective ETL processes. Following these guidelines will facilitate a robust and efficient data warehousing environment.
