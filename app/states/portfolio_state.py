import reflex as rx
from typing import TypedDict


class Holding(TypedDict):
    id: str
    symbol: str
    name: str
    asset_class: str
    quantity: float
    cost_basis: float
    current_price: float
    prev_close: float


ASSET_CLASSES: list[str] = ["Equity", "ETF", "Crypto", "Bond", "Cash"]


class PortfolioState(rx.State):
    holdings: list[Holding] = [
        {
            "id": "1",
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "asset_class": "Equity",
            "quantity": 25.0,
            "cost_basis": 152.30,
            "current_price": 189.45,
            "prev_close": 187.12,
        },
        {
            "id": "2",
            "symbol": "MSFT",
            "name": "Microsoft Corp.",
            "asset_class": "Equity",
            "quantity": 18.0,
            "cost_basis": 289.10,
            "current_price": 412.68,
            "prev_close": 415.22,
        },
        {
            "id": "3",
            "symbol": "NVDA",
            "name": "NVIDIA Corp.",
            "asset_class": "Equity",
            "quantity": 12.0,
            "cost_basis": 245.80,
            "current_price": 495.30,
            "prev_close": 488.71,
        },
        {
            "id": "4",
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "asset_class": "Equity",
            "quantity": 15.0,
            "cost_basis": 118.45,
            "current_price": 156.22,
            "prev_close": 158.03,
        },
        {
            "id": "5",
            "symbol": "AMZN",
            "name": "Amazon.com Inc.",
            "asset_class": "Equity",
            "quantity": 20.0,
            "cost_basis": 128.90,
            "current_price": 178.55,
            "prev_close": 175.90,
        },
        {
            "id": "6",
            "symbol": "VOO",
            "name": "Vanguard S&P 500 ETF",
            "asset_class": "ETF",
            "quantity": 30.0,
            "cost_basis": 380.15,
            "current_price": 458.72,
            "prev_close": 456.10,
        },
        {
            "id": "7",
            "symbol": "QQQ",
            "name": "Invesco QQQ Trust",
            "asset_class": "ETF",
            "quantity": 22.0,
            "cost_basis": 340.25,
            "current_price": 425.88,
            "prev_close": 423.15,
        },
        {
            "id": "8",
            "symbol": "BTC",
            "name": "Bitcoin",
            "asset_class": "Crypto",
            "quantity": 0.35,
            "cost_basis": 32500.00,
            "current_price": 67420.00,
            "prev_close": 66850.00,
        },
        {
            "id": "9",
            "symbol": "ETH",
            "name": "Ethereum",
            "asset_class": "Crypto",
            "quantity": 3.2,
            "cost_basis": 1850.00,
            "current_price": 3520.00,
            "prev_close": 3480.00,
        },
        {
            "id": "10",
            "symbol": "BND",
            "name": "Vanguard Total Bond ETF",
            "asset_class": "Bond",
            "quantity": 40.0,
            "cost_basis": 78.20,
            "current_price": 74.15,
            "prev_close": 74.02,
        },
        {
            "id": "11",
            "symbol": "TLT",
            "name": "iShares 20+ Yr Treasury",
            "asset_class": "Bond",
            "quantity": 25.0,
            "cost_basis": 105.40,
            "current_price": 92.30,
            "prev_close": 92.85,
        },
        {
            "id": "12",
            "symbol": "USD",
            "name": "Cash Reserve",
            "asset_class": "Cash",
            "quantity": 8500.0,
            "cost_basis": 1.0,
            "current_price": 1.0,
            "prev_close": 1.0,
        },
    ]

    search_query: str = ""
    filter_class: str = "All"
    show_add_form: bool = False
    editing_id: str = ""
    edit_quantity: float = 0.0
    edit_cost: float = 0.0

    @rx.var
    def total_value(self) -> float:
        return sum(h["quantity"] * h["current_price"] for h in self.holdings)

    @rx.var
    def total_cost(self) -> float:
        return sum(h["quantity"] * h["cost_basis"] for h in self.holdings)

    @rx.var
    def total_gain(self) -> float:
        return self.total_value - self.total_cost

    @rx.var
    def total_gain_pct(self) -> float:
        return (
            (self.total_gain / self.total_cost * 100)
            if self.total_cost > 0
            else 0.0
        )

    @rx.var
    def daily_change(self) -> float:
        return sum(
            h["quantity"] * (h["current_price"] - h["prev_close"])
            for h in self.holdings
        )

    @rx.var
    def daily_change_pct(self) -> float:
        prev_total = sum(h["quantity"] * h["prev_close"] for h in self.holdings)
        return (self.daily_change / prev_total * 100) if prev_total > 0 else 0.0

    @rx.var
    def holdings_count(self) -> int:
        return len(self.holdings)

    @rx.var
    def enriched_holdings(self) -> list[dict[str, str | float | int | bool]]:
        total = self.total_value if self.total_value > 0 else 1.0
        result: list[dict[str, str | float | int | bool]] = []
        for h in self.holdings:
            market_value = h["quantity"] * h["current_price"]
            cost = h["quantity"] * h["cost_basis"]
            gain = market_value - cost
            gain_pct = (gain / cost * 100) if cost > 0 else 0.0
            day_change = h["quantity"] * (h["current_price"] - h["prev_close"])
            day_pct = (
                ((h["current_price"] - h["prev_close"]) / h["prev_close"] * 100)
                if h["prev_close"] > 0
                else 0.0
            )
            allocation = market_value / total * 100
            result.append(
                {
                    "id": h["id"],
                    "symbol": h["symbol"],
                    "name": h["name"],
                    "asset_class": h["asset_class"],
                    "quantity": h["quantity"],
                    "cost_basis": h["cost_basis"],
                    "current_price": h["current_price"],
                    "market_value": market_value,
                    "gain": gain,
                    "gain_pct": gain_pct,
                    "day_change": day_change,
                    "day_pct": day_pct,
                    "allocation": allocation,
                    "is_gain": gain >= 0,
                    "is_day_gain": day_change >= 0,
                }
            )
        return result

    @rx.var
    def filtered_holdings(self) -> list[dict[str, str | float | int | bool]]:
        q = self.search_query.lower()
        result = self.enriched_holdings
        if self.filter_class != "All":
            result = [
                h for h in result if h["asset_class"] == self.filter_class
            ]
        if q:
            result = [
                h
                for h in result
                if q in str(h["symbol"]).lower() or q in str(h["name"]).lower()
            ]
        return result

    @rx.var
    def allocation_by_class(self) -> list[dict[str, str | float]]:
        totals: dict[str, float] = {}
        for h in self.holdings:
            mv = h["quantity"] * h["current_price"]
            totals[h["asset_class"]] = totals.get(h["asset_class"], 0.0) + mv
        total = self.total_value if self.total_value > 0 else 1.0
        colors = {
            "Equity": "#2563eb",
            "ETF": "#0ea5e9",
            "Crypto": "#f59e0b",
            "Bond": "#10b981",
            "Cash": "#64748b",
        }
        return [
            {
                "name": k,
                "value": round(v, 2),
                "pct": round(v / total * 100, 2),
                "fill": colors.get(k, "#94a3b8"),
            }
            for k, v in sorted(totals.items(), key=lambda x: -x[1])
        ]

    @rx.var
    def top_movers(self) -> list[dict[str, str | float | bool]]:
        sorted_h = sorted(
            self.enriched_holdings,
            key=lambda h: abs(float(h["day_pct"])),
            reverse=True,
        )
        return sorted_h[:5]

    @rx.var
    def recent_activity(self) -> list[dict[str, str]]:
        return [
            {
                "type": "Buy",
                "symbol": "NVDA",
                "detail": "Added 4 shares @ $492.15",
                "time": "2h ago",
                "icon": "trending-up",
            },
            {
                "type": "Dividend",
                "symbol": "VOO",
                "detail": "Received $84.20 dividend",
                "time": "1d ago",
                "icon": "dollar-sign",
            },
            {
                "type": "Sell",
                "symbol": "TLT",
                "detail": "Sold 5 shares @ $93.10",
                "time": "2d ago",
                "icon": "trending-down",
            },
            {
                "type": "Buy",
                "symbol": "BTC",
                "detail": "Added 0.05 BTC @ $65,200",
                "time": "4d ago",
                "icon": "trending-up",
            },
            {
                "type": "Rebalance",
                "symbol": "Portfolio",
                "detail": "Auto-rebalanced allocations",
                "time": "1w ago",
                "icon": "refresh-cw",
            },
        ]

    @rx.event
    def set_search(self, q: str):
        self.search_query = q

    @rx.event
    def set_filter_class(self, c: str):
        self.filter_class = c

    @rx.event
    def toggle_add_form(self):
        self.show_add_form = not self.show_add_form

    @rx.event
    def start_edit(self, hid: str):
        self.editing_id = hid
        for h in self.holdings:
            if h["id"] == hid:
                self.edit_quantity = h["quantity"]
                self.edit_cost = h["cost_basis"]
                break

    @rx.event
    def cancel_edit(self):
        self.editing_id = ""

    @rx.event
    def set_edit_quantity(self, v: str):
        try:
            self.edit_quantity = float(v)
        except ValueError:
            self.edit_quantity = 0.0

    @rx.event
    def set_edit_cost(self, v: str):
        try:
            self.edit_cost = float(v)
        except ValueError:
            self.edit_cost = 0.0

    @rx.event
    def save_edit(self):
        for i, h in enumerate(self.holdings):
            if h["id"] == self.editing_id:
                self.holdings[i] = {
                    **h,
                    "quantity": self.edit_quantity,
                    "cost_basis": self.edit_cost,
                }
                break
        self.editing_id = ""

    @rx.event
    def delete_holding(self, hid: str):
        self.holdings = [h for h in self.holdings if h["id"] != hid]

    @rx.event
    def add_holding(self, form_data: dict):
        try:
            new_id = str(
                max((int(h["id"]) for h in self.holdings), default=0) + 1
            )
            price = float(form_data.get("price", 0) or 0)
            new: Holding = {
                "id": new_id,
                "symbol": str(form_data.get("symbol", "")).upper(),
                "name": str(form_data.get("name", "")),
                "asset_class": str(form_data.get("asset_class", "Equity")),
                "quantity": float(form_data.get("quantity", 0) or 0),
                "cost_basis": float(form_data.get("cost_basis", 0) or 0),
                "current_price": price,
                "prev_close": price,
            }
            if new["symbol"] and new["quantity"] > 0:
                self.holdings.append(new)
            self.show_add_form = False
        except (ValueError, TypeError):
            self.show_add_form = False
