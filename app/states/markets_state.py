import reflex as rx
import logging
import csv
import math
import random
import hashlib
from bisect import bisect_right
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import TypedDict


class AssetRow(TypedDict):
    ticker: str
    sector: str
    asset_class: str
    name: str


INTERVAL_LABELS: list[tuple[str, str]] = [
    ("5Y", "5 Years"),
    ("3Y", "3 Years"),
    ("12M", "12 Months"),
    ("6M", "6 Months"),
    ("10W", "10 Weeks"),
    ("5W", "5 Weeks"),
    ("30D", "30 Days"),
    ("10D", "10 Days"),
]


# Each entry is (granularity, column_count, step_between_periods)
INTERVAL_CONFIG: dict[str, tuple[str, int, int]] = {
    "10D": ("day", 10, 1),
    "30D": ("day", 10, 3),
    "5W": ("week", 5, 1),
    "10W": ("week", 10, 1),
    "6M": ("month", 6, 1),
    "12M": ("month", 12, 1),
    "3Y": ("quarter", 12, 1),
    "5Y": ("quarter", 20, 1),
}


GRANULARITY_LABELS: dict[str, dict[str, str]] = {
    "day": {
        "adj": "daily",
        "period": "Day-over-day",
        "unit": "Daily",
    },
    "week": {
        "adj": "weekly",
        "period": "Week-over-week",
        "unit": "Weekly",
    },
    "month": {
        "adj": "monthly",
        "period": "Month-over-month",
        "unit": "Monthly",
    },
    "quarter": {
        "adj": "quarterly",
        "period": "Quarter-over-quarter",
        "unit": "Quarterly",
    },
}


def _seed_from(symbol: str) -> int:
    return int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)


def _color_class_for(value: float) -> str:
    if value >= 20:
        return "bg-emerald-600 text-white border border-emerald-700"
    if value >= 10:
        return "bg-emerald-400 text-emerald-950 border border-emerald-500"
    if value >= 3:
        return "bg-emerald-200 text-emerald-900 border border-emerald-300"
    if value >= 0:
        return "bg-emerald-50 text-emerald-800 border border-emerald-100"
    if value >= -3:
        return "bg-amber-100 text-amber-900 border border-amber-200"
    if value >= -10:
        return "bg-red-200 text-red-900 border border-red-300"
    return "bg-red-600 text-white border border-red-700"


def _load_asset_universe() -> list[AssetRow]:
    csv_path = Path("assets/assets2.csv")
    result: list[AssetRow] = []
    if not csv_path.exists():
        return result
    try:
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = str(row.get("Ticker", "")).strip()
                if not ticker:
                    continue
                result.append(
                    {
                        "ticker": ticker,
                        "sector": str(row.get("Sector", "")).strip(),
                        "asset_class": str(row.get("Class", "")).strip(),
                        "name": str(row.get("Name", "")).strip(),
                    }
                )
    except Exception as e:
        logging.exception(f"Failed to load asset universe: {e}")
    return result


ASSET_UNIVERSE: list[AssetRow] = _load_asset_universe()


def _last_day_of_month(y: int, m: int) -> date:
    if m == 12:
        return date(y, 12, 31)
    return date(y, m + 1, 1) - timedelta(days=1)


def _quarter_end(y: int, q: int) -> date:
    return _last_day_of_month(y, q * 3)


