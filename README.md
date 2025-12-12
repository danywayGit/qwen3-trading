# Qwen3 Trading Analysis

AI-powered trading analysis system combining quantitative data analysis with visual chart recognition for comprehensive trade setups.

## Quick Start

```powershell
# 1. Setup virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Ollama models
ollama list
# Should show: qwen3-coder-30b-ctx32k-quant:latest
#              qwen3-vl-8b-ctx32k-trading:latest

# 4. Test CCXT connection
python scripts/setup_ccxt.py

# 5. Run analysis
python src/cli/analyze.py --symbol BTC/USDT --timeframe 4h
```

## Architecture

**Two-Model Pipeline:**
```
Raw OHLCV Data → Qwen-Coder (Quantitative) → Context → Qwen-VL (Visual) + Chart → Trade Setup
```

- **Model 1**: `qwen3-coder-30b-ctx32k-quant` - Numerical analysis, indicators, levels
- **Model 2**: `qwen3-vl-8b-ctx32k-trading` - Chart patterns, visual confirmation

## Project Status

🚧 **Currently in development** - See [PROJECT_PLAN.md](PROJECT_PLAN.md) for roadmap

- ✅ Phase 1: Foundation Setup (In Progress)
- ⏳ Phase 2: Data Layer
- ⏳ Phase 3: Analysis Layer
- ⏳ Phase 4: CLI Tools

## Features

- **Dual Data Sources**: CCXT (Binance default) + Manual CSV imports (TradingView)
- **Two-Model Analysis**: Numerical precision + Visual pattern recognition
- **Divergence Detection**: Identify when models disagree (key trading signals)
- **JSON Output**: Structured results for downstream integration
- **Multi-Timeframe**: Support for 1H, 4H, Daily analysis

## Documentation

- [Copilot Instructions](.github/copilot-instructions.md) - AI agent guidelines
- [Project Plan](PROJECT_PLAN.md) - Development roadmap
- [Related Repos](#related-repositories) - Integration opportunities

## Related Repositories

- **qwen3-vl**: Visual analysis reference implementation
- **OllamaTools**: Model definitions and configurations
- **BacktestingMCP**: Strategy backtesting (future integration)
- **BackTestingSignals**: Signal validation (future integration)
- **Trading-WebHook-Bot**: Trade execution (future integration)

## Requirements

- Python 3.10+
- Ollama with both models installed
- RTX 4090 or similar GPU (recommended)
- CCXT-compatible exchange API access (optional)

## License

MIT License - See LICENSE file for details

---

⚠️ **Disclaimer**: This is a trading analysis tool, not financial advice. Always validate signals, use proper risk management, and never risk more than you can afford to lose.
