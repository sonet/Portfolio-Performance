import reflex as rx
from app.states.portfolio_state import PortfolioState, ASSET_CLASSES


def _class_badge(cls: rx.Var) -> rx.Component:
    return rx.match(
        cls,
        (
            "Equity",
            rx.el.span(
                "Equity",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-100 w-fit",
            ),
        ),
        (
            "ETF",
            rx.el.span(
                "ETF",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-sky-50 text-sky-700 border border-sky-100 w-fit",
            ),
        ),
        (
            "Crypto",
            rx.el.span(
                "Crypto",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-100 w-fit",
            ),
        ),
        (
            "Bond",
            rx.el.span(
                "Bond",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100 w-fit",
            ),
        ),
        (
            "Cash",
            rx.el.span(
                "Cash",
                class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 w-fit",
            ),
        ),
        rx.el.span(
            cls,
            class_name="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-gray-100 text-gray-700 w-fit",
        ),
    )


def _filter_pill(name: str) -> rx.Component:
    is_active = PortfolioState.filter_class == name
    return rx.el.button(
        name,
        on_click=lambda: PortfolioState.set_filter_class(name),
        class_name=rx.cond(
            is_active,
            "px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white border border-blue-600",
            "px-3 py-1.5 rounded-lg text-xs font-medium bg-white text-gray-700 border border-gray-200 hover:bg-gray-50",
        ),
        type="button",
    )


