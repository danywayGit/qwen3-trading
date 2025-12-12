# Qwen3 Trading Project - AI Agent Instructions

## Project Overview
Trading analysis application using a **two-model pipeline**: quantitative data analysis (Qwen3-Coder) + visual chart analysis (Qwen3-VL) via Ollama HTTP API. Combines numerical precision with pattern recognition for comprehensive trade setups.

## Critical Rules

### Python Environment
- **ALWAYS use virtual environment**: `.venv` in project root
- **Never install packages globally**: All dependencies go in `.venv`
- **Activation required**: Ensure `.venv` is activated before running any Python commands
- **Package installation**: Use `pip install` only within activated `.venv`

### Model Management (External)
- **Models defined in OllamaTools repo**: `C:\Users\danyw\Documents\Git\DanywayGit\OllamaTools\ollama\`
- **Do NOT create Modelfiles here**: Never generate or modify Ollama Modelfile configurations in this repo
- **Model references only**: Reference by name in code/config
- **Two primary models**:
  - `qwen3-coder-30b-ctx32k-quant:latest` - Quantitative data analysis
  - `qwen3-vl-8b-ctx32k-trading:latest` - Visual chart analysis

### Architecture: Two-Model Pipeline
```
Raw Data (CSV/JSON) → Qwen-Coder (Quant) → Numerical Context → Qwen-VL (Trading) + Chart → Final Analysis
```

**Why Two Models?**
- **Qwen-Coder**: Precise calculations, statistical patterns, exact levels from raw OHLCV data
- **Qwen-VL**: Visual patterns, chart formations, indicator confirmation
- **Together**: Divergence detection, higher confidence when aligned, comprehensive analysis

### Ollama API Usage
- **Endpoint**: `/api/chat` (not `/api/generate`)
- **Response parsing**: 
  - Qwen-Coder: Standard `"message"` field
  - Qwen-VL: Output in `"message"` field (trading-specific prompts)
- **No HuggingFace**: Ollama exclusively, not transformers/torch directly

## Model Configurations

### qwen3-coder-30b-ctx32k-quant
```
Purpose: Analyze raw OHLCV data, calculate indicators, detect statistical patterns
Context: 32K tokens
Temperature: 0.1 (precise, deterministic)
Top-p: 0.95
System Prompt: Quantitative trading analyst specializing in numerical data
```

### qwen3-vl-8b-ctx32k-trading
```
Purpose: Analyze chart images, identify visual patterns, provide trade setups
Context: 32K tokens (optimal for RTX 4090, ~21GB GPU usage)
Temperature: 0.2 (consistent chart analysis)
Top-p: 0.9, Top-k: 40
System Prompt: Expert trading analyst with chart analysis capabilities
```

## Project Structure (Expected)
```
qwen3-trading/
├── .venv/                    # Virtual environment (REQUIRED, gitignored)
├── .github/
│   └── copilot-instructions.md  # This file
├── requirements.txt          # Python dependencies (ccxt, pandas, requests, pillow, numpy)
├── config.json              # Model & analysis settings + exchange configs
├── data/
│   ├── ccxt/                # CCXT fetched data (JSON/CSV, gitignored)
│   └── csv_imports/         # Manual TradingView CSV exports (gitignored)
├── charts/
│   ├── manual/              # Manual screenshots from TradingView (gitignored)
│   └── generated/           # Auto-generated charts (future, gitignored)
├── results/
│   ├── json/                # JSON analysis outputs (gitignored)
│   └── reports/             # Human-readable reports (gitignored)
├── src/
│   ├── data/
│   │   ├── ccxt_client.py   # CCXT exchange client
│   │   ├── csv_loader.py    # CSV file loader/parser
│   │   └── data_manager.py  # Unified data source manager
│   ├── analysis/
│   │   ├── quant_analyzer.py    # Step 1: Quantitative analysis
│   │   ├── visual_analyzer.py   # Step 2: Visual chart analysis
│   │   └── pipeline.py          # Combined two-model workflow
│   ├── charts/
│   │   ├── chart_generator.py   # Future: Automated chart generation
│   │   └── screenshot_helper.py # Future: Browser automation
│   ├── utils/
│   │   └── ollama_client.py     # Ollama HTTP client (from qwen3-vl)
│   └── cli/
│       ├── fetch_data.py        # CLI: Fetch data via CCXT
│       ├── analyze.py           # CLI: Run analysis pipeline
│       └── batch_analyze.py     # CLI: Batch analysis
└── scripts/
    ├── setup_ccxt.py        # Setup and test CCXT connection
    └── validate_csv.py      # Validate TradingView CSV format
