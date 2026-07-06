import reflex as rx
from app.states.market_state import MarketState


def _asset_card(item: rx.Var) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        item["symbol"],
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    rx.el.span(
                        item["asset_class"],
                        class_name="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100 w-fit",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.p(
                    item["name"],
                    class_name="text-xs text-gray-600 mt-1 truncate",
                ),
                rx.el.p(
                    item["sector"],
                    class_name="text-[11px] text-gray-400 mt-0.5",
                ),
            ),
            rx.el.div(
                rx.icon(
                    "arrow-up-right",
                    class_name="h-4 w-4 text-gray-400 group-hover:text-blue-600 transition-colors",
                ),
                class_name="shrink-0",
            ),
            class_name="flex items-start justify-between gap-3",
        ),
        href=f"/asset/{item['symbol']}",
        class_name="group block bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition-all",
    )


def discover_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
                ),
                rx.el.input(
                    placeholder="Search by symbol, name, or sector…",
                    default_value=MarketState.discover_query,
                    on_change=MarketState.set_discover_query.debounce(300),
                    class_name="w-full pl-9 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white",
                ),
                class_name="relative flex-1 max-w-2xl",
            ),
            class_name="mb-5",
        ),
        rx.el.div(
            rx.el.p(
                "Popular Assets",
                class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3",
            ),
            rx.el.div(
                rx.foreach(MarketState.filtered_discover, _asset_card),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3",
            ),
            rx.cond(
                MarketState.filtered_discover.length() == 0,
                rx.el.div(
                    rx.icon(
                        "search-x", class_name="h-8 w-8 text-gray-300 mb-2"
                    ),
                    rx.el.p(
                        "No matching assets",
                        class_name="text-sm font-medium text-gray-600",
                    ),
                    rx.el.p(
                        "Try a different search term",
                        class_name="text-xs text-gray-400 mt-1",
                    ),
                    class_name="flex flex-col items-center justify-center py-16 bg-white border border-gray-200 rounded-xl",
                ),
                rx.el.div(),
            ),
        ),
        class_name="flex flex-col",
    )
