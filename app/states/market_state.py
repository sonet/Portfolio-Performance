import reflex as rx
import logging
import math
import random
import hashlib
from datetime import datetime, timedelta
from typing import TypedDict


class PricePoint(TypedDict):
    date: str
    price: float
    benchmark: float


class AssetMetrics(TypedDict):
    symbol: str
    name: str
    latest_price: float
    prev_close: float
    day_change: float
    day_change_pct: float
    year_change_pct: float
    week_high_52: float
    week_low_52: float
    volatility: float
    avg_volume: float
    currency: str
    is_up: bool


POPULAR_SYMBOLS: list[dict[str, str]] = [
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_class": "Equity",
        "sector": "Technology",
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "asset_class": "Equity",
        "sector": "Technology",
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corp.",
        "asset_class": "Equity",
        "sector": "Semiconductors",
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "asset_class": "Equity",
        "sector": "Communication",
    },
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "asset_class": "Equity",
        "sector": "Consumer",
    },
    {
        "symbol": "META",
        "name": "Meta Platforms Inc.",
        "asset_class": "Equity",
        "sector": "Communication",
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "asset_class": "Equity",
        "sector": "Automotive",
    },
    {
        "symbol": "BRK-B",
        "name": "Berkshire Hathaway",
        "asset_class": "Equity",
        "sector": "Financials",
    },
    {
        "symbol": "JPM",
        "name": "JPMorgan Chase & Co.",
        "asset_class": "Equity",
        "sector": "Financials",
    },
    {
        "symbol": "V",
        "name": "Visa Inc.",
        "asset_class": "Equity",
        "sector": "Financials",
    },
    {
        "symbol": "UNH",
        "name": "UnitedHealth Group",
        "asset_class": "Equity",
        "sector": "Healthcare",
    },
    {
        "symbol": "XOM",
        "name": "Exxon Mobil Corp.",
        "asset_class": "Equity",
        "sector": "Energy",
    },
    {
        "symbol": "VOO",
        "name": "Vanguard S&P 500 ETF",
        "asset_class": "ETF",
        "sector": "Broad Market",
    },
    {
        "symbol": "QQQ",
        "name": "Invesco QQQ Trust",
        "asset_class": "ETF",
        "sector": "Technology",
    },
    {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF",
        "asset_class": "ETF",
        "sector": "Broad Market",
    },
    {
        "symbol": "VTI",
        "name": "Vanguard Total Stock ETF",
        "asset_class": "ETF",
        "sector": "Broad Market",
    },
    {
        "symbol": "BND",
        "name": "Vanguard Total Bond ETF",
        "asset_class": "Bond",
        "sector": "Fixed Income",
    },
    {
        "symbol": "TLT",
        "name": "iShares 20+ Yr Treasury",
        "asset_class": "Bond",
        "sector": "Fixed Income",
    },
    {
        "symbol": "GLD",
        "name": "SPDR Gold Shares",
        "asset_class": "Commodity",
        "sector": "Precious Metals",
    },
    {
        "symbol": "BTC-USD",
        "name": "Bitcoin",
        "asset_class": "Crypto",
        "sector": "Digital Assets",
    },
    {
        "symbol": "ETH-USD",
        "name": "Ethereum",
        "asset_class": "Crypto",
        "sector": "Digital Assets",
    },
    {
        "symbol": "SOL-USD",
        "name": "Solana",
        "asset_class": "Crypto",
        "sector": "Digital Assets",
    },
]

RANGE_DAYS: dict[str, int] = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
}


def _seed_from(symbol: str) -> int:
    return int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)


def _synthetic_history(
    symbol: str, current_price: float, days: int = 365, drift: float = 0.0
) -> list[dict[str, float | str]]:
    rng = random.Random(_seed_from(symbol))
    volatility = 0.018 if "-USD" in symbol else 0.014
    if drift == 0.0:
        drift = rng.uniform(-0.0004, 0.0009)
    prices: list[float] = []
    p = float(current_price)
    for _ in range(days):
        prices.append(p)
        shock = rng.gauss(0, volatility)
        p = p / (1 + drift + shock) if p > 0 else current_price
        p = max(p, 0.01)
    prices.reverse()
    scale = current_price / prices[-1] if prices[-1] > 0 else 1.0
    prices = [round(x * scale, 4) for x in prices]
    today = datetime.utcnow().date()
    return [
        {
            "date": (today - timedelta(days=days - 1 - i)).isoformat(),
            "price": prices[i],
        }
        for i in range(days)
    ]


def _synthetic_benchmark(days: int = 365, base: float = 458.0) -> list[float]:
    rng = random.Random(42)
    p = base
    prices: list[float] = []
    for _ in range(days):
        prices.append(p)
        shock = rng.gauss(0, 0.009)
        p = p / (1 + 0.0004 + shock)
        p = max(p, 1.0)
    prices.reverse()
    scale = base / prices[-1] if prices[-1] > 0 else 1.0
    return [round(x * scale, 4) for x in prices]


