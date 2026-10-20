# Olist E-Commerce Data Pipeline

Portfolio project using Amazon S3, EC2, DynamoDB, Python/Pandas, and DuckDB to process and analyze the Olist Brazilian E-Commerce dataset.

## Architecture

Olist CSVs → S3 `Raw/` → EC2 Python/Pandas ETL → S3 `Processed/` → DuckDB SQL analytics.

DynamoDB is used for a small order-status lookup demonstration. DuckDB provides SQL analytics in a lightweight local warehouse; the design can be extended to Amazon Redshift for managed cloud warehousing.

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

ETL removes exact duplicate rows, parses selected date/time columns, writes cleaned CSVs to S3, and generates JSON data-quality reports. Date-quality metrics distinguish original missing values from malformed non-empty date values that could not be parsed. Geolocation shrank from 1,000,163 to 738,332 rows after exact-row deduplication; validate the intended grain before using this as a production transformation.

## Cost note

DuckDB is used for local analytics to keep the project lightweight and cost-conscious. Amazon Redshift is a natural next step for scaling the analytical layer into a managed cloud data warehouse. The DynamoDB demo uses a limited sample of orders and is not a complete replica of the orders dataset.

## Repository contents

Code and SQL only. Raw datasets, processed data, local database files, and credentials should never be committed.

## Run the project

### 1. Install dependencies

Python 3.9 or newer is recommended.

```bash
python -m pip install -r requirements.txt
```

### 2. Run the AWS ETL on EC2

Attach an IAM instance role with read access to `Raw/*` and write access to `Processed/*` in your bucket. Then set the bucket if it differs from the default:

```bash
export OLIST_BUCKET=olist-aws-project
export AWS_REGION=ap-southeast-2
python src/process_all_olist.py
```

The script writes cleaned CSVs and `all_datasets_quality_report.json` to the S3 `Processed/` prefix. The script uses the instance role; never put access keys in source code.

### 3. Download processed CSVs for local analytics

Download all nine `*_cleaned.csv` files from your S3 `Processed/` prefix into the repository's `data/` directory. Keep this directory out of Git.

### 4. Create DuckDB tables

```bash
python src/load_data.py
```

The script creates `olist.duckdb` and one table per cleaned CSV. Then run queries from `sql/analytics.sql` in a DuckDB SQL client or notebook.

### 5. Optional DynamoDB lookup demo

```bash
python src/load_orders_dynamodb.py
```

This loads a small sample (100 rows by default) into `OlistOrderStatus`. The EC2 role needs permission to read the processed CSV and write items to that table. To change the sample size, set `ORDER_SAMPLE_LIMIT`. The table is for demonstrating key-based lookups, not a full data warehouse.

## Tests

Run the regression tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover the canonical CSV-to-table mappings and date-quality reporting helpers. They do not replace running the full AWS pipeline and all SQL queries against the complete datasets.
