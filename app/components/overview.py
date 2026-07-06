import reflex as rx
from app.states.portfolio_state import PortfolioState


def _kpi_card(
    label: str, value: rx.Component, sub: rx.Component, icon: str, icon_bg: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-xs font-medium text-gray-500 uppercase tracking-wide",
                ),
                value,
                sub,
                class_name="flex flex-col gap-1",
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-5 w-5"),
                class_name=f"h-10 w-10 rounded-lg flex items-center justify-center {icon_bg}",
            ),
            class_name="flex items-start justify-between",
        ),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def kpi_grid() -> rx.Component:
    return rx.el.div(
        _kpi_card(
            "Total Value",
            rx.el.p(
                f"${PortfolioState.total_value:,.2f}",
                class_name="text-2xl font-semibold text-gray-900",
            ),
            rx.el.p(
                rx.cond(
                    PortfolioState.holdings_count > 0,
                    f"{PortfolioState.holdings_count} holdings",
                    "No holdings",
                ),
                class_name="text-xs text-gray-500",
            ),
            "wallet",
            "bg-blue-50 text-blue-600",
        ),
        _kpi_card(
            "Total Gain/Loss",
            rx.el.p(
                f"${PortfolioState.total_gain:,.2f}",
                class_name=rx.cond(
                    PortfolioState.total_gain >= 0,
                    "text-2xl font-semibold text-emerald-600",
                    "text-2xl font-semibold text-red-600",
                ),
            ),
            rx.el.div(
                rx.icon(
                    rx.cond(
                        PortfolioState.total_gain >= 0,
                        "trending-up",
                        "trending-down",
                    ),
                    class_name="h-3 w-3",
                ),
                rx.el.span(f"{PortfolioState.total_gain_pct:.2f}%"),
                class_name=rx.cond(
                    PortfolioState.total_gain >= 0,
                    "flex items-center gap-1 text-xs font-medium text-emerald-600",
                    "flex items-center gap-1 text-xs font-medium text-red-600",
                ),
            ),
            "chart-line",
            rx.cond(
                PortfolioState.total_gain >= 0,
                "bg-emerald-50 text-emerald-600",
                "bg-red-50 text-red-600",
            ),
        ),
        _kpi_card(
            "Cost Basis",
            rx.el.p(
                f"${PortfolioState.total_cost:,.2f}",
                class_name="text-2xl font-semibold text-gray-900",
            ),
            rx.el.p("Total invested", class_name="text-xs text-gray-500"),
            "landmark",
            "bg-slate-100 text-slate-600",
        ),
        _kpi_card(
            "Today's Change",
            rx.el.p(
                f"${PortfolioState.daily_change:,.2f}",
                class_name=rx.cond(
                    PortfolioState.daily_change >= 0,
                    "text-2xl font-semibold text-emerald-600",
                    "text-2xl font-semibold text-red-600",
                ),
            ),
            rx.el.div(
                rx.icon(
                    rx.cond(
                        PortfolioState.daily_change >= 0,
                        "arrow-up-right",
                        "arrow-down-right",
                    ),
                    class_name="h-3 w-3",
                ),
                rx.el.span(f"{PortfolioState.daily_change_pct:.2f}%"),
                class_name=rx.cond(
                    PortfolioState.daily_change >= 0,
                    "flex items-center gap-1 text-xs font-medium text-emerald-600",
                    "flex items-center gap-1 text-xs font-medium text-red-600",
                ),
            ),
            "activity",
            rx.cond(
                PortfolioState.daily_change >= 0,
                "bg-emerald-50 text-emerald-600",
                "bg-red-50 text-red-600",
            ),
        ),
        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
    )


def _allocation_row(item: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    class_name="h-2.5 w-2.5 rounded-full shrink-0",
                    style={"backgroundColor": item["fill"]},
                ),
                rx.el.p(
                    item["name"], class_name="text-sm font-medium text-gray-900"
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.el.p(
                    f"${item['value'].to(float):,.2f}",
                    class_name="text-sm font-medium text-gray-900",
                ),
                rx.el.p(
                    f"{item['pct'].to(float):.1f}%",
                    class_name="text-xs text-gray-500",
                ),
                class_name="text-right",
            ),
            class_name="flex items-center justify-between mb-1.5",
        ),
        rx.el.div(
            rx.el.div(
                class_name="h-full rounded-full",
                style={
                    "width": f"{item['pct']}%",
                    "backgroundColor": item["fill"],
                },
            ),
            class_name="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden",
        ),
        class_name="mb-3",
    )


