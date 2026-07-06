import reflex as rx


def _nav_item(
    icon: str, label: str, href: str, active_route: str
) -> rx.Component:
    is_active = active_route == href
    return rx.el.a(
        rx.icon(icon, class_name="h-4 w-4 shrink-0"),
        rx.el.span(label, class_name="text-sm font-medium"),
        href=href,
        aria_label=f"Navigate to {label}",
        aria_current=rx.cond(is_active, "page", "false"),
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 px-3 py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-100 focus:outline-hidden focus:ring-2 focus:ring-blue-500",
            "flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors focus:outline-hidden focus:ring-2 focus:ring-blue-500",
        ),
    )


def sidebar(active_route: str = "/") -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "chart-candlestick", class_name="h-5 w-5 text-white"
                    ),
                    class_name="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center",
                    aria_hidden="true",
                ),
                rx.el.div(
                    rx.el.p(
                        "Portfolio",
                        class_name="text-sm font-semibold text-gray-900 leading-tight",
                    ),
                    rx.el.p(
                        "Companion",
                        class_name="text-xs text-gray-500 leading-tight",
                    ),
                ),
                class_name="flex items-center gap-3 px-4 h-16 border-b border-gray-200",
            ),
            rx.el.nav(
                rx.el.p(
                    "MAIN",
                    class_name="text-[10px] font-semibold text-gray-400 tracking-wider px-3 mb-2",
                ),
                _nav_item("layout-dashboard", "Overview", "/", active_route),
                _nav_item("wallet", "Holdings", "/holdings", active_route),
                _nav_item(
                    "chart-line", "Performance", "/performance", active_route
                ),
                rx.el.p(
                    "MARKETS",
                    class_name="text-[10px] font-semibold text-gray-400 tracking-wider px-3 mt-6 mb-2",
                ),
                _nav_item("search", "Discover", "/discover", active_route),
                _nav_item("chart-bar", "Markets", "/markets", active_route),
                rx.el.p(
                    "MANAGE",
                    class_name="text-[10px] font-semibold text-gray-400 tracking-wider px-3 mt-6 mb-2",
                ),
                _nav_item(
                    "arrow-left-right",
                    "Transactions",
                    "/transactions",
                    active_route,
                ),
                _nav_item("settings", "Settings", "/settings", active_route),
                class_name="flex flex-col gap-1 p-3 flex-1 overflow-y-auto",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.img(
                        src="https://api.dicebear.com/9.x/notionists/svg?seed=investor",
                        class_name="h-8 w-8 rounded-full bg-gray-100",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Alex Morgan",
                            class_name="text-xs font-semibold text-gray-900 leading-tight",
                        ),
                        rx.el.p(
                            "Premium Plan",
                            class_name="text-[11px] text-gray-500 leading-tight",
                        ),
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="border-t border-gray-200 p-4",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name="hidden md:flex flex-col w-60 shrink-0 bg-white border-r border-gray-200 h-screen sticky top-0",
        aria_label="Primary navigation",
    )


def mobile_header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.icon("chart-candlestick", class_name="h-4 w-4 text-white"),
            class_name="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center",
        ),
        rx.el.p(
            "Portfolio Companion",
            class_name="text-sm font-semibold text-gray-900",
        ),
        class_name="md:hidden flex items-center gap-3 px-4 h-14 bg-white border-b border-gray-200 sticky top-0 z-10",
    )