def _fetch_yfinance(
    symbol: str, period: str = "1y"
) -> list[dict[str, float | str]] | None:
    try:
        import yfinance as yf

        df = yf.download(
            symbol,
            period=period,
            interval="1d",
            progress=False,
            threads=False,
            timeout=6,
        )
        if df is None or df.empty:
            return None
        close = df["Close"]
        result: list[dict[str, float | str]] = []
        for idx, row in close.iterrows():
            val = float(row.iloc[0]) if hasattr(row, "iloc") else float(row)
            date_str = (
                idx.strftime("%Y-%m-%d")
                if hasattr(idx, "strftime")
                else str(idx)[:10]
            )
            result.append({"date": date_str, "price": round(val, 4)})
        return result
    except Exception as e:
        logging.exception(f"yfinance fetch failed for {symbol}: {e}")
        return None


def _compute_metrics(
    symbol: str, name: str, history: list[dict[str, float | str]]
) -> AssetMetrics:
    prices = [float(p["price"]) for p in history]
    if len(prices) < 2:
        return AssetMetrics(
            symbol=symbol,
            name=name,
            latest_price=0.0,
            prev_close=0.0,
            day_change=0.0,
            day_change_pct=0.0,
            year_change_pct=0.0,
            week_high_52=0.0,
            week_low_52=0.0,
            volatility=0.0,
            avg_volume=0.0,
            currency="USD",
            is_up=True,
        )
    latest = prices[-1]
    prev = prices[-2]
    year_ago = prices[0]
    day_change = latest - prev
    day_pct = (day_change / prev * 100) if prev > 0 else 0.0
    year_pct = ((latest - year_ago) / year_ago * 100) if year_ago > 0 else 0.0
    hi = max(prices)
    lo = min(prices)
    returns: list[float] = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])
    if returns:
        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / len(returns)
        vol = math.sqrt(var) * math.sqrt(252) * 100
    else:
        vol = 0.0
    return AssetMetrics(
        symbol=symbol,
        name=name,
        latest_price=round(latest, 2),
        prev_close=round(prev, 2),
        day_change=round(day_change, 2),
        day_change_pct=round(day_pct, 2),
        year_change_pct=round(year_pct, 2),
        week_high_52=round(hi, 2),
        week_low_52=round(lo, 2),
        volatility=round(vol, 2),
        avg_volume=0.0,
        currency="USD",
        is_up=day_change >= 0,
    )


