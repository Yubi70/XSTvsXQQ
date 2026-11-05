"""Read the dashboard's live data from the public GitHub main branch."""

import json
import math
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REPOSITORY = "Yubi70/XSTvsXQQ"
BRANCH = "main"
LOG_PATH = "src/monitor_log.csv"
STATE_PATH = "src/position_state.json"
STATE_EDIT_URL = f"https://github.com/{REPOSITORY}/edit/{BRANCH}/{STATE_PATH}"


class RemoteDataError(RuntimeError):
    """GitHub data could not be loaded or validated."""


def read_text(path: str) -> str:
    url = f"https://raw.githubusercontent.com/{REPOSITORY}/{BRANCH}/{quote(path)}"
    request = Request(url, headers={"User-Agent": "XSTvsXQQ-dashboard"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8-sig")
    except HTTPError as error:
        raise RemoteDataError(f"Could not load {path} from GitHub (HTTP {error.code}).") from error
    except (URLError, OSError, UnicodeDecodeError) as error:
        raise RemoteDataError(f"Could not load {path} from GitHub. Please try refreshing.") from error


def read_position_state() -> dict:
    try:
        state = json.loads(read_text(STATE_PATH))
    except json.JSONDecodeError as error:
        raise RemoteDataError("The GitHub position state is not valid JSON.") from error
    try:
        return validate_position_state(state)
    except ValueError as error:
        raise RemoteDataError(str(error)) from error


def validate_position_state(state: object) -> dict:
    if not isinstance(state, dict) or state.get("holding") not in ("XST", "XQQ"):
        raise ValueError("The GitHub position state must specify holding as XST or XQQ.")
    costs = state.get("cost_basis")
    if not isinstance(costs, dict):
        raise ValueError("The GitHub position state must contain a cost_basis object.")
    values = [(f"cost_basis.{ticker}", costs.get(ticker)) for ticker in ("XST", "XQQ")]
    if "approx_amount_cad" in state:
        values.append(("approx_amount_cad", state["approx_amount_cad"]))
    for name, value in values:
        if value is None and name.startswith("cost_basis."):
            continue
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value <= 0
        ):
            raise ValueError(f"The GitHub position state's {name} must be a positive finite number.")
    if "last_switch_date" in state:
        try:
            date.fromisoformat(state["last_switch_date"])
        except (TypeError, ValueError) as error:
            raise ValueError("The GitHub last_switch_date must use YYYY-MM-DD.") from error
    if "last_switch_at" in state:
        _validate_switch_time(state["last_switch_at"], "last_switch_at")
    history = state.get("switch_history", [])
    if not isinstance(history, list):
        raise ValueError("The GitHub switch_history must be a list.")
    for index, trade in enumerate(history):
        prefix = f"switch_history[{index}]"
        if not isinstance(trade, dict):
            raise ValueError(f"The GitHub {prefix} must be an object.")
        _validate_switch_time(trade.get("switched_at"), f"{prefix}.switched_at")
        if (
            trade.get("sold_ticker") not in ("XST", "XQQ")
            or trade.get("bought_ticker") not in ("XST", "XQQ")
            or trade["sold_ticker"] == trade["bought_ticker"]
        ):
            raise ValueError(f"The GitHub {prefix} must sell one ETF and buy the other.")
        for field in ("sold_price", "bought_price", "sold_quantity", "bought_quantity"):
            value = trade.get(field)
            if field.endswith("_quantity") and value is None:
                continue
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(f"The GitHub {prefix}.{field} must be a positive finite number.")
    return state


def _validate_switch_time(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"The GitHub {name} must be a Toronto-local date or timestamp.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"The GitHub {name} must use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.") from error
    if parsed.tzinfo is not None or len(value) not in (10, 19):
        raise ValueError(f"The GitHub {name} must be a Toronto-local date or timestamp.")
