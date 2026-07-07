import reflex as rx
from app.states.settings_state import SettingsState, CURRENCIES

CSV_UPLOAD_ID = "csv_upload"


def _section(
    title: str, subtitle: str, icon: str, content: rx.Component
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(icon, class_name="h-4 w-4 text-violet-300"),
                    class_name="h-8 w-8 rounded-lg bg-violet-500/15 border border-violet-500/30 flex items-center justify-center",
                ),
                rx.el.div(
                    rx.el.h3(
                        title,
                        class_name="text-sm font-semibold text-slate-100",
                    ),
                    rx.el.p(
                        subtitle, class_name="text-xs text-slate-500 mt-0.5"
                    ),
                ),
                class_name="flex items-start gap-3",
            ),
            class_name="mb-4",
        ),
        content,
        class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-xl p-5",
    )


def _toggle(label: str, sub: str, checked: rx.Var, on_click) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-slate-100"),
            rx.el.p(sub, class_name="text-xs text-slate-500 mt-0.5"),
        ),
        rx.el.button(
            rx.el.span(
                class_name=rx.cond(
                    checked,
                    "inline-block h-4 w-4 rounded-full bg-white shadow transform translate-x-4 transition-transform",
                    "inline-block h-4 w-4 rounded-full bg-slate-300 shadow transform translate-x-0 transition-transform",
                ),
            ),
            on_click=on_click,
            class_name=rx.cond(
                checked,
                "relative inline-flex h-5 w-9 items-center rounded-full bg-violet-600 transition-colors shrink-0 px-0.5 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
                "relative inline-flex h-5 w-9 items-center rounded-full bg-slate-700 transition-colors shrink-0 px-0.5",
            ),
            type="button",
        ),
        class_name="flex items-center justify-between py-3 border-b border-slate-800/60 last:border-0",
    )


def _source_kind_badge(kind: rx.Var) -> rx.Component:
    return rx.match(
        kind,
        (
            "API",
            rx.el.span(
                "API",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-violet-500/15 text-violet-300 border border-violet-500/30 w-fit",
            ),
        ),
        (
            "Manual",
            rx.el.span(
                "Manual",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 w-fit",
            ),
        ),
        (
            "CSV",
            rx.el.span(
                "CSV",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 w-fit",
            ),
        ),
        (
            "Cache",
            rx.el.span(
                "Cache",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 w-fit",
            ),
        ),
        rx.el.span(
            kind,
            class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 w-fit",
        ),
    )


def _source_row(s: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    s["priority"].to_string(),
                    class_name="h-6 w-6 rounded-md bg-slate-800 text-slate-300 text-xs font-mono flex items-center justify-center shrink-0 border border-slate-700",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            s["name"],
                            class_name="text-sm font-semibold text-slate-100",
                        ),
                        _source_kind_badge(s["kind"]),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.p(
                        s["description"],
                        class_name="text-xs text-slate-500 mt-0.5",
                    ),
                ),
                class_name="flex items-start gap-3 flex-1 min-w-0",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        class_name=rx.cond(
                            s["enabled"],
                            "h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]",
                            "h-2 w-2 rounded-full bg-slate-600",
                        ),
                    ),
                    rx.el.p(
                        s["status"],
                        class_name="text-[11px] font-medium text-slate-400",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                rx.el.p(
                    s["last_sync"],
                    class_name="text-[11px] text-slate-500 mt-0.5 font-mono",
                ),
                class_name="text-right shrink-0",
            ),
            class_name="flex items-start justify-between gap-3 mb-2",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("chevron-up", class_name="h-3.5 w-3.5"),
                on_click=lambda: SettingsState.move_source_up(s["id"].to(str)),
                class_name="p-1.5 rounded-md text-slate-400 hover:bg-slate-800 border border-slate-700",
                type="button",
            ),
            rx.el.button(
                rx.icon("chevron-down", class_name="h-3.5 w-3.5"),
                on_click=lambda: SettingsState.move_source_down(
                    s["id"].to(str)
                ),
                class_name="p-1.5 rounded-md text-slate-400 hover:bg-slate-800 border border-slate-700",
                type="button",
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-3.5 w-3.5"),
                "Sync",
                on_click=lambda: SettingsState.sync_source(s["id"].to(str)),
                class_name="px-2 py-1 rounded-md text-xs font-medium text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-700 flex items-center gap-1",
                type="button",
            ),
            rx.el.button(
                rx.cond(s["enabled"], "Disable", "Enable"),
                on_click=lambda: SettingsState.toggle_source(s["id"].to(str)),
                class_name=rx.cond(
                    s["enabled"],
                    "px-2 py-1 rounded-md text-xs font-medium text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30",
                    "px-2 py-1 rounded-md text-xs font-medium text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30",
                ),
                type="button",
            ),
            class_name="flex items-center gap-1.5",
        ),
        class_name="p-3 bg-slate-950/60 border border-slate-800 rounded-lg mb-2 last:mb-0",
    )


