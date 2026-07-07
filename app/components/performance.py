import reflex as rx
from app.states.market_state import MarketState, PERF_PRESET_LABELS
from app.states.portfolio_state import PortfolioState
from app.components.chart_utils import TOOLTIP_PROPS, CHART_TOOLTIP_CN


def _preset_button(preset_key: str, label: str) -> rx.Component:
    is_active = (
        MarketState.perf_range_preset == preset_key
    ) & ~MarketState.perf_use_custom
    return rx.el.button(
        label,
        on_click=lambda: MarketState.set_perf_preset(preset_key),
        class_name=rx.cond(
            is_active,
            "px-3 py-1.5 rounded-md text-xs font-semibold bg-violet-600 text-white border border-violet-500 whitespace-nowrap shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
            "px-3 py-1.5 rounded-md text-xs font-medium bg-slate-900/60 text-slate-300 border border-slate-700 hover:border-violet-500/50 whitespace-nowrap",
        ),
        type="button",
    )


def _range_controls() -> rx.Component:
    input_cn = "w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100"
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Time Range",
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    MarketState.perf_range_summary,
                    class_name="text-xs text-slate-500 mt-0.5",
                ),
            ),
            rx.icon("calendar-range", class_name="h-4 w-4 text-cyan-400"),
            class_name="flex items-start justify-between mb-3",
        ),
        rx.el.div(
            rx.el.p(
                "Presets",
                class_name="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2",
            ),
            rx.el.div(
                rx.foreach(
                    PERF_PRESET_LABELS,
                    lambda item: _preset_button(item[0], item[1]),
                ),
                class_name="flex items-center gap-1.5 flex-wrap",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.p(
                "Custom Range",
                class_name="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Start date",
                        class_name="text-[11px] font-medium text-slate-400 mb-1 block",
                    ),
                    rx.el.input(
                        type="date",
                        default_value=MarketState.perf_start_date,
                        on_change=MarketState.set_perf_start_date.debounce(200),
                        class_name=input_cn,
                    ),
                    class_name="flex-1 min-w-[140px]",
                ),
                rx.el.div(
                    rx.el.label(
                        "End date",
                        class_name="text-[11px] font-medium text-slate-400 mb-1 block",
                    ),
                    rx.el.input(
                        type="date",
                        default_value=MarketState.perf_end_date,
                        on_change=MarketState.set_perf_end_date.debounce(200),
                        class_name=input_cn,
                    ),
                    class_name="flex-1 min-w-[140px]",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("x", class_name="h-3.5 w-3.5"),
                        "Clear",
                        on_click=MarketState.clear_perf_custom,
                        type="button",
                        class_name="px-3 py-2 text-xs font-medium text-slate-300 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-800 flex items-center gap-1.5 h-[38px] mt-[19px]",
                    ),
                    class_name="shrink-0",
                ),
                class_name="flex items-end gap-2 flex-wrap",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5 mb-4",
    )


def _kpi(
    label: str, value: rx.Component, sub: rx.Component, icon: str, tone: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-[11px] font-medium text-slate-500 uppercase tracking-wide",
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
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-4",
    )


def _status_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                MarketState.loading,
                rx.el.div(
                    rx.icon(
                        "loader-circle",
                        class_name="h-3.5 w-3.5 text-violet-400 animate-spin",
                    ),
                    rx.el.p(
                        MarketState.status_message,
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name=rx.cond(
                            MarketState.data_source == "live",
                            "h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]",
                            "h-2 w-2 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]",
                        ),
                    ),
                    rx.el.p(
                        MarketState.status_message,
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center gap-2",
                ),
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-3 w-3"),
                "Refresh",
                on_click=MarketState.load_portfolio_history,
                class_name="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-900 text-slate-300 border border-slate-700 hover:border-violet-500/50",
                type="button",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="bg-slate-900/60 border border-slate-800/80 rounded-lg px-3 py-2 mb-4",
    )


