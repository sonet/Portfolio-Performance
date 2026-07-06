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
                    class_name="text-[11px] font-medium text-gray-500 uppercase tracking-wide",
                ),
                value,
                rx.el.p(sub, class_name="text-xs text-gray-500"),
                class_name="flex flex-col gap-1",
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-4 w-4"),
                class_name=f"h-9 w-9 rounded-lg flex items-center justify-center {tone}",
            ),
            class_name="flex items-start justify-between",
        ),
        class_name="bg-white border border-gray-200 rounded-xl p-4",
    )


def _type_badge(t: rx.Var) -> rx.Component:
    return rx.match(
        t,
        (
            "Buy",
            rx.el.span(
                "Buy",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100 w-fit",
            ),
        ),
        (
            "Sell",
            rx.el.span(
                "Sell",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-red-50 text-red-700 border border-red-100 w-fit",
            ),
        ),
        (
            "Dividend",
            rx.el.span(
                "Dividend",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-100 w-fit",
            ),
        ),
        (
            "Deposit",
            rx.el.span(
                "Deposit",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 w-fit",
            ),
        ),
        (
            "Withdrawal",
            rx.el.span(
                "Withdrawal",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-100 w-fit",
            ),
        ),
        rx.el.span(
            t,
            class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-gray-100 text-gray-700 w-fit",
        ),
    )


def _source_badge(s: rx.Var) -> rx.Component:
    return rx.el.span(
        s,
        class_name="text-[10px] font-medium px-1.5 py-0.5 rounded bg-gray-100 text-gray-600 border border-gray-200 w-fit",
    )


def _filter_pill(name: str, current: rx.Var, on_click) -> rx.Component:
    return rx.el.button(
        name,
        on_click=on_click,
        class_name=rx.cond(
            current == name,
            "px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white border border-blue-600",
            "px-3 py-1.5 rounded-lg text-xs font-medium bg-white text-gray-700 border border-gray-200 hover:bg-gray-50",
        ),
        type="button",
    )


def _add_form() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Date",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        type="date",
                        name="date",
                        required=True,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Type",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.foreach(
                                TRANSACTION_TYPES,
                                lambda t: rx.el.option(t, value=t),
                            ),
                            name="type",
                            class_name="w-full px-3 py-2 pr-8 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 appearance-none",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none",
                        ),
                        class_name="relative",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Symbol",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="symbol",
                        placeholder="AAPL",
                        required=True,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Quantity",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        type="number",
                        step="0.0001",
                        name="quantity",
                        placeholder="0",
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Price",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        type="number",
                        step="0.01",
                        name="price",
                        placeholder="0.00",
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Fees",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        type="number",
                        step="0.01",
                        name="fees",
                        default_value="0",
                        placeholder="0.00",
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Notes",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="notes",
                        placeholder="Optional",
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
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
                        class_name="h-3.5 w-3.5 text-red-600",
                    ),
                    rx.el.p(
                        TransactionState.form_error,
                        class_name="text-xs font-medium text-red-700",
                    ),
                    class_name="flex items-center gap-2 mb-3 px-3 py-2 bg-red-50 border border-red-100 rounded-lg",
                ),
                rx.el.div(),
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    type="button",
                    on_click=TransactionState.toggle_add_form,
                    class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add Transaction",
                    type="submit",
                    class_name="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-1.5",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            on_submit=TransactionState.add_transaction,
            reset_on_submit=True,
        ),
        class_name="bg-blue-50/40 border border-blue-100 rounded-xl p-4 mb-4",
    )


def _tx_row(t: rx.Var) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.p(
                t["date"],
                class_name="text-xs font-mono text-gray-700",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(_type_badge(t["type"]), class_name="px-4 py-3"),
        rx.el.td(
            rx.el.a(
                rx.el.p(
                    t["symbol"],
                    class_name="text-sm font-semibold text-gray-900 hover:text-blue-600",
                ),
                href=f"/asset/{t['symbol']}",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            rx.el.p(
                f"{t['quantity'].to(float):,.4f}",
                class_name="text-sm text-gray-900 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${t['price'].to(float):,.2f}",
                class_name="text-sm text-gray-900 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${t['fees'].to(float):,.2f}",
                class_name="text-xs text-gray-500 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${t['total'].to(float):,.2f}",
                class_name="text-sm font-semibold text-gray-900 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(_source_badge(t["source"]), class_name="px-4 py-3"),
        rx.el.td(
            rx.el.p(
                t["notes"],
                class_name="text-xs text-gray-500 truncate max-w-[180px]",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                on_click=lambda: TransactionState.delete_transaction(
                    t["id"].to(str)
                ),
                class_name="p-1.5 rounded-md text-gray-500 hover:bg-red-50 hover:text-red-600 border border-transparent hover:border-red-100",
                type="button",
            ),
            class_name="px-4 py-3 text-right",
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50/60 transition-colors",
    )


def transactions_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            _kpi(
                "Total Transactions",
                rx.el.p(
                    TransactionState.transaction_count.to_string(),
                    class_name="text-xl font-semibold text-gray-900",
                ),
                "All-time entries",
                "list",
                "bg-slate-100 text-slate-600",
            ),
            _kpi(
                "Net Invested",
                rx.el.p(
                    f"${TransactionState.net_invested:,.2f}",
                    class_name="text-xl font-semibold text-gray-900",
                ),
                "Buys minus sells",
                "arrow-down-up",
                "bg-blue-50 text-blue-600",
            ),
            _kpi(
                "Dividends",
                rx.el.p(
                    f"${TransactionState.total_dividends:,.2f}",
                    class_name="text-xl font-semibold text-emerald-600",
                ),
                "Total received",
                "coins",
                "bg-emerald-50 text-emerald-600",
            ),
            _kpi(
                "Fees Paid",
                rx.el.p(
                    f"${TransactionState.total_fees:,.2f}",
                    class_name="text-xl font-semibold text-amber-600",
                ),
                "Trading costs",
                "receipt",
                "bg-amber-50 text-amber-600",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
                    ),
                    rx.el.input(
                        placeholder="Filter by symbol…",
                        default_value=TransactionState.filter_symbol,
                        on_change=TransactionState.set_filter_symbol.debounce(
                            300
                        ),
                        class_name="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white",
                    ),
                    class_name="relative flex-1 max-w-xs",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add Transaction",
                    on_click=TransactionState.toggle_add_form,
                    class_name="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-1.5 shrink-0",
                    type="button",
                ),
                class_name="flex items-center gap-3 mb-3 flex-wrap",
            ),
            rx.el.div(
                rx.el.p(
                    "Type:",
                    class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mr-1 self-center",
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
                    class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mr-1 self-center",
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
                            rx.el.th(
                                "Date",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Type",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Symbol",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Quantity",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Price",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Fees",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Total",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Source",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Notes",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th("", class_name="px-4 py-3"),
                            class_name="bg-gray-50/70 border-b border-gray-200",
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
                    rx.icon("receipt", class_name="h-8 w-8 text-gray-300 mb-2"),
                    rx.el.p(
                        "No transactions match your filters",
                        class_name="text-sm font-medium text-gray-600",
                    ),
                    rx.el.p(
                        "Try adjusting or add a new transaction",
                        class_name="text-xs text-gray-400 mt-1",
                    ),
                    class_name="flex flex-col items-center justify-center py-16",
                ),
                rx.el.div(),
            ),
            class_name="bg-white border border-gray-200 rounded-xl overflow-hidden",
        ),
        class_name="flex flex-col",
    )
