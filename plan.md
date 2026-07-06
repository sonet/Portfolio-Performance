# Portfolio Companion Implementation Plan

## Phase 1: Core Portfolio Experience ✅
- [x] Establish a clean, modern financial dashboard aesthetic with a white/light sidebar, blue accent color, bordered cards on a gray-50 background, compact typography, responsive layout, and accessible navigation.
- [x] Build the main portfolio overview with total value, unrealized gain/loss, cash invested, daily change, allocation summary, and recent activity.
- [x] Add holdings management with searchable holdings, asset-class badges, editable quantities/cost basis, current prices, market value, allocation percent, and P&L indicators.
- [x] Connect portfolio-level calculations to asset price and performance data so aggregate metrics update from individual holdings.

## Phase 2: Asset Performance and Market Data ✅
- [x] Add an asset discovery and detail experience with ticker search, asset profile, latest price, price changes, volatility, 52-week range, and benchmark comparison.
- [x] Integrate market-data retrieval for historical prices and latest prices, with resilient loading, refresh status, and clear error states.
- [x] Build time-series visualizations for asset price trends, portfolio value history, allocation, and returns using responsive chart components.
- [x] Add asset metric calculations for daily change, one-year change, highs/lows, volatility, and performance contribution to portfolio totals.

## Phase 3: Transactions, Data Sources, Imports, and Settings ✅
- [x] Build transaction management with buy/sell entry, fees, transaction dates, validation, history filters, and portfolio impact calculations.
- [x] Add data source management for API, CSV import, and manual entries with priority ordering, source labels, and update status.
- [x] Implement CSV import workflow with preview, validation feedback, and conversion into holdings and transactions.
- [x] Add settings and manual override controls for prices, source priority, currency display, cache behavior, and portfolio preferences.

## Phase 4: Testing and Polish ✅
- [x] Validate key state flows for navigation, data refresh, holding changes, transaction entry, CSV parsing, and manual overrides.
- [x] Ensure responsive behavior across desktop, tablet, and mobile layouts with complete empty, loading, success, and error states.
- [x] Finalize cohesive UI polish, realistic starter data, accessibility labels, and helpful user guidance throughout the app.

## Phase 5: Markets Performance Screen ✅
- [x] Add a Markets performance page under the Markets navigation group with the same clean light dashboard design and blue accent.
- [x] Convert the uploaded notebook workflow into app data processing for asset-class monthly prices, quarterly returns, cumulative return, and CAGR.
- [x] Add market filters for search, sector, class, custom date range, and predefined intervals with loading, cached, success, and error states.
- [x] Build notebook-inspired performance reporting with summary cards, top/bottom performers, sector/class breakdowns, and a color-scaled quarterly return table.

## Phase 6: Markets Performance Validation ✅
- [x] Validate ticker universe loading from the uploaded asset list and resilient fallback behavior when live market data is unavailable.
- [x] Validate interval, custom range, sector, class, and search filtering logic.
- [x] Ensure the Markets performance page is responsive, accessible, and clearly distinguished from holdings-focused Performance.

## Phase 7: Dynamic Markets Return Columns ✅
- [x] Update Markets return periods so selected intervals control the number and granularity of percent-change columns.
- [x] Add daily, weekly, monthly, and quarterly period generation while preserving cumulative return and CAGR summaries.
- [x] Update the report table labeling and empty states so users understand the active interval granularity.
- [x] Validate examples including 12 months, 10 days, 10 weeks, 30 days, and 3 years.