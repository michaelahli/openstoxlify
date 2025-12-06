# OpenStoxlify Library Documentation

## LIBRARY PURPOSE

Python library for algorithmic trading with:

- Multi-source market data fetching
- Technical indicator calculation  
- Strategy signal generation
- Professional multi-panel financial visualization

## CORE COMPONENTS

### Data Module (`fetch`)

```python
from openstoxlify.fetch import fetch
from openstoxlify.models import Provider, Period

data = fetch(symbol, provider, period)
```

### Plotting Module (`plot`)

```python
from openstoxlify.plotter import plot
from openstoxlify.models import PlotType

plot(PlotType.LINE, label, timestamp, value, screen_index=0)
```

**Important**: `screen_index` controls which subplot to use:

- `0` (default): Main price chart
- `1`, `2`, `3`, etc.: Separate indicator panels with independent scales
- Each screen_index creates a new subplot with its own y-axis

### Strategy Module (`act`)

```python
from openstoxlify.strategy import act
from openstoxlify.models import ActionType

act(ActionType.LONG, timestamp, amount)
```

### Visualization (`draw`)

```python
from openstoxlify.draw import draw

draw()
```

## DATA MODELS

### MarketData

```python
class MarketData:
    quotes: List[Quote]
```

### Quote  

```python
class Quote:
    timestamp: datetime
    open: float
    high: float  
    low: float
    close: float
    volume: float
```

### Enums

```python
class Provider:
    YFinance = "yfinance"
    Binance = "binance"

class Period:
    MINUTELY = "1m"
    QUINTLY = "5m" 
    HOURLY = "1h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1mo"

class PlotType:
    LINE = "line"
    HISTOGRAM = "histogram"
    AREA = "area"

class ActionType:
    LONG = "long"
    SHORT = "short" 
    HOLD = "hold"
```

## USAGE PATTERNS

### Basic Data Fetching

```python
market_data = fetch("BTC-USD", Provider.YFinance, Period.DAILY)
```

### Price Plotting (Main Chart)

```python
for quote in market_data.quotes:
    plot(PlotType.LINE, "Price", quote.timestamp, quote.close, screen_index=0)
```

### Secondary Data Plotting (Separate Panel)

```python
for timestamp, value in secondary_data:
    plot(PlotType.HISTOGRAM, "Secondary", timestamp, value, screen_index=1)
```

### Signal Generation

```python
act(ActionType.LONG, timestamp, 1.0)
```

### Complete Strategy Template with Multi-Panel

```python
from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act

market_data = fetch("SYMBOL", Provider.Binance, Period.DAILY)

# Main price chart (screen_index=0)
for quote in market_data.quotes:
    plot(PlotType.LINE, "Price", quote.timestamp, quote.close, screen_index=0)

# Additional data on separate panel (screen_index=1)
for timestamp, data_value in calculated_data:
    plot(PlotType.LINE, "Data", timestamp, data_value, screen_index=1)

act(ActionType.LONG, market_data.quotes[0].timestamp, 1)
draw()
```

## CALCULATION PATTERNS

### Simple Moving Average Calculation

```python
def calculate_average(market_data, window):
    prices = [quote.close for quote in market_data.quotes]
    return [
        (market_data.quotes[i + window - 1].timestamp, sum(prices[i:i + window]) / window)
        for i in range(len(prices) - window + 1)
    ]
```

### Oscillator Calculation Pattern

```python
def calculate_oscillator(market_data, period):
    quotes = market_data.quotes
    highs = [q.high for q in quotes]
    lows = [q.low for q in quotes]
    closes = [q.close for q in quotes]
    
    results = []
    for i in range(period - 1, len(closes)):
        high_range = max(highs[i - period + 1:i + 1])
        low_range = min(lows[i - period + 1:i + 1])
        value = 100 * ((closes[i] - low_range) / (high_range - low_range)) if high_range != low_range else 50
        results.append((quotes[i].timestamp, value))
    
    return results
```

### Momentum Calculation Pattern

```python
def calculate_momentum(market_data, fast_period, slow_period):
    closes = [q.close for q in market_data.quotes]
    
    fast_values = calculate_average_values(closes, fast_period)
    slow_values = calculate_average_values(closes, slow_period)
    
    momentum_line = [f - s for f, s in zip(fast_values, slow_values)]
    signal_line = calculate_average_values(momentum_line, 9)
    histogram = [m - s for m, s in zip(momentum_line, signal_line)]
    
    timestamps = [market_data.quotes[i].timestamp for i in range(slow_period - 1, len(closes))]
    return [(t, h) for t, h in zip(timestamps, histogram)]
```

## SIGNAL GENERATION PATTERNS

### Crossover Strategy

```python
fast_series = calculate_series(market_data, 9)
slow_series = calculate_series(market_data, 21)

fast_dict = dict(fast_series)
slow_dict = dict(slow_series)

for timestamp, fast_value in fast_series:
    slow_value = slow_dict.get(timestamp)
    if fast_value > slow_value:
        act(ActionType.LONG, timestamp, 1)
    elif fast_value < slow_value:
        act(ActionType.SHORT, timestamp, 1)
```

### Multi-Panel Strategy with Independent Scales

