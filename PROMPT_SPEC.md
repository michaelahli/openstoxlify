# OpenStoxlify - LLM Prompt Specification

**Version**: 1.0  
**Target**: Large Language Models (LLMs) generating trading strategies  
**Library**: OpenStoxlify

---

## Overview

OpenStoxlify is a Python library for algorithmic trading strategy development. As an LLM, you can generate complete, runnable trading strategies using this library's simple, context-based API.

---

## Core Concepts

### 1. Basic Structure

Every strategy follows this pattern:

```python
import sys
from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.providers.stoxlify.provider import Provider
from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries

# 1. Setup
provider = Provider(DefaultProvider.YFinance)  # or DefaultProvider.Binance
ctx = Context(sys.argv, provider, "SYMBOL", Period.PERIOD)

# 2. Get market data
quotes = ctx.quotes()

# 3. Implement your strategy logic
# ... your calculations here ...

# 4. Plot indicators
ctx.plot("Label", PlotType.LINE, FloatSeries(timestamp, value), screen_index=0)

# 5. Generate signals
ctx.signal(ActionSeries(timestamp, ActionType.LONG, amount))

# 6. Visualize
canvas = Canvas(ctx)
canvas.draw()

# 7. Optional: Live trading
ctx.authenticate()
ctx.execute()
```

---

## API Reference

### Context Initialization

```python
ctx = Context(
    agrv=sys.argv,           # REQUIRED: Always pass sys.argv
    provider=provider,       # Provider instance
    symbol="BTC-USD",        # Trading symbol
    period=Period.DAILY      # Timeframe
)
```

### Available Periods

```python
Period.MINUTELY    # 1-minute candles
Period.QUINTLY     # 5-minute candles
Period.HALFHOURLY  # 30-minute candles
Period.HOURLY      # 1-hour candles
Period.DAILY       # Daily candles
Period.WEEKLY      # Weekly candles
Period.MONTHLY     # Monthly candles
```

### Available Providers

```python
DefaultProvider.YFinance  # Yahoo Finance (stocks, crypto, forex)
DefaultProvider.Binance   # Binance (crypto only)
```

### Market Data Access

```python
quotes = ctx.quotes()  # Returns List[Quote]

# Quote structure:
# quote.timestamp  -> datetime (timezone-aware UTC)
# quote.open       -> float
# quote.high       -> float
# quote.low        -> float
# quote.close      -> float
# quote.volume     -> float
```

### Plotting Indicators

```python
ctx.plot(
    label="Indicator Name",      # String identifier
    plot_type=PlotType.LINE,     # LINE, HISTOGRAM, or AREA
    data=FloatSeries(timestamp, value),
    screen_index=0               # 0 = main chart, 1+ = subplots
)
```

**Plot Types**:

- `PlotType.LINE` - Continuous line (moving averages, price lines)
- `PlotType.HISTOGRAM` - Vertical bars (volume, MACD histogram)
- `PlotType.AREA` - Filled area (Bollinger Bands, clouds)

**Screen Indices**:

- `0` - Main chart (overlays on price)
- `1, 2, 3...` - Separate subplot panels below main chart

### Generating Trading Signals

```python
ctx.signal(ActionSeries(
    timestamp=quote.timestamp,   # When to trade
    action=ActionType.LONG,      # LONG, SHORT, or HOLD
    amount=1.0                   # Position size
))
```

**Action Types**:

- `ActionType.LONG` - Buy/Enter long position
- `ActionType.SHORT` - Sell/Enter short position
- `ActionType.HOLD` - No action (amount automatically set to 0)

### Visualization

```python
canvas = Canvas(ctx)

# Basic draw
canvas.draw()

# With customization
canvas.draw(
    show_legend=True,
    figsize=(16, 9),
    title="Strategy Name",
    candle_linewidth=1.5,
    marker_size=10
)
```

---

## Strategy Implementation Guidelines

### Rule 1: Always Import sys

```python
import sys
# ... other imports ...
ctx = Context(sys.argv, provider, symbol, period)
```

### Rule 2: Extract Quote Data Correctly

```python
quotes = ctx.quotes()

# Access individual fields
for quote in quotes:
    timestamp = quote.timestamp
    price = quote.close
    # ... your logic ...
```

### Rule 3: Build Time Series for Plotting

When plotting indicators, call `ctx.plot()` for each data point:

```python
# Example: Plot all closing prices
for quote in quotes:
    ctx.plot("Close", PlotType.LINE, FloatSeries(quote.timestamp, quote.close))

# Example: Plot calculated indicator
indicator_values = calculate_your_indicator(quotes)
for timestamp, value in indicator_values:
    ctx.plot("My Indicator", PlotType.LINE, FloatSeries(timestamp, value))
```

### Rule 4: Signal Only at Decision Points

Don't signal on every candle. Only call `ctx.signal()` when your strategy makes a decision:

