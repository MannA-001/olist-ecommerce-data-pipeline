"""Load a small sample of processed orders into DynamoDB as a lookup demo.

Required environment variables: OLIST_BUCKET (default: olist-aws-project).
The EC2 role needs s3:GetObject for Processed/, and DynamoDB DescribeTable and
write permission for the configured table. Writes are keyed by order_id and
safe to rerun.
"""
import os
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
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


def validate_table(table, dynamodb_client):
    """Fail early if the table is missing or its primary key is incompatible."""
    try:
        description = dynamodb_client.describe_table(TableName=TABLE_NAME)["Table"]
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code == "ResourceNotFoundException":
            raise SystemExit(
                f"DynamoDB table '{TABLE_NAME}' does not exist in {REGION}. "
                "Create it with partition key order_id (String) first."
            ) from exc
        raise

    if description.get("TableStatus") != "ACTIVE":
        raise SystemExit(
            f"DynamoDB table '{TABLE_NAME}' is {description.get('TableStatus')}, not ACTIVE."
        )

    key_schema = description.get("KeySchema", [])
    definitions = {
        item["AttributeName"]: item["AttributeType"]
        for item in description.get("AttributeDefinitions", [])
    }
    hash_keys = [key["AttributeName"] for key in key_schema if key["KeyType"] == "HASH"]
    if hash_keys != ["order_id"] or definitions.get("order_id") != "S":
        raise SystemExit(
            f"DynamoDB table '{TABLE_NAME}' must have a String partition key named order_id. "
            f"Found key schema: {key_schema}; attribute definitions: {definitions}"
        )


def main():
    if LIMIT < 1:
        raise SystemExit("ORDER_SAMPLE_LIMIT must be at least 1.")

    session = boto3.Session(region_name=REGION)
    s3 = session.client("s3")
    response = s3.get_object(Bucket=BUCKET, Key=KEY)
    columns = [
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
    df = pd.read_csv(BytesIO(response["Body"].read()), usecols=lambda c: c in columns).head(LIMIT)
    if "order_id" not in df.columns:
        raise SystemExit(f"Source CSV {KEY} does not contain required column order_id.")

    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    validate_table(table, session.client("dynamodb"))

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