def _data_sources_section() -> rx.Component:
    return _section(
        "Data Sources",
        "Manage priority order and status of live, manual, and cached feeds",
        "database",
        rx.el.div(
            rx.foreach(SettingsState.sorted_data_sources, _source_row),
        ),
    )


def _preferences_section() -> rx.Component:
    input_cn = "w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100"
    select_cn = "w-full px-3 py-2 pr-8 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100 appearance-none"
    label_cn = "text-xs font-medium text-slate-300 mb-1 block"
    return _section(
        "Preferences",
        "Portfolio display and refresh behavior",
        "sliders_horizontal",
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.label("Currency", class_name=label_cn),
                    rx.el.div(
                        rx.el.select(
                            rx.foreach(
                                CURRENCIES,
                                lambda c: rx.el.option(c, value=c),
                            ),
                            default_value=SettingsState.currency,
                            on_change=SettingsState.set_currency,
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
                    rx.el.label("Default Chart Range", class_name=label_cn),
                    rx.el.div(
                        rx.el.select(
                            rx.el.option("1M", value="1M"),
                            rx.el.option("3M", value="3M"),
                            rx.el.option("6M", value="6M"),
                            rx.el.option("1Y", value="1Y"),
                            default_value=SettingsState.default_range,
                            on_change=SettingsState.set_default_range,
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
                    rx.el.label("Refresh Interval (min)", class_name=label_cn),
                    rx.el.input(
                        type="number",
                        min="1",
                        default_value=SettingsState.refresh_interval_min.to_string(),
                        on_change=SettingsState.set_refresh_interval.debounce(
                            300
                        ),
                        class_name=input_cn,
                    ),
                ),
                rx.el.div(
                    rx.el.label("Cache TTL (min)", class_name=label_cn),
                    rx.el.input(
                        type="number",
                        min="1",
                        default_value=SettingsState.cache_ttl_min.to_string(),
                        on_change=SettingsState.set_cache_ttl.debounce(300),
                        class_name=input_cn,
                    ),
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3",
            ),
            _toggle(
                "Show percent change",
                "Display % change alongside dollar amounts",
                SettingsState.show_percent_change,
                SettingsState.toggle_percent_change,
            ),
            _toggle(
                "Auto-refresh prices",
                "Automatically pull new quotes on the interval above",
                SettingsState.auto_refresh,
                SettingsState.toggle_auto_refresh,
            ),
            _toggle(
                "Enable notifications",
                "Get alerts on large moves and dividends",
                SettingsState.notifications_enabled,
                SettingsState.toggle_notifications,
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("trash", class_name="h-3.5 w-3.5"),
                    "Clear cache",
                    on_click=SettingsState.clear_cache,
                    class_name="px-3 py-2 text-xs font-medium text-slate-300 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-800 flex items-center gap-1.5",
                    type="button",
                ),
                class_name="mt-3 pt-3 border-t border-slate-800",
            ),
        ),
    )


def _override_row(o: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                o["symbol"],
                class_name="text-sm font-semibold text-slate-100",
            ),
            rx.el.p(
                f"Updated {o['updated']}",
                class_name="text-[11px] text-slate-500",
            ),
        ),
        rx.el.div(
            rx.el.p(
                f"${o['price'].to(float):,.2f}",
                class_name="text-sm font-semibold text-slate-100 font-mono",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-3.5 w-3.5"),
                on_click=lambda: SettingsState.remove_override(
                    o["symbol"].to(str)
                ),
                class_name="p-1 rounded-md text-slate-500 hover:bg-rose-500/15 hover:text-rose-300",
                type="button",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex items-center justify-between py-2 border-b border-slate-800/60 last:border-0",
    )


def _overrides_section() -> rx.Component:
    input_cn = "flex-1 px-3 py-2 text-sm bg-slate-950 border border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-violet-400 text-slate-100 placeholder:text-slate-600"
    return _section(
        "Manual Price Overrides",
        "Override live prices for illiquid or private assets",
        "pencil",
        rx.el.div(
            rx.el.form(
                rx.el.div(
                    rx.el.input(
                        name="symbol",
                        placeholder="Symbol (e.g. USD)",
                        required=True,
                        class_name=input_cn,
                    ),
                    rx.el.input(
                        name="price",
                        type="number",
                        step="0.01",
                        placeholder="Price",
                        required=True,
                        class_name=input_cn,
                    ),
                    rx.el.button(
                        rx.icon("plus", class_name="h-4 w-4"),
                        "Save",
                        type="submit",
                        class_name="px-3 py-2 text-sm font-medium text-white bg-violet-600 rounded-lg hover:bg-violet-500 flex items-center gap-1.5 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
                    ),
                    class_name="flex items-center gap-2",
                ),
                on_submit=SettingsState.apply_override,
                reset_on_submit=True,
            ),
            rx.el.div(
                rx.foreach(SettingsState.manual_overrides, _override_row),
                class_name="mt-3",
            ),
            rx.cond(
                SettingsState.manual_overrides.length() == 0,
                rx.el.p(
                    "No manual overrides yet",
                    class_name="text-xs text-slate-500 mt-3",
                ),
                rx.el.div(),
            ),
        ),
    )


def _csv_row(r: rx.Var) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.cond(
                r["valid"],
                rx.icon("circle-check", class_name="h-4 w-4 text-emerald-400"),
                rx.icon("circle-alert", class_name="h-4 w-4 text-rose-400"),
            ),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(r["date"], class_name="text-xs font-mono text-slate-300"),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(r["type"], class_name="text-xs font-medium text-slate-300"),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(
                r["symbol"], class_name="text-xs font-semibold text-slate-100"
            ),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(
                f"{r['quantity'].to(float):,.4f}",
                class_name="text-xs text-slate-300 font-mono",
            ),
            class_name="px-3 py-2 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${r['price'].to(float):,.2f}",
                class_name="text-xs text-slate-300 font-mono",
            ),
            class_name="px-3 py-2 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${r['fees'].to(float):,.2f}",
                class_name="text-xs text-slate-500 font-mono",
            ),
            class_name="px-3 py-2 text-right",
        ),
        rx.el.td(
            rx.cond(
                r["error"] != "",
                rx.el.p(
                    r["error"],
                    class_name="text-[11px] text-rose-300 font-medium",
                ),
                rx.el.p("—", class_name="text-[11px] text-slate-600"),
            ),
            class_name="px-3 py-2",
        ),
        class_name=rx.cond(
            r["valid"],
            "border-b border-slate-800/60",
            "border-b border-slate-800/60 bg-rose-500/5",
        ),
    )


