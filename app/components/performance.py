import reflex as rx
from app.states.market_state import MarketState
from app.states.portfolio_state import PortfolioState
from app.components.chart_utils import TOOLTIP_PROPS, CHART_TOOLTIP_CN


def _kpi(
    label: str, value: rx.Component, sub: rx.Component, icon: str, tone: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-[11px] font-medium text-gray-500 uppercase tracking-wide",
                ),
                value,
                sub,
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


def _status_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                MarketState.loading,
                rx.el.div(
                    rx.icon(
                        "loader-circle",
                        class_name="h-3.5 w-3.5 text-blue-600 animate-spin",
                    ),
                    rx.el.p(
                        MarketState.status_message,
                        class_name="text-xs font-medium text-gray-700",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name=rx.cond(
                            MarketState.data_source == "live",
                            "h-2 w-2 rounded-full bg-emerald-500",
                            "h-2 w-2 rounded-full bg-amber-500",
                        ),
                    ),
                    rx.el.p(
                        MarketState.status_message,
                        class_name="text-xs font-medium text-gray-700",
                    ),
                    class_name="flex items-center gap-2",
                ),
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-3 w-3"),
                "Refresh",
                on_click=MarketState.load_portfolio_history,
                class_name="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-white text-gray-700 border border-gray-200 hover:bg-gray-50",
                type="button",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 mb-4",
    )


def _portfolio_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Portfolio Value",
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    "1-year value trajectory of your holdings",
                    class_name="text-xs text-gray-500 mt-0.5",
                ),
            ),
            rx.icon("chart-area", class_name="h-4 w-4 text-gray-400"),
            class_name="flex items-start justify-between mb-4",
        ),
        rx.cond(
            MarketState.portfolio_history.length() > 0,
            rx.recharts.area_chart(
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.area(
                    data_key="value",
                    name="Portfolio Value",
                    stroke="#2563eb",
                    fill="#2563eb",
                    fill_opacity=0.18,
                    stroke_width=2,
                    type_="monotone",
                    dot=False,
                ),
                rx.recharts.x_axis(
                    data_key="date",
                    axis_line=False,
                    tick_line=False,
                    tick_size=10,
                    min_tick_gap=40,
                    custom_attrs={"fontSize": "11px"},
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick_size=10,
                    custom_attrs={"fontSize": "11px"},
                ),
                data=MarketState.portfolio_history,
                height=300,
                width="100%",
                margin={"left": 10, "right": 10, "top": 10, "bottom": 0},
                class_name=CHART_TOOLTIP_CN,
            ),
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-6 w-6 text-blue-500 animate-spin mb-2",
                ),
                rx.el.p(
                    "Building portfolio history…",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex flex-col items-center justify-center h-[300px]",
            ),
        ),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def _benchmark_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "vs. S&P 500 Benchmark",
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Both indexed to 100 at the start of the period",
                    class_name="text-xs text-gray-500 mt-0.5",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        class_name="h-2.5 w-2.5 rounded-full bg-blue-600"
                    ),
                    rx.el.span(
                        "Portfolio",
                        class_name="text-xs font-medium text-gray-700",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name="h-2.5 w-2.5 rounded-full bg-gray-400"
                    ),
                    rx.el.span(
                        "S&P 500",
                        class_name="text-xs font-medium text-gray-700",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex items-start justify-between mb-4 flex-wrap gap-3",
        ),
        rx.cond(
            MarketState.portfolio_history.length() > 0,
            rx.recharts.line_chart(
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.line(
                    data_key="benchmark_indexed",
                    name="S&P 500",
                    stroke="#94a3b8",
                    stroke_width=2,
                    type_="monotone",
                    dot=False,
                ),
                rx.recharts.line(
                    data_key="portfolio_indexed",
                    name="Portfolio",
                    stroke="#2563eb",
                    stroke_width=2,
                    type_="monotone",
                    dot=False,
                ),
                rx.recharts.x_axis(
                    data_key="date",
                    axis_line=False,
                    tick_line=False,
                    tick_size=10,
                    min_tick_gap=40,
                    custom_attrs={"fontSize": "11px"},
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick_size=10,
                    custom_attrs={"fontSize": "11px"},
                ),
                data=MarketState.portfolio_history,
                height=280,
                width="100%",
                margin={"left": 10, "right": 10, "top": 10, "bottom": 0},
                class_name=CHART_TOOLTIP_CN,
            ),
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-6 w-6 text-blue-500 animate-spin mb-2",
                ),
                rx.el.p(
                    "Comparing to benchmark…",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex flex-col items-center justify-center h-[280px]",
            ),
        ),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def _contribution_row(h: rx.Var) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    h["symbol"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    f"{h['allocation'].to(float):.1f}% of portfolio",
                    class_name="text-[11px] text-gray-500",
                ),
            ),
            rx.el.div(
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
                        "text-[11px] font-medium text-emerald-600 text-right",
                        "text-[11px] font-medium text-red-600 text-right",
                    ),
                ),
            ),
            class_name="flex items-center justify-between",
        ),
        href=f"/asset/{h['symbol']}",
        class_name="block py-3 border-b border-gray-100 last:border-0 hover:bg-gray-50 -mx-2 px-2 rounded transition-colors",
    )