class MarketState(rx.State):
    asset_metrics: dict[str, AssetMetrics] = {}
    asset_history: dict[str, list[dict[str, float | str]]] = {}
    benchmark_history: list[dict[str, float | str]] = []
    portfolio_history: list[dict[str, str | float]] = []

    loading: bool = False
    status_message: str = "Ready"
    error_message: str = ""
    data_source: str = "cached"
    last_updated: str = ""

    range_selection: str = "6M"
    discover_query: str = ""
    popular_symbols: list[dict[str, str]] = POPULAR_SYMBOLS

    @rx.var
    def filtered_discover(self) -> list[dict[str, str]]:
        q = self.discover_query.strip().lower()
        if not q:
            return self.popular_symbols
        return [
            s
            for s in self.popular_symbols
            if q in s["symbol"].lower()
            or q in s["name"].lower()
            or q in s["sector"].lower()
        ]

    @rx.var
    def current_symbol(self) -> str:
        return self.router.page.params.get("ticker", "").upper()

    @rx.var
    def current_asset(self) -> AssetMetrics:
        sym = self.current_symbol
        return self.asset_metrics.get(
            sym,
            AssetMetrics(
                symbol=sym,
                name=sym,
                latest_price=0.0,
                prev_close=0.0,
                day_change=0.0,
                day_change_pct=0.0,
                year_change_pct=0.0,
                week_high_52=0.0,
                week_low_52=0.0,
                volatility=0.0,
                avg_volume=0.0,
                currency="USD",
                is_up=True,
            ),
        )

    @rx.var
    def current_history(self) -> list[dict[str, float | str]]:
        sym = self.current_symbol
        full = self.asset_history.get(sym, [])
        days = RANGE_DAYS.get(self.range_selection, 180)
        sliced = full[-days:] if len(full) > days else full
        bench = (
            self.benchmark_history[-len(sliced) :]
            if self.benchmark_history
            else []
        )
        if not sliced:
            return []
        base_p = float(sliced[0]["price"]) if sliced else 1.0
        base_b = float(bench[0]["price"]) if bench else 1.0
        result: list[dict[str, float | str]] = []
        for i, pt in enumerate(sliced):
            price = float(pt["price"])
            b_price = float(bench[i]["price"]) if i < len(bench) else base_b
            asset_norm = (price / base_p * 100) if base_p > 0 else 100.0
            bench_norm = (b_price / base_b * 100) if base_b > 0 else 100.0
            result.append(
                {
                    "date": str(pt["date"]),
                    "price": round(price, 2),
                    "asset_indexed": round(asset_norm, 2),
                    "benchmark_indexed": round(bench_norm, 2),
                }
            )
        return result

    @rx.var
    def current_position(self) -> dict[str, float | str | bool]:
        # portfolio contribution info if held
        # avoid circular import at class scope
        return {}

    def _lookup_symbol_name(self, sym: str) -> str:
        for p in self.popular_symbols:
            if p["symbol"].upper() == sym.upper():
                return p["name"]
        return sym

    @rx.event(background=True)
    async def load_asset(self):
        async with self:
            sym = self.current_symbol
            if not sym:
                return
            self.loading = True
            self.status_message = f"Fetching market data for {sym}…"
            self.error_message = ""

        history = _fetch_yfinance(sym, "1y")
        source = "live"
        if not history or len(history) < 5:
            source = "cached"
            # need a base price
            base = 100.0
            from app.states.portfolio_state import PortfolioState

            async with self:
                port = await self.get_state(PortfolioState)
                for h in port.holdings:
                    if h["symbol"].upper() == sym:
                        base = float(h["current_price"])
                        break
                for p in self.popular_symbols:
                    if p["symbol"].upper() == sym and base == 100.0:
                        seed = _seed_from(sym)
                        base = 20 + (seed % 500)
                        break
            history = _synthetic_history(sym, base, days=365)

        # benchmark
        bench = _fetch_yfinance("SPY", "1y")
        if not bench or len(bench) < 5:
            bench_prices = _synthetic_benchmark(days=len(history), base=458.0)
            today = datetime.utcnow().date()
            n = len(history)
            bench = [
                {
                    "date": (today - timedelta(days=n - 1 - i)).isoformat(),
                    "price": bench_prices[i],
                }
                for i in range(n)
            ]

        name = self._lookup_symbol_name(sym)
        metrics = _compute_metrics(sym, name, history)

        async with self:
            self.asset_history[sym] = history
            self.benchmark_history = bench
            self.asset_metrics[sym] = metrics
            self.data_source = source
            self.status_message = (
                f"Live data from Yahoo Finance"
                if source == "live"
                else "Using cached synthetic data (network unavailable)"
            )
            self.last_updated = datetime.utcnow().strftime(
                "%b %d, %Y %H:%M UTC"
            )
            self.loading = False

    @rx.event(background=True)
    async def load_portfolio_history(self):
        async with self:
            self.loading = True
            self.status_message = "Building portfolio history…"

        from app.states.portfolio_state import PortfolioState

        async with self:
            port = await self.get_state(PortfolioState)
            holdings = list(port.holdings)

        # Build per-symbol synthetic history and aggregate
        combined: dict[str, float] = {}
        days = 365
        today = datetime.utcnow().date()
        cost_basis_total = sum(
            h["quantity"] * h["cost_basis"] for h in holdings
        )
        for h in holdings:
            sym = h["symbol"]
            hist = _fetch_yfinance(sym, "1y")
            if not hist or len(hist) < 5:
                hist = _synthetic_history(
                    sym, float(h["current_price"]), days=days
                )
            for pt in hist:
                d = str(pt["date"])
                combined[d] = combined.get(d, 0.0) + float(pt["price"]) * float(
                    h["quantity"]
                )

        bench = _fetch_yfinance("SPY", "1y")
        if not bench or len(bench) < 5:
            b_prices = _synthetic_benchmark(days=days, base=458.0)
            bench = [
                {
                    "date": (today - timedelta(days=days - 1 - i)).isoformat(),
                    "price": b_prices[i],
                }
                for i in range(days)
            ]
        bench_map = {str(pt["date"]): float(pt["price"]) for pt in bench}

        sorted_dates = sorted(combined.keys())
        if not sorted_dates:
            async with self:
                self.portfolio_history = []
                self.loading = False
                self.status_message = "No holdings to chart"
            return

        base_val = combined[sorted_dates[0]]
        # find first bench value present
        first_bench = 1.0
        for d in sorted_dates:
            if d in bench_map:
                first_bench = bench_map[d]
                break

        result: list[dict[str, str | float]] = []
        for d in sorted_dates:
            v = combined[d]
            b = bench_map.get(d, first_bench)
            portfolio_indexed = (v / base_val * 100) if base_val > 0 else 100.0
            benchmark_indexed = (
                (b / first_bench * 100) if first_bench > 0 else 100.0
            )
            result.append(
                {
                    "date": d,
                    "value": round(v, 2),
                    "cost_basis": round(cost_basis_total, 2),
                    "portfolio_indexed": round(portfolio_indexed, 2),
                    "benchmark_indexed": round(benchmark_indexed, 2),
                }
            )

        async with self:
            self.portfolio_history = result
            self.benchmark_history = bench
            self.loading = False
            self.status_message = "Portfolio history ready"
            self.last_updated = datetime.utcnow().strftime(
                "%b %d, %Y %H:%M UTC"
            )

    @rx.event
    def set_range(self, r: str):
        self.range_selection = r

    @rx.event
    def set_discover_query(self, q: str):
        self.discover_query = q

    @rx.event
    def clear_error(self):
        self.error_message = ""
