# Olist E-Commerce Data Pipeline

Portfolio project using Amazon S3, EC2, DynamoDB, Python/Pandas, and DuckDB to process and analyze the Olist Brazilian E-Commerce dataset.

## Architecture

Olist CSVs → S3 `Raw/` → EC2 Python/Pandas ETL → S3 `Processed/` → DuckDB SQL analytics.

DynamoDB is used for a small order-status lookup demonstration. Redshift is not currently provisioned; DuckDB keeps analytics cost-conscious.

## Datasets

The pipeline processes nine datasets: customers, geolocation, order items, order payments, order reviews, orders, products, sellers, and product-category translation.

## Technologies

- Amazon S3: raw and cleaned CSV storage
- Amazon EC2: ETL execution
- IAM instance role and AWS CLI
- Python, Pandas, Boto3
- Amazon DynamoDB: order-status lookup demo
- DuckDB and SQL: analytical queries

## Processing results

| Dataset | Cleaned rows |
|---|---:|
| Customers | 99,441 |
| Geolocation | 738,332 |
| Order items | 112,650 |
| Payments | 103,886 |
| Reviews | 99,224 |
| Orders | 99,441 |
| Products | 32,951 |
| Sellers | 3,095 |
| Category translation | 71 |

ETL removes exact duplicate rows, parses selected date/time columns, writes cleaned CSVs to S3, and generates JSON data-quality reports. Geolocation shrank from 1,000,163 to 738,332 rows after exact-row deduplication; validate the intended grain before using this as a production transformation.

## Cost note

Redshift has not been provisioned. DuckDB is used for local analytics to avoid unnecessary ongoing warehouse costs. The DynamoDB demo uses a limited sample of orders and is not a complete replica of the orders dataset.

## Repository contents

Code and SQL only. Raw datasets, processed data, local database files, and credentials should never be committed.