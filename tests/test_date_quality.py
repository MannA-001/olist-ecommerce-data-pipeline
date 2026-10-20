"""Tests that missing and malformed date values are reported separately."""
import unittest

import pandas as pd

from src.process_all_olist import parse_dates_with_quality


class DateQualityTests(unittest.TestCase):
    def test_missing_and_invalid_dates_are_distinguished(self):
        df = pd.DataFrame({
            "event_date": ["2024-01-02", "", None, "not-a-date"]
        })
        quality = parse_dates_with_quality(df, ["event_date"])["event_date"]

        self.assertEqual(quality["original_missing_values"], 2)
        self.assertEqual(quality["invalid_nonempty_values"], 1)
        self.assertEqual(quality["parsed_missing_values"], 3)
        self.assertEqual(str(df["event_date"].dtype), "datetime64[ns]")

    def test_missing_column_is_reported(self):
        df = pd.DataFrame({"other": [1]})
        quality = parse_dates_with_quality(df, ["event_date"])["event_date"]
        self.assertEqual(quality, {"column_present": False})


if __name__ == "__main__":
    unittest.main()