def _period_end_dates(
    granularity: str, count: int, step: int, end_d: date
) -> list[date]:
    """Return count+1 period-end boundary dates so we can compute `count`
    period-over-period percent-change columns."""
    ends: list[date] = []
    if granularity == "day":
        for i in range(count + 1):
            ends.append(end_d - timedelta(days=(count - i) * step))
    elif granularity == "week":
        # anchor: last Friday <= end_d (weekday 4)
        anchor = end_d - timedelta(days=(end_d.weekday() - 4) % 7)
        for i in range(count + 1):
            ends.append(anchor - timedelta(weeks=(count - i) * step))
    elif granularity == "month":
        y, m = end_d.year, end_d.month
        for i in range(count + 1):
            offset = (count - i) * step
            ny, nm = y, m - offset
            while nm <= 0:
                nm += 12
                ny -= 1
            ends.append(_last_day_of_month(ny, nm))
    elif granularity == "quarter":
        y, m = end_d.year, end_d.month
        cq = (m - 1) // 3 + 1
        for i in range(count + 1):
            offset = (count - i) * step
            nq = cq - offset
            ny = y
            while nq <= 0:
                nq += 4
                ny -= 1
            ends.append(_quarter_end(ny, nq))
    return ends


def _format_period_label(granularity: str, d: date) -> str:
    if granularity == "day":
        return d.strftime("%b %d")
    if granularity == "week":
        iso_week = d.isocalendar()[1]
        return f"W{iso_week:02d} '{d.strftime('%y')}"
    if granularity == "month":
        return d.strftime("%b '%y")
    return f"{d.year} Q{(d.month - 1) // 3 + 1}"


