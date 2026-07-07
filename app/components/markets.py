import reflex as rx
from app.states.markets_state import MarketsState, INTERVAL_LABELS


def _cell_class(value: rx.Var) -> rx.Var:
    return rx.cond(
        value >= 20,
        "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-emerald-500 text-white border border-emerald-400",
        rx.cond(
            value >= 10,
            "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-emerald-500/60 text-emerald-50 border border-emerald-400/50",
            rx.cond(
                value >= 3,
                "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-emerald-500/30 text-emerald-200 border border-emerald-400/30",
                rx.cond(
                    value >= 0,
                    "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20",
                    rx.cond(
                        value >= -3,
                        "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30",
                        rx.cond(
                            value >= -10,
                            "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-rose-500/30 text-rose-200 border border-rose-400/40",
                            "text-[11px] font-mono font-semibold text-center px-2 py-1.5 rounded bg-rose-500 text-white border border-rose-400",
                        ),
                    ),
                ),
            ),
        ),
    )


def _status_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                MarketsState.loading,
                rx.el.div(
                    rx.icon(
                        "loader-circle",
                        class_name="h-3.5 w-3.5 text-violet-400 animate-spin",
                    ),
                    rx.el.p(
                        MarketsState.status_message,
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name=rx.match(
                            MarketsState.data_source,
                            (
                                "live",
                                "h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]",
                            ),
                            (
                                "mixed",
                                "h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]",
                            ),
                            "h-2 w-2 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]",
                        ),
                    ),
                    rx.el.p(
                        MarketsState.status_message,
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center gap-2",
                ),
            ),
            rx.el.div(
                rx.cond(
                    MarketsState.last_updated != "",
                    rx.el.p(
                        f"Updated {MarketsState.last_updated}",
                        class_name="text-[11px] text-slate-500 font-mono",
                    ),
                    rx.el.div(),
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="h-3 w-3"),
                    "Refresh",
                    on_click=MarketsState.refresh_report,
                    class_name="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-900 text-slate-300 border border-slate-700 hover:border-violet-500/50",
                    type="button",
                    disabled=MarketsState.loading,
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="flex items-center justify-between flex-wrap gap-2",
        ),
        class_name="bg-slate-900/60 border border-slate-800/80 rounded-lg px-3 py-2 mb-4",
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


def _summary_grid() -> rx.Component:
    s = MarketsState.summary_stats
    return rx.el.div(
        _kpi(
            "Assets Analyzed",
            rx.el.p(
                s["count"].to(int).to_string(),
                class_name="text-xl font-semibold text-slate-100",
            ),
            rx.el.p(
                f"of {MarketsState.universe_size} in universe",
                class_name="text-xs text-slate-500",
            ),
            "layers",
            "bg-slate-800 text-slate-300 border border-slate-700",
        ),
        _kpi(
            "Avg. Return",
            rx.el.p(
                f"{s['avg_return']:.2f}%",
                class_name=rx.cond(
                    s["avg_return"].to(float) >= 0,
                    "text-xl font-semibold text-emerald-400",
                    "text-xl font-semibold text-rose-400",
                ),
            ),
            rx.el.p(
                f"Median {s['median']:.2f}%",
                class_name="text-xs text-slate-500",
            ),
            "trending-up",
            rx.cond(
                s["avg_return"].to(float) >= 0,
                "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
                "bg-rose-500/15 text-rose-300 border border-rose-500/30",
            ),
        ),
        _kpi(
            "Avg. CAGR",
            rx.el.p(
                f"{s['avg_cagr']:.2f}%",
                class_name=rx.cond(
                    s["avg_cagr"].to(float) >= 0,
                    "text-xl font-semibold text-emerald-400",
                    "text-xl font-semibold text-rose-400",
                ),
            ),
            rx.el.p("Annualized", class_name="text-xs text-slate-500"),
            "gauge",
            "bg-violet-500/15 text-violet-300 border border-violet-500/30",
        ),
        _kpi(
            "Winners / Losers",
            rx.el.p(
                f"{s['positive_count'].to(int)} / {s['negative_count'].to(int)}",
                class_name="text-xl font-semibold text-slate-100",
            ),
            rx.el.p(
                f"{s['positive_pct']:.1f}% positive",
                class_name="text-xs text-slate-500",
            ),
            "scale",
            "bg-amber-500/15 text-amber-300 border border-amber-500/30",
        ),
        _kpi(
            "Best Return",
            rx.el.p(
                f"{s['best']:.2f}%",
                class_name="text-xl font-semibold text-emerald-400",
            ),
            rx.el.p("Top performer", class_name="text-xs text-slate-500"),
            "trophy",
            "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
        ),
        _kpi(
            "Worst Return",
            rx.el.p(
                f"{s['worst']:.2f}%",
                class_name="text-xl font-semibold text-rose-400",
            ),
            rx.el.p("Biggest laggard", class_name="text-xs text-slate-500"),
            "trending-down",
            "bg-rose-500/15 text-rose-300 border border-rose-500/30",
        ),
        class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4",
    )


