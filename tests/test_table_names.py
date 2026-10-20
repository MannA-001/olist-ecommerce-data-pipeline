"""Regression tests for the CSV-to-DuckDB table mapping."""
import unittest

from src.load_data import table_name


class TableNameTests(unittest.TestCase):
    def test_names_match_analytics_sql(self):
        expected = {
            "olist_customers_dataset_cleaned.csv": "customers",
            "olist_geolocation_dataset_cleaned.csv": "geolocation",
            "olist_order_items_dataset_cleaned.csv": "order_items",
            "olist_order_payments_dataset_cleaned.csv": "order_payments",
            "olist_order_reviews_dataset_cleaned.csv": "order_reviews",
            "olist_orders_dataset_cleaned.csv": "orders",
            "olist_products_dataset_cleaned.csv": "products",
            "olist_sellers_dataset_cleaned.csv": "sellers",
            "product_category_name_translation_cleaned.csv": "category_translation",
        }
        for filename, table in expected.items():
            with self.subTest(filename=filename):
                self.assertEqual(table_name(filename), table)


if __name__ == "__main__":
    unittest.main()
