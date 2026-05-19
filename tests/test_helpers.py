import unittest

from src.data_handling import build_donation_doc, normalize_item_name, parse_iso_date


# Attempt to parse data into expected formats and checks for correct handling of edge cases
class HelpersTest(unittest.TestCase):
    def test_normalize_item_name(self) -> None:
        self.assertEqual(normalize_item_name("  Canned   Beans "), "canned beans")

    def test_parse_iso_date(self) -> None:
        self.assertEqual(parse_iso_date("2026-05-18"), "2026-05-18")
        self.assertIsNone(parse_iso_date(None))

    def test_build_donation_doc(self) -> None:
        doc = build_donation_doc(
            "donor123",
            [
                {
                    "name": "Apples",
                    "quantity": "12",
                    "unit": "kg",
                    "category": "produce",
                    "expiry_date": "2026-05-25",
                }
            ],
            recipient_id="recipient456",
            status="available",
        )
        self.assertEqual(doc["donor_id"], "donor123")
        self.assertEqual(doc["recipient_id"], "recipient456")
        self.assertEqual(doc["items"][0]["name"], "apples")
        self.assertEqual(doc["items"][0]["quantity"], 12.0)

# Call __main__ to test
if __name__ == "__main__":
    unittest.main()