def _preset_button(item: rx.Var) -> rx.Component:
    is_active = (
        MarketsState.interval == item[0]
    ) & ~MarketsState.use_custom_range
    return rx.el.button(
        item[1],
        on_click=lambda: MarketsState.set_interval(item[0].to(str)),
        aria_label=f"Select {item[1]} preset",
        aria_pressed=is_active.to_string(),
        class_name=rx.cond(
            is_active,
            "px-3 py-1.5 rounded-md text-xs font-semibold bg-violet-600 text-white border border-violet-500 whitespace-nowrap focus:outline-hidden focus:ring-2 focus:ring-violet-400 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
            "px-3 py-1.5 rounded-md text-xs font-medium bg-slate-900/60 text-slate-300 border border-slate-700 hover:border-violet-500/50 whitespace-nowrap focus:outline-hidden focus:ring-2 focus:ring-violet-400",
        ),
        type="button",
    )


def _range_card() -> rx.Component:
    input_cn = "w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100"
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Time Range",
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    MarketsState.interval_summary,
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
                rx.foreach(INTERVAL_LABELS, _preset_button),
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
                        default_value=MarketsState.start_date,
                        on_change=MarketsState.set_start_date.debounce(200),
                        aria_label="Custom range start date",
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
                        default_value=MarketsState.end_date,
                        on_change=MarketsState.set_end_date.debounce(200),
                        aria_label="Custom range end date",
                        class_name=input_cn,
                    ),
                    class_name="flex-1 min-w-[140px]",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("x", class_name="h-3.5 w-3.5"),
                        "Clear",
                        on_click=MarketsState.clear_custom_range,
                        type="button",
                        aria_label="Clear custom date range",
                        class_name="px-3 py-2 text-xs font-medium text-slate-300 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-800 flex items-center gap-1.5 h-[38px] mt-[19px]",
                    ),
                    class_name="shrink-0",
                ),
                class_name="flex items-end gap-2 flex-wrap",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5 mb-4",
    )


def _filter_card() -> rx.Component:
    input_cn = "w-full pl-9 pr-3 py-2 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100 placeholder:text-slate-600"
    select_cn = "w-full px-3 py-2 pr-8 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100 appearance-none"
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Filters",
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    "Narrow the universe by search, sector, and asset class",
                    class_name="text-xs text-slate-500 mt-0.5",
                ),
            ),
            rx.el.button(
                rx.icon("rotate-ccw", class_name="h-3 w-3"),
                "Reset",
                on_click=MarketsState.reset_filters,
                aria_label="Reset all filters and time range",
                class_name="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-900 text-slate-300 border border-slate-700 hover:border-violet-500/50 focus:outline-hidden focus:ring-2 focus:ring-violet-400",
                type="button",
            ),
            class_name="flex items-start justify-between mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Search",
                    class_name="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1 block",
                ),
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2",
                    ),
                    rx.el.input(
                        placeholder="Ticker, name, sector…",
                        default_value=MarketsState.search_query,
                        on_change=MarketsState.set_search.debounce(300),
                        aria_label="Search assets by ticker, name, or sector",
                        class_name=input_cn,
                    ),
                    class_name="relative",
                ),
                class_name="min-w-0",
            ),
            rx.el.div(
                rx.el.label(
                    "Sector",
                    class_name="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1 block",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.foreach(
                            MarketsState.sector_options,
                            lambda s: rx.el.option(s, value=s),
                        ),
                        default_value=MarketsState.filter_sector,
                        on_change=MarketsState.set_sector,
                        aria_label="Filter by sector",
                        class_name=select_cn,
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Asset Class",
                    class_name="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1 block",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.foreach(
                            MarketsState.class_options,
                            lambda c: rx.el.option(c, value=c),
                        ),
                        default_value=MarketsState.filter_class,
                        on_change=MarketsState.set_class,
                        aria_label="Filter by asset class",
                        class_name=select_cn,
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-3",
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5 mb-4",
    )


def _performer_row(p: rx.Var) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    p["ticker"],
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    p["name"],
                    class_name="text-xs text-slate-500 truncate max-w-[200px]",
                ),
                rx.el.p(
                    f"{p['sector']} · {p['asset_class']}",
                    class_name="text-[11px] text-slate-600 mt-0.5",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    f"{p['cumulative']:.2f}%",
                    class_name=rx.cond(
                        p["is_positive"],
                        "text-sm font-semibold text-emerald-400 font-mono",
                        "text-sm font-semibold text-rose-400 font-mono",
                    ),
                ),
                rx.el.p(
                    f"{p['cagr']:.2f}% CAGR",
                    class_name="text-[11px] text-slate-500 font-mono text-right",
                ),
            ),
            class_name="flex items-center justify-between",
        ),
        href=f"/asset/{p['ticker']}",
        class_name="block py-2.5 border-b border-slate-800/60 last:border-0 hover:bg-slate-800/40 -mx-2 px-2 rounded transition-colors",
    )


