# OpenStoxlify Library Documentation

## LIBRARY PURPOSE

Python library for algorithmic trading with:

- Multi-source market data fetching via providers
- Context-based strategy development
- Technical indicator calculation and visualization
- Professional multi-panel financial visualization with Canvas

## CORE COMPONENTS

### 1. Provider Module

Initialize data providers for market data:

```python
from openstoxlify.providers.stoxlify.provider import Provider
from openstoxlify.models.enum import DefaultProvider

provider = Provider(DefaultProvider.YFinance)
# or
provider = Provider(DefaultProvider.Binance)
```

### 2. Context Module

Central manager for market data, plots, and signals:

```python
from openstoxlify.context import Context
from openstoxlify.models.enum import Period

ctx = Context(provider, symbol="BTC-USD", period=Period.DAILY)
```

**Context Methods**:

- `ctx.quotes()` - Fetch market data (cached)
- `ctx.plot(label, plot_type, data, screen_index)` - Add plot data
- `ctx.signal(action_series)` - Record trading signal
- `ctx.authenticate(token)` - Authenticate with provider
- `ctx.execute()` - Execute latest signal
- `ctx.plots()` - Get all plot data
- `ctx.signals()` - Get all signals

### 3. Plotting with Context

```python
from openstoxlify.models.enum import PlotType
from openstoxlify.models.series import FloatSeries

ctx.plot(
    label="SMA 20",
    plot_type=PlotType.LINE,
    data=FloatSeries(timestamp, value),
    screen_index=0  # Main chart (0) or subplots (1, 2, ...)
)
```

**Important**: `screen_index` controls which subplot to use:

- `0` (default): Main price chart
- `1`, `2`, `3`, etc.: Separate indicator panels with independent scales
- Each screen_index creates a new subplot with its own y-axis

### 4. Strategy Signals

```python
from openstoxlify.models.enum import ActionType
from openstoxlify.models.series import ActionSeries

ctx.signal(ActionSeries(
    timestamp=timestamp,
    action=ActionType.LONG,
    amount=1.0
))
```

### 5. Visualization with Canvas

```python
from openstoxlify.draw import Canvas

canvas = Canvas(ctx)
canvas.draw()
```

## DATA MODELS

### Quote

```python
@dataclass
class Quote:
    timestamp: datetime  # Time of measurement
    high: float          # Period high price
    low: float           # Period low price
    open: float          # Opening price
    close: float         # Closing price
    volume: float        # Trading volume
```

### FloatSeries

Used for plotting numerical data points:

```python
@dataclass
class FloatSeries:
    timestamp: datetime
    value: float
```

### ActionSeries

Used for trading signals:

```python
@dataclass
class ActionSeries:
    timestamp: datetime
    action: ActionType  # LONG, SHORT, or HOLD
    amount: float       # Position size (set to 0.0 for HOLD)
```

### Enums

```python
from openstoxlify.models.enum import DefaultProvider, Period, PlotType, ActionType

# Providers
DefaultProvider.YFinance
DefaultProvider.Binance

# Periods
Period.MINUTELY   # 1m
Period.QUINTLY    # 5m
Period.HALFHOURLY # 30m
Period.HOURLY     # 1h
Period.DAILY      # 1d
Period.WEEKLY     # 1w
Period.MONTHLY    # 1mo

# Plot Types
PlotType.LINE       # Continuous line
PlotType.HISTOGRAM  # Vertical bars
PlotType.AREA       # Filled area

# Action Types
ActionType.LONG   # Buy signal
ActionType.SHORT  # Sell signal
ActionType.HOLD   # No action
```

## USAGE PATTERNS

### Basic Setup and Data Fetching

```python
from openstoxlify.context import Context
from openstoxlify.providers.stoxlify.provider import Provider
from openstoxlify.models.enum import DefaultProvider, Period

provider = Provider(DefaultProvider.YFinance)
ctx = Context(provider, "BTC-USD", Period.DAILY)
quotes = ctx.quotes()
```

### Price Plotting (Main Chart)

