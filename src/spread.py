"""Holding-relative spread and directional switch rules."""

SWITCH_UP_THRESHOLD_PCT = 11.5
SWITCH_DOWN_THRESHOLD_PCT = 7.0


def holding_delta(delta: float, holding: str) -> float:
    if holding not in ("XST", "XQQ"):
        raise ValueError("Holding must be XST or XQQ.")
    return delta if holding == "XST" else -delta


def switch_threshold(holding: str) -> float:
    if holding == "XST":
        return SWITCH_UP_THRESHOLD_PCT
    if holding == "XQQ":
        return SWITCH_DOWN_THRESHOLD_PCT
    raise ValueError("Holding must be XST or XQQ.")


def switch_signal(delta: float | None, holding: str) -> str:
    threshold = switch_threshold(holding)
    if delta is None:
        return "DATA ERROR"
    if delta >= threshold:
        other = "XQQ" if holding == "XST" else "XST"
        return f"{holding} HIGH vs {other}"
    return ""