```

## Development Workflow

### Initial Setup
```powershell
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install ccxt pandas numpy requests pillow python-dotenv

# 3. Create config and data directories
New-Item -ItemType Directory -Force -Path data/ccxt, data/csv_imports, charts/manual, charts/generated, results/json, results/reports

# 4. Create Ollama models (in OllamaTools repo)
cd C:\Users\danyw\Documents\Git\DanywayGit\OllamaTools\ollama
ollama create qwen3-coder-30b-ctx32k-quant -f Modelfile.qwen3-coder-30b-ctx32k-quant
ollama create qwen3-vl-8b-ctx32k-trading -f Modelfile.qwen3-vl-8b-ctx32k-trading

# 5. Verify models and test CCXT
cd C:\Users\danyw\Documents\Git\DanywayGit\qwen3-trading
ollama list
python scripts/setup_ccxt.py  # Test exchange connectivity
```

### Two-Model Analysis Pattern
```python
import ollama

# STEP 1: Quantitative Analysis
def analyze_raw_data(df, symbol):
    """Analyze OHLCV data with quant model"""
    prompt = f"""
    Analyze {symbol} OHLCV data:
    Last 50 closes: {df['close'].tail(50).to_list()}
    Last 50 volumes: {df['volume'].tail(50).to_list()}
    
    Calculate: momentum, volatility (ATR), volume trend, key levels, moving averages
    Output precise numbers with specific price levels.
    """
    response = ollama.chat(
        model='qwen3-coder-30b-ctx32k-quant:latest',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']

# STEP 2: Visual + Integrated Analysis
def combined_analysis(chart_path, quant_context, symbol, timeframe):
    """Combine numerical + visual analysis"""
    prompt = f"""
    {symbol} {timeframe} Trading Setup
    
    QUANTITATIVE CONTEXT:
    {quant_context}
    
    Analyze the chart image and integrate with numerical analysis above.
    
    Provide:
    - Overall trend (data + visual confirmation)
    - Entry price (specific level)
    - Stop loss (specific level and % risk)
    - Take profit targets (TP1, TP2 with prices)
    - Risk-reward ratio
    - Confidence level (1-10) based on data+visual alignment
    - Key risks or divergences between data and chart
    """
    response = ollama.chat(
        model='qwen3-vl-8b-ctx32k-trading:latest',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [chart_path]
        }]
    )
    return response['message']['content']
```

## Code Conventions

### Import Pattern (from qwen3-vl)
```python
# Reuse Ollama client from qwen3-vl repo
from src.ollama_client import OllamaClient

# Or implement simplified version:
import ollama
client = ollama.chat(model='...', messages=[...])
```

### Configuration Management
```python
# config.json structure
{
  "models": {
    "quantitative": "qwen3-coder-30b-ctx32k-quant:latest",
    "visual": "qwen3-vl-8b-ctx32k-trading:latest"
  },
  "exchanges": {
    "default": "binance",
    "available": ["binance", "coinbase", "kraken", "bybit"],
    "ccxt_config": {
      "enableRateLimit": true,
      "timeout": 30000
    }
  },
  "data_sources": {
    "ccxt_enabled": true,
    "csv_enabled": true,
    "csv_folder": "data/csv_imports/",
    "output_format": "json"
  },
  "analysis": {
    "data_periods": 100,
    "timeframes": ["1H", "4H", "Daily"],
    "output_format": "json",
    "save_intermediate": true
  },
  "charts": {
    "manual_folder": "charts/manual/",
    "generated_folder": "charts/generated/",
    "auto_generate": false,
    "required_indicators": ["RSI", "MACD", "Volume", "EMA"]
  }
}
```

### CCXT Integration Pattern
```python
import ccxt
import pandas as pd