```python
from openstoxlify.models.enum import PlotType
from openstoxlify.models.series import FloatSeries

for quote in quotes:
    ctx.plot(
        label="Price",
        plot_type=PlotType.LINE,
        data=FloatSeries(quote.timestamp, quote.close),
        screen_index=0
    )
```

### Secondary Data Plotting (Separate Panel)

```python
for timestamp, value in secondary_data:
    ctx.plot(
        label="Indicator",
        plot_type=PlotType.HISTOGRAM,
        data=FloatSeries(timestamp, value),
        screen_index=1
    )
```

### Signal Generation

```python
from openstoxlify.models.enum import ActionType
from openstoxlify.models.series import ActionSeries

ctx.signal(ActionSeries(
    timestamp=quote.timestamp,
    action=ActionType.LONG,
    amount=1.0
))
```

## SIGNAL GENERATION PATTERNS

### Simple Threshold Strategy

```python
from openstoxlify.models.enum import ActionType
from openstoxlify.models.series import ActionSeries

lowest = min(quotes, key=lambda q: q.close)
highest = max(quotes, key=lambda q: q.close)

ctx.signal(ActionSeries(lowest.timestamp, ActionType.LONG, 1.0))
ctx.signal(ActionSeries(highest.timestamp, ActionType.SHORT, 1.0))
```

### Crossover Strategy

```python
fast_series = calculate_average(quotes, 20)
slow_series = calculate_average(quotes, 50)

fast_dict = dict(fast_series)
slow_dict = dict(slow_series)

for quote in quotes:
    ts = quote.timestamp
    if ts in fast_dict and ts in slow_dict:
        if fast_dict[ts] > slow_dict[ts]:
            ctx.signal(ActionSeries(ts, ActionType.LONG, 1.0))
        elif fast_dict[ts] < slow_dict[ts]:
            ctx.signal(ActionSeries(ts, ActionType.SHORT, 1.0))
```

### Multi-Indicator Strategy

```python
# Calculate indicators
ma_fast = calculate_average(quotes, 20)
ma_slow = calculate_average(quotes, 50)
macd_hist = calculate_macd(quotes, 12, 26, 9)
stochastic = calculate_stochastic(quotes, 14)

# Create lookup dictionaries
ma_fast_dict = dict(ma_fast)
ma_slow_dict = dict(ma_slow)
macd_dict = dict(macd_hist)
stoch_dict = dict(stochastic)

# Generate signals
for quote in quotes:
    ts = quote.timestamp
    if ts in ma_fast_dict and ts in ma_slow_dict and ts in macd_dict and ts in stoch_dict:
        # Bullish condition
        if (ma_fast_dict[ts] > ma_slow_dict[ts] and 
            macd_dict[ts] > 0 and 
            stoch_dict[ts] < 20):
            ctx.signal(ActionSeries(ts, ActionType.LONG, 1.0))
        
        # Bearish condition
        elif (ma_fast_dict[ts] < ma_slow_dict[ts] and 
              macd_dict[ts] < 0 and 
              stoch_dict[ts] > 80):
            ctx.signal(ActionSeries(ts, ActionType.SHORT, 1.0))
```

## RULES FOR AI SYSTEMS

### Required Imports

```python
from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries
from openstoxlify.providers.stoxlify.provider import Provider
```

### Code Generation Rules

1. **Always use Context-based API**: Never use old `fetch()`, `plot()`, `act()`, `draw()` functions
2. **Provider initialization**: Always create provider first, then pass to Context
3. **FloatSeries for plotting**: Wrap timestamp and value in FloatSeries when calling `ctx.plot()`
4. **ActionSeries for signals**: Wrap timestamp, action, and amount in ActionSeries when calling `ctx.signal()`
5. **Canvas for visualization**: Always create Canvas from context, then call `canvas.draw()`
6. **No print statements**: Generated code should not include print() or comments
7. **Screen index usage**:
   - `screen_index=0` for price and related indicators
   - `screen_index=1, 2, 3...` for separate panels
