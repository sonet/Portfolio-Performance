import reflex as rx
from app.components.layout import page_layout
from app.components.overview import overview_content
from app.components.holdings import holdings_content
from app.components.discover import discover_content
from app.components.asset_detail import asset_detail_content
from app.components.performance import performance_content
from app.components.transactions import transactions_content
from app.components.settings import settings_content
from app.states.market_state import MarketState


def index() -> rx.Component:
    return page_layout(
        overview_content(),
        active_route="/",
        title="Portfolio Overview",
        subtitle="A snapshot of your total value, performance, and recent activity.",
    )


def holdings_page() -> rx.Component:
    return page_layout(
        holdings_content(),
        active_route="/holdings",
        title="Holdings",
        subtitle="Manage your positions with real-time market values and allocations.",
    )


def discover_page() -> rx.Component:
    return page_layout(
        discover_content(),
        active_route="/discover",
        title="Discover Assets",
        subtitle="Explore popular equities, ETFs, bonds, and crypto across markets.",
    )


def asset_page() -> rx.Component:
    return page_layout(
        asset_detail_content(),
        active_route="/discover",
        title="Asset Detail",
        subtitle="Live market data, historical performance, and benchmark comparison.",
    )


def performance_page() -> rx.Component:
    return page_layout(
        performance_content(),
        active_route="/performance",
        title="Portfolio Performance",
        subtitle="Track value over time and measure returns against the S&P 500.",
    )


def transactions_page() -> rx.Component:
    return page_layout(
        transactions_content(),
        active_route="/transactions",
        title="Transactions",
        subtitle="Log buys, sells, dividends, and cash flows with full audit history.",
    )


def settings_page() -> rx.Component:
    return page_layout(
        settings_content(),
        active_route="/settings",
        title="Settings",
        subtitle="Data sources, imports, manual overrides, and portfolio preferences.",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    asset_page, route="/asset/[ticker]", on_load=MarketState.load_asset
)
app.add_page(index, route="/")
app.add_page(holdings_page, route="/holdings")
app.add_page(discover_page, route="/discover")
app.add_page(
    performance_page,
    route="/performance",
    on_load=MarketState.load_portfolio_history,
)
app.add_page(transactions_page, route="/transactions")
app.add_page(settings_page, route="/settings")
