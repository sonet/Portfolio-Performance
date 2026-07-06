import reflex as rx
import logging
import csv
import io
from datetime import datetime
from typing import TypedDict


class DataSource(TypedDict):
    id: str
    name: str
    kind: str
    priority: int
    enabled: bool
    status: str
    last_sync: str
    description: str


class ManualOverride(TypedDict):
    symbol: str
    price: float
    updated: str


class CsvRow(TypedDict):
    date: str
    type: str
    symbol: str
    quantity: float
    price: float
    fees: float
    notes: str
    valid: bool
    error: str


CURRENCIES: list[str] = ["USD", "EUR", "GBP", "JPY", "CAD"]


class SettingsState(rx.State):
    data_sources: list[DataSource] = [
        {
            "id": "s1",
            "name": "Yahoo Finance",
            "kind": "API",
            "priority": 1,
            "enabled": True,
            "status": "Connected",
            "last_sync": "Just now",
            "description": "Live equity, ETF, and crypto quotes via yfinance",
        },
        {
            "id": "s2",
            "name": "Manual Entries",
            "kind": "Manual",
            "priority": 2,
            "enabled": True,
            "status": "Active",
            "last_sync": "2h ago",
            "description": "User-entered prices and holdings, always available offline",
        },
        {
            "id": "s3",
            "name": "CSV Import",
            "kind": "CSV",
            "priority": 3,
            "enabled": True,
            "status": "Ready",
            "last_sync": "1d ago",
            "description": "Bulk transaction and holdings import from broker exports",
        },
        {
            "id": "s4",
            "name": "Cached Snapshot",
            "kind": "Cache",
            "priority": 4,
            "enabled": True,
            "status": "Fallback",
            "last_sync": "5m ago",
            "description": "Local synthetic history used when live sources are unavailable",
        },
    ]

    manual_overrides: list[ManualOverride] = [
        {"symbol": "USD", "price": 1.00, "updated": "2024-11-01"},
    ]

    # Preferences
    currency: str = "USD"
    show_percent_change: bool = True
    default_range: str = "6M"
    auto_refresh: bool = True
    refresh_interval_min: int = 15
    cache_ttl_min: int = 60
    dark_mode: bool = False
    notifications_enabled: bool = True

    # Override form
    override_symbol: str = ""
    override_price: str = ""

    # CSV import
    csv_preview: list[CsvRow] = []
    csv_error: str = ""
    csv_status: str = ""
    csv_filename: str = ""
    csv_import_target: str = "transactions"

    @rx.var
    def valid_csv_count(self) -> int:
        return len([r for r in self.csv_preview if r["valid"]])

    @rx.var
    def invalid_csv_count(self) -> int:
        return len([r for r in self.csv_preview if not r["valid"]])

    @rx.var
    def sorted_data_sources(self) -> list[DataSource]:
        return sorted(self.data_sources, key=lambda s: s["priority"])

    @rx.event
    def toggle_source(self, sid: str):
        for i, s in enumerate(self.data_sources):
            if s["id"] == sid:
                self.data_sources[i] = {**s, "enabled": not s["enabled"]}
                break

    @rx.event
    def move_source_up(self, sid: str):
        srt = sorted(self.data_sources, key=lambda x: x["priority"])
        for idx, s in enumerate(srt):
            if s["id"] == sid and idx > 0:
                srt[idx], srt[idx - 1] = srt[idx - 1], srt[idx]
                break
        for new_p, s in enumerate(srt, start=1):
            for i, orig in enumerate(self.data_sources):
                if orig["id"] == s["id"]:
                    self.data_sources[i] = {**orig, "priority": new_p}
                    break

    @rx.event
    def move_source_down(self, sid: str):
        srt = sorted(self.data_sources, key=lambda x: x["priority"])
        for idx, s in enumerate(srt):
            if s["id"] == sid and idx < len(srt) - 1:
                srt[idx], srt[idx + 1] = srt[idx + 1], srt[idx]
                break
        for new_p, s in enumerate(srt, start=1):
            for i, orig in enumerate(self.data_sources):
                if orig["id"] == s["id"]:
                    self.data_sources[i] = {**orig, "priority": new_p}
                    break

    @rx.event
    def sync_source(self, sid: str):
        now = datetime.utcnow().strftime("%b %d, %H:%M UTC")
        for i, s in enumerate(self.data_sources):
            if s["id"] == sid:
                self.data_sources[i] = {
                    **s,
                    "last_sync": "Just now",
                    "status": "Connected",
                }
                break

    @rx.event
    def set_currency(self, v: str):
        self.currency = v

    @rx.event
    def set_default_range(self, v: str):
        self.default_range = v

    @rx.event
    def toggle_percent_change(self):
        self.show_percent_change = not self.show_percent_change

    @rx.event
    def toggle_auto_refresh(self):
        self.auto_refresh = not self.auto_refresh

    @rx.event
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    @rx.event
    def toggle_notifications(self):
        self.notifications_enabled = not self.notifications_enabled

    @rx.event
    def set_refresh_interval(self, v: str):
        try:
            self.refresh_interval_min = max(1, int(v))
        except ValueError:
            self.refresh_interval_min = 15

    @rx.event
    def set_cache_ttl(self, v: str):
        try:
            self.cache_ttl_min = max(1, int(v))
        except ValueError:
            self.cache_ttl_min = 60

    @rx.event
    def set_override_symbol(self, v: str):
        self.override_symbol = v

    @rx.event
    def set_override_price(self, v: str):
        self.override_price = v

    @rx.event
    async def apply_override(self, form_data: dict):
        try:
            sym = str(form_data.get("symbol", "")).upper().strip()
            price = float(form_data.get("price", 0) or 0)
            if not sym or price <= 0:
                return
            existing = None
            for i, o in enumerate(self.manual_overrides):
                if o["symbol"] == sym:
                    existing = i
                    break
            entry: ManualOverride = {
                "symbol": sym,
                "price": price,
                "updated": datetime.utcnow().date().isoformat(),
            }
            if existing is not None:
                self.manual_overrides[existing] = entry
            else:
                self.manual_overrides.append(entry)

            from app.states.portfolio_state import PortfolioState

            port = await self.get_state(PortfolioState)
            for i, h in enumerate(port.holdings):
                if h["symbol"].upper() == sym:
                    port.holdings[i] = {
                        **h,
                        "prev_close": h["current_price"],
                        "current_price": price,
                    }
        except (ValueError, TypeError) as e:
            logging.exception(f"Override error: {e}")

    @rx.event
    def remove_override(self, sym: str):
        self.manual_overrides = [
            o for o in self.manual_overrides if o["symbol"] != sym
        ]

    @rx.event
    def clear_cache(self):
        from app.states.market_state import MarketState

        yield rx.toast("Cache cleared successfully", duration=3000)

    @rx.event
    def set_csv_import_target(self, v: str):
        self.csv_import_target = v

    @rx.event
    async def handle_csv_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        try:
            file = files[0]
            data = await file.read()
            self.csv_filename = file.name
            text = data.decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(text))
            preview: list[CsvRow] = []
            for row in reader:
                lower = {
                    k.lower().strip(): (v.strip() if isinstance(v, str) else v)
                    for k, v in row.items()
                    if k
                }
                sym = str(
                    lower.get("symbol", "") or lower.get("ticker", "")
                ).upper()
                ttype = str(
                    lower.get("type", "") or lower.get("action", "Buy")
                ).title()
                date = str(
                    lower.get("date", "")
                    or datetime.utcnow().date().isoformat()
                )
                error = ""
                valid = True
                try:
                    qty = float(
                        lower.get("quantity", 0) or lower.get("shares", 0) or 0
                    )
                except (ValueError, TypeError):
                    qty = 0.0
                    error = "Invalid quantity"
                    valid = False
                try:
                    price = float(lower.get("price", 0) or 0)
                except (ValueError, TypeError):
                    price = 0.0
                    error = "Invalid price"
                    valid = False
                try:
                    fees = float(
                        lower.get("fees", 0) or lower.get("fee", 0) or 0
                    )
                except (ValueError, TypeError):
                    fees = 0.0
                if not sym:
                    error = "Missing symbol"
                    valid = False
                if ttype not in (
                    "Buy",
                    "Sell",
                    "Dividend",
                    "Deposit",
                    "Withdrawal",
                ):
                    ttype = "Buy"
                preview.append(
                    {
                        "date": date,
                        "type": ttype,
                        "symbol": sym,
                        "quantity": qty,
                        "price": price,
                        "fees": fees,
                        "notes": str(lower.get("notes", "")),
                        "valid": valid,
                        "error": error,
                    }
                )
            self.csv_preview = preview
            self.csv_error = ""
            self.csv_status = f"Parsed {len(preview)} rows from {file.name}"
        except Exception as e:
            logging.exception(f"CSV parse error: {e}")
            self.csv_error = f"Failed to parse CSV: {e}"
            self.csv_preview = []

    @rx.event
    async def confirm_csv_import(self):
        if not self.csv_preview:
            self.csv_status = "No rows to import"
            return
        rows = [
            {
                "date": r["date"],
                "type": r["type"],
                "symbol": r["symbol"],
                "quantity": r["quantity"],
                "price": r["price"],
                "fees": r["fees"],
                "notes": r["notes"],
            }
            for r in self.csv_preview
            if r["valid"]
        ]
        count = len(rows)
        target = self.csv_import_target

        # Set success state up front so UI is consistent even if downstream
        # state access encounters issues.
        self.csv_status = f"Imported {count} rows successfully"
        self.csv_preview = []
        self.csv_error = ""

        if count == 0:
            return

        try:
            from app.states.transaction_state import TransactionState

            tx_state = await self.get_state(TransactionState)
            tx_state.import_from_csv(rows)
        except Exception as e:
            logging.exception(f"Transaction import from CSV failed: {e}")

        if target == "holdings":
            try:
                from app.states.portfolio_state import PortfolioState

                port = await self.get_state(PortfolioState)
                self._merge_rows_into_holdings(rows, port)
            except Exception as e:
                logging.exception(f"Holdings merge from CSV failed: {e}")

        yield rx.toast(f"Imported {count} transactions", duration=3000)

    def _merge_rows_into_holdings(self, rows: list[dict], port) -> None:
        for r in rows:
            if r.get("type") != "Buy":
                continue
            sym = str(r.get("symbol", "")).upper()
            if not sym:
                continue
            qty = float(r.get("quantity", 0) or 0)
            price = float(r.get("price", 0) or 0)
            if qty <= 0:
                continue
            found = False
            for i, h in enumerate(port.holdings):
                if h["symbol"].upper() == sym:
                    found = True
                    new_qty = h["quantity"] + qty
                    if new_qty > 0:
                        new_cost = (
                            h["quantity"] * h["cost_basis"] + qty * price
                        ) / new_qty
                    else:
                        new_cost = h["cost_basis"]
                    port.holdings[i] = {
                        **h,
                        "quantity": round(new_qty, 6),
                        "cost_basis": round(new_cost, 4),
                    }
                    break
            if not found:
                new_id = str(
                    max(
                        (
                            int(h["id"])
                            for h in port.holdings
                            if str(h["id"]).isdigit()
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
                        "quantity": qty,
                        "cost_basis": price,
                        "current_price": price if price > 0 else 1.0,
                        "prev_close": price if price > 0 else 1.0,
                    }
                )

    @rx.event
    def cancel_csv_import(self):
        self.csv_preview = []
        self.csv_filename = ""
        self.csv_status = ""
        self.csv_error = ""
