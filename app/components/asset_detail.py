import reflex as rx
from app.states.market_state import MarketState, RANGE_DAYS
from app.states.portfolio_state import PortfolioState
from app.components.chart_utils import TOOLTIP_PROPS, CHART_TOOLTIP_CN


def _range_pill(label: str) -> rx.Component:
    is_active = MarketState.range_selection == label
    return rx.el.button(
        label,
        on_click=lambda: MarketState.set_range(label),
        class_name=rx.cond(
            is_active,
            "px-3 py-1 rounded-md text-xs font-semibold bg-violet-600 text-white border border-violet-500 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
            "px-3 py-1 rounded-md text-xs font-medium bg-slate-900/60 text-slate-300 border border-slate-700 hover:border-violet-500/50",
        ),
        type="button",
    )


def _kpi(
    label: str, value: rx.Component, sub: rx.Component, icon: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                label,
                class_name="text-[11px] font-medium text-slate-500 uppercase tracking-wide",
            ),
            rx.icon(icon, class_name="h-3.5 w-3.5 text-slate-500"),
            class_name="flex items-center justify-between mb-1.5",
        ),
        value,
        sub,
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
            rx.cond(
                MarketState.last_updated != "",
                rx.el.p(
                    f"Updated {MarketState.last_updated}",
                    class_name="text-[11px] text-slate-500 font-mono",
                ),
                rx.el.div(),
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="bg-slate-900/60 border border-slate-800/80 rounded-lg px-3 py-2 mb-4",
    )


def _price_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Price Performance",
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    "Indexed to 100 vs. S&P 500 benchmark",
                    class_name="text-xs text-slate-500 mt-0.5",
                ),
            ),
            rx.el.div(
                _range_pill("1M"),
                _range_pill("3M"),
                _range_pill("6M"),
                _range_pill("1Y"),
                class_name="flex items-center gap-1.5",
            ),
            class_name="flex items-start justify-between mb-4 flex-wrap gap-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        class_name="h-2.5 w-2.5 rounded-full bg-violet-400"
                    ),
                    rx.el.span(
                        MarketState.current_symbol,
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
                class_name="flex items-center gap-4 mb-2",
            ),
            rx.cond(
                MarketState.current_history.length() > 0,
                rx.recharts.area_chart(
                    rx.recharts.cartesian_grid(
                        horizontal=True, vertical=False, class_name="opacity-25"
                    ),
                    rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                    rx.recharts.area(
                        data_key="benchmark_indexed",
                        name="S&P 500",
                        stroke="#22d3ee",
                        fill="#22d3ee",
                        fill_opacity=0.08,
                        stroke_width=1.5,
                        type_="monotone",
                        dot=False,
                    ),
                    rx.recharts.area(
                        data_key="asset_indexed",
                        name=MarketState.current_symbol,
                        stroke="#a78bfa",
                        fill="#a78bfa",
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
                    data=MarketState.current_history,
                    height=320,
                    width="100%",
                    margin={"left": 0, "right": 10, "top": 10, "bottom": 0},
                    class_name=CHART_TOOLTIP_CN,
                ),
                rx.el.div(
                    rx.icon(
                        "chart-line",
                        class_name="h-8 w-8 text-slate-600 mb-2",
                    ),
                    rx.el.p(
                        "Loading price data…",
                        class_name="text-sm text-slate-500",
                    ),
                    class_name="flex flex-col items-center justify-center h-[320px]",
                ),
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _position_card() -> rx.Component:
    sym = MarketState.current_symbol
    holdings = PortfolioState.enriched_holdings
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Your Position",
                class_name="text-sm font-semibold text-slate-100",
            ),
            rx.icon("wallet", class_name="h-4 w-4 text-violet-400"),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.foreach(
            holdings,
            lambda h: rx.cond(
                h["symbol"] == sym,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Quantity",
                                class_name="text-[11px] text-slate-500 uppercase tracking-wide",
                            ),
                            rx.el.p(
                                f"{h['quantity'].to(float):,.4f}",
                                class_name="text-sm font-semibold text-slate-100 font-mono mt-0.5",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Cost Basis",
                                class_name="text-[11px] text-slate-500 uppercase tracking-wide",
                            ),
                            rx.el.p(
                                f"${h['cost_basis'].to(float):,.2f}",
                                class_name="text-sm font-semibold text-slate-100 font-mono mt-0.5",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Market Value",
                                class_name="text-[11px] text-slate-500 uppercase tracking-wide",
                            ),
                            rx.el.p(
                                f"${h['market_value'].to(float):,.2f}",
                                class_name="text-sm font-semibold text-slate-100 font-mono mt-0.5",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "P&L",
                                class_name="text-[11px] text-slate-500 uppercase tracking-wide",
                            ),
                            rx.el.p(
                                f"${h['gain'].to(float):,.2f}",
                                class_name=rx.cond(
                                    h["is_gain"],
                                    "text-sm font-semibold text-emerald-400 font-mono mt-0.5",
                                    "text-sm font-semibold text-rose-400 font-mono mt-0.5",
                                ),
                            ),
                            rx.el.p(
                                f"{h['gain_pct'].to(float):.2f}%",
                                class_name=rx.cond(
                                    h["is_gain"],
                                    "text-[11px] font-medium text-emerald-400",
                                    "text-[11px] font-medium text-rose-400",
                                ),
                            ),
                        ),
                        class_name="grid grid-cols-2 gap-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Portfolio Contribution",
                                class_name="text-[11px] text-slate-500 uppercase tracking-wide",
                            ),
                            rx.el.p(
                                f"{h['allocation'].to(float):.2f}%",
                                class_name="text-sm font-semibold text-violet-300 font-mono",
                            ),
                            class_name="flex items-center justify-between mb-1.5",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="h-full bg-violet-500 rounded-full",
                                style={"width": f"{h['allocation']}%"},
                            ),
                            class_name="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden",
                        ),
                        class_name="mt-4 pt-4 border-t border-slate-800",
                    ),
                    class_name="",
                ),
                rx.el.div(),
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _range_summary_row(label: str, value: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-xs text-slate-500"),
        value,
        class_name="flex items-center justify-between py-2 border-b border-slate-800/60 last:border-0",
    )