def fetch_ohlcv(symbol, timeframe='4h', limit=200, exchange='binance'):
    """Fetch OHLCV data using CCXT"""
    exchange_obj = getattr(ccxt, exchange)({
        'enableRateLimit': True
    })
    
    ohlcv = exchange_obj.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    return df

# Usage
df = fetch_ohlcv('BTC/USDT', '4h', 200, 'binance')
```

### CSV Loading Pattern
```python
def load_tradingview_csv(csv_path):
    """Load TradingView exported CSV"""
    df = pd.read_csv(csv_path)
    
    # TradingView format: time, open, high, low, close, volume
    # Rename if needed
    if 'time' in df.columns:
        df.rename(columns={'time': 'timestamp'}, inplace=True)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Usage
df = load_tradingview_csv('data/csv_imports/BTC_USDT_4H.csv')
```

### Error Handling
```python
# Always wrap Ollama calls
try:
    response = ollama.chat(model='...', messages=[...])
    result = response['message']['content']
except Exception as e:
    print(f"Ollama API error: {e}")
    # Fallback or retry logic
```

## Performance Expectations (RTX 4090)

| Model | Size | GPU Memory | Speed | Best For |
|-------|------|------------|-------|----------|
| **Coder-30B** | 19GB | ~35GB | 5-10s | Numerical calculations |
| **VL-8B** | 6.1GB | ~21GB | 3-4s per image | Chart analysis |

**Combined Pipeline**: ~8-14s total (quant → visual)

## Common Tasks

### Analyzing Single Trade Setup
```python
# 1. Load data (CSV from exchange API)
df = pd.read_csv('BTC_USDT_4H.csv')

# 2. Quantitative analysis
quant = analyze_raw_data(df, 'BTC/USDT')
print("=== QUANT ANALYSIS ===")
print(quant)

# 3. Visual analysis with quant context
trade_setup = combined_analysis(
    'btc_4h_chart.png',
    quant,
    'BTC/USDT',
    '4H'
)
print("=== TRADE SETUP ===")
print(trade_setup)
```

### Batch Analysis (Multiple Symbols)
```python
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

for symbol in symbols:
    df = load_data(symbol)
    chart_path = f'charts/{symbol.replace("/", "_")}.png'
    
    quant = analyze_raw_data(df, symbol)
    setup = combined_analysis(chart_path, quant, symbol, '4H')
    
    save_result(symbol, quant, setup)
```

### Divergence Detection (Key Feature)
```python
# When quant and visual models disagree = important signal!
if "bullish" in quant.lower() and "bearish" in visual.lower():
    print("⚠️ DIVERGENCE: Quant bullish, Chart bearish - potential reversal")
elif "oversold" in quant.lower() and "breakdown" in visual.lower():
    print("⚠️ CONFLICT: RSI oversold but chart breaking down - wait for clarity")
```

## Data Sources & Workflow

### Input Requirements

#### 1. OHLCV Data (Dual Source)
**Primary: CCXT Framework**
- Default exchange: Binance (configurable to other exchanges)
- Programmatic data fetch via CCXT API
- Columns: timestamp, open, high, low, close, volume
- Minimum: 100 periods for statistical analysis

**Secondary: Manual CSV Upload**
- TradingView CSV exports (manual download)
- Drop CSV files in `data/` folder
- Format: TradingView export format (timestamp, open, high, low, close, volume)
- Future: TradingView API integration (if available)

**Configuration:**
```python
# config.json
{
  "data_sources": {
    "ccxt": {
      "default_exchange": "binance",
      "available_exchanges": ["binance", "coinbase", "kraken", "bybit"],
      "rate_limit": true
    },
    "csv_folder": "data/csv_imports/",
    "tradingview": {
      "manual_export": true,
      "api_integration": false  # Future enhancement
    }
  }
}
```

#### 2. Chart Images (Hybrid Approach)
**Manual Screenshots** (Primary for now)
- TradingView chart screenshots
- Save to `charts/` folder
- Naming convention: `{SYMBOL}_{TIMEFRAME}_{TIMESTAMP}.png`
- Resolution: 1920x1080+ recommended
- Indicators: RSI(14), MACD, Volume, EMA(20,50,200)

**Automated Chart Generation** (Future Enhancement)
```python
# Planned approaches:
# 1. Selenium/Playwright: Automate TradingView browser capture
# 2. Matplotlib/Plotly: Generate charts from OHLCV data
# 3. TradingView Webhooks: Trigger screenshot on signal
```

### Example Workflows

#### Workflow 1: CCXT Data + Manual Chart
```powershell
# 1. Fetch data via CCXT
python src/fetch_data.py --symbol BTC/USDT --timeframe 4h --periods 200 --exchange binance

