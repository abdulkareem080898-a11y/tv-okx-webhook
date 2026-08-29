# TradingView Pine Script Strategies

This directory contains example Pine Script trading strategies designed to work with the OKX webhook receiver.

## Strategies Included

### 1. MA Crossover Strategy (`ma_crossover.pine`)
**Description:** Simple moving average crossover strategy that generates signals when fast and slow MAs cross.

**How it works:**
- **LONG Signal:** When 9-period SMA crosses above 21-period SMA
- **SHORT Signal:** When 9-period SMA crosses below 21-period SMA

**Best for:** Trending markets, medium timeframes (4H, daily)

**Parameters:**
- `fast_ma_length`: Length of fast moving average (default: 9)
- `slow_ma_length`: Length of slow moving average (default: 21)

---

### 2. RSI Momentum Strategy (`rsi_strategy.pine`)
**Description:** Momentum-based strategy using Relative Strength Index (RSI) for mean reversion signals.

**How it works:**
- **LONG Signal:** RSI crosses above oversold level (default: 30)
- **SHORT Signal:** RSI crosses below overbought level (default: 70)
- **CLOSE Signal:** RSI reaches extreme levels (>80 or <20)

**Best for:** Mean reversion, choppy/consolidating markets

**Parameters:**
- `rsi_length`: RSI calculation period (default: 14)
- `overbought`: RSI overbought threshold (default: 70)
- `oversold`: RSI oversold threshold (default: 30)

---

### 3. Breakout Strategy (`breakout_strategy.pine`)
**Description:** Support and resistance breakout strategy that triggers on price breaks.

**How it works:**
- **LONG Signal:** Price breaks above previous resistance + threshold
- **SHORT Signal:** Price breaks below previous support - threshold
- Includes built-in stop loss and take profit levels

**Best for:** Volatile markets, news events, breakout trades

**Parameters:**
- `lookback`: Period for calculating resistance/support (default: 20)
- `breakout_threshold`: Percentage threshold for breakout confirmation (default: 0.2%)
- `stop_loss_percent`: Stop loss distance from entry (default: 2%)
- `take_profit_percent`: Take profit distance from entry (default: 5%)

---

### 4. Multi-Indicator Strategy (`multi_indicator_strategy.pine`)
**Description:** Advanced strategy combining moving averages, RSI, and MACD for confirmation signals.

**How it works:**
- **LONG Signal:** Price above long MA + Short MA above Long MA + RSI not overbought + MACD positive + Volume confirmation
- **SHORT Signal:** Price below long MA + Short MA below Long MA + RSI not oversold + MACD negative + Volume confirmation
- **EXIT:** When trend reverses or RSI extremes reached

**Best for:** Strong trends, higher success rate due to multiple confirmations

**Parameters:**
- `ma_short`: Short MA period (default: 9)
- `ma_long`: Long MA period (default: 21)
- `rsi_len`: RSI period (default: 14)
- `rsi_lower`: RSI lower bound (default: 35)
- `rsi_upper`: RSI upper bound (default: 65)
- `macd_fast`: MACD fast period (default: 12)
- `macd_slow`: MACD slow period (default: 26)
- `macd_signal`: MACD signal period (default: 9)
- `use_volume`: Enable volume filter (default: true)

---

## Setup Instructions

### 1. In TradingView

1. Go to [TradingView Chart](https://www.tradingview.com/chart/)
2. Open Pine Script Editor (Alt+E)
3. Copy the entire contents of one of the strategy files
4. Create a new strategy
5. Paste the code and click "Save"

### 2. Configure Alerts

1. Click "Add alert" on the chart
2. Select your strategy from the dropdown
3. Set alert frequency (once per candle recommended)
4. **Webhook URL:** Use the format:
   ```
   http://your-server:5000/webhook?secret=your_webhook_secret
   ```
5. **Message:** Leave as is - the strategy sends JSON in alerts

### 3. Set Environment Variables

On your server running the webhook receiver:

```bash
export OKX_API_KEY="your_okx_api_key"
export OKX_SECRET="your_okx_secret"
export OKX_PASSPHRASE="your_okx_passphrase"
export WEBHOOK_SECRET="your_webhook_secret"
export INST_ID="ETH-USDT-SWAP"  # or your preferred instrument
export TRADE_SIZE="2"            # contract size
export LEVERAGE="5"              # leverage (be careful!)
```

---

## Expected Alert Format

All strategies send alerts in this JSON format:

```json
{
  "signal": "LONG|SHORT|CLOSE",
  "symbol": "BINANCE:ETHUSDT",
  "price": "2500.50",
  "strategy": "Strategy Name",
  "rsi": "45.23",
  "reason": "Optional reason for the signal"
}
```

The webhook receiver processes:
- **LONG**: Opens a long position (closes short if open)
- **SHORT**: Opens a short position (closes long if open)  
- **CLOSE** or **LONG EXIT**: Closes all positions

---

## Important Notes

⚠️ **Risk Management:**
- Start with small position sizes
- Test strategies on demo account first
- Use stop losses and take profits
- Never risk more than you can afford to lose
- Monitor live trades during first deployment

⚠️ **Technical Considerations:**
- Alerts trigger at candle close (frequency: once per bar)
- Network latency may cause slippage on market orders
- TradingView may have alert rate limits
- Test your webhook URL from TradingView before live trading

---

## Customizing Strategies

To create your own strategy:

1. Start with one of these as a template
2. Modify the indicator calculations and signals
3. Test on historical data using Strategy Tester
4. Adjust parameters for your preferred timeframe
5. Send webhook alerts with the expected JSON format

Example structure:
```pinescript
if your_signal_condition
    alert(json.stringify(map.new()
        .put("signal", "LONG")
        .put("symbol", syminfo.tickerid)
        .put("price", str.tostring(close))
        .put("strategy", "Your Strategy Name")
        ), alert.freq_once_per_bar)
```

---

## Troubleshooting

**Alerts not being received:**
- Check webhook URL and secret match
- Verify server is running and accessible
- Check TradingView alert logs

**Orders not executing:**
- Verify OKX API credentials
- Check account has sufficient margin/balance
- Ensure INST_ID matches your trading pair
- Verify leverage and position mode settings

**Strategy not triggering:**
- Check indicator values on chart
- Verify alert frequency setting
- Review TradingView script logs (click alert → view message)

---

## References

- [Pine Script Documentation](https://www.tradingview.com/pine-script-docs/)
- [Strategy Tester Guide](https://www.tradingview.com/pine-script-docs/en/v5/concepts/Strategies.html)
- [OKX API Documentation](https://www.okx.com/docs-v5/en/)
