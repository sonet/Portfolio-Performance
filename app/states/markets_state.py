import reflex as rx
import logging
import csv
import math
import random
import hashlib
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import TypedDict


class AssetRow(TypedDict):
    ticker: str
    sector: str
    asset_class: str
    name: str


class ReportRow(TypedDict):
    ticker: str
    sector: str
    asset_class: str
    name: str
    quarter_prices: dict[str, float]
    quarter_returns: dict[str, float]
    cumulative: float
    cagr: float
    is_positive: bool


INTERVAL_LABELS: list[tuple[str, str]] = [
    ("5Y", "5 Years"),
    ("12M", "12 Months"),
    ("6M", "6 Months"),
    ("10W", "10 Weeks"),
    ("5W", "5 Weeks"),
    ("30D", "30 Days"),
    ("10D", "10 Days"),
]

INTERVAL_LOOKBACK_QUARTERS: dict[str, int] = {
    "5Y": 20,
    "12M": 4,
    "6M": 2,
    "10W": 1,
    "5W": 1,
    "30D": 1,
    "10D": 1,
}

INTERVAL_DAYS: dict[str, int] = {
    "5Y": 1825,
    "12M": 365,
    "6M": 180,
    "10W": 70,
    "5W": 35,
    "30D": 30,
    "10D": 10,
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


def _quarter_labels(year_start: int = 2022) -> list[str]:
    today = datetime.utcnow().date()
    current_year = today.year
    current_quarter = (today.month - 1) // 3 + 1
    labels: list[str] = []
    for y in range(year_start, current_year + 1):
        max_q = current_quarter if y == current_year else 4
        for q in range(1, max_q + 1):
            labels.append(f"{y}-Q{q}")
    return labels


def _quarter_end_date(label: str) -> date:
    y_str, q_str = label.split("-Q")
    y = int(y_str)
    q = int(q_str)
    month = q * 3
    if month == 3:
        return date(y, 3, 31)
    if month == 6:
        return date(y, 6, 30)
    if month == 9:
        return date(y, 9, 30)
    return date(y, 12, 31)


def _synthetic_monthly_prices(
    ticker: str, months: int
) -> list[tuple[date, float]]:
    rng = random.Random(_seed_from(ticker))
    base = 20 + (_seed_from(ticker) % 480)
    is_crypto = "-USD" in ticker.upper()
    vol = 0.09 if is_crypto else 0.045
    drift = rng.uniform(-0.004, 0.014)
    p = float(base)
    prices: list[float] = []
    for _ in range(months):
        prices.append(p)
        shock = rng.gauss(0, vol)
        p = max(p * (1 + drift + shock), 0.01)
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    result: list[tuple[date, float]] = []
    for i in range(months):
        m_offset = months - 1 - i
        y = year
        m = month - m_offset
        while m <= 0:
            m += 12
            y -= 1
        try:
            d = date(y, m, 28)
        except ValueError:
            d = date(y, m, 1)
        result.append((d, round(prices[i], 4)))
    return result


def _fetch_monthly_prices_yf(
    ticker: str,
) -> list[tuple[date, float]] | None:
    try:
        import yfinance as yf

        df = yf.download(
            ticker,
            interval="1mo",
            start="2020-01-01",
            progress=False,
            threads=False,
            timeout=6,
        )
        if df is None or df.empty:
            return None
        close = df["Close"]
        result: list[tuple[date, float]] = []
        for idx, row in close.iterrows():
            val = float(row.iloc[0]) if hasattr(row, "iloc") else float(row)
            if math.isnan(val):
                continue
            d = (
                idx.date()
                if hasattr(idx, "date")
                else datetime.strptime(str(idx)[:10], "%Y-%m-%d").date()
            )
            result.append((d, round(val, 4)))
        return result if result else None
    except Exception as e:
        logging.exception(f"yfinance monthly fetch failed for {ticker}: {e}")
        return None


def _extract_quarter_prices(
    monthly: list[tuple[date, float]], quarter_labels: list[str]
) -> dict[str, float]:
    result: dict[str, float] = {}
    if not monthly:
        return result
    monthly_sorted = sorted(monthly, key=lambda x: x[0])
    for label in quarter_labels:
        target = _quarter_end_date(label)
        best_price: float | None = None
        for d, p in monthly_sorted:
            if d.year == target.year and d.month == target.month:
                best_price = p
                break
        if best_price is None:
            for d, p in monthly_sorted:
                if d <= target:
                    best_price = p
        if best_price is not None:
            result[label] = round(best_price, 4)
    return result


def _compute_report_row(
    asset: AssetRow,
    monthly: list[tuple[date, float]],
    quarter_labels: list[str],
) -> ReportRow:
    prices = _extract_quarter_prices(monthly, quarter_labels)
    returns: dict[str, float] = {}
    prev: float | None = None
    for label in quarter_labels:
        cur = prices.get(label)
        if cur is not None and prev is not None and prev > 0:
            returns[label] = round((cur / prev - 1) * 100, 2)
        prev = cur if cur is not None else prev

    valid_labels = [q for q in quarter_labels if q in prices]
    cumulative = 0.0
    cagr = 0.0
    if len(valid_labels) >= 2:
        first = prices[valid_labels[0]]
        last = prices[valid_labels[-1]]
        if first > 0:
            cumulative = round((last / first - 1) * 100, 2)
            start_d = _quarter_end_date(valid_labels[0])
            end_d = _quarter_end_date(valid_labels[-1])
            years = max((end_d - start_d).days / 365.25, 0.01)
            if last / first > 0:
                cagr = round(((last / first) ** (1 / years) - 1) * 100, 2)

    return {
        "ticker": asset["ticker"],
        "sector": asset["sector"],
        "asset_class": asset["asset_class"],
        "name": asset["name"],
        "quarter_prices": prices,
        "quarter_returns": returns,
        "cumulative": cumulative,
        "cagr": cagr,
        "is_positive": cumulative >= 0,
    }


class MarketsState(rx.State):
    universe: list[AssetRow] = ASSET_UNIVERSE
    report_rows: list[ReportRow] = []
    quarter_labels: list[str] = _quarter_labels(2022)

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
    interval: str = "5Y"
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

    @rx.var
    def visible_quarter_labels(self) -> list[str]:
        labels = self.quarter_labels
        if self.use_custom_range and (self.start_date or self.end_date):
            start = self.start_date
            end = self.end_date
            filtered: list[str] = []
            for lbl in labels:
                d = _quarter_end_date(lbl).isoformat()
                if start and d < start:
                    continue
                if end and d > end:
                    continue
                filtered.append(lbl)
            return filtered if filtered else labels[-1:]
        lookback = INTERVAL_LOOKBACK_QUARTERS.get(self.interval, 20)
        return labels[-lookback:] if lookback < len(labels) else labels

    @rx.var
    def filtered_rows(
        self,
    ) -> list[dict[str, str | float | bool | int | list]]:
        q = self.search_query.strip().lower()
        vis_labels = self.visible_quarter_labels
        if not vis_labels:
            return []
        rows: list[dict[str, str | float | bool | int | list]] = []
        for r in self.report_rows:
            if (
                self.filter_sector != "All"
                and r["sector"] != self.filter_sector
            ):
                continue
            if (
                self.filter_class != "All"
                and r["asset_class"] != self.filter_class
            ):
                continue
            if q and not (
                q in r["ticker"].lower()
                or q in r["name"].lower()
                or q in r["sector"].lower()
                or q in r["asset_class"].lower()
            ):
                continue
            prices = r["quarter_prices"]
            returns = r["quarter_returns"]
            valid = [lbl for lbl in vis_labels if lbl in prices]
            if len(valid) >= 2:
                first_p = prices[valid[0]]
                last_p = prices[valid[-1]]
                if first_p > 0:
                    period_cumulative = round((last_p / first_p - 1) * 100, 2)
                    start_d = _quarter_end_date(valid[0])
                    end_d = _quarter_end_date(valid[-1])
                    years = max((end_d - start_d).days / 365.25, 0.01)
                    period_cagr = (
                        round(((last_p / first_p) ** (1 / years) - 1) * 100, 2)
                        if last_p / first_p > 0
                        else 0.0
                    )
                else:
                    period_cumulative = 0.0
                    period_cagr = 0.0
            elif len(valid) == 1:
                period_cumulative = returns.get(valid[0], 0.0)
                period_cagr = 0.0
            else:
                period_cumulative = 0.0
                period_cagr = 0.0

            latest_return = 0.0
            if valid:
                latest_return = returns.get(valid[-1], 0.0)

            quarter_cells: list[dict[str, str | float | bool]] = []
            for lbl in vis_labels:
                has_ret = lbl in returns
                val = returns.get(lbl, 0.0) if has_ret else 0.0
                quarter_cells.append(
                    {
                        "label": lbl,
                        "value": val,
                        "display": f"{val:.1f}%" if has_ret else "—",
                        "has_data": has_ret,
                        "color_class": _color_class_for(val) if has_ret else "",
                    }
                )

            cumulative_class = (
                _color_class_for(period_cumulative) if valid else ""
            )

            row: dict[str, str | float | bool | int | list] = {
                "ticker": r["ticker"],
                "sector": r["sector"],
                "asset_class": r["asset_class"],
                "name": r["name"],
                "cumulative": period_cumulative,
                "cumulative_class": cumulative_class,
                "cagr": period_cagr,
                "latest_return": latest_return,
                "is_positive": period_cumulative >= 0,
                "has_data": len(valid) > 0,
                "quarter_cells": quarter_cells,
            }
            rows.append(row)

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
        if self.use_custom_range and (self.start_date or self.end_date):
            s = self.start_date or "start"
            e = self.end_date or "today"
            return f"Custom range: {s} → {e}"
        for k, label in INTERVAL_LABELS:
            if k == self.interval:
                return f"Preset: {label}"
        return "Preset: 5 Years"

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
        self.interval = "5Y"
        self.start_date = ""
        self.end_date = ""
        self.use_custom_range = False

    @rx.event(background=True)
    async def load_report(self):
        async with self:
            if self.loaded and self.report_rows:
                return
            self.loading = True
            self.status_message = (
                f"Loading market data for {len(self.universe)} tickers…"
            )
            self.error_message = ""
            universe = list(self.universe)
            labels = list(self.quarter_labels)

        rows: list[ReportRow] = []
        live = 0
        fallback = 0
        for asset in universe:
            monthly = _fetch_monthly_prices_yf(asset["ticker"])
            if monthly and len(monthly) >= 4:
                live += 1
            else:
                monthly = _synthetic_monthly_prices(asset["ticker"], months=72)
                fallback += 1
            row = _compute_report_row(asset, monthly, labels)
            rows.append(row)

        async with self:
            self.report_rows = rows
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
                    f"Live data from Yahoo Finance for all {live} tickers"
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
                    f"Using cached synthetic data for {fallback} tickers "
                    f"(network unavailable)"
                )

    @rx.event(background=True)
    async def refresh_report(self):
        async with self:
            self.loaded = False
            self.report_rows = []
        return MarketsState.load_report
