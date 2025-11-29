# OpenStoxlify Library Documentation

## LIBRARY PURPOSE

Python library for algorithmic trading with:

- Multi-source market data fetching
- Technical indicator calculation  
- Strategy signal generation
- Professional financial visualization

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

plot(PlotType.LINE, label, timestamp, value)
```

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

### Price Plotting

```python
for quote in market_data.quotes:
    plot(PlotType.LINE, "Price", quote.timestamp, quote.close)
```

### Signal Generation

```python
act(ActionType.LONG, timestamp, 1.0)
```

### Complete Strategy Template

```python
from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act

market_data = fetch("SYMBOL", Provider.Binance, Period.DAILY)

for quote in market_data.quotes:
    plot(PlotType.LINE, "Price", quote.timestamp, quote.close)

act(ActionType.LONG, market_data.quotes[0].timestamp, 1)
draw()
```

## INDICATOR IMPLEMENTATION

### Moving Average

```python
def calculate_sma(market_data, window):
    prices = [quote.close for quote in market_data.quotes]
    return [
        (market_data.quotes[i + window - 1].timestamp, sum(prices[i:i + window]) / window)
        for i in range(len(prices) - window + 1)
    ]
```

### Stochastic Oscillator

```python
def calculate_stochastic(market_data, k_period=14, d_period=3):
    quotes = market_data.quotes
    highs = [q.high for q in quotes]
    lows = [q.low for q in quotes]
    closes = [q.close for q in quotes]
    
    stoch_k = []
    for i in range(k_period - 1, len(closes)):
        current_high = max(highs[i - k_period + 1:i + 1])
        current_low = min(lows[i - k_period + 1:i + 1])
        k = 100 * ((closes[i] - current_low) / (current_high - current_low)) if current_high != current_low else 50
        stoch_k.append((quotes[i].timestamp, k))
    
    return stoch_k, stoch_d
```

## SIGNAL GENERATION PATTERNS

### Crossover Strategy

```python
sma_fast = calculate_sma(market_data, 9)
sma_slow = calculate_sma(market_data, 21)

fast_dict = dict(sma_fast)
slow_dict = dict(sma_slow)

for timestamp, fast_value in sma_fast:
    slow_value = slow_dict.get(timestamp)
    if fast_value > slow_value:
        act(ActionType.LONG, timestamp, 1)
    elif fast_value < slow_value:
        act(ActionType.SHORT, timestamp, 1)
```

### Oscillator Strategy

```python
stoch_k, stoch_d = calculate_stochastic(market_data)
k_dict = dict(stoch_k)
d_dict = dict(stoch_d)

for quote in market_data.quotes:
    if quote.timestamp in k_dict and quote.timestamp in d_dict:
        k = k_dict[quote.timestamp]
        d = d_dict[quote.timestamp]
        if k < 20 and d < 20:
            act(ActionType.LONG, quote.timestamp, 1)
        elif k > 80 and d > 80:
            act(ActionType.SHORT, quote.timestamp, 1)
```

## RULES FOR AI SYSTEMS

- Use only functions and models defined in this documentation
- No additional imports beyond openstoxlify modules
- No print statements or comments in generated code
- Follow the exact patterns shown in examples
- All plotting must use plot() function
- All actions must use act() function
- Always call draw() at the end
- Maintain timestamp alignment across series