def _choose_custom_config(days: int) -> tuple[str, int, int]:
    """Pick a sensible granularity, count, and step for a custom date range."""
    if days <= 20:
        return ("day", max(min(days, 15), 3), 1)
    if days <= 60:
        step = max(days // 10, 1)
        return ("day", 10, step)
    if days <= 90:
        return ("week", max(days // 7, 3), 1)
    if days <= 180:
        return ("week", 10, max(days // 70, 1))
    if days <= 3 * 365:
        return ("month", max(min(days // 30, 24), 3), 1)
    if days <= 6 * 365:
        return ("quarter", max(min(days // 90, 20), 4), 1)
    return ("quarter", 20, max(days // (20 * 90), 1))


def _synthetic_daily_prices(
    ticker: str, days: int = 1825
) -> list[list[str | float]]:
    rng = random.Random(_seed_from(ticker))
    base = 20 + (_seed_from(ticker) % 480)
    is_crypto = "-USD" in ticker.upper()
    vol = 0.03 if is_crypto else 0.014
    drift = rng.uniform(-0.0002, 0.0007)
    p = float(base)
    prices: list[float] = []
    for _ in range(days):
        prices.append(p)
        shock = rng.gauss(0, vol)
        p = max(p * (1 + drift + shock), 0.01)
    today = datetime.utcnow().date()
    return [
        [
            (today - timedelta(days=days - 1 - i)).isoformat(),
            round(prices[i], 4),
        ]
        for i in range(days)
    ]


def _fetch_daily_prices_yf(
    ticker: str,
) -> list[list[str | float]] | None:
    try:
        import yfinance as yf

        df = yf.download(
            ticker,
            period="5y",
            interval="1d",
            progress=False,
            threads=False,
            timeout=6,
        )
        if df is None or df.empty:
            return None
        close = df["Close"]
        result: list[list[str | float]] = []
        for idx, row in close.iterrows():
            val = float(row.iloc[0]) if hasattr(row, "iloc") else float(row)
            if math.isnan(val):
                continue
            d_iso = (
                idx.strftime("%Y-%m-%d")
                if hasattr(idx, "strftime")
                else str(idx)[:10]
            )
            result.append([d_iso, round(val, 4)])
        return result if result else None
    except Exception as e:
        logging.exception(f"yfinance daily fetch failed for {ticker}: {e}")
        return None


def _prices_at_boundaries(
    daily_prices: list[list[str | float]], boundary_isos: list[str]
) -> list[float | None]:
    """For each boundary date, return the last known price at or before it."""
    if not daily_prices:
        return [None] * len(boundary_isos)
    result: list[float | None] = []
    for iso in boundary_isos:
        # bisect_right on the list of [date_iso, price] pairs. Because Python
        # compares lists lexicographically, [iso, +inf] slots after every
        # [d, p] where d <= iso.
        idx = bisect_right(daily_prices, [iso, float("inf")]) - 1
        if idx < 0:
            result.append(None)
        else:
            try:
                result.append(float(daily_prices[idx][1]))
            except (ValueError, TypeError):
                result.append(None)
    return result


class MarketsState(rx.State):
    universe: list[AssetRow] = ASSET_UNIVERSE
    # daily_prices[ticker] is a list of [date_iso, price] pairs sorted by date.
    daily_prices: dict[str, list[list[str | float]]] = {}

    loading: bool = False
    loaded: bool = False
    data_source: str = "cached"
    status_message: str = "Ready to load market data"
    error_message: str = ""
    last_updated: str = ""
    live_count: int = 0
    fallback_count: int = 0

    search_query: str = ""
    filter_sector: str = "All"
    filter_class: str = "All"
    interval: str = "12M"
    start_date: str = ""
    end_date: str = ""
    use_custom_range: bool = False
    sort_by: str = "cumulative"
    sort_dir: str = "desc"

    @rx.var
    def sector_options(self) -> list[str]:
        seen: dict[str, bool] = {}
        for a in self.universe:
            s = a["sector"]
            if s and s not in seen:
                seen[s] = True
        return ["All"] + sorted(seen.keys())

    @rx.var
    def class_options(self) -> list[str]:
        seen: dict[str, bool] = {}
        for a in self.universe:
            c = a["asset_class"]
            if c and c not in seen:
                seen[c] = True
        return ["All"] + sorted(seen.keys())

    @rx.var
    def universe_size(self) -> int:
        return len(self.universe)

    def _active_config(self) -> tuple[str, int, int, date]:
        """Return (granularity, count, step, end_date) driving the columns."""
        today = datetime.utcnow().date()
        if self.use_custom_range and (self.start_date or self.end_date):
            try:
                s = (
                    datetime.strptime(self.start_date, "%Y-%m-%d").date()
                    if self.start_date
                    else today - timedelta(days=365)
                )
            except ValueError:
                s = today - timedelta(days=365)
            try:
                e = (
                    datetime.strptime(self.end_date, "%Y-%m-%d").date()
                    if self.end_date
                    else today
                )
            except ValueError:
                e = today
            if e < s:
                s, e = e, s
            days = max((e - s).days, 1)
            gran, count, step = _choose_custom_config(days)
            return (gran, count, step, e)
        gran, count, step = INTERVAL_CONFIG.get(self.interval, ("month", 12, 1))
        return (gran, count, step, today)

    def _boundary_dates(self) -> list[date]:
        gran, count, step, end_d = self._active_config()
        return _period_end_dates(gran, count, step, end_d)

    @rx.var
    def granularity(self) -> str:
        gran, _, _, _ = self._active_config()
        return gran

    @rx.var
    def granularity_adjective(self) -> str:
        return GRANULARITY_LABELS.get(self.granularity, {}).get("adj", "period")

    @rx.var
    def granularity_period_label(self) -> str:
        return GRANULARITY_LABELS.get(self.granularity, {}).get(
            "period", "Period-over-period"
        )

    @rx.var
    def granularity_unit(self) -> str:
        return GRANULARITY_LABELS.get(self.granularity, {}).get(
            "unit", "Period"
        )

    @rx.var
    def visible_quarter_labels(self) -> list[str]:
        gran, count, step, end_d = self._active_config()
        boundaries = _period_end_dates(gran, count, step, end_d)
        return [_format_period_label(gran, b) for b in boundaries[1:]]

    @rx.var
    def column_count(self) -> int:
        return len(self.visible_quarter_labels)

    @rx.var
    def report_title(self) -> str:
        return f"{self.granularity_unit} Returns Report"

    @rx.var
    def report_subtitle(self) -> str:
        return (
            f"{self.granularity_period_label} returns across "
            f"{self.column_count} {self.granularity_adjective} periods — "
            f"cells color-scaled from red (loss) to green (gain), with "
            f"cumulative and CAGR summaries"
        )

    @rx.var
    def column_summary(self) -> str:
        return f"{self.column_count} {self.granularity_adjective} columns"

    @rx.var
    def filtered_rows(
        self,
    ) -> list[dict[str, str | float | bool | int | list]]:
        gran, count, step, end_d = self._active_config()
        boundaries = _period_end_dates(gran, count, step, end_d)
        boundary_isos = [b.isoformat() for b in boundaries]
        labels = [_format_period_label(gran, b) for b in boundaries[1:]]
        if not labels:
            return []

        span_days = max((boundaries[-1] - boundaries[0]).days, 1)
        years = max(span_days / 365.25, 0.01)

        q = self.search_query.strip().lower()
        rows: list[dict[str, str | float | bool | int | list]] = []
        for asset in self.universe:
            if (
                self.filter_sector != "All"
                and asset["sector"] != self.filter_sector
            ):
                continue
            if (
                self.filter_class != "All"
                and asset["asset_class"] != self.filter_class
            ):
                continue
            if q and not (
                q in asset["ticker"].lower()
                or q in asset["name"].lower()
                or q in asset["sector"].lower()
                or q in asset["asset_class"].lower()
            ):
                continue

            prices_raw = self.daily_prices.get(asset["ticker"], [])
            period_prices = _prices_at_boundaries(prices_raw, boundary_isos)

            cells: list[dict[str, str | float | bool]] = []
            for i, lbl in enumerate(labels):
                prev_p = period_prices[i]
                cur_p = period_prices[i + 1]
                has_ret = (
                    prev_p is not None and cur_p is not None and prev_p > 0
                )
                val = ((cur_p / prev_p - 1) * 100) if has_ret else 0.0
                cells.append(
                    {
                        "label": lbl,
                        "value": round(val, 2),
                        "display": f"{val:.1f}%" if has_ret else "—",
                        "has_data": has_ret,
                        "color_class": (
                            _color_class_for(val) if has_ret else ""
                        ),
                    }
                )

            first_p: float | None = None
            for p in period_prices:
                if p is not None:
                    first_p = p
                    break
            last_p: float | None = None
            for p in reversed(period_prices):
                if p is not None:
                    last_p = p
                    break
            has_data = (
                first_p is not None and last_p is not None and first_p > 0
            )
            if has_data:
                cumulative = round((last_p / first_p - 1) * 100, 2)
                if last_p > 0 and first_p > 0:
                    cagr = round(
                        ((last_p / first_p) ** (1 / years) - 1) * 100, 2
                    )
                else:
                    cagr = 0.0
            else:
                cumulative = 0.0
                cagr = 0.0

            latest_return = 0.0
            if cells and bool(cells[-1]["has_data"]):
                latest_return = float(cells[-1]["value"])

            rows.append(
                {
                    "ticker": asset["ticker"],
                    "sector": asset["sector"],
                    "asset_class": asset["asset_class"],
                    "name": asset["name"],
                    "cumulative": cumulative,
                    "cumulative_class": (
                        _color_class_for(cumulative) if has_data else ""
                    ),
                    "cagr": cagr,
                    "latest_return": latest_return,
                    "is_positive": cumulative >= 0,
                    "has_data": has_data,
                    "quarter_cells": cells,
                }
            )

        key = self.sort_by
        reverse = self.sort_dir == "desc"
        try:
            if key in ("cumulative", "cagr", "latest_return"):
                rows.sort(key=lambda x: float(x[key]), reverse=reverse)
            elif key == "ticker":
                rows.sort(key=lambda x: str(x["ticker"]), reverse=reverse)
            else:
                rows.sort(key=lambda x: float(x["cumulative"]), reverse=reverse)
        except (ValueError, TypeError):
            pass
        return rows

    @rx.var
    def summary_stats(self) -> dict[str, float]:
        rows = self.filtered_rows
        if not rows:
            return {
                "count": 0.0,
                "avg_return": 0.0,
                "avg_cagr": 0.0,
                "positive_count": 0.0,
                "negative_count": 0.0,
                "best": 0.0,
                "worst": 0.0,
                "median": 0.0,
                "positive_pct": 0.0,
            }
        cums = [float(r["cumulative"]) for r in rows if bool(r["has_data"])]
        cagrs = [float(r["cagr"]) for r in rows if bool(r["has_data"])]
        pos = len([c for c in cums if c >= 0])
        neg = len([c for c in cums if c < 0])
        avg_ret = sum(cums) / len(cums) if cums else 0.0
        avg_cg = sum(cagrs) / len(cagrs) if cagrs else 0.0
        best = max(cums) if cums else 0.0
        worst = min(cums) if cums else 0.0
        sorted_c = sorted(cums)
        median = sorted_c[len(sorted_c) // 2] if sorted_c else 0.0
        return {
            "count": float(len(rows)),
            "avg_return": round(avg_ret, 2),
            "avg_cagr": round(avg_cg, 2),
            "positive_count": float(pos),
            "negative_count": float(neg),
            "best": round(best, 2),
            "worst": round(worst, 2),
            "median": round(median, 2),
            "positive_pct": round(pos / len(cums) * 100 if cums else 0.0, 1),
        }

    @rx.var
    def top_performers(self) -> list[dict[str, str | float | bool]]:
        rows = [r for r in self.filtered_rows if bool(r["has_data"])]
        rows_sorted = sorted(
            rows, key=lambda x: float(x["cumulative"]), reverse=True
        )
        return [
            {
                "ticker": str(r["ticker"]),
                "name": str(r["name"]),
                "sector": str(r["sector"]),
                "asset_class": str(r["asset_class"]),
                "cumulative": float(r["cumulative"]),
                "cagr": float(r["cagr"]),
                "is_positive": bool(r["is_positive"]),
            }
            for r in rows_sorted[:6]
        ]

    @rx.var
    def bottom_performers(self) -> list[dict[str, str | float | bool]]:
        rows = [r for r in self.filtered_rows if bool(r["has_data"])]
        rows_sorted = sorted(rows, key=lambda x: float(x["cumulative"]))
        return [
            {
                "ticker": str(r["ticker"]),
                "name": str(r["name"]),
                "sector": str(r["sector"]),
                "asset_class": str(r["asset_class"]),
                "cumulative": float(r["cumulative"]),
                "cagr": float(r["cagr"]),
                "is_positive": bool(r["is_positive"]),
            }
            for r in rows_sorted[:6]
        ]

    @rx.var
    def sector_breakdown(self) -> list[dict[str, str | float | int]]:
        buckets: dict[str, list[float]] = {}
        for r in self.filtered_rows:
            if not bool(r["has_data"]):
                continue
            key = str(r["sector"]) or "Unknown"
            buckets.setdefault(key, []).append(float(r["cumulative"]))
        result: list[dict[str, str | float | int]] = []
        for name, vals in buckets.items():
            avg = sum(vals) / len(vals) if vals else 0.0
            result.append(
                {
                    "name": name,
                    "count": len(vals),
                    "avg_return": round(avg, 2),
                    "best": round(max(vals), 2) if vals else 0.0,
                    "worst": round(min(vals), 2) if vals else 0.0,
                }
            )
        result.sort(key=lambda x: float(x["avg_return"]), reverse=True)
        return result

    @rx.var
    def class_breakdown(self) -> list[dict[str, str | float | int]]:
        buckets: dict[str, list[float]] = {}
        for r in self.filtered_rows:
            if not bool(r["has_data"]):
                continue
            key = str(r["asset_class"]) or "Unknown"
            buckets.setdefault(key, []).append(float(r["cumulative"]))
        result: list[dict[str, str | float | int]] = []
        for name, vals in buckets.items():
            avg = sum(vals) / len(vals) if vals else 0.0
            result.append(
                {
                    "name": name,
                    "count": len(vals),
                    "avg_return": round(avg, 2),
                    "best": round(max(vals), 2) if vals else 0.0,
                    "worst": round(min(vals), 2) if vals else 0.0,
                }
            )
        result.sort(key=lambda x: float(x["avg_return"]), reverse=True)
        return result

    @rx.var
    def interval_summary(self) -> str:
        col_summary = self.column_summary
        if self.use_custom_range and (self.start_date or self.end_date):
            s = self.start_date or "start"
            e = self.end_date or "today"
            return f"Custom: {s} → {e} · {col_summary}"
        for k, label in INTERVAL_LABELS:
            if k == self.interval:
                return f"Preset: {label} · {col_summary}"
        return f"Preset · {col_summary}"

    @rx.event
    def set_search(self, v: str):
        self.search_query = v

    @rx.event
    def set_sector(self, v: str):
        self.filter_sector = v

    @rx.event
    def set_class(self, v: str):
        self.filter_class = v

    @rx.event
    def set_interval(self, v: str):
        if v not in INTERVAL_CONFIG:
            v = "12M"
        self.interval = v
        self.use_custom_range = False
        self.start_date = ""
        self.end_date = ""

    @rx.event
    def set_start_date(self, v: str):
        self.start_date = v
        if v or self.end_date:
            self.use_custom_range = True

    @rx.event
    def set_end_date(self, v: str):
        self.end_date = v
        if v or self.start_date:
            self.use_custom_range = True

    @rx.event
    def clear_custom_range(self):
        self.start_date = ""
        self.end_date = ""
        self.use_custom_range = False

    @rx.event
    def set_sort(self, key: str):
        if self.sort_by == key:
            self.sort_dir = "asc" if self.sort_dir == "desc" else "desc"
        else:
            self.sort_by = key
            self.sort_dir = "desc"

    @rx.event
    def reset_filters(self):
        self.search_query = ""
        self.filter_sector = "All"
        self.filter_class = "All"
        self.interval = "12M"
        self.start_date = ""
        self.end_date = ""
        self.use_custom_range = False

    @rx.event(background=True)
    async def load_report(self):
        async with self:
            if self.loaded and self.daily_prices:
                return
            self.loading = True
            self.status_message = (
                f"Loading daily market data for {len(self.universe)} tickers…"
            )
            self.error_message = ""
            universe = list(self.universe)

        daily_map: dict[str, list[list[str | float]]] = {}
        live = 0
        fallback = 0
        for asset in universe:
            prices = _fetch_daily_prices_yf(asset["ticker"])
            if prices and len(prices) >= 30:
                live += 1
            else:
                prices = _synthetic_daily_prices(asset["ticker"], days=1825)
                fallback += 1
            daily_map[asset["ticker"]] = prices

        async with self:
            self.daily_prices = daily_map
            self.live_count = live
            self.fallback_count = fallback
            self.loaded = True
            self.loading = False
            self.last_updated = datetime.utcnow().strftime(
                "%b %d, %Y %H:%M UTC"
            )
            if live > 0 and fallback == 0:
                self.data_source = "live"
                self.status_message = (
                    f"Live daily data from Yahoo Finance for all {live} tickers"
                )
            elif live > 0 and fallback > 0:
                self.data_source = "mixed"
                self.status_message = (
                    f"Live for {live} tickers, cached synthetic for "
                    f"{fallback} unavailable tickers"
                )
            else:
                self.data_source = "cached"
                self.status_message = (
                    f"Using cached synthetic daily data for "
                    f"{fallback} tickers (network unavailable)"
                )

    @rx.event(background=True)
    async def refresh_report(self):
        async with self:
            self.loaded = False
            self.daily_prices = {}
        return MarketsState.load_report