def _holding_row(h: rx.Var) -> rx.Component:
    is_editing = PortfolioState.editing_id == h["id"]
    return rx.el.tr(
        rx.el.td(
            rx.el.a(
                rx.el.div(
                    rx.el.p(
                        h["symbol"],
                        class_name="text-sm font-semibold text-gray-900 hover:text-blue-600",
                    ),
                    _class_badge(h["asset_class"]),
                    rx.icon(
                        "arrow-up-right",
                        class_name="h-3 w-3 text-gray-300",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.p(
                    h["name"],
                    class_name="text-xs text-gray-500 mt-0.5 truncate max-w-[220px]",
                ),
                href=f"/asset/{h['symbol']}",
                class_name="flex flex-col group",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            rx.cond(
                is_editing,
                rx.el.input(
                    type="number",
                    step="0.0001",
                    default_value=PortfolioState.edit_quantity.to_string(),
                    on_change=PortfolioState.set_edit_quantity.debounce(300),
                    class_name="w-24 px-2 py-1 text-sm border border-blue-300 rounded-md focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                ),
                rx.el.p(
                    f"{h['quantity'].to(float):,.4f}",
                    class_name="text-sm text-gray-900 font-mono",
                ),
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.cond(
                is_editing,
                rx.el.input(
                    type="number",
                    step="0.01",
                    default_value=PortfolioState.edit_cost.to_string(),
                    on_change=PortfolioState.set_edit_cost.debounce(300),
                    class_name="w-24 px-2 py-1 text-sm border border-blue-300 rounded-md focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                ),
                rx.el.p(
                    f"${h['cost_basis'].to(float):,.2f}",
                    class_name="text-sm text-gray-700 font-mono",
                ),
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${h['current_price'].to(float):,.2f}",
                class_name="text-sm text-gray-900 font-mono",
            ),
            rx.el.div(
                rx.icon(
                    rx.cond(h["is_day_gain"], "arrow-up", "arrow-down"),
                    class_name="h-2.5 w-2.5",
                ),
                rx.el.span(f"{h['day_pct'].to(float):.2f}%"),
                class_name=rx.cond(
                    h["is_day_gain"],
                    "flex items-center gap-0.5 text-[11px] font-medium text-emerald-600 justify-end mt-0.5",
                    "flex items-center gap-0.5 text-[11px] font-medium text-red-600 justify-end mt-0.5",
                ),
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${h['market_value'].to(float):,.2f}",
                class_name="text-sm font-semibold text-gray-900 font-mono",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="h-full bg-blue-500 rounded-full",
                        style={"width": f"{h['allocation']}%"},
                    ),
                    class_name="h-1.5 w-16 bg-gray-100 rounded-full overflow-hidden",
                ),
                rx.el.p(
                    f"{h['allocation'].to(float):.1f}%",
                    class_name="text-xs text-gray-600 font-mono",
                ),
                class_name="flex items-center gap-2 justify-end",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${h['gain'].to(float):,.2f}",
                class_name=rx.cond(
                    h["is_gain"],
                    "text-sm font-semibold text-emerald-600 font-mono",
                    "text-sm font-semibold text-red-600 font-mono",
                ),
            ),
            rx.el.p(
                f"{h['gain_pct'].to(float):.2f}%",
                class_name=rx.cond(
                    h["is_gain"],
                    "text-[11px] font-medium text-emerald-600 mt-0.5",
                    "text-[11px] font-medium text-red-600 mt-0.5",
                ),
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            rx.cond(
                is_editing,
                rx.el.div(
                    rx.el.button(
                        rx.icon("check", class_name="h-3.5 w-3.5"),
                        on_click=PortfolioState.save_edit,
                        class_name="p-1.5 rounded-md bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-100",
                        type="button",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-3.5 w-3.5"),
                        on_click=PortfolioState.cancel_edit,
                        class_name="p-1.5 rounded-md bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200",
                        type="button",
                    ),
                    class_name="flex items-center gap-1 justify-end",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("pencil", class_name="h-3.5 w-3.5"),
                        on_click=lambda: PortfolioState.start_edit(
                            h["id"].to(str)
                        ),
                        class_name="p-1.5 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-900 border border-transparent hover:border-gray-200",
                        type="button",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                        on_click=lambda: PortfolioState.delete_holding(
                            h["id"].to(str)
                        ),
                        class_name="p-1.5 rounded-md text-gray-500 hover:bg-red-50 hover:text-red-600 border border-transparent hover:border-red-100",
                        type="button",
                    ),
                    class_name="flex items-center gap-1 justify-end",
                ),
            ),
            class_name="px-4 py-3",
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50/60 transition-colors",
    )


def add_holding_form() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Symbol",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="symbol",
                        placeholder="AAPL",
                        required=True,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Name",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="name",
                        placeholder="Apple Inc.",
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Asset Class",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.select(
                        rx.foreach(
                            ASSET_CLASSES, lambda c: rx.el.option(c, value=c)
                        ),
                        name="asset_class",
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white appearance-none",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Quantity",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="quantity",
                        type="number",
                        step="0.0001",
                        placeholder="10",
                        required=True,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Cost Basis",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="cost_basis",
                        type="number",
                        step="0.01",
                        placeholder="150.00",
                        required=True,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Current Price",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        name="price",
                        type="number",
                        step="0.01",
                        placeholder="185.00",
                        required=True,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                    ),
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    type="button",
                    on_click=PortfolioState.toggle_add_form,
                    class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add Holding",
                    type="submit",
                    class_name="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-1.5",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            on_submit=PortfolioState.add_holding,
            reset_on_submit=True,
        ),
        class_name="bg-blue-50/40 border border-blue-100 rounded-xl p-4 mb-4",
    )


def holdings_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
                    ),
                    rx.el.input(
                        placeholder="Search by symbol or name...",
                        default_value=PortfolioState.search_query,
                        on_change=PortfolioState.set_search.debounce(300),
                        class_name="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white",
                    ),
                    class_name="relative flex-1 max-w-md",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add Holding",
                    on_click=PortfolioState.toggle_add_form,
                    class_name="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-1.5 shrink-0",
                    type="button",
                ),
                class_name="flex items-center gap-3 mb-3 flex-wrap",
            ),
            rx.el.div(
                _filter_pill("All"),
                rx.foreach(ASSET_CLASSES, _filter_pill),
                class_name="flex items-center gap-2 flex-wrap",
            ),
            class_name="mb-4",
        ),
        rx.cond(PortfolioState.show_add_form, add_holding_form(), rx.el.div()),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Asset",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Quantity",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Cost Basis",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Price",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Market Value",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Allocation",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "P&L",
                                class_name="px-4 py-3 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th("", class_name="px-4 py-3"),
                            class_name="bg-gray-50/70 border-b border-gray-200",
                        ),
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            PortfolioState.filtered_holdings, _holding_row
                        ),
                    ),
                    class_name="table-auto min-w-full",
                ),
                class_name="overflow-x-auto",
            ),
            rx.cond(
                PortfolioState.filtered_holdings.length() == 0,
                rx.el.div(
                    rx.icon("inbox", class_name="h-8 w-8 text-gray-300 mb-2"),
                    rx.el.p(
                        "No holdings match your filters",
                        class_name="text-sm font-medium text-gray-600",
                    ),
                    rx.el.p(
                        "Try adjusting your search or filter criteria",
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
