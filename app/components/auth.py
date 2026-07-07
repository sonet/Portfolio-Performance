import reflex as rx
from reflex_google_auth import (
    GoogleAuthState,
    google_login,
    google_oauth_provider,
)


def _feature_row(icon: str, title: str, subtitle: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-violet-300"),
            class_name="h-9 w-9 rounded-lg bg-violet-500/15 border border-violet-500/30 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-semibold text-slate-100"),
            rx.el.p(subtitle, class_name="text-xs text-slate-400 mt-0.5"),
        ),
        class_name="flex items-start gap-3",
    )


def _auth_error_banner() -> rx.Component:
    return rx.cond(
        (GoogleAuthState.id_token_json != "") & ~GoogleAuthState.token_is_valid,
        rx.el.div(
            rx.icon("circle-alert", class_name="h-3.5 w-3.5 text-rose-400"),
            rx.el.p(
                "Your session has expired or is invalid. Please sign in again.",
                class_name="text-xs font-medium text-rose-300",
            ),
            class_name="flex items-center gap-2 px-3 py-2 bg-rose-500/10 border border-rose-500/30 rounded-lg mb-4",
            aria_live="polite",
        ),
        rx.el.div(),
    )


def auth_landing() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "chart-candlestick", class_name="h-6 w-6 text-white"
                    ),
                    class_name="h-12 w-12 rounded-xl flex items-center justify-center shadow-[0_0_28px_-4px_rgba(139,92,246,0.7)] mb-5",
                    style={
                        "background": "linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)"
                    },
                    aria_hidden="true",
                ),
                rx.el.h1(
                    "Portfolio Companion",
                    class_name="text-2xl font-semibold text-slate-100 tracking-tight",
                ),
                rx.el.p(
                    "The intelligent way to track assets, analyze markets, and measure performance.",
                    class_name="text-sm text-slate-400 mt-1.5 max-w-md",
                ),
                class_name="mb-6",
            ),
            _auth_error_banner(),
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Sign In",
                        class_name="text-lg font-semibold text-slate-100",
                    ),
                    rx.el.p(
                        "Sign in with your Google account to securely sync your portfolio across all devices.",
                        class_name="text-xs text-slate-400 mt-1",
                    ),
                    class_name="mb-5",
                ),
                rx.cond(
                    GoogleAuthState.client_id != "",
                    rx.el.div(
                        google_login(),
                        class_name="flex items-center justify-center [&>div]:!w-full",
                    ),
                    rx.el.div(
                        rx.icon(
                            "triangle-alert",
                            class_name="h-4 w-4 text-amber-300",
                        ),
                        rx.el.p(
                            "Google sign-in is currently unavailable. Please contact support or check back later.",
                            class_name="text-xs font-medium text-amber-200",
                        ),
                        class_name="flex items-start gap-2 px-3 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg",
                    ),
                ),
                rx.el.div(
                    rx.el.div(class_name="flex-1 h-px bg-slate-800"),
                    rx.el.span(
                        "Onboarding",
                        class_name="text-[11px] uppercase tracking-wider text-slate-500 font-semibold",
                    ),
                    rx.el.div(class_name="flex-1 h-px bg-slate-800"),
                    class_name="flex items-center gap-3 my-5",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "sparkles",
                            class_name="h-4 w-4 text-cyan-400 shrink-0 mt-0.5",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Instant Account Creation",
                                class_name="text-sm font-semibold text-slate-100",
                            ),
                            rx.el.p(
                                "Your secure workspace is automatically provisioned on your first sign-in. No separate registration forms or passwords required.",
                                class_name="text-xs text-slate-400 mt-1 leading-relaxed",
                            ),
                        ),
                        class_name="flex items-start gap-3",
                    ),
                    class_name="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80",
                ),
                class_name="bg-slate-900/60 backdrop-blur-sm border border-slate-800/80 rounded-2xl p-6 mb-6 shadow-[0_0_40px_-12px_rgba(139,92,246,0.35)]",
            ),
            rx.el.div(
                _feature_row(
                    "wallet",
                    "Track every position",
                    "Live market values, cost basis, and unrealized P&L across your holdings.",
                ),
                _feature_row(
                    "chart-line",
                    "Benchmark performance",
                    "Compare your portfolio against the S&P 500 across custom time ranges.",
                ),
                _feature_row(
                    "chart-bar",
                    "Explore markets",
                    "Quarterly returns, CAGR, and sector breakdowns for the tracked universe.",
                ),
                _feature_row(
                    "shield-check",
                    "Secure by default",
                    "Signed in with Google OAuth — we never see or store your password.",
                ),
                class_name="flex flex-col gap-4",
            ),
            rx.el.p(
                "By continuing you agree to use Portfolio Companion for informational purposes only. This is not investment advice.",
                class_name="text-[11px] text-slate-500 mt-6 leading-relaxed",
            ),
            class_name="max-w-lg w-full",
        ),
        class_name="min-h-screen flex items-center justify-center px-4 sm:px-6 py-10 font-['Inter']",
        style={
            "background": "radial-gradient(ellipse 80% 60% at 20% 0%, rgba(76, 29, 149, 0.28), transparent 60%), radial-gradient(ellipse 60% 50% at 90% 10%, rgba(8, 145, 178, 0.18), transparent 60%), #050814",
        },
    )


def auth_loading_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "loader-circle",
                class_name="h-6 w-6 text-violet-300 animate-spin",
            ),
            rx.el.p(
                "Signing you in…",
                class_name="text-sm font-medium text-slate-200 mt-3",
            ),
            class_name="flex flex-col items-center",
        ),
        class_name="min-h-screen flex items-center justify-center font-['Inter']",
        style={"background": "#050814"},
    )


def with_google_provider(content: rx.Component) -> rx.Component:
    return google_oauth_provider(content)


def require_auth(content: rx.Component) -> rx.Component:
    return with_google_provider(
        rx.cond(
            GoogleAuthState.is_hydrated,
            rx.cond(
                GoogleAuthState.token_is_valid,
                content,
                auth_landing(),
            ),
            auth_loading_view(),
        ),
    )