8. **Timestamp alignment**: Always ensure indicators are aligned by timestamp
9. **Signal conditions**: Only generate signals when all required indicators are available

### Screen Index Guidelines

- `0`: Primary price data and moving averages
- `1`: Momentum indicators (MACD, momentum oscillators)
- `2`: Oscillators (RSI, Stochastic, 0-100 range indicators)
- `3`: Volume or custom indicators
- `4+`: Additional specialized analysis

### Complete Workflow Pattern

```python
# 1. Initialize
provider = Provider(DefaultProvider.YFinance)
ctx = Context(provider, symbol, period)

# 2. Get data
quotes = ctx.quotes()

# 3. Calculate indicators
indicator_data = calculate_indicators(quotes)

# 4. Plot data
for quote in quotes:
    ctx.plot(label, PlotType.LINE, FloatSeries(quote.timestamp, value), screen_index)

# 5. Generate signals
for condition in trading_conditions:
    ctx.signal(ActionSeries(timestamp, action, amount))

# 6. Visualize
canvas = Canvas(ctx)
canvas.draw()
```

## VISUALIZATION CUSTOMIZATION

### Basic Customization

```python
canvas.draw()  # Default settings
```

### Advanced Customization

```python
canvas.draw(
    show_legend=True,           # Show/hide legend
    figsize=(16, 9),            # Figure size (width, height)
    offset_multiplier=0.05,     # Signal marker offset
    rotation=30,                # X-axis label rotation
    ha='right',                 # Horizontal alignment
    title="Strategy Analysis",  # Chart title
    xlabel="Date",              # X-axis label
    ylabel="Price",             # Y-axis label
    candle_linewidth=1,         # Candle wick width
    candle_body_width=4,        # Candle body width
    marker_size=8,              # Signal marker size
    annotation_fontsize=9,      # Signal text size
    histogram_alpha=0.6,        # Histogram transparency
    area_alpha=0.3,             # Area transparency
    line_width=2                # Line width
)
```

## AUTHENTICATION AND EXECUTION

### For Live Trading

```python
# Authenticate
ctx.authenticate("your-api-token")

# Execute latest signal (if authenticated)
ctx.execute()
```

**Notes**:

- `execute()` only runs if authenticated
- Only executes signal at the latest timestamp
- Skips `ActionType.HOLD` signals
- Calls `provider.execute(symbol, signal, amount)`

## EXAMPLE: SIMPLE STRATEGY

```python
from statistics import median
from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries
from openstoxlify.providers.stoxlify.provider import Provider

provider = Provider(DefaultProvider.YFinance)
ctx = Context(provider, "BTC-USD", Period.DAILY)

quotes = ctx.quotes()
prices = [quote.close for quote in quotes]
median_value = median(prices)

lowest = min(quotes, key=lambda q: q.close)
highest = max(quotes, key=lambda q: q.close)

for quote in quotes:
    ctx.plot("Median", PlotType.LINE, FloatSeries(quote.timestamp, median_value))

ctx.signal(ActionSeries(lowest.timestamp, ActionType.LONG, 1))
ctx.signal(ActionSeries(highest.timestamp, ActionType.SHORT, 1))

canvas = Canvas(ctx)
canvas.draw()

## SUMMARY CHECKLIST

When generating code with OpenStoxlify:

- ✅ Import from correct new modules (context, draw, models.enum, models.series, providers)
- ✅ Initialize Provider first
- ✅ Create Context with provider, symbol, and period
- ✅ Use `ctx.quotes()` to get market data
- ✅ Wrap plot data in `FloatSeries(timestamp, value)`
- ✅ Wrap signals in `ActionSeries(timestamp, action, amount)`
- ✅ Use `ctx.plot()` for indicators
- ✅ Use `ctx.signal()` for trading decisions
- ✅ Create Canvas from context
- ✅ Call `canvas.draw()` to visualize
- ✅ Use appropriate screen_index for multi-panel layouts
- ✅ Align timestamps across all indicators
- ✅ No print statements or comments in generated code