def allocation_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Asset Allocation",
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Distribution across asset classes",
                    class_name="text-xs text-gray-500 mt-0.5",
                ),
            ),
            rx.icon("chart-pie", class_name="h-4 w-4 text-gray-400"),
            class_name="flex items-start justify-between mb-5",
        ),
        rx.el.div(
            rx.foreach(PortfolioState.allocation_by_class, _allocation_row),
        ),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def _mover_row(h: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    h["symbol"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    h["name"],
                    class_name="text-xs text-gray-500 truncate max-w-[140px]",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    f"${h['current_price'].to(float):,.2f}",
                    class_name="text-sm font-medium text-gray-900",
                ),
                rx.el.div(
                    rx.icon(
                        rx.cond(
                            h["is_day_gain"], "trending-up", "trending-down"
                        ),
                        class_name="h-3 w-3",
                    ),
                    rx.el.span(f"{h['day_pct'].to(float):.2f}%"),
                    class_name=rx.cond(
                        h["is_day_gain"],
                        "flex items-center gap-1 text-xs font-medium text-emerald-600 justify-end",
                        "flex items-center gap-1 text-xs font-medium text-red-600 justify-end",
                    ),
                ),
                class_name="text-right",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="py-3 border-b border-gray-100 last:border-0",
    )


def top_movers_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Top Movers",
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Biggest daily changes",
                    class_name="text-xs text-gray-500 mt-0.5",
                ),
            ),
            rx.icon("zap", class_name="h-4 w-4 text-gray-400"),
            class_name="flex items-start justify-between mb-2",
        ),
        rx.el.div(rx.foreach(PortfolioState.top_movers, _mover_row)),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def _activity_row(a: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(a["icon"], class_name="h-4 w-4 text-gray-600"),
            class_name="h-9 w-9 rounded-lg bg-gray-100 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    a["type"], class_name="text-sm font-medium text-gray-900"
                ),
                rx.el.span(
                    a["symbol"],
                    class_name="text-xs font-medium text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.p(a["detail"], class_name="text-xs text-gray-500 mt-0.5"),
        ),
        rx.el.p(a["time"], class_name="text-xs text-gray-400 shrink-0 ml-auto"),
        class_name="flex items-center gap-3 py-3 border-b border-gray-100 last:border-0",
    )


def activity_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Recent Activity",
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Latest transactions and events",
                    class_name="text-xs text-gray-500 mt-0.5",
                ),
            ),
            rx.icon("history", class_name="h-4 w-4 text-gray-400"),
            class_name="flex items-start justify-between mb-2",
        ),
        rx.el.div(rx.foreach(PortfolioState.recent_activity, _activity_row)),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def _empty_portfolio_state() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("wallet", class_name="h-8 w-8 text-blue-600"),
            class_name="h-14 w-14 rounded-full bg-blue-50 flex items-center justify-center mb-3",
        ),
        rx.el.h3(
            "No holdings yet",
            class_name="text-base font-semibold text-gray-900",
        ),
        rx.el.p(
            "Add your first holding to start tracking performance, allocations, and activity.",
            class_name="text-sm text-gray-500 mt-1 max-w-sm text-center",
        ),
        rx.el.a(
            rx.icon("plus", class_name="h-4 w-4"),
            "Add a holding",
            href="/holdings",
            class_name="mt-4 inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-hidden focus:ring-2 focus:ring-blue-500",
            aria_label="Go to holdings page to add a new holding",
        ),
        class_name="flex flex-col items-center justify-center py-16 bg-white border border-gray-200 rounded-xl",
    )


def overview_content() -> rx.Component:
    return rx.cond(
        PortfolioState.holdings_count > 0,
        rx.el.div(
            kpi_grid(),
            rx.el.div(
                rx.el.div(allocation_card(), class_name="lg:col-span-1"),
                rx.el.div(top_movers_card(), class_name="lg:col-span-1"),
                rx.el.div(activity_card(), class_name="lg:col-span-1"),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4",
            ),
            class_name="flex flex-col gap-2",
        ),
        _empty_portfolio_state(),
    )