def _contribution_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Position Contributions",
                class_name="text-sm font-semibold text-gray-900",
            ),
            rx.icon("layers", class_name="h-4 w-4 text-gray-400"),
            class_name="flex items-center justify-between mb-2",
        ),
        rx.el.p(
            "Click any position to view its detail",
            class_name="text-xs text-gray-500 mb-2",
        ),
        rx.foreach(PortfolioState.enriched_holdings, _contribution_row),
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def performance_content() -> rx.Component:
    return rx.el.div(
        _status_bar(),
        rx.el.div(
            _kpi(
                "Total Value",
                rx.el.p(
                    f"${PortfolioState.total_value:,.2f}",
                    class_name="text-xl font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Current market value", class_name="text-xs text-gray-500"
                ),
                "wallet",
                "bg-blue-50 text-blue-600",
            ),
            _kpi(
                "Total Return",
                rx.el.p(
                    f"{PortfolioState.total_gain_pct:.2f}%",
                    class_name=rx.cond(
                        PortfolioState.total_gain >= 0,
                        "text-xl font-semibold text-emerald-600",
                        "text-xl font-semibold text-red-600",
                    ),
                ),
                rx.el.p(
                    f"${PortfolioState.total_gain:,.2f} unrealized",
                    class_name="text-xs text-gray-500",
                ),
                "trending-up",
                rx.cond(
                    PortfolioState.total_gain >= 0,
                    "bg-emerald-50 text-emerald-600",
                    "bg-red-50 text-red-600",
                ),
            ),
            _kpi(
                "Daily Change",
                rx.el.p(
                    f"{PortfolioState.daily_change_pct:.2f}%",
                    class_name=rx.cond(
                        PortfolioState.daily_change >= 0,
                        "text-xl font-semibold text-emerald-600",
                        "text-xl font-semibold text-red-600",
                    ),
                ),
                rx.el.p(
                    f"${PortfolioState.daily_change:,.2f} today",
                    class_name="text-xs text-gray-500",
                ),
                "activity",
                rx.cond(
                    PortfolioState.daily_change >= 0,
                    "bg-emerald-50 text-emerald-600",
                    "bg-red-50 text-red-600",
                ),
            ),
            _kpi(
                "Positions",
                rx.el.p(
                    PortfolioState.holdings_count.to_string(),
                    class_name="text-xl font-semibold text-gray-900",
                ),
                rx.el.p("Active holdings", class_name="text-xs text-gray-500"),
                "layers",
                "bg-slate-100 text-slate-600",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4",
        ),
        _portfolio_chart(),
        rx.el.div(
            rx.el.div(_benchmark_chart(), class_name="lg:col-span-2"),
            rx.el.div(_contribution_card()),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4",
        ),
        class_name="flex flex-col",
    )
