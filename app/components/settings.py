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
                    rx.icon(icon, class_name="h-4 w-4 text-blue-600"),
                    class_name="h-8 w-8 rounded-lg bg-blue-50 flex items-center justify-center",
                ),
                rx.el.div(
                    rx.el.h3(
                        title,
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        subtitle, class_name="text-xs text-gray-500 mt-0.5"
                    ),
                ),
                class_name="flex items-start gap-3",
            ),
            class_name="mb-4",
        ),
        content,
        class_name="bg-white border border-gray-200 rounded-xl p-5",
    )


def _toggle(label: str, sub: str, checked: rx.Var, on_click) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-900"),
            rx.el.p(sub, class_name="text-xs text-gray-500 mt-0.5"),
        ),
        rx.el.button(
            rx.el.span(
                class_name=rx.cond(
                    checked,
                    "inline-block h-4 w-4 rounded-full bg-white shadow transform translate-x-4 transition-transform",
                    "inline-block h-4 w-4 rounded-full bg-white shadow transform translate-x-0 transition-transform",
                ),
            ),
            on_click=on_click,
            class_name=rx.cond(
                checked,
                "relative inline-flex h-5 w-9 items-center rounded-full bg-blue-600 transition-colors shrink-0 px-0.5",
                "relative inline-flex h-5 w-9 items-center rounded-full bg-gray-300 transition-colors shrink-0 px-0.5",
            ),
            type="button",
        ),
        class_name="flex items-center justify-between py-3 border-b border-gray-100 last:border-0",
    )


def _source_kind_badge(kind: rx.Var) -> rx.Component:
    return rx.match(
        kind,
        (
            "API",
            rx.el.span(
                "API",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100 w-fit",
            ),
        ),
        (
            "Manual",
            rx.el.span(
                "Manual",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 w-fit",
            ),
        ),
        (
            "CSV",
            rx.el.span(
                "CSV",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100 w-fit",
            ),
        ),
        (
            "Cache",
            rx.el.span(
                "Cache",
                class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-100 w-fit",
            ),
        ),
        rx.el.span(
            kind,
            class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 w-fit",
        ),
    )


def _source_row(s: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    s["priority"].to_string(),
                    class_name="h-6 w-6 rounded-md bg-gray-100 text-gray-600 text-xs font-mono flex items-center justify-center shrink-0",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            s["name"],
                            class_name="text-sm font-semibold text-gray-900",
                        ),
                        _source_kind_badge(s["kind"]),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.p(
                        s["description"],
                        class_name="text-xs text-gray-500 mt-0.5",
                    ),
                ),
                class_name="flex items-start gap-3 flex-1 min-w-0",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        class_name=rx.cond(
                            s["enabled"],
                            "h-2 w-2 rounded-full bg-emerald-500",
                            "h-2 w-2 rounded-full bg-gray-300",
                        ),
                    ),
                    rx.el.p(
                        s["status"],
                        class_name="text-[11px] font-medium text-gray-600",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                rx.el.p(
                    s["last_sync"],
                    class_name="text-[11px] text-gray-400 mt-0.5 font-mono",
                ),
                class_name="text-right shrink-0",
            ),
            class_name="flex items-start justify-between gap-3 mb-2",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("chevron-up", class_name="h-3.5 w-3.5"),
                on_click=lambda: SettingsState.move_source_up(s["id"].to(str)),
                class_name="p-1.5 rounded-md text-gray-500 hover:bg-gray-100 border border-gray-200",
                type="button",
            ),
            rx.el.button(
                rx.icon("chevron-down", class_name="h-3.5 w-3.5"),
                on_click=lambda: SettingsState.move_source_down(
                    s["id"].to(str)
                ),
                class_name="p-1.5 rounded-md text-gray-500 hover:bg-gray-100 border border-gray-200",
                type="button",
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-3.5 w-3.5"),
                "Sync",
                on_click=lambda: SettingsState.sync_source(s["id"].to(str)),
                class_name="px-2 py-1 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-200 flex items-center gap-1",
                type="button",
            ),
            rx.el.button(
                rx.cond(s["enabled"], "Disable", "Enable"),
                on_click=lambda: SettingsState.toggle_source(s["id"].to(str)),
                class_name=rx.cond(
                    s["enabled"],
                    "px-2 py-1 rounded-md text-xs font-medium text-red-600 bg-white hover:bg-red-50 border border-red-100",
                    "px-2 py-1 rounded-md text-xs font-medium text-emerald-700 bg-white hover:bg-emerald-50 border border-emerald-100",
                ),
                type="button",
            ),
            class_name="flex items-center gap-1.5",
        ),
        class_name="p-3 bg-gray-50/70 border border-gray-100 rounded-lg mb-2 last:mb-0",
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
    return _section(
        "Preferences",
        "Portfolio display and refresh behavior",
        "sliders_horizontal",
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Currency",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.foreach(
                                CURRENCIES,
                                lambda c: rx.el.option(c, value=c),
                            ),
                            default_value=SettingsState.currency,
                            on_change=SettingsState.set_currency,
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
                        "Default Chart Range",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.el.option("1M", value="1M"),
                            rx.el.option("3M", value="3M"),
                            rx.el.option("6M", value="6M"),
                            rx.el.option("1Y", value="1Y"),
                            default_value=SettingsState.default_range,
                            on_change=SettingsState.set_default_range,
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
                        "Refresh Interval (min)",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        type="number",
                        min="1",
                        default_value=SettingsState.refresh_interval_min.to_string(),
                        on_change=SettingsState.set_refresh_interval.debounce(
                            300
                        ),
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Cache TTL (min)",
                        class_name="text-xs font-medium text-gray-700 mb-1 block",
                    ),
                    rx.el.input(
                        type="number",
                        min="1",
                        default_value=SettingsState.cache_ttl_min.to_string(),
                        on_change=SettingsState.set_cache_ttl.debounce(300),
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
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
                    class_name="px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-1.5",
                    type="button",
                ),
                class_name="mt-3 pt-3 border-t border-gray-100",
            ),
        ),
    )


