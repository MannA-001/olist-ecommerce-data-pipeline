"""Load a small sample of processed orders into DynamoDB as a lookup demo.

Required environment variables: OLIST_BUCKET (default: olist-aws-project).
The EC2 role needs s3:GetObject for Processed/ and DynamoDB write permission
for the configured table. Writes are keyed by order_id and safe to rerun.
"""
import os
from io import BytesIO

import boto3
import pandas as pd

BUCKET = os.environ.get("OLIST_BUCKET", "olist-aws-project")
REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "OlistOrderStatus")
KEY = os.environ.get("ORDERS_KEY", "Processed/olist_orders_cleaned.csv")
LIMIT = int(os.environ.get("ORDER_SAMPLE_LIMIT", "100"))


def clean_value(value):
    if pd.isna(value) or str(value).strip() == "":
        return None
    return str(value)


def main():
    s3 = boto3.client("s3", region_name=REGION)
    response = s3.get_object(Bucket=BUCKET, Key=KEY)
    columns = [
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
    df = pd.read_csv(BytesIO(response["Body"].read()), usecols=lambda c: c in columns).head(LIMIT)
    table = boto3.resource("dynamodb", region_name=REGION).Table(TABLE_NAME)
    written = 0
    with table.batch_writer() as batch:
        for row in df.to_dict(orient="records"):
            item = {}
            for key, value in row.items():
                cleaned = clean_value(value)
                if cleaned is not None:
                    item[key] = cleaned
            if item.get("order_id"):
                batch.put_item(Item=item)
                written += 1
    print(f"Wrote {written} order-status records to {TABLE_NAME} in {REGION}.")
    print("This is a sample lookup table, not a full replica of the orders dataset.")


if __name__ == "__main__":
    main()
