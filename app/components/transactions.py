import reflex as rx
from app.states.transaction_state import TransactionState, TRANSACTION_TYPES


def _kpi(
    label: str, value: rx.Component, sub: str, icon: str, tone: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-[11px] font-medium text-slate-500 uppercase tracking-wide",
                ),
                value,
                rx.el.p(sub, class_name="text-xs text-slate-500"),
                class_name="flex flex-col gap-1",
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-4 w-4"),
                class_name=f"h-9 w-9 rounded-lg flex items-center justify-center {tone}",
            ),
            class_name="flex items-start justify-between",
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-4",
    )


def _type_badge(t: rx.Var) -> rx.Component:
    return rx.match(
        t,
        (
            "Buy",
            rx.el.span(
                "Buy",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 w-fit",
            ),
        ),
        (
            "Sell",
            rx.el.span(
                "Sell",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-rose-500/15 text-rose-300 border border-rose-500/30 w-fit",
            ),
        ),
        (
            "Dividend",
            rx.el.span(
                "Dividend",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 w-fit",
            ),
        ),
        (
            "Deposit",
            rx.el.span(
                "Deposit",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-violet-500/15 text-violet-300 border border-violet-500/30 w-fit",
            ),
        ),
        (
            "Withdrawal",
            rx.el.span(
                "Withdrawal",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-amber-500/15 text-amber-300 border border-amber-500/30 w-fit",
            ),
        ),
        rx.el.span(
            t,
            class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 w-fit",
        ),
    )


def _source_badge(s: rx.Var) -> rx.Component:
    return rx.el.span(
        s,
        class_name="text-[10px] font-medium px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 w-fit",
    )


def _filter_pill(name: str, current: rx.Var, on_click) -> rx.Component:
    return rx.el.button(
        name,
        on_click=on_click,
        class_name=rx.cond(
            current == name,
            "px-3 py-1.5 rounded-lg text-xs font-medium bg-violet-600 text-white border border-violet-500 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
            "px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900/60 text-slate-300 border border-slate-700 hover:border-violet-500/50",
        ),
        type="button",
    )


def _add_form() -> rx.Component:
    input_cn = "w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100 placeholder:text-slate-600"
    label_cn = "text-xs font-medium text-slate-300 mb-1 block"
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label("Date", class_name=label_cn),
                    rx.el.input(
                        type="date",
                        name="date",
                        required=True,
                        class_name=input_cn,
                    ),
                ),
                rx.el.div(
                    rx.el.label("Type", class_name=label_cn),
                    rx.el.select(
                        rx.foreach(
                            TRANSACTION_TYPES,
                            lambda t: rx.el.option(t, value=t),
                        ),
                        name="type",
                        class_name=input_cn + " appearance-none",
                    ),
                ),
                rx.el.div(
                    rx.el.label("Symbol", class_name=label_cn),
                    rx.el.input(
                        name="symbol",
                        placeholder="AAPL",
                        required=True,
                        class_name=input_cn,
                    ),
                ),
                rx.el.div(
                    rx.el.label("Quantity", class_name=label_cn),
                    rx.el.input(
                        type="number",
                        step="0.0001",
                        name="quantity",
                        placeholder="0",
                        class_name=input_cn,
                    ),
                ),
                rx.el.div(
                    rx.el.label("Price", class_name=label_cn),
                    rx.el.input(
                        type="number",
                        step="0.01",
                        name="price",
                        placeholder="0.00",
                        class_name=input_cn,
                    ),
                ),
                rx.el.div(
                    rx.el.label("Fees", class_name=label_cn),
                    rx.el.input(
                        type="number",
                        step="0.01",
                        name="fees",
                        default_value="0",
                        placeholder="0.00",
                        class_name=input_cn,
                    ),
                ),
                rx.el.div(
                    rx.el.label("Notes", class_name=label_cn),
                    rx.el.input(
                        name="notes",
                        placeholder="Optional",
                        class_name=input_cn,
                    ),
                    class_name="sm:col-span-2 lg:col-span-3",
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4",
            ),
            rx.cond(
                TransactionState.form_error != "",
                rx.el.div(
                    rx.icon(
                        "circle-alert",
                        class_name="h-3.5 w-3.5 text-rose-400",
                    ),
                    rx.el.p(
                        TransactionState.form_error,
                        class_name="text-xs font-medium text-rose-300",
                    ),
                    class_name="flex items-center gap-2 mb-3 px-3 py-2 bg-rose-500/10 border border-rose-500/30 rounded-lg",
                ),
                rx.el.div(),
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    type="button",
                    on_click=TransactionState.toggle_add_form,
                    class_name="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-800",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add Transaction",
                    type="submit",
                    class_name="px-4 py-2 text-sm font-medium text-white bg-violet-600 border border-violet-500 rounded-lg hover:bg-violet-500 flex items-center gap-1.5 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            on_submit=TransactionState.add_transaction,
            reset_on_submit=True,
        ),
        class_name="bg-violet-500/5 border border-violet-500/30 rounded-xl p-4 mb-4",
    )