def _csv_import_section() -> rx.Component:
    th_cn = (
        "px-3 py-2 text-left text-[10px] font-semibold text-slate-400 uppercase"
    )
    return _section(
        "CSV Import",
        "Bulk import transactions from your broker's export",
        "upload",
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="radio",
                        name="csv_target",
                        value="transactions",
                        checked=SettingsState.csv_import_target
                        == "transactions",
                        on_change=lambda: SettingsState.set_csv_import_target(
                            "transactions"
                        ),
                        class_name="mr-2 accent-violet-500",
                    ),
                    rx.el.span(
                        "Transactions only",
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center cursor-pointer",
                ),
                rx.el.label(
                    rx.el.input(
                        type="radio",
                        name="csv_target",
                        value="holdings",
                        checked=SettingsState.csv_import_target == "holdings",
                        on_change=lambda: SettingsState.set_csv_import_target(
                            "holdings"
                        ),
                        class_name="mr-2 accent-violet-500",
                    ),
                    rx.el.span(
                        "Transactions + update holdings",
                        class_name="text-xs font-medium text-slate-300",
                    ),
                    class_name="flex items-center cursor-pointer",
                ),
                class_name="flex items-center gap-4 mb-3",
            ),
            rx.upload.root(
                rx.el.div(
                    rx.icon(
                        "cloud-upload",
                        class_name="h-8 w-8 text-slate-500 mb-2",
                    ),
                    rx.el.p(
                        "Drop your CSV file here",
                        class_name="text-sm font-medium text-slate-200",
                    ),
                    rx.el.p(
                        "or click to browse — expected columns: date, type, symbol, quantity, price, fees, notes",
                        class_name="text-xs text-slate-500 mt-1 text-center max-w-sm",
                    ),
                    class_name="flex flex-col items-center justify-center py-6",
                ),
                id=CSV_UPLOAD_ID,
                accept={"text/csv": [".csv"]},
                max_files=1,
                on_drop=SettingsState.handle_csv_upload(
                    rx.upload_files(upload_id=CSV_UPLOAD_ID)
                ),
                class_name="border-2 border-dashed border-slate-700 rounded-xl bg-slate-950/40 hover:bg-violet-500/5 hover:border-violet-500/50 transition-colors cursor-pointer",
            ),
            rx.cond(
                SettingsState.csv_error != "",
                rx.el.div(
                    rx.icon(
                        "circle-alert",
                        class_name="h-3.5 w-3.5 text-rose-400",
                    ),
                    rx.el.p(
                        SettingsState.csv_error,
                        class_name="text-xs font-medium text-rose-300",
                    ),
                    class_name="flex items-center gap-2 mt-3 px-3 py-2 bg-rose-500/10 border border-rose-500/30 rounded-lg",
                ),
                rx.el.div(),
            ),
            rx.cond(
                SettingsState.csv_preview.length() > 0,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                SettingsState.csv_status,
                                class_name="text-xs font-medium text-slate-300",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    rx.el.span(
                                        SettingsState.valid_csv_count.to_string(),
                                        class_name="font-mono font-semibold text-emerald-300",
                                    ),
                                    " valid",
                                    class_name="text-[11px] text-emerald-300 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded",
                                ),
                                rx.el.span(
                                    rx.el.span(
                                        SettingsState.invalid_csv_count.to_string(),
                                        class_name="font-mono font-semibold text-rose-300",
                                    ),
                                    " invalid",
                                    class_name="text-[11px] text-rose-300 bg-rose-500/10 border border-rose-500/30 px-2 py-0.5 rounded",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            class_name="flex items-center justify-between mb-2 flex-wrap gap-2",
                        ),
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th("", class_name=th_cn),
                                        rx.el.th("Date", class_name=th_cn),
                                        rx.el.th("Type", class_name=th_cn),
                                        rx.el.th("Symbol", class_name=th_cn),
                                        rx.el.th(
                                            "Qty",
                                            class_name="px-3 py-2 text-right text-[10px] font-semibold text-slate-400 uppercase",
                                        ),
                                        rx.el.th(
                                            "Price",
                                            class_name="px-3 py-2 text-right text-[10px] font-semibold text-slate-400 uppercase",
                                        ),
                                        rx.el.th(
                                            "Fees",
                                            class_name="px-3 py-2 text-right text-[10px] font-semibold text-slate-400 uppercase",
                                        ),
                                        rx.el.th("Issue", class_name=th_cn),
                                        class_name="bg-slate-900/80 border-b border-slate-800",
                                    ),
                                ),
                                rx.el.tbody(
                                    rx.foreach(
                                        SettingsState.csv_preview, _csv_row
                                    ),
                                ),
                                class_name="table-auto min-w-full",
                            ),
                            class_name="overflow-x-auto max-h-72 overflow-y-auto border border-slate-800 rounded-lg",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=SettingsState.cancel_csv_import,
                                type="button",
                                class_name="px-3 py-2 text-xs font-medium text-slate-300 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-800",
                            ),
                            rx.el.button(
                                rx.icon("check", class_name="h-3.5 w-3.5"),
                                f"Import {SettingsState.valid_csv_count} rows",
                                on_click=SettingsState.confirm_csv_import,
                                type="button",
                                class_name="px-3 py-2 text-xs font-medium text-white bg-violet-600 rounded-lg hover:bg-violet-500 flex items-center gap-1.5 shadow-[0_0_12px_-4px_rgba(139,92,246,0.6)]",
                            ),
                            class_name="flex items-center justify-end gap-2 mt-3",
                        ),
                    ),
                    class_name="mt-3",
                ),
                rx.cond(
                    SettingsState.csv_status != "",
                    rx.el.p(
                        SettingsState.csv_status,
                        class_name="text-xs text-emerald-300 mt-3 font-medium",
                    ),
                    rx.el.div(),
                ),
            ),
        ),
    )


def settings_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            _data_sources_section(),
            _preferences_section(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4",
        ),
        rx.el.div(
            _csv_import_section(),
            _overrides_section(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-4",
        ),
        class_name="flex flex-col",
    )
