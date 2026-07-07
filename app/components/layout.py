import reflex as rx
from app.components.sidebar import sidebar, mobile_header


def page_layout(
    content: rx.Component, active_route: str, title: str, subtitle: str
) -> rx.Component:
    return rx.el.div(
        rx.el.a(
            "Skip to main content",
            href="#main-content",
            class_name="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-3 focus:py-2 focus:bg-violet-600 focus:text-white focus:rounded-lg focus:text-sm focus:font-medium",
        ),
        sidebar(active_route),
        rx.el.div(
            mobile_header(),
            rx.el.main(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            title,
                            class_name="text-xl sm:text-2xl font-semibold text-slate-100 tracking-tight",
                        ),
                        rx.el.p(
                            subtitle,
                            class_name="text-xs sm:text-sm text-slate-400 mt-1",
                        ),
                        class_name="mb-5 sm:mb-6",
                    ),
                    content,
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-5 sm:py-6 md:py-8",
                ),
                id="main-content",
                class_name="flex-1 min-h-screen",
                aria_label=f"{title} main content",
            ),
            class_name="flex-1 flex flex-col min-w-0",
        ),
        class_name="flex min-h-screen font-['Inter'] text-slate-100",
        style={
            "background": "radial-gradient(ellipse 80% 60% at 20% 0%, rgba(76, 29, 149, 0.18), transparent 60%), radial-gradient(ellipse 60% 50% at 90% 10%, rgba(8, 145, 178, 0.12), transparent 60%), #050814",
        },
    )