def _portfolio_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Portfolio Value",
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    "Value trajectory over selected range",
                    class_name="text-xs text-slate-500 mt-0.5",
                ),
            ),
            rx.icon("chart-area", class_name="h-4 w-4 text-violet-400"),
            class_name="flex items-start justify-between mb-4",
        ),
        rx.cond(
            MarketState.filtered_portfolio_history.length() > 0,
            rx.recharts.area_chart(
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.area(
                    data_key="value",
                    name="Portfolio Value",
                    stroke="#a78bfa",
                    fill="#a78bfa",
                    fill_opacity=0.2,
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
                data=MarketState.filtered_portfolio_history,
                height=300,
                width="100%",
                margin={"left": 10, "right": 10, "top": 10, "bottom": 0},
                class_name=CHART_TOOLTIP_CN,
            ),
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-6 w-6 text-violet-400 animate-spin mb-2",
                ),
                rx.el.p(
                    "Building portfolio history…",
                    class_name="text-sm text-slate-500",
                ),
                class_name="flex flex-col items-center justify-center h-[300px]",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _benchmark_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "vs. S&P 500 Benchmark",
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    "Both indexed to 100 at the start of the period",
                    class_name="text-xs text-slate-500 mt-0.5",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        class_name="h-2.5 w-2.5 rounded-full bg-violet-400"
                    ),
                    rx.el.span(
                        "Portfolio",
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name="h-2.5 w-2.5 rounded-full bg-cyan-400"
                    ),
                    rx.el.span(
                        "S&P 500",
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex items-start justify-between mb-4 flex-wrap gap-3",
        ),
        rx.cond(
            MarketState.filtered_portfolio_history.length() > 0,
            rx.recharts.line_chart(
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.line(
                    data_key="benchmark_indexed",
                    name="S&P 500",
                    stroke="#22d3ee",
                    stroke_width=2,
                    type_="monotone",
                    dot=False,
                ),
                rx.recharts.line(
                    data_key="portfolio_indexed",
                    name="Portfolio",
                    stroke="#a78bfa",
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
                data=MarketState.filtered_portfolio_history,
                height=280,
                width="100%",
                margin={"left": 10, "right": 10, "top": 10, "bottom": 0},
                class_name=CHART_TOOLTIP_CN,
            ),
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-6 w-6 text-violet-400 animate-spin mb-2",
                ),
                rx.el.p(
                    "Comparing to benchmark…",
                    class_name="text-sm text-slate-500",
                ),
                class_name="flex flex-col items-center justify-center h-[280px]",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _contribution_row(h: rx.Var) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    h["symbol"],
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    f"{h['allocation'].to(float):.1f}% of portfolio",
                    class_name="text-[11px] text-slate-500",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    f"${h['gain'].to(float):,.2f}",
                    class_name=rx.cond(
                        h["is_gain"],
                        "text-sm font-semibold text-emerald-400 font-mono",
                        "text-sm font-semibold text-rose-400 font-mono",
                    ),
                ),
                rx.el.p(
                    f"{h['gain_pct'].to(float):.2f}%",
                    class_name=rx.cond(
                        h["is_gain"],
                        "text-[11px] font-medium text-emerald-400 text-right",
                        "text-[11px] font-medium text-rose-400 text-right",
                    ),
                ),
            ),
            class_name="flex items-center justify-between",
        ),
        href=f"/asset/{h['symbol']}",
        class_name="block py-3 border-b border-slate-800/60 last:border-0 hover:bg-slate-800/40 -mx-2 px-2 rounded transition-colors",
    )


def _contribution_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Position Contributions",
                class_name="text-sm font-semibold text-slate-100",
            ),
            rx.icon("layers", class_name="h-4 w-4 text-cyan-400"),
            class_name="flex items-center justify-between mb-2",
        ),
        rx.el.p(
            "Click any position to view its detail",
            class_name="text-xs text-slate-500 mb-2",
        ),
        rx.foreach(PortfolioState.enriched_holdings, _contribution_row),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def performance_content() -> rx.Component:
    return rx.el.div(
        _status_bar(),
        rx.el.div(
            _kpi(
                "Total Value",
                rx.el.p(
                    f"${PortfolioState.total_value:,.2f}",
                    class_name="text-xl font-semibold text-slate-100",
                ),
                rx.el.p(
                    "Current market value", class_name="text-xs text-slate-500"
                ),
                "wallet",
                "bg-violet-500/15 text-violet-300 border border-violet-500/30",
            ),
            _kpi(
                "Total Return",
                rx.el.p(
                    f"{PortfolioState.total_gain_pct:.2f}%",
                    class_name=rx.cond(
                        PortfolioState.total_gain >= 0,
                        "text-xl font-semibold text-emerald-400",
                        "text-xl font-semibold text-rose-400",
                    ),
                ),
                rx.el.p(
                    f"${PortfolioState.total_gain:,.2f} unrealized",
                    class_name="text-xs text-slate-500",
                ),
                "trending-up",
                rx.cond(
                    PortfolioState.total_gain >= 0,
                    "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
                    "bg-rose-500/15 text-rose-300 border border-rose-500/30",
                ),
            ),
            _kpi(
                "Daily Change",
                rx.el.p(
                    f"{PortfolioState.daily_change_pct:.2f}%",
                    class_name=rx.cond(
                        PortfolioState.daily_change >= 0,
                        "text-xl font-semibold text-emerald-400",
                        "text-xl font-semibold text-rose-400",
                    ),
                ),
                rx.el.p(
                    f"${PortfolioState.daily_change:,.2f} today",
                    class_name="text-xs text-slate-500",
                ),
                "activity",
                rx.cond(
                    PortfolioState.daily_change >= 0,
                    "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30",
                    "bg-rose-500/15 text-rose-300 border border-rose-500/30",
                ),
            ),
            _kpi(
                "Positions",
                rx.el.p(
                    PortfolioState.holdings_count.to_string(),
                    class_name="text-xl font-semibold text-slate-100",
                ),
                rx.el.p("Active holdings", class_name="text-xs text-slate-500"),
                "layers",
                "bg-slate-800 text-slate-300 border border-slate-700",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4",
        ),
        _range_controls(),
        _portfolio_chart(),
        rx.el.div(
            rx.el.div(_benchmark_chart(), class_name="lg:col-span-2"),
            rx.el.div(_contribution_card()),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4",
        ),
        class_name="flex flex-col",
    )
