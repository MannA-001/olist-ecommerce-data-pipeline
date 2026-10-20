"""Clean the nine Olist CSV datasets from S3 and write outputs to Processed/.

Configure OLIST_BUCKET and optionally AWS_REGION in the environment. The EC2
instance should use an IAM role; do not hardcode AWS credentials.
"""
import json
import os
from datetime import datetime, timezone
from io import BytesIO

import boto3
import pandas as pd

BUCKET = os.environ.get("OLIST_BUCKET", "olist-aws-project")
REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
RAW_PREFIX = os.environ.get("OLIST_RAW_PREFIX", "Raw/")
PROCESSED_PREFIX = os.environ.get("OLIST_PROCESSED_PREFIX", "Processed/")
DATASETS = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]
DATE_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_reviews_dataset.csv": ["review_creation_date", "review_answer_timestamp"],
}


def main():
    s3 = boto3.client("s3", region_name=REGION)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "bucket": BUCKET,
        "datasets": {},
    }

    for filename in DATASETS:
        source_key = f"{RAW_PREFIX}{filename}"
        response = s3.get_object(Bucket=BUCKET, Key=source_key)
        df = pd.read_csv(BytesIO(response["Body"].read()))
        input_rows = len(df)
        duplicate_rows = int(df.duplicated().sum())
        df = df.drop_duplicates().copy()
        for column in DATE_COLUMNS.get(filename, []):
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], errors="coerce")

        output_name = filename[:-4] + "_cleaned.csv"
        output_key = f"{PROCESSED_PREFIX}{output_name}"
        buffer = BytesIO()
        df.to_csv(buffer, index=False, date_format="%Y-%m-%d %H:%M:%S")
        buffer.seek(0)
        s3.put_object(Bucket=BUCKET, Key=output_key, Body=buffer.getvalue(), ContentType="text/csv")

        missing = {str(col): int(count) for col, count in df.isna().sum().items() if count}
        report["datasets"][filename] = {
            "input_rows": input_rows,
            "output_rows": len(df),
            "exact_duplicate_rows_removed": duplicate_rows,
            "missing_values_by_column": missing,
            "output_s3_uri": f"s3://{BUCKET}/{output_key}",
        }
        print(f"{filename}: {input_rows:,} -> {len(df):,} rows; removed {duplicate_rows:,} exact duplicates")

    report_key = f"{PROCESSED_PREFIX}all_datasets_quality_report.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=report_key,
        Body=json.dumps(report, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Quality report: s3://{BUCKET}/{report_key}")


if __name__ == "__main__":
    main()