def _override_row(o: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                o["symbol"],
                class_name="text-sm font-semibold text-gray-900",
            ),
            rx.el.p(
                f"Updated {o['updated']}",
                class_name="text-[11px] text-gray-500",
            ),
        ),
        rx.el.div(
            rx.el.p(
                f"${o['price'].to(float):,.2f}",
                class_name="text-sm font-semibold text-gray-900 font-mono",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-3.5 w-3.5"),
                on_click=lambda: SettingsState.remove_override(
                    o["symbol"].to(str)
                ),
                class_name="p-1 rounded-md text-gray-400 hover:bg-red-50 hover:text-red-600",
                type="button",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex items-center justify-between py-2 border-b border-gray-100 last:border-0",
    )


def _overrides_section() -> rx.Component:
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
                        class_name="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                    rx.el.input(
                        name="price",
                        type="number",
                        step="0.01",
                        placeholder="Price",
                        required=True,
                        class_name="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white text-gray-900",
                    ),
                    rx.el.button(
                        rx.icon("plus", class_name="h-4 w-4"),
                        "Save",
                        type="submit",
                        class_name="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-1.5",
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
                    class_name="text-xs text-gray-400 mt-3",
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
                rx.icon("circle-check", class_name="h-4 w-4 text-emerald-600"),
                rx.icon("circle-alert", class_name="h-4 w-4 text-red-600"),
            ),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(r["date"], class_name="text-xs font-mono text-gray-700"),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(r["type"], class_name="text-xs font-medium text-gray-700"),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(
                r["symbol"], class_name="text-xs font-semibold text-gray-900"
            ),
            class_name="px-3 py-2",
        ),
        rx.el.td(
            rx.el.p(
                f"{r['quantity'].to(float):,.4f}",
                class_name="text-xs text-gray-700 font-mono",
            ),
            class_name="px-3 py-2 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${r['price'].to(float):,.2f}",
                class_name="text-xs text-gray-700 font-mono",
            ),
            class_name="px-3 py-2 text-right",
        ),
        rx.el.td(
            rx.el.p(
                f"${r['fees'].to(float):,.2f}",
                class_name="text-xs text-gray-500 font-mono",
            ),
            class_name="px-3 py-2 text-right",
        ),
        rx.el.td(
            rx.cond(
                r["error"] != "",
                rx.el.p(
                    r["error"],
                    class_name="text-[11px] text-red-600 font-medium",
                ),
                rx.el.p("—", class_name="text-[11px] text-gray-300"),
            ),
            class_name="px-3 py-2",
        ),
        class_name=rx.cond(
            r["valid"],
            "border-b border-gray-100",
            "border-b border-gray-100 bg-red-50/30",
        ),
    )