def _performers_card(
    title: str, subtitle: str, icon: str, rows: rx.Var, tone: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    title, class_name="text-sm font-semibold text-slate-100"
                ),
                rx.el.p(subtitle, class_name="text-xs text-slate-500 mt-0.5"),
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-4 w-4"),
                class_name=f"h-9 w-9 rounded-lg flex items-center justify-center {tone}",
            ),
            class_name="flex items-start justify-between mb-2",
        ),
        rx.cond(
            rows.length() > 0,
            rx.el.div(rx.foreach(rows, _performer_row)),
            rx.el.p(
                "No matching data",
                class_name="text-xs text-slate-500 py-6 text-center",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _breakdown_row(b: rx.Var) -> rx.Component:
    abs_val = b["avg_return"].to(float) * rx.cond(
        b["avg_return"].to(float) >= 0, 1, -1
    )
    width_pct = rx.cond(abs_val * 2 > 100, 100, abs_val * 2)
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    b["name"], class_name="text-sm font-medium text-slate-100"
                ),
                rx.el.p(
                    f"{b['count']} assets",
                    class_name="text-[11px] text-slate-500",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    f"{b['avg_return']:.2f}%",
                    class_name=rx.cond(
                        b["avg_return"].to(float) >= 0,
                        "text-sm font-semibold text-emerald-400 font-mono",
                        "text-sm font-semibold text-rose-400 font-mono",
                    ),
                ),
                rx.el.p(
                    f"{b['worst']:.1f}% / {b['best']:.1f}%",
                    class_name="text-[11px] text-slate-500 font-mono text-right",
                ),
            ),
            class_name="flex items-center justify-between mb-1.5",
        ),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    b["avg_return"].to(float) >= 0,
                    "h-full bg-emerald-500 rounded-full",
                    "h-full bg-rose-500 rounded-full",
                ),
                style={"width": f"{width_pct}%"},
            ),
            class_name="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden",
        ),
        class_name="py-2.5 border-b border-slate-800/60 last:border-0",
    )