def _range_summary() -> rx.Component:
    a = MarketState.current_asset
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Key Metrics", class_name="text-sm font-semibold text-slate-100"
            ),
            rx.icon("gauge", class_name="h-4 w-4 text-cyan-400"),
            class_name="flex items-center justify-between mb-3",
        ),
        _range_summary_row(
            "52-Week High",
            rx.el.p(
                f"${a['week_high_52'].to(float):,.2f}",
                class_name="text-sm font-semibold text-slate-100 font-mono",
            ),
        ),
        _range_summary_row(
            "52-Week Low",
            rx.el.p(
                f"${a['week_low_52'].to(float):,.2f}",
                class_name="text-sm font-semibold text-slate-100 font-mono",
            ),
        ),
        _range_summary_row(
            "1-Year Return",
            rx.el.p(
                f"{a['year_change_pct'].to(float):.2f}%",
                class_name=rx.cond(
                    a["year_change_pct"].to(float) >= 0,
                    "text-sm font-semibold text-emerald-400 font-mono",
                    "text-sm font-semibold text-rose-400 font-mono",
                ),
            ),
        ),
        _range_summary_row(
            "Annualized Volatility",
            rx.el.p(
                f"{a['volatility'].to(float):.2f}%",
                class_name="text-sm font-semibold text-slate-100 font-mono",
            ),
        ),
        _range_summary_row(
            "Prev. Close",
            rx.el.p(
                f"${a['prev_close'].to(float):,.2f}",
                class_name="text-sm font-semibold text-slate-100 font-mono",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def asset_detail_content() -> rx.Component:
    a = MarketState.current_asset
    return rx.el.div(
        _status_bar(),
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("arrow-left", class_name="h-3.5 w-3.5"),
                    "Back to Discover",
                    href="/discover",
                    class_name="inline-flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-slate-100 mb-3",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            MarketState.current_symbol,
                            class_name="text-3xl font-bold text-slate-100 tracking-tight",
                        ),
                        rx.el.p(
                            a["name"],
                            class_name="text-sm text-slate-400 mt-0.5",
                        ),
                        class_name="",
                    ),
                    rx.el.div(
                        rx.el.p(
                            f"${a['latest_price'].to(float):,.2f}",
                            class_name="text-3xl font-bold text-slate-100 font-mono tracking-tight",
                        ),
                        rx.el.div(
                            rx.icon(
                                rx.cond(
                                    a["is_up"], "trending-up", "trending-down"
                                ),
                                class_name="h-3.5 w-3.5",
                            ),
                            rx.el.span(
                                f"${a['day_change'].to(float):,.2f}",
                                class_name="font-mono",
                            ),
                            rx.el.span("·"),
                            rx.el.span(
                                f"{a['day_change_pct'].to(float):.2f}%",
                                class_name="font-mono",
                            ),
                            class_name=rx.cond(
                                a["is_up"],
                                "flex items-center gap-1.5 text-sm font-semibold text-emerald-400 mt-1 justify-end",
                                "flex items-center gap-1.5 text-sm font-semibold text-rose-400 mt-1 justify-end",
                            ),
                        ),
                        class_name="text-right",
                    ),
                    class_name="flex items-start justify-between gap-4 flex-wrap",
                ),
            ),
            class_name="mb-5",
        ),
        rx.el.div(
            _kpi(
                "Day Change",
                rx.el.p(
                    f"{a['day_change_pct'].to(float):.2f}%",
                    class_name=rx.cond(
                        a["is_up"],
                        "text-xl font-semibold text-emerald-400",
                        "text-xl font-semibold text-rose-400",
                    ),
                ),
                rx.el.p(
                    f"${a['day_change'].to(float):,.2f}",
                    class_name="text-xs text-slate-500 font-mono",
                ),
                "activity",
            ),
            _kpi(
                "1Y Return",
                rx.el.p(
                    f"{a['year_change_pct'].to(float):.2f}%",
                    class_name=rx.cond(
                        a["year_change_pct"].to(float) >= 0,
                        "text-xl font-semibold text-emerald-400",
                        "text-xl font-semibold text-rose-400",
                    ),
                ),
                rx.el.p(
                    "Trailing 12 months", class_name="text-xs text-slate-500"
                ),
                "trending-up",
            ),
            _kpi(
                "52W Range",
                rx.el.p(
                    f"${a['week_low_52'].to(float):,.2f} — ${a['week_high_52'].to(float):,.2f}",
                    class_name="text-sm font-semibold text-slate-100 font-mono",
                ),
                rx.el.p("Low / High", class_name="text-xs text-slate-500 mt-1"),
                "arrow_up_down",
            ),
            _kpi(
                "Volatility",
                rx.el.p(
                    f"{a['volatility'].to(float):.2f}%",
                    class_name="text-xl font-semibold text-slate-100",
                ),
                rx.el.p("Annualized", class_name="text-xs text-slate-500"),
                "waves",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4",
        ),
        rx.el.div(
            rx.el.div(_price_chart(), class_name="lg:col-span-2"),
            rx.el.div(
                _range_summary(),
                _position_card(),
                class_name="flex flex-col gap-4",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4",
        ),
        class_name="flex flex-col",
    )