```python
# Primary data on main chart (screen_index=0)
for quote in market_data.quotes:
    plot(PlotType.LINE, "Primary", quote.timestamp, quote.close, screen_index=0)

# Derived series on first additional panel (screen_index=1)
series_a = calculate_series_a(market_data)
for timestamp, value in series_a:
    plot(PlotType.LINE, "Series A", timestamp, value, screen_index=1)

# Another derived series on second panel (screen_index=2)  
series_b = calculate_series_b(market_data)
for timestamp, value in series_b:
    plot(PlotType.HISTOGRAM, "Series B", timestamp, value, screen_index=2)

# Trading signals based on multiple series
a_dict = dict(series_a)
for quote in market_data.quotes:
    if quote.timestamp in a_dict:
        value = a_dict[quote.timestamp]
        if value < 20:  # Threshold condition
            act(ActionType.LONG, quote.timestamp, 1)
        elif value > 80:  # Another threshold
            act(ActionType.SHORT, quote.timestamp, 1)
```

## RULES FOR AI SYSTEMS

- Use only functions and models defined in this documentation
- No additional imports beyond openstoxlify modules
- No print statements or comments in generated code
- Follow the exact patterns shown in examples
- All plotting must use `plot()` function with appropriate `screen_index`
- All actions must use `act()` function
- Always call `draw()` at the end
- Maintain timestamp alignment across series
- Use `screen_index=0` for primary price data
- Use `screen_index=1`, `2`, `3`, etc. for derived series with different scales
- Each `screen_index` creates a separate subplot with its own y-axis scale

### Screen Index Guidelines

- `0`: Primary data series (prices, main averages)
- `1`: First derived series (typically 0-100 range)
- `2`: Second derived series (momentum-based values)
- `3`: Volume-based or additional series
- `4+`: Custom series or specialized analysis

## VISUALIZATION CONFIGURATION

The `draw()` function automatically creates multiple subplots based on the highest `screen_index` used:

```python
# Example: Creates 3 subplots (0, 1, 2)
plot(..., screen_index=0)  # Primary chart
plot(..., screen_index=1)  # First derived series
plot(..., screen_index=2)  # Second derived series
draw()  # Creates 3 vertically stacked panels
```

### Customizing Multi-Panel Layout

```python
draw(
    show_legend=True,
    figsize=(16, 12),  # Taller for multiple panels
    subplot_height_ratios=[3, 1, 1],  # Main panel 3x taller than others
    title="Multi-Series Analysis",
    xlabel="Date",
    ylabels=["Primary Scale", "Series A Scale", "Series B Scale"]  # Separate y-axis labels
)
```

## EXAMPLE: COMPLETE ANALYSIS WITH MULTIPLE PANELS

```python
from openstoxlify.models import *
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act

# Fetch data
market_data = fetch("AAPL", Provider.YFinance, Period.DAILY)

# Calculate different series
series_1 = calculate_series_1(market_data, 20)
series_2 = calculate_series_2(market_data, 50)
series_3 = calculate_series_3(market_data, 14)
series_4 = calculate_series_4(market_data)

# Plot on main chart (screen_index=0)
for quote in market_data.quotes:
    plot(PlotType.LINE, "Close", quote.timestamp, quote.close, screen_index=0)

for timestamp, value in series_1:
    plot(PlotType.LINE, "Series 1", timestamp, value, screen_index=0)

for timestamp, value in series_2:
    plot(PlotType.LINE, "Series 2", timestamp, value, screen_index=0)

# Plot series 3 on separate panel (screen_index=1)
for timestamp, value in series_3:
    plot(PlotType.LINE, "Series 3", timestamp, value, screen_index=1)

# Plot series 4 on another panel (screen_index=2)
for timestamp, value in series_4:
    plot(PlotType.HISTOGRAM, "Series 4", timestamp, value, screen_index=2)

# Generate signals based on multiple series
series1_dict = dict(series_1)
series2_dict = dict(series_2)
series3_dict = dict(series_3)

for quote in market_data.quotes:
    timestamp = quote.timestamp
    if timestamp in series1_dict and timestamp in series2_dict and timestamp in series3_dict:
        if (series1_dict[timestamp] > series2_dict[timestamp] and 
            series3_dict[timestamp] < 30):
            act(ActionType.LONG, timestamp, 1)
        elif (series1_dict[timestamp] < series2_dict[timestamp] and 
              series3_dict[timestamp] > 70):
            act(ActionType.SHORT, timestamp, 1)

# Visualize
draw()
```

## HELPER FUNCTIONS FOR CALCULATIONS

### Generic Average Calculation

```python
def calculate_average_values(values, period):
    return [
        sum(values[i:i + period]) / period
        for i in range(len(values) - period + 1)
    ]
```

### Range-Based Calculation

```python
def calculate_range_based(highs, lows, closes, period):
    results = []
    for i in range(period - 1, len(closes)):
        high_val = max(highs[i - period + 1:i + 1])
        low_val = min(lows[i - period + 1:i + 1])
        if high_val != low_val:
            value = 100 * ((closes[i] - low_val) / (high_val - low_val))
        else:
            value = 50
        results.append(value)
    return results
```

### Difference Calculation

```python
def calculate_difference(series_a, series_b):
    return [a - b for a, b in zip(series_a, series_b)]
```
