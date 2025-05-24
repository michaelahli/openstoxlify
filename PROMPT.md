**OpenStoxlify Library Documentation Template for AI Systems**

# LIBRARY PURPOSE

Python library for algorithmic trading with:

- Multi-source market data fetching
- Technical indicator calculation
- Strategy signal generation
- Professional financial visualization

# CORE COMPONENTS

## 1. Data Module (`fetch`)

```python
from openstoxlify import fetch
from openstoxlify.models import Provider, Period

# Usage pattern:
data = fetch(
    symbol: str,               # Trading pair (e.g., "BTCUSDT")
    provider: Provider,        # Provider.YFinance or Provider.Binance
    period: Period            # Timeframe (e.g., Period.DAILY)
)
```

## 2. Plotting Module (`plot`)

```python
from openstoxlify import plot
from openstoxlify.models import PlotType

# Usage patterns:
plot(
    PlotType.LINE,            # LINE/HISTOGRAM/AREA
    label: str,               # Display name
    timestamp: datetime,      # Point in time
    value: float              # Data value
)
```

## 3. Strategy Module (`act`)

```python
from openstoxlify import act
from openstoxlify.models import ActionType

# Usage pattern:
act(
    ActionType.LONG/SHORT,    # Trade direction
    timestamp: datetime,      # Entry time
    amount: float             # Position size
)
```

## 4. Visualization (`draw`)

```python
from openstoxlify import draw

# Renders all plotted elements
draw()  
```

# STRATEGY CREATION TEMPLATE

```python
# 1. Configure strategy parameters
SYMBOL = "BTCUSDT"
TIMEFRAME = Period.HOURLY
INDICATOR_PARAMS = {...}

# 2. Fetch market data
data = fetch(SYMBOL, Provider.Binance, TIMEFRAME)

# 3. Calculate indicators
def calculate_indicator(values):
    # Implement indicator logic
    return indicator_values

# 4. Generate signals
for i, quote in enumerate(data.quotes):
    # Plot price data
    plot(PlotType.LINE, "Price", quote.timestamp, quote.close)
    
    # Generate signals based on conditions
    if buy_condition:
        act(ActionType.LONG, quote.timestamp, 1)
    elif sell_condition:
        act(ActionType.SHORT, quote.timestamp, 1)

# 5. Visualize results
draw()
```

# INDICATOR IMPLEMENTATION GUIDE

Common patterns for indicators:

1. **Moving Averages**:

   ```python
   def sma(data, window):
       return [sum(data[i-window:i])/window 
               for i in range(window, len(data)+1)]
   ```

2. **Oscillators (RSI, MACD)**:

   ```python
   def rsi(prices, window=14):
       deltas = np.diff(prices)
       gains = deltas.clip(min=0)
       losses = -deltas.clip(max=0)
       return 100 - (100 / (1 + (gains.mean()/losses.mean())))
   ```

# SIGNAL GENERATION PATTERNS

1. **Crossover Signals**:

   ```python
   if fast_ma[i-1] < slow_ma[i-1] and fast_ma[i] > slow_ma[i]:
       act(ActionType.LONG, ...)
   ```

2. **Threshold Breakouts**:

   ```python
   if rsi_value < 30:
       act(ActionType.LONG, ...)
   elif rsi_value > 70:
       act(ActionType.SHORT, ...)
   ```

# VISUALIZATION OPTIONS

1. **Multi-panel Layouts**:

   ```python
   fig, (ax1, ax2) = plt.subplots(2, 1)
   draw(ax=ax1)  # Price + indicators
   plot_volume(ax=ax2)  # Custom volume plot
   ```

2. **Style Customization**:

   ```python
   plt.style.use('dark_background')
   plt.rcParams['lines.linewidth'] = 1.5
   ```

# EXAMPLE STRATEGIES

1. **Moving Average Crossover**
2. **Bollinger Band Mean Reversion**
3. **MACD Divergence**
4. **Support/Resistance Breakout**

# ERROR HANDLING

Common issues:

- Check `len(data) > window` before indicator calc
- Verify timestamp alignment when comparing series
- Handle division by zero in indicators

# BEST PRACTICES

1. Test strategies with:

   ```python
   data = fetch(..., Period.DAILY)  # Start with daily
   ```

2. Visualize all components:

   ```python
   plot(PlotType.LINE, "Indicator", ...)
   ```

3. Document signal logic with:

   ```python
   act(..., notes="EMA9 > EMA21")
   ```

# Rules for LLM  

- **No comments**  
- **No descriptions**  
- **No print statements**  
- **No new arguments**  
- **Only use variables/functions defined above**  
- **Strictly follow the template structure**  

**Example Output Format:**  

```python  
from openstoxlify.models import Period, Provider, PlotType, ActionType  
from openstoxlify.fetch import fetch  
from openstoxlify.plotter import plot  
from openstoxlify.strategy import act  
from openstoxlify.draw import draw  

data = fetch("BTCUSDT", Provider.Binance, Period.HOURLY)  
quotes = data.quotes  
closes = [q.close for q in quotes]  

def calculate_ema(data, window):  
    return [...]  

ema12 = calculate_ema(closes, 12)  
ema26 = calculate_ema(closes, 26)  

for i in range(26, len(closes)):  
    current_time = quotes[i].timestamp  
    current_price = closes[i]  

    plot(PlotType.LINE, "Price", current_time, current_price)  
    plot(PlotType.LINE, "EMA12", current_time, ema12[i-12])  
    plot(PlotType.LINE, "EMA26", current_time, ema26[i-26])  

    if ema12[i-12] > ema26[i-26] and ema12[i-13] <= ema26[i-27]:  
        act(ActionType.LONG, current_time, 1)  
    elif ema12[i-12] < ema26[i-26] and ema12[i-13] >= ema26[i-27]:  
        act(ActionType.SHORT, current_time, 1)  

draw()  
```  

**Strict Compliance Required.**  
**No Deviations.**  
**No Explanations.**