# 2. Manual screenshot from TradingView
# - Open TradingView with BTC/USDT 4H
# - Add indicators: RSI(14), MACD, Volume, EMA(20,50,200)
# - Export > Download image > Save to charts/BTC_USDT_4H_20251212.png

# 3. Run two-model analysis
python src/pipeline.py --symbol BTC/USDT --timeframe 4H --data-source ccxt

# 4. Results saved to results/BTC_USDT_4H_20251212.json
```

#### Workflow 2: CSV Import + Manual Chart
```powershell
# 1. Export from TradingView
# - Select timeframe and date range
# - Export > Export chart data > Save to data/csv_imports/BTC_USDT_4H.csv

# 2. Take screenshot (same timeframe)
# - Save to charts/BTC_USDT_4H_20251212.png

# 3. Run analysis with CSV
python src/pipeline.py --symbol BTC/USDT --timeframe 4H --data-source csv --csv-file data/csv_imports/BTC_USDT_4H.csv

# 4. Results in results/BTC_USDT_4H_20251212.json
```

#### Workflow 3: Batch Analysis (Multiple Symbols)
```powershell
# 1. Fetch all data via CCXT
python src/batch_fetch.py --symbols BTC/USDT,ETH/USDT,SOL/USDT --timeframe 4H

# 2. Take screenshots for each symbol
# - Save as charts/BTC_USDT_4H.png, charts/ETH_USDT_4H.png, etc.

# 3. Run batch analysis
python src/batch_analyze.py --symbols-file symbols.txt --timeframe 4H