def _csv_import_section() -> rx.Component:
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
                        class_name="mr-2",
                    ),
                    rx.el.span(
                        "Transactions only",
                        class_name="text-xs font-medium text-gray-700",
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
                        class_name="mr-2",
                    ),
                    rx.el.span(
                        "Transactions + update holdings",
                        class_name="text-xs font-medium text-gray-700",
                    ),
                    class_name="flex items-center cursor-pointer",
                ),
                class_name="flex items-center gap-4 mb-3",
            ),
            rx.upload.root(
                rx.el.div(
                    rx.icon(
                        "cloud-upload",
                        class_name="h-8 w-8 text-gray-400 mb-2",
                    ),
                    rx.el.p(
                        "Drop your CSV file here",
                        class_name="text-sm font-medium text-gray-700",
                    ),
                    rx.el.p(
                        "or click to browse — expected columns: date, type, symbol, quantity, price, fees, notes",
                        class_name="text-xs text-gray-500 mt-1 text-center max-w-sm",
                    ),
                    class_name="flex flex-col items-center justify-center py-6",
                ),
                id=CSV_UPLOAD_ID,
                accept={"text/csv": [".csv"]},
                max_files=1,
                on_drop=SettingsState.handle_csv_upload(
                    rx.upload_files(upload_id=CSV_UPLOAD_ID)
                ),
                class_name="border-2 border-dashed border-gray-300 rounded-xl bg-gray-50/50 hover:bg-blue-50/40 hover:border-blue-300 transition-colors cursor-pointer",
            ),
            rx.cond(
                SettingsState.csv_error != "",
                rx.el.div(
                    rx.icon(
                        "circle-alert",
                        class_name="h-3.5 w-3.5 text-red-600",
                    ),
                    rx.el.p(
                        SettingsState.csv_error,
                        class_name="text-xs font-medium text-red-700",
                    ),
                    class_name="flex items-center gap-2 mt-3 px-3 py-2 bg-red-50 border border-red-100 rounded-lg",
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
                                class_name="text-xs font-medium text-gray-700",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    rx.el.span(
                                        SettingsState.valid_csv_count.to_string(),
                                        class_name="font-mono font-semibold text-emerald-700",
                                    ),
                                    " valid",
                                    class_name="text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded",
                                ),
                                rx.el.span(
                                    rx.el.span(
                                        SettingsState.invalid_csv_count.to_string(),
                                        class_name="font-mono font-semibold text-red-700",
                                    ),
                                    " invalid",
                                    class_name="text-[11px] text-red-700 bg-red-50 px-2 py-0.5 rounded",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            class_name="flex items-center justify-between mb-2 flex-wrap gap-2",
                        ),
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th(
                                            "",
                                            class_name="px-3 py-2 text-left text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Date",
                                            class_name="px-3 py-2 text-left text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Type",
                                            class_name="px-3 py-2 text-left text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Symbol",
                                            class_name="px-3 py-2 text-left text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Qty",
                                            class_name="px-3 py-2 text-right text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Price",
                                            class_name="px-3 py-2 text-right text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Fees",
                                            class_name="px-3 py-2 text-right text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        rx.el.th(
                                            "Issue",
                                            class_name="px-3 py-2 text-left text-[10px] font-semibold text-gray-500 uppercase",
                                        ),
                                        class_name="bg-gray-50 border-b border-gray-200",
                                    ),
                                ),
                                rx.el.tbody(
                                    rx.foreach(
                                        SettingsState.csv_preview, _csv_row
                                    ),
                                ),
                                class_name="table-auto min-w-full",
                            ),
                            class_name="overflow-x-auto max-h-72 overflow-y-auto border border-gray-200 rounded-lg",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=SettingsState.cancel_csv_import,
                                type="button",
                                class_name="px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50",
                            ),
                            rx.el.button(
                                rx.icon("check", class_name="h-3.5 w-3.5"),
                                f"Import {SettingsState.valid_csv_count} rows",
                                on_click=SettingsState.confirm_csv_import,
                                type="button",
                                class_name="px-3 py-2 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-1.5",
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
                        class_name="text-xs text-emerald-700 mt-3 font-medium",
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
