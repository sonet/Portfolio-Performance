import reflex as rx
import logging
from datetime import datetime
from typing import TypedDict


class Transaction(TypedDict):
    id: str
    date: str
    type: str
    symbol: str
    quantity: float
    price: float
    fees: float
    total: float
    notes: str
    source: str


TRANSACTION_TYPES: list[str] = [
    "Buy",
    "Sell",
    "Dividend",
    "Deposit",
    "Withdrawal",
]


class TransactionState(rx.State):
    transactions: list[Transaction] = [
        {
            "id": "t1",
            "date": "2024-11-14",
            "type": "Buy",
            "symbol": "NVDA",
            "quantity": 4.0,
            "price": 492.15,
            "fees": 1.99,
            "total": 1970.59,
            "notes": "Added to core position",
            "source": "API",
        },
        {
            "id": "t2",
            "date": "2024-11-13",
            "type": "Dividend",
            "symbol": "VOO",
            "quantity": 0.0,
            "price": 0.0,
            "fees": 0.0,
            "total": 84.20,
            "notes": "Q4 distribution",
            "source": "API",
        },
        {
            "id": "t3",
            "date": "2024-11-12",
            "type": "Sell",
            "symbol": "TLT",
            "quantity": 5.0,
            "price": 93.10,
            "fees": 1.99,
            "total": 463.51,
            "notes": "Trimmed exposure",
            "source": "Manual",
        },
        {
            "id": "t4",
            "date": "2024-11-10",
            "type": "Buy",
            "symbol": "BTC",
            "quantity": 0.05,
            "price": 65200.00,
            "fees": 12.50,
            "total": 3272.50,
            "notes": "DCA entry",
            "source": "CSV",
        },
        {
            "id": "t5",
            "date": "2024-11-05",
            "type": "Buy",
            "symbol": "AAPL",
            "quantity": 5.0,
            "price": 185.30,
            "fees": 1.99,
            "total": 928.49,
            "notes": "",
            "source": "API",
        },
        {
            "id": "t6",
            "date": "2024-10-28",
            "type": "Deposit",
            "symbol": "USD",
            "quantity": 2500.0,
            "price": 1.0,
            "fees": 0.0,
            "total": 2500.0,
            "notes": "Monthly contribution",
            "source": "Manual",
        },
        {
            "id": "t7",
            "date": "2024-10-22",
            "type": "Buy",
            "symbol": "MSFT",
            "quantity": 3.0,
            "price": 415.00,
            "fees": 1.99,
            "total": 1246.99,
            "notes": "",
            "source": "API",
        },
        {
            "id": "t8",
            "date": "2024-10-15",
            "type": "Sell",
            "symbol": "QQQ",
            "quantity": 2.0,
            "price": 421.50,
            "fees": 1.99,
            "total": 841.01,
            "notes": "Rebalance",
            "source": "Manual",
        },
    ]

    filter_type: str = "All"
    filter_symbol: str = ""
    filter_source: str = "All"
    show_add_form: bool = False
    form_error: str = ""

    @rx.var
    def sorted_transactions(self) -> list[Transaction]:
        return sorted(self.transactions, key=lambda t: t["date"], reverse=True)

    @rx.var
    def filtered_transactions(self) -> list[Transaction]:
        result = self.sorted_transactions
        if self.filter_type != "All":
            result = [t for t in result if t["type"] == self.filter_type]
        if self.filter_source != "All":
            result = [t for t in result if t["source"] == self.filter_source]
        q = self.filter_symbol.strip().upper()
        if q:
            result = [t for t in result if q in t["symbol"].upper()]
        return result

    @rx.var
    def total_buys(self) -> float:
        return sum(t["total"] for t in self.transactions if t["type"] == "Buy")

    @rx.var
    def total_sells(self) -> float:
        return sum(t["total"] for t in self.transactions if t["type"] == "Sell")

    @rx.var
    def total_dividends(self) -> float:
        return sum(
            t["total"] for t in self.transactions if t["type"] == "Dividend"
        )

    @rx.var
    def total_fees(self) -> float:
        return sum(t["fees"] for t in self.transactions)

    @rx.var
    def net_invested(self) -> float:
        return self.total_buys - self.total_sells

    @rx.var
    def transaction_count(self) -> int:
        return len(self.transactions)

    @rx.event
    def set_filter_type(self, v: str):
        self.filter_type = v

    @rx.event
    def set_filter_source(self, v: str):
        self.filter_source = v

    @rx.event
    def set_filter_symbol(self, v: str):
        self.filter_symbol = v

    @rx.event
    def toggle_add_form(self):
        self.show_add_form = not self.show_add_form
        self.form_error = ""

    @rx.event
    async def add_transaction(self, form_data: dict):
        try:
            symbol = str(form_data.get("symbol", "")).upper().strip()
            ttype = str(form_data.get("type", "Buy"))
            quantity = float(form_data.get("quantity", 0) or 0)
            price = float(form_data.get("price", 0) or 0)
            fees = float(form_data.get("fees", 0) or 0)
            date = str(
                form_data.get("date", datetime.utcnow().date().isoformat())
            )
            notes = str(form_data.get("notes", ""))

            if not symbol:
                self.form_error = "Symbol is required"
                return
            if ttype in ("Buy", "Sell") and (quantity <= 0 or price <= 0):
                self.form_error = "Quantity and price must be greater than 0"
                return
            if not date:
                self.form_error = "Transaction date is required"
                return

            total = quantity * price + fees
            if ttype == "Sell":
                total = quantity * price - fees
            elif ttype in ("Dividend", "Deposit", "Withdrawal"):
                total = float(
                    form_data.get("total", quantity * max(price, 1))
                    or (quantity * max(price, 1))
                )

            new_id = f"t{len(self.transactions) + 1}_{datetime.utcnow().timestamp():.0f}"
            new_tx: Transaction = {
                "id": new_id,
                "date": date,
                "type": ttype,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "fees": fees,
                "total": round(total, 2),
                "notes": notes,
                "source": "Manual",
            }
            self.transactions.append(new_tx)
            self.form_error = ""
            self.show_add_form = False

            # Portfolio impact
            from app.states.portfolio_state import PortfolioState

            port = await self.get_state(PortfolioState)
            self._apply_to_portfolio(new_tx, port)
        except (ValueError, TypeError) as e:
            logging.exception(f"Error adding transaction: {e}")
            self.form_error = "Invalid input values"

    def _apply_to_portfolio(self, tx: Transaction, port) -> None:
        sym = tx["symbol"]
        if tx["type"] == "Buy":
            existing = None
            for h in port.holdings:
                if h["symbol"].upper() == sym:
                    existing = h
                    break
            if existing:
                new_qty = existing["quantity"] + tx["quantity"]
                if new_qty > 0:
                    new_cost = (
                        existing["quantity"] * existing["cost_basis"]
                        + tx["quantity"] * tx["price"]
                    ) / new_qty
                else:
                    new_cost = existing["cost_basis"]
                for i, h in enumerate(port.holdings):
                    if h["id"] == existing["id"]:
                        port.holdings[i] = {
                            **h,
                            "quantity": round(new_qty, 6),
                            "cost_basis": round(new_cost, 4),
                            "current_price": tx["price"],
                        }
                        break
            else:
                new_id = str(
                    max(
                        (
                            int(h["id"])
                            for h in port.holdings
                            if h["id"].isdigit()
                        ),
                        default=0,
                    )
                    + 1
                )
                port.holdings.append(
                    {
                        "id": new_id,
                        "symbol": sym,
                        "name": sym,
                        "asset_class": "Equity",
                        "quantity": tx["quantity"],
                        "cost_basis": tx["price"],
                        "current_price": tx["price"],
                        "prev_close": tx["price"],
                    }
                )
        elif tx["type"] == "Sell":
            for i, h in enumerate(port.holdings):
                if h["symbol"].upper() == sym:
                    new_qty = max(h["quantity"] - tx["quantity"], 0)
                    port.holdings[i] = {**h, "quantity": round(new_qty, 6)}
                    break

    @rx.event
    def delete_transaction(self, tid: str):
        self.transactions = [t for t in self.transactions if t["id"] != tid]

    @rx.event
    def import_from_csv(self, rows: list[dict]):
        added = 0
        for row in rows:
            try:
                new_id = f"csv_{len(self.transactions) + 1}_{datetime.utcnow().timestamp():.0f}_{added}"
                qty = float(row.get("quantity", 0) or 0)
                price = float(row.get("price", 0) or 0)
                fees = float(row.get("fees", 0) or 0)
                ttype = str(row.get("type", "Buy")).title()
                if ttype not in TRANSACTION_TYPES:
                    ttype = "Buy"
                total = (
                    qty * price + fees if ttype == "Buy" else qty * price - fees
                )
                self.transactions.append(
                    {
                        "id": new_id,
                        "date": str(
                            row.get(
                                "date", datetime.utcnow().date().isoformat()
                            )
                        ),
                        "type": ttype,
                        "symbol": str(row.get("symbol", "")).upper(),
                        "quantity": qty,
                        "price": price,
                        "fees": fees,
                        "total": round(total, 2),
                        "notes": str(row.get("notes", "")),
                        "source": "CSV",
                    }
                )
                added += 1
            except (ValueError, TypeError) as e:
                logging.exception(f"CSV row import failed: {e}")
                continue