# 4. Consolidated results in results/batch_analysis_20251212.json
```

## Anti-Patterns to Avoid
❌ Installing packages without `.venv` activation  
❌ Creating Modelfiles in this repository (use OllamaTools)  
❌ Using only one model (defeats purpose of pipeline)  
❌ Mismatched timeframes (1H data with 4H chart)  
❌ Low-quality chart images (model can't read indicators)  
❌ Ignoring divergences between quant and visual models  
❌ Hardcoding model names (use config.json)  

## Best Practices
✅ Use virtual environment for all Python operations  
✅ Run quant analysis first, feed context to visual model  
✅ Pay special attention when models disagree (divergence signals)  
✅ Match data timeframe to chart timeframe exactly  
✅ Include 100+ periods in data for statistical significance  
✅ Use high-resolution chart screenshots with clear indicators  
✅ Save all analyses to files for later review  
✅ Apply proper risk management (1-2% per trade max)  

## Output Format

### JSON Analysis Output
```json
{
  "metadata": {
    "symbol": "BTC/USDT",
    "timeframe": "4H",
    "timestamp": "2025-12-12T10:30:00Z",
    "data_source": "ccxt",
    "exchange": "binance"
  },
  "quantitative_analysis": {
    "momentum": {
      "5_period": 2.3,
      "10_period": 5.7,
      "20_period": 8.2
    },
    "volatility": {
      "atr": 850.5,
      "atr_percentile": 65
    },
    "volume": {
      "current": 45000,
      "vs_20ma": "+23%",
      "trend": "increasing"
    },
    "key_levels": {
      "resistance": [43500, 45000, 47200],
      "support": [41000, 39500, 38000]
    },
    "indicators": {
      "rsi": 58,
      "macd": "bullish_crossover",
      "ema_20": 42100,
      "ema_50": 41500,
      "ema_200": 40000
    }
  },
  "visual_analysis": {
    "trend": "uptrend",
    "chart_patterns": ["ascending_triangle", "higher_lows"],
    "indicator_confirmation": true,
    "divergences": []
  },
  "integrated_analysis": {
    "alignment": "high",
    "confidence": 8,
    "trade_setup": {
      "direction": "long",
      "entry": 42500,
      "stop_loss": 41200,
      "stop_loss_pct": -3.1,
      "take_profit_1": 44000,
      "take_profit_2": 46500,
      "risk_reward_tp1": 1.5,
      "risk_reward_tp2": 3.1
    },
    "risks": [
      "Counter-trend in higher timeframe (Daily)",
      "Approaching resistance zone"
    ],
    "recommendation": "Long entry with tight risk management"
  }
}
```

**Future Enhancements:**
- Interactive dashboards (Plotly Dash, Streamlit)
- Real-time monitoring UI
- Portfolio aggregation views
- Backtesting integration (see related repos)

## Related Repositories

### Analysis & Models
- **qwen3-vl**: `C:\Users\danyw\Documents\Git\DanywayGit\qwen3-vl` - Visual analysis patterns, ollama_client.py reference
- **OllamaTools**: `C:\Users\danyw\Documents\Git\DanywayGit\OllamaTools\ollama\` - Model definitions, Modelfiles, context configs

### Trading Infrastructure (For Future Integration)
- **BacktestingMCP**: `C:\Users\danyw\Documents\Git\DanywayGit\BacktestingMCP` - Create, optimize, and backtest strategies
- **BackTestingSignals**: `C:\Users\danyw\Documents\Git\DanywayGit\BackTestingSignals` - Backtest signals from Discord/Telegram
- **Trading-WebHook-Bot**: `C:\Users\danyw\Documents\Git\DanywayGit\Trading-WebHook-Bot` - TradingView webhooks, Binance execution, position sizing

**Integration Opportunities:**
1. Use qwen3-trading analysis as input to BacktestingMCP strategies
2. Feed AI-generated signals to BackTestingSignals for validation
3. Connect AI trade setups to Trading-WebHook-Bot for automated execution
4. Compare AI analysis quality vs Discord/Telegram signals

## Hardware Context
- **Target GPU**: NVIDIA RTX 4090 (24GB VRAM)
- **Coder-30B**: Runs with some layers on CPU (~35GB total memory)
- **VL-8B**: Fully on GPU (~21GB usage, 3GB headroom)
- **Why 32K context**: Optimal balance - enough for detailed analysis, fits memory

## Chart Automation (Future Enhancement)

### Approach 1: Browser Automation
```python
# Using Playwright to automate TradingView screenshots
from playwright.sync_api import sync_playwright

def capture_tradingview_chart(symbol, timeframe):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f'https://www.tradingview.com/chart/?symbol={symbol}&interval={timeframe}')
        page.screenshot(path=f'charts/generated/{symbol}_{timeframe}.png')
        browser.close()
```

### Approach 2: Matplotlib Chart Generation
```python
# Generate charts from OHLCV data
import mplfinance as mpf

def generate_chart(df, symbol, timeframe, save_path):
    """Generate chart from DataFrame"""
    mpf.plot(df, type='candle', volume=True, 
             mav=(20, 50, 200),
             savefig=save_path)
```

## References
- **TRADING_README.md**: `OllamaTools\ollama\TRADING_README.md` - Visual model usage guide
- **TWO_MODEL_PIPELINE.md**: `OllamaTools\ollama\TWO_MODEL_PIPELINE.md` - Pipeline architecture details
- **qwen3-vl README**: Pattern reference for Ollama HTTP API usage
- **CCXT Documentation**: https://docs.ccxt.com/ - Exchange API integration

---
*This is a trading analysis tool, not financial advice. Always validate signals, use proper risk management, and never risk more than you can afford to lose.*
