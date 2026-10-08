"""The excluding clause is quoted. A near miss is not a failure."""

from __future__ import annotations

import unittest

from blocked_by import BlockedByError, screen
from blocked_by.__main__ import CLAUSES, PATIENT


class ScreenTests(unittest.TestCase):
    def test_one_safety_clause_fires_and_names_the_flip(self) -> None:
        report = screen(PATIENT, CLAUSES)
        self.assertFalse(report["eligible"])
        self.assertTrue(report["single_clause"])
        firing = report["firing"]
        assert isinstance(firing, dict)
        self.assertEqual(firing["quote"], "eGFR at least 30 mL/min.")
        self.assertEqual(firing["kind"], "safety")
        self.assertEqual(firing["what_would_flip"], "raise egfr from 28 to 30")
        near = report["near_misses"]
        assert isinstance(near, list)
        self.assertEqual(near[0]["quote"], "Age 70 years or younger.")
        self.assertEqual(near[0]["margin"], 2)

    def test_clear_patient_is_eligible(self) -> None:
        patient = {**PATIENT, "egfr": 55, "age": 40}
        report = screen(patient, CLAUSES)
        self.assertTrue(report["eligible"])
        self.assertIsNone(report["firing"])
        self.assertEqual(report["near_misses"], [])

    def test_missing_field_raises(self) -> None:
        with self.assertRaises(BlockedByError):
            screen({"disease": "ALS"}, CLAUSES)

    def test_empty_protocol_raises(self) -> None:
        with self.assertRaises(BlockedByError):
            screen(PATIENT, [])


if __name__ == "__main__":
    unittest.main()