```python
for i, quote in enumerate(quotes):
    # Your strategy logic
    if buy_condition:
        ctx.signal(ActionSeries(quote.timestamp, ActionType.LONG, 1.0))
    elif sell_condition:
        ctx.signal(ActionSeries(quote.timestamp, ActionType.SHORT, 1.0))
    # No signal if HOLD
```

### Rule 5: Use Subplots for Separate Indicators

```python
# Main chart (screen 0): Price and moving averages
ctx.plot("Price", PlotType.LINE, FloatSeries(ts, price), 0)
ctx.plot("MA", PlotType.LINE, FloatSeries(ts, ma), 0)

# Subplot 1: Volume or momentum indicator
ctx.plot("Volume", PlotType.HISTOGRAM, FloatSeries(ts, volume), 1)

# Subplot 2: Oscillator
ctx.plot("RSI", PlotType.LINE, FloatSeries(ts, rsi), 2)
```

---

## Common Patterns

### Pattern 1: Simple Moving Average

```python
def calculate_sma(prices, window):
    return [
        sum(prices[i:i+window]) / window 
        for i in range(len(prices) - window + 1)
    ]

quotes = ctx.quotes()
prices = [q.close for q in quotes]
sma_values = calculate_sma(prices, 20)

# Plot SMA (note the offset for alignment)
for i in range(len(sma_values)):
    quote_index = i + 19  # window - 1
    ctx.plot("SMA 20", PlotType.LINE, 
             FloatSeries(quotes[quote_index].timestamp, sma_values[i]))
```

### Pattern 2: Crossover Detection

```python
fast = calculate_sma(prices, 10)
slow = calculate_sma(prices, 20)

for i in range(1, len(fast)):
    # Align indices (fast starts at index 9, slow at index 19)
    slow_idx = i
    quote_idx = i + 19
    
    if i >= len(slow):
        break
    
    prev_fast, curr_fast = fast[i-1], fast[i]
    prev_slow, curr_slow = slow[slow_idx-1], slow[slow_idx]
    
    # Bullish crossover
    if prev_fast <= prev_slow and curr_fast > curr_slow:
        ctx.signal(ActionSeries(quotes[quote_idx].timestamp, ActionType.LONG, 1.0))
    
    # Bearish crossover
    elif prev_fast >= prev_slow and curr_fast < curr_slow:
        ctx.signal(ActionSeries(quotes[quote_idx].timestamp, ActionType.SHORT, 1.0))
```

### Pattern 3: Multi-Indicator Combination

```python
# Calculate multiple indicators
indicator1 = calculate_indicator_1(quotes)
indicator2 = calculate_indicator_2(quotes)

# Create lookup dictionaries for easy access
ind1_dict = dict(indicator1)  # List of (timestamp, value) tuples
ind2_dict = dict(indicator2)

# Generate signals when conditions align
for quote in quotes:
    ts = quote.timestamp
    
    if ts in ind1_dict and ts in ind2_dict:
        if ind1_dict[ts] > threshold1 and ind2_dict[ts] < threshold2:
            ctx.signal(ActionSeries(ts, ActionType.LONG, 1.0))
```

### Pattern 4: Finding Extremes

```python
quotes = ctx.quotes()

# Find highest/lowest
highest = max(quotes, key=lambda q: q.high)
lowest = min(quotes, key=lambda q: q.low)

# Signal at extremes
ctx.signal(ActionSeries(lowest.timestamp, ActionType.LONG, 1.0))
ctx.signal(ActionSeries(highest.timestamp, ActionType.SHORT, 1.0))
```

---

## Data Handling Best Practices

### Lists vs Dictionaries

```python
# For sequential processing: Use lists
indicator_list = [(quote.timestamp, value) for ...]

# For timestamp lookups: Use dictionaries
indicator_dict = {ts: value for ts, value in indicator_list}

# Then access by timestamp
if timestamp in indicator_dict:
    value = indicator_dict[timestamp]
```

### Index Alignment

When working with calculated indicators that don't start at index 0:

```python
# Original data: 100 quotes
quotes = ctx.quotes()  # indices 0-99

# SMA with window=20 produces 81 values
sma = calculate_sma(prices, 20)  # indices 0-80

# To align: quote index = sma index + (window - 1)
for i, sma_value in enumerate(sma):
    quote_index = i + 19
    timestamp = quotes[quote_index].timestamp
    ctx.plot("SMA", PlotType.LINE, FloatSeries(timestamp, sma_value))
```

### Preventing Index Errors

```python
# Always check bounds
for i in range(len(indicator_values)):
    quote_index = i + offset
    if quote_index >= len(quotes):
        break  # Prevent index out of range
    # ... use quotes[quote_index] ...
```

---

## Complete Strategy Template