def _tx_row(t: rx.Var) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.p(
                t["date"],
                class_name="text-xs font-mono text-slate-300",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(_type_badge(t["type"]), class_name="px-4 py-3"),
        rx.el.td(
            rx.el.a(
                rx.el.p(
                    t["symbol"],
                    class_name="text-sm font-semibold text-slate-100 hover:text-violet-300",
                ),
                href=f"/asset/{t['symbol']}",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            rx.el.p(
                f"{t['quantity'].to(float):,.4f}",
                class_name="text-sm text-slate-100 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${t['price'].to(float):,.2f}",
                class_name="text-sm text-slate-100 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${t['fees'].to(float):,.2f}",
                class_name="text-xs text-slate-500 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${t['total'].to(float):,.2f}",
                class_name="text-sm font-semibold text-slate-100 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(_source_badge(t["source"]), class_name="px-4 py-3"),
        rx.el.td(
            rx.el.p(
                t["notes"],
                class_name="text-xs text-slate-500 truncate max-w-[180px]",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                on_click=lambda: TransactionState.delete_transaction(
                    t["id"].to(str)
                ),
                class_name="p-1.5 rounded-md text-slate-400 hover:bg-rose-500/15 hover:text-rose-300 border border-transparent hover:border-rose-500/30",
                type="button",
            ),
            class_name="px-4 py-3 text-right",
        ),
        class_name="border-b border-slate-800/60 hover:bg-slate-800/40 transition-colors",
    )


def transactions_content() -> rx.Component:
    th_cn = "px-4 py-3 text-left text-[11px] font-semibold text-slate-400 uppercase tracking-wider"
    th_r_cn = "px-4 py-3 text-right text-[11px] font-semibold text-slate-400 uppercase tracking-wider"
    return rx.el.div(
        rx.el.div(
            _kpi(
                "Total Transactions",
                rx.el.p(
                    TransactionState.transaction_count.to_string(),
                    class_name="text-xl font-semibold text-slate-100",
                ),
                "All-time entries",
                "list",
                "bg-slate-800 text-slate-300 border border-slate-700",
            ),
            _kpi(
                "Net Invested",
                rx.el.p(
                    f"${TransactionState.net_invested:,.2f}",
                    class_name="text-xl font-semibold text-slate-100",
                ),
                "Buys minus sells",
                "arrow-down-up",
                "bg-violet-500/15 text-violet-300 border border-violet-500/30",
            ),
            _kpi(
                "Dividends",
                rx.el.p(
                    f"${TransactionState.total_dividends:,.2f}",
                    class_name="text-xl font-semibold text-emerald-400",
                ),
                "Total received",
                "coins",
                "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
            ),
            _kpi(
                "Fees Paid",
                rx.el.p(
                    f"${TransactionState.total_fees:,.2f}",
                    class_name="text-xl font-semibold text-amber-400",
                ),
                "Trading costs",
                "receipt",
                "bg-amber-500/15 text-amber-300 border border-amber-500/30",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2",
                    ),
                    rx.el.input(
                        placeholder="Filter by symbol…",
                        default_value=TransactionState.filter_symbol,
                        on_change=TransactionState.set_filter_symbol.debounce(
                            300
                        ),
                        class_name="w-full pl-9 pr-3 py-2 text-sm bg-slate-900/60 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100 placeholder:text-slate-500",
                    ),
                    class_name="relative flex-1 max-w-xs",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add Transaction",
                    on_click=TransactionState.toggle_add_form,
                    class_name="px-3 py-2 text-sm font-medium text-white bg-violet-600 rounded-lg hover:bg-violet-500 flex items-center gap-1.5 shrink-0 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
                    type="button",
                ),
                class_name="flex items-center gap-3 mb-3 flex-wrap",
            ),
            rx.el.div(
                rx.el.p(
                    "Type:",
                    class_name="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-1 self-center",
                ),
                _filter_pill(
                    "All",
                    TransactionState.filter_type,
                    lambda: TransactionState.set_filter_type("All"),
                ),
                rx.foreach(
                    TRANSACTION_TYPES,
                    lambda t: _filter_pill(
                        t,
                        TransactionState.filter_type,
                        lambda: TransactionState.set_filter_type(t),
                    ),
                ),
                class_name="flex items-center gap-2 flex-wrap mb-2",
            ),
            rx.el.div(
                rx.el.p(
                    "Source:",
                    class_name="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-1 self-center",
                ),
                _filter_pill(
                    "All",
                    TransactionState.filter_source,
                    lambda: TransactionState.set_filter_source("All"),
                ),
                _filter_pill(
                    "API",
                    TransactionState.filter_source,
                    lambda: TransactionState.set_filter_source("API"),
                ),
                _filter_pill(
                    "Manual",
                    TransactionState.filter_source,
                    lambda: TransactionState.set_filter_source("Manual"),
                ),
                _filter_pill(
                    "CSV",
                    TransactionState.filter_source,
                    lambda: TransactionState.set_filter_source("CSV"),
                ),
                class_name="flex items-center gap-2 flex-wrap",
            ),
            class_name="mb-4",
        ),
        rx.cond(TransactionState.show_add_form, _add_form(), rx.el.div()),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Date", class_name=th_cn),
                            rx.el.th("Type", class_name=th_cn),
                            rx.el.th("Symbol", class_name=th_cn),
                            rx.el.th("Quantity", class_name=th_r_cn),
                            rx.el.th("Price", class_name=th_r_cn),
                            rx.el.th("Fees", class_name=th_r_cn),
                            rx.el.th("Total", class_name=th_r_cn),
                            rx.el.th("Source", class_name=th_cn),
                            rx.el.th("Notes", class_name=th_cn),
                            rx.el.th("", class_name="px-4 py-3"),
                            class_name="bg-slate-900/80 border-b border-slate-800",
                        ),
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            TransactionState.filtered_transactions, _tx_row
                        ),
                    ),
                    class_name="table-auto min-w-full",
                ),
                class_name="overflow-x-auto",
            ),
            rx.cond(
                TransactionState.filtered_transactions.length() == 0,
                rx.el.div(
                    rx.icon(
                        "receipt", class_name="h-8 w-8 text-slate-600 mb-2"
                    ),
                    rx.el.p(
                        "No transactions match your filters",
                        class_name="text-sm font-medium text-slate-300",
                    ),
                    rx.el.p(
                        "Try adjusting or add a new transaction",
                        class_name="text-xs text-slate-500 mt-1",
                    ),
                    class_name="flex flex-col items-center justify-center py-16",
                ),
                rx.el.div(),
            ),
            class_name="bg-slate-900/40 backdrop-blur-sm border border-slate-800/80 rounded-xl overflow-hidden",
        ),
        class_name="flex flex-col",
    )
