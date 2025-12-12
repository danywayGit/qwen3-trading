# Qwen3 Trading - Quick Start Guide

## 🎯 What You Have Now

A complete **two-model AI trading analysis system** that combines:
- **Quantitative Analysis** (Qwen3-Coder) - Precise numerical calculations from OHLCV data
- **Visual Analysis** (Qwen3-VL) - Chart pattern recognition and technical analysis
- **Divergence Detection** - Identifies when models disagree (important signals!)

## ✅ What's Been Built

### Phase 1: Foundation ✓
- Project structure with all directories
- Virtual environment with dependencies installed
- Configuration system
- Ollama client for model interaction

### Phase 2: Data Layer ✓
- **CCXT Client** - Fetch data from Binance (or other exchanges)
- **CSV Loader** - Import TradingView CSV exports
- **Data Manager** - Unified interface with caching

### Phase 3: Analysis Layer ✓
- **Quantitative Analyzer** - Statistical analysis with Qwen3-Coder
- **Visual Analyzer** - Chart analysis with Qwen3-VL
- **Analysis Pipeline** - Orchestrates two-model workflow

### Phase 4: CLI Tools ✓
- `fetch_data.py` - Download OHLCV data
- `analyze.py` - Run single symbol analysis
- `batch_analyze.py` - Analyze multiple symbols
- `validate_csv.py` - Check CSV file quality

## 🚀 Usage Examples

### 1. Fetch Data from Exchange
```powershell
.venv\Scripts\activate
python src/cli/fetch_data.py BTC/USDT --timeframe 4h --periods 200
```

### 2. Analyze Single Trade Setup
```powershell
# Requirements:
# - OHLCV data (auto-fetched from Binance if using CCXT)
# - Chart screenshot saved to charts/manual/BTC_USDT_4H.png

python src/cli/analyze.py BTC/USDT --timeframe 4h --chart charts/manual/BTC_USDT_4H.png

# With full report
python src/cli/analyze.py BTC/USDT -t 4h -c charts/manual/BTC_USDT_4H.png --report
```

### 3. Analyze with CSV Data
```powershell
# Export CSV from TradingView, save to data/csv_imports/
python src/cli/analyze.py BTC/USDT -t 4h -c charts/manual/BTC_USDT_4H.png --data-source csv --csv-file data/csv_imports/BTC_USDT_4H.csv
```

### 4. Batch Analysis (Multiple Symbols)
```powershell
# Create symbols.txt with list of pairs
python src/cli/batch_analyze.py --symbols-file symbols.txt --timeframe 4h

# Or specify directly
python src/cli/batch_analyze.py --symbols BTC/USDT ETH/USDT SOL/USDT -t 4h
```

### 5. Validate CSV Before Use
```powershell
python scripts/validate_csv.py data/csv_imports/BTC_USDT_4H.csv --verbose
```

## 📊 Workflow: Manual Chart Analysis

1. **Get OHLCV Data**
   ```powershell
   python src/cli/fetch_data.py BTC/USDT -t 4h -p 200
   ```

2. **Take Chart Screenshot**
   - Open TradingView with BTC/USDT 4H chart
   - Add indicators: RSI(14), MACD, Volume, EMA(20,50,200)
   - Take screenshot
   - Save to `charts/manual/BTC_USDT_4H.png`

3. **Run Analysis**
   ```powershell
   python src/cli/analyze.py BTC/USDT -t 4h -c charts/manual/BTC_USDT_4H.png --report
   ```

4. **Review Results**
   - JSON output in `results/json/`
   - Human-readable report in terminal (with --report flag)
   - Check for divergences between models

## 📁 Where Things Are

```
qwen3-trading/
├── data/
│   ├── ccxt/           # Auto-downloaded exchange data
│   └── csv_imports/    # Your TradingView CSV exports
├── charts/
│   ├── manual/         # Your chart screenshots (put them here!)
│   └── generated/      # Future: auto-generated charts
├── results/
│   ├── json/           # Analysis results (JSON format)
│   └── reports/        # Future: formatted reports
└── src/
    ├── data/           # CCXT & CSV loaders
    ├── analysis/       # Two-model analyzers
    ├── utils/          # Ollama client, config loader
    └── cli/            # Command-line tools
```

## 🔧 Configuration

Edit `config.json` to customize:
- Model names and parameters
- Exchange settings (switch from Binance to others)
- Data source preferences
- Output formats
- Analysis thresholds

## ⚠️ Important Notes

1. **Chart Naming Convention**:
   - Use format: `{SYMBOL}_{TIMEFRAME}.png`
   - Example: `BTC_USDT_4H.png`, `ETH_USDT_1D.png`
   - Batch analysis auto-detects charts this way

2. **Timeframe Matching**:
   - Data timeframe MUST match chart timeframe
   - 4H data with 1H chart = inaccurate analysis

3. **Ollama Must Be Running**:
   - Start: `ollama serve`
   - Verify models: `ollama list`

4. **Results Are Saved**:
   - All analyses auto-save to `results/json/`
   - Include timestamp in filename
   - Can be loaded for later review

## 🎓 Understanding Divergences

When quant and visual models disagree:
```
Quant: "Bullish momentum, RSI oversold"
Visual: "Bearish breakdown below support"
```

**This is important!** Divergences often signal:
- Market transitions/reversals
- False breakouts
- Require extra caution

## 🔜 Next Steps (Future Enhancements)

- **Chart Automation**: Playwright/Selenium to auto-capture TradingView
- **Real-time Monitoring**: Live analysis on schedule
- **Integration**: Connect to BacktestingMCP, Trading-WebHook-Bot
- **Dashboard**: Interactive UI with Plotly/Streamlit

## 💡 Tips

1. **Start Simple**: Analyze one symbol first to understand workflow
2. **High Quality Charts**: Use 1920x1080+ screenshots with clear indicators
3. **Compare Timeframes**: Run same symbol on 1H, 4H, 1D for multi-TF analysis
4. **Trust Divergences**: When models disagree, proceed with extra caution
5. **Risk Management**: 1-2% position size max, always use stop losses

## 🐛 Troubleshooting

**"Import errors"**: Activate venv first
```powershell
.venv\Scripts\activate
```

**"Ollama connection failed"**: Start Ollama
```powershell
ollama serve
```

**"Model not found"**: Create models in OllamaTools repo
```powershell
cd C:\Users\danyw\Documents\Git\DanywayGit\OllamaTools\ollama
ollama create qwen3-coder-30b-ctx32k-quant -f Modelfile.qwen3-coder-30b-ctx32k-quant
ollama create qwen3-vl-8b-ctx32k-trading -f Modelfile.qwen3-vl-8b-ctx32k-trading
```

**"Chart not found"**: Check filename matches pattern
```
Expected: charts/manual/BTC_USDT_4H.png
Actual:   charts/manual/bitcoin_4h.png  ❌
```

---

**Remember**: This is analysis tooling, not financial advice. Always validate, use proper risk management, never risk more than you can afford to lose.