```python
import sys
from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.providers.stoxlify.provider import Provider
from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries

# ============================================================================
# CONFIGURATION
# ============================================================================

SYMBOL = "BTC-USD"
PERIOD = Period.DAILY
PROVIDER = DefaultProvider.YFinance

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def your_calculation_function(quotes):
    """Implement your indicator calculation here"""
    results = []
    for i, quote in enumerate(quotes):
        # Your logic
        value = quote.close  # Replace with actual calculation
        results.append((quote.timestamp, value))
    return results

# ============================================================================
# MAIN STRATEGY
# ============================================================================

# Initialize
provider = Provider(PROVIDER)
ctx = Context(sys.argv, provider, SYMBOL, PERIOD)

# Get market data
quotes = ctx.quotes()

# Calculate indicators
indicator = your_calculation_function(quotes)

# Plot indicators
for quote in quotes:
    ctx.plot("Price", PlotType.LINE, FloatSeries(quote.timestamp, quote.close), 0)

for timestamp, value in indicator:
    ctx.plot("Indicator", PlotType.LINE, FloatSeries(timestamp, value), 1)

# Generate trading signals
for timestamp, value in indicator:
    if value > 0:  # Replace with your condition
        ctx.signal(ActionSeries(timestamp, ActionType.LONG, 1.0))
    elif value < 0:  # Replace with your condition
        ctx.signal(ActionSeries(timestamp, ActionType.SHORT, 1.0))

# Visualize
canvas = Canvas(ctx)
canvas.draw(title="Your Strategy Name")

# Optional: Live trading (requires --token and --id CLI arguments)
ctx.authenticate()
ctx.execute()
```

---

## Error Prevention Checklist

✅ **Import `sys`** - Required for Context initialization  
✅ **Pass `sys.argv`** - First argument to Context constructor  
✅ **Check index bounds** - Prevent index out of range errors  
✅ **Align timestamps** - Match indicator values to correct quote timestamps  
✅ **Use correct PlotType** - LINE, HISTOGRAM, or AREA  
✅ **Signal only on conditions** - Don't signal every candle  
✅ **Handle edge cases** - Check for division by zero, empty lists, etc.  
✅ **Use UTC timestamps** - All timestamps are timezone-aware UTC  

---

## Common Mistakes to Avoid

❌ **Forgetting sys.argv**:

```python
# WRONG
ctx = Context(provider, "BTC-USD", Period.DAILY)

# CORRECT
ctx = Context(sys.argv, provider, "BTC-USD", Period.DAILY)
```

❌ **Index misalignment**:

```python
# WRONG - timestamps won't match
for i, value in enumerate(indicator):
    ctx.plot("Ind", PlotType.LINE, FloatSeries(quotes[i].timestamp, value))

# CORRECT - use the timestamp from indicator tuple
for timestamp, value in indicator:
    ctx.plot("Ind", PlotType.LINE, FloatSeries(timestamp, value))
```

❌ **Signaling on every candle**:

```python
# WRONG - too many signals
for quote in quotes:
    ctx.signal(ActionSeries(quote.timestamp, ActionType.HOLD, 0))

# CORRECT - signal only on decisions
for quote in quotes:
    if buy_condition:
        ctx.signal(ActionSeries(quote.timestamp, ActionType.LONG, 1.0))
```

❌ **Wrong screen_index for overlays**:

```python
# WRONG - moving average on separate panel
ctx.plot("MA", PlotType.LINE, FloatSeries(ts, ma), 1)

# CORRECT - moving average overlaid on price
ctx.plot("MA", PlotType.LINE, FloatSeries(ts, ma), 0)
```

---

## Output Format

When generating strategies for users:

1. **Include all necessary imports** at the top
2. **Add comments** explaining strategy logic
3. **Use descriptive variable names** for clarity
4. **Provide configuration section** at the top for easy modification
5. **Include visualization** with `canvas.draw()`
6. **Keep authentication/execution** at the bottom (optional for backtesting)

---

## Symbol Format by Provider

### YFinance (DefaultProvider.YFinance)

- Stocks: `"AAPL"`, `"TSLA"`, `"GOOGL"`
- Crypto: `"BTC-USD"`, `"ETH-USD"`
- Forex: `"EURUSD=X"`
- Indices: `"^GSPC"` (S&P 500), `"^DJI"` (Dow Jones)

### Binance (DefaultProvider.Binance)

- Crypto pairs: `"BTCUSDT"`, `"ETHUSDT"`, `"BNBUSDT"`
- No hyphens, all uppercase

---

## Final Notes

- **This library is for backtesting AND live trading** - the same code works for both
- **Authentication is optional** - only needed for live execution
- **All timestamps are UTC** - no timezone conversions needed
- **Quote data is cached** - calling `ctx.quotes()` multiple times is efficient
- **Plot calls are cumulative** - each `ctx.plot()` adds to the time series

When generating code, prioritize clarity and correctness over complexity. Users should be able to understand and modify the strategy easil
