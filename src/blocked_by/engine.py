"""Screen one patient against quoted protocol clauses.

The result names the clause that fired. It does not return a bare
"ineligible", and it does not invent a model score.
"""

from __future__ import annotations

from typing import Mapping


class BlockedByError(ValueError):
    """The patient or the clause list cannot be screened."""


def screen(patient: Mapping[str, object], clauses: list[Mapping[str, object]]) -> dict[str, object]:
    if not clauses:
        raise BlockedByError("a protocol with no clauses cannot exclude anyone")
    firing: list[dict[str, object]] = []
    near: list[dict[str, object]] = []
    for clause in clauses:
        row = _evaluate(patient, clause)
        if row["status"] == "fail":
            firing.append(row)
        elif row["status"] == "near":
            near.append(row)
    primary = None
    if firing:
        safety = [row for row in firing if row["kind"] == "safety"]
        primary = safety[0] if safety else firing[0]
    return {
        "eligible": not firing,
        "single_clause": len(firing) == 1,
        "firing": primary,
        "all_firing": firing,
        "near_misses": near,
    }


def format_report(report: dict[str, object]) -> str:
    lines = ["blocked-by", ""]
    if report["eligible"]:
        lines.append("eligible: yes")
        lines.append("firing clause: none")
    else:
        firing = report["firing"]
        assert isinstance(firing, dict)
        lines.append("eligible: no")
        lines.append(f"single clause: {str(report['single_clause']).lower()}")
        lines.append(f"quote: {firing['quote']}")
        lines.append(f"kind: {firing['kind']}")
        lines.append(f"what would flip it: {firing['what_would_flip']}")
    near = report["near_misses"]
    assert isinstance(near, list)
    if near:
        lines.append("near misses:")
        for row in near:
            lines.append(f"  {row['quote']}  margin {row['margin']}")
    else:
        lines.append("near misses: none")
    lines.append("")
    lines.append("not an eligibility decision")
    return "\n".join(lines)


def _evaluate(patient: Mapping[str, object], clause: Mapping[str, object]) -> dict[str, object]:
    field = str(clause.get("field", "")).strip()
    op = str(clause.get("op", "")).strip()
    kind = str(clause.get("kind", "")).strip()
    quote = str(clause.get("quote", "")).strip()
    if not field or not quote:
        raise BlockedByError("a clause needs a field and a quote")
    if kind not in {"safety", "convenience", "uncited"}:
        raise BlockedByError("kind must be safety, convenience, or uncited")
    if field not in patient:
        raise BlockedByError(f"patient has no {field}")
    actual = patient[field]
    bound = clause.get("value")
    ok, margin = _compare(op, actual, bound)
    near_within = clause.get("near")
    status = "pass" if ok else "fail"
    if ok and margin is not None and isinstance(near_within, (int, float)) and margin <= float(near_within):
        status = "near"
    return {
        "id": str(clause.get("id", field)),
        "quote": quote,
        "kind": kind,
        "field": field,
        "status": status,
        "margin": margin,
        "what_would_flip": None if ok else _flip(field, op, actual, bound),
    }


def _compare(op: str, actual: object, bound: object) -> tuple[bool, float | None]:
    if op == "eq":
        return actual == bound, None
    if not isinstance(actual, (int, float)) or isinstance(actual, bool):
        raise BlockedByError("numeric clause needs a numeric patient value")
    if not isinstance(bound, (int, float)) or isinstance(bound, bool):
        raise BlockedByError("numeric clause needs a numeric bound")
    if op == "ge":
        return actual >= bound, float(actual) - float(bound)
    if op == "le":
        return actual <= bound, float(bound) - float(actual)
    raise BlockedByError("op must be ge, le, or eq")


def _flip(field: str, op: str, actual: object, bound: object) -> str:
    if op == "eq":
        return f"set {field} to {bound}"
    if op == "ge":
        return f"raise {field} from {actual} to {bound}"
    return f"lower {field} from {actual} to {bound}"
