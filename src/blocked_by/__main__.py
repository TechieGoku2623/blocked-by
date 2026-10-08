"""Screen a designed patient against four quoted clauses."""

from __future__ import annotations

from .engine import format_report, screen

PATIENT = {"disease": "ALS", "age": 68, "egfr": 28, "prior_lines": 1}

CLAUSES = [
    {
        "id": "disease",
        "field": "disease",
        "op": "eq",
        "value": "ALS",
        "kind": "safety",
        "quote": "Confirmed ALS.",
    },
    {
        "id": "age",
        "field": "age",
        "op": "le",
        "value": 70,
        "near": 5,
        "kind": "convenience",
        "quote": "Age 70 years or younger.",
    },
    {
        "id": "egfr",
        "field": "egfr",
        "op": "ge",
        "value": 30,
        "kind": "safety",
        "quote": "eGFR at least 30 mL/min.",
    },
    {
        "id": "lines",
        "field": "prior_lines",
        "op": "le",
        "value": 1,
        "kind": "uncited",
        "quote": "No more than one prior therapy line.",
    },
]


def main() -> int:
    print(format_report(screen(PATIENT, CLAUSES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