def _breakdown_card(
    title: str, subtitle: str, icon: str, rows: rx.Var
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    title, class_name="text-sm font-semibold text-slate-100"
                ),
                rx.el.p(subtitle, class_name="text-xs text-slate-500 mt-0.5"),
            ),
            rx.icon(icon, class_name="h-4 w-4 text-cyan-400"),
            class_name="flex items-start justify-between mb-2",
        ),
        rx.cond(
            rows.length() > 0,
            rx.el.div(rx.foreach(rows, _breakdown_row)),
            rx.el.p(
                "No breakdown data",
                class_name="text-xs text-slate-500 py-6 text-center",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _table_header_cell(label: str, key: str) -> rx.Component:
    is_active = MarketsState.sort_by == key
    return rx.el.th(
        rx.el.button(
            rx.el.span(label),
            rx.cond(
                is_active,
                rx.icon(
                    rx.cond(
                        MarketsState.sort_dir == "desc",
                        "arrow-down",
                        "arrow-up",
                    ),
                    class_name="h-3 w-3 ml-1",
                ),
                rx.icon(
                    "chevrons-up-down",
                    class_name="h-3 w-3 ml-1 text-slate-600",
                ),
            ),
            on_click=lambda: MarketsState.set_sort(key),
            class_name="flex items-center hover:text-slate-100",
            type="button",
        ),
        class_name="px-3 py-2 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap sticky top-0 bg-slate-900 z-10",
    )


def _quarter_header(lbl: rx.Var) -> rx.Component:
    return rx.el.th(
        lbl,
        class_name="px-2 py-2 text-right text-[10px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap sticky top-0 bg-slate-900 font-mono",
    )


def _quarter_return_cell(cell: rx.Var) -> rx.Component:
    return rx.el.td(
        rx.cond(
            cell["has_data"].to(bool),
            rx.el.div(
                cell["display"].to(str),
                class_name=_cell_class(cell["value"].to(float)),
            ),
            rx.el.p(
                cell["display"].to(str),
                class_name="text-xs text-slate-600 text-center",
            ),
        ),
        class_name="px-1 py-1",
    )


def _table_row(row: rx.Var) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.a(
                rx.el.p(
                    row["ticker"],
                    class_name="text-xs font-semibold text-slate-100 hover:text-violet-300",
                ),
                rx.el.p(
                    row["name"],
                    class_name="text-[10px] text-slate-500 truncate max-w-[160px]",
                ),
                href=f"/asset/{row['ticker']}",
                class_name="block",
            ),
            class_name="px-3 py-2 sticky left-0 bg-slate-950/95 z-[1] border-r border-slate-800",
        ),
        rx.el.td(
            rx.el.p(
                row["sector"],
                class_name="text-[11px] text-slate-400 whitespace-nowrap",
            ),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(
                row["asset_class"],
                class_name="text-[11px] text-slate-400 whitespace-nowrap",
            ),
            class_name="px-3 py-2",
        ),
        rx.foreach(
            row["quarter_cells"].to(list[dict[str, str | float | bool]]),
            _quarter_return_cell,
        ),
        rx.el.td(
            rx.cond(
                row["has_data"].to(bool),
                rx.el.div(
                    f"{row['cumulative'].to(float):.1f}%",
                    class_name=_cell_class(row["cumulative"].to(float)),
                ),
                rx.el.p("—", class_name="text-xs text-slate-600 text-center"),
            ),
            class_name="px-1 py-1",
        ),
        rx.el.td(
            rx.cond(
                row["has_data"].to(bool),
                rx.el.p(
                    f"{row['cagr'].to(float):.2f}%",
                    class_name=rx.cond(
                        row["cagr"].to(float) >= 0,
                        "text-xs font-semibold text-emerald-400 font-mono text-right",
                        "text-xs font-semibold text-rose-400 font-mono text-right",
                    ),
                ),
                rx.el.p("—", class_name="text-xs text-slate-600 text-right"),
            ),
            class_name="px-3 py-2",
        ),
        class_name="border-b border-slate-800/60 hover:bg-slate-800/40",
    )


def _returns_table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    MarketsState.report_title,
                    class_name="text-sm font-semibold text-slate-100",
                ),
                rx.el.p(
                    MarketsState.report_subtitle,
                    class_name="text-xs text-slate-500 mt-0.5",
                ),
                rx.el.p(
                    MarketsState.column_summary,
                    class_name="text-[11px] text-violet-300 bg-violet-500/10 border border-violet-500/30 rounded px-2 py-0.5 mt-1.5 w-fit font-medium",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        class_name="w-3 h-3 rounded-sm bg-rose-500",
                    ),
                    rx.el.span(
                        "≤ -10%",
                        class_name="text-[10px] font-medium text-slate-400",
                    ),
                    class_name="flex items-center gap-1",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name="w-3 h-3 rounded-sm bg-amber-500/40",
                    ),
                    rx.el.span(
                        "±3%",
                        class_name="text-[10px] font-medium text-slate-400",
                    ),
                    class_name="flex items-center gap-1",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name="w-3 h-3 rounded-sm bg-emerald-500",
                    ),
                    rx.el.span(
                        "≥ 20%",
                        class_name="text-[10px] font-medium text-slate-400",
                    ),
                    class_name="flex items-center gap-1",
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="flex items-start justify-between mb-3 flex-wrap gap-2",
        ),
        rx.cond(
            MarketsState.filtered_rows.length() > 0,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            _table_header_cell("Ticker", "ticker"),
                            rx.el.th(
                                "Sector",
                                class_name="px-3 py-2 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap sticky top-0 bg-slate-900",
                            ),
                            rx.el.th(
                                "Class",
                                class_name="px-3 py-2 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap sticky top-0 bg-slate-900",
                            ),
                            rx.foreach(
                                MarketsState.visible_quarter_labels,
                                _quarter_header,
                            ),
                            _table_header_cell("Cumulative", "cumulative"),
                            _table_header_cell("CAGR", "cagr"),
                            class_name="bg-slate-900 border-b border-slate-800",
                        ),
                    ),
                    rx.el.tbody(
                        rx.foreach(MarketsState.filtered_rows, _table_row),
                    ),
                    class_name="table-auto min-w-full",
                ),
                class_name="overflow-auto max-h-[640px] border border-slate-800 rounded-lg",
            ),
            rx.el.div(
                rx.icon(
                    "database",
                    class_name="h-8 w-8 text-slate-600 mb-2",
                ),
                rx.el.p(
                    "No matching assets",
                    class_name="text-sm font-medium text-slate-300",
                ),
                rx.el.p(
                    "Try adjusting filters or reset to defaults",
                    class_name="text-xs text-slate-500 mt-1",
                ),
                class_name="flex flex-col items-center justify-center py-16 bg-slate-950/40 rounded-lg",
            ),
        ),
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _empty_state() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("database", class_name="h-8 w-8 text-violet-300"),
            class_name="h-14 w-14 rounded-full bg-violet-500/15 border border-violet-500/30 flex items-center justify-center mb-3",
        ),
        rx.el.h3(
            "Loading market universe…",
            class_name="text-base font-semibold text-slate-100",
        ),
        rx.el.p(
            f"Analyzing {MarketsState.universe_size} tickers with daily prices "
            "across sectors and asset classes. Live data is fetched via Yahoo "
            "Finance with cached synthetic fallback for resilience.",
            class_name="text-sm text-slate-400 mt-1 max-w-md text-center",
        ),
        rx.cond(
            MarketsState.loading,
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-5 w-5 text-violet-400 animate-spin",
                ),
                rx.el.p(
                    MarketsState.status_message,
                    class_name="text-xs font-medium text-slate-300",
                ),
                class_name="flex items-center gap-2 mt-4",
            ),
            rx.el.button(
                rx.icon("play", class_name="h-4 w-4"),
                "Load Report",
                on_click=MarketsState.load_report,
                class_name="mt-4 inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-violet-600 rounded-lg hover:bg-violet-500 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
                type="button",
            ),
        ),
        class_name="flex flex-col items-center justify-center py-20 bg-slate-900/60 border border-slate-800/80 rounded-xl",
    )


def markets_content() -> rx.Component:
    return rx.el.div(
        _status_bar(),
        rx.cond(
            MarketsState.loaded,
            rx.el.div(
                _summary_grid(),
                _range_card(),
                _filter_card(),
                rx.el.div(
                    _performers_card(
                        "Top Performers",
                        "Highest cumulative returns in range",
                        "trophy",
                        MarketsState.top_performers,
                        "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
                    ),
                    _performers_card(
                        "Bottom Performers",
                        "Lowest cumulative returns in range",
                        "trending-down",
                        MarketsState.bottom_performers,
                        "bg-rose-500/15 text-rose-300 border border-rose-500/30",
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4",
                ),
                rx.el.div(
                    _breakdown_card(
                        "Sector Breakdown",
                        "Average cumulative return by sector",
                        "chart-bar",
                        MarketsState.sector_breakdown,
                    ),
                    _breakdown_card(
                        "Asset Class Breakdown",
                        "Average cumulative return by class",
                        "layers",
                        MarketsState.class_breakdown,
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4",
                ),
                _returns_table(),
                class_name="flex flex-col",
            ),
            _empty_state(),
        ),
        class_name="flex flex-col",
    )
