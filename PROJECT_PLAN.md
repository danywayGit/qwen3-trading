# Qwen3 Trading - Development Plan

## Project Goal
Build a two-model AI trading analysis system combining quantitative data analysis (Qwen3-Coder) with visual chart analysis (Qwen3-VL) for comprehensive trade setups.

## Phase 1: Foundation Setup ✅ COMPLETE

### Step 1.1: Project Structure ✅
- [x] Create directory structure
- [x] Set up virtual environment (.venv)
- [x] Create .gitignore
- [x] Create requirements.txt
- [x] Create config.json

### Step 1.2: Core Dependencies ✅
- [x] Install CCXT for exchange data
- [x] Install pandas, numpy for data processing
- [x] Install pillow for image handling
- [x] Install requests for Ollama API
- [x] Test imports and environment

### Step 1.3: Ollama Models Setup ✅
- [x] Verify qwen3-coder-30b-ctx32k-quant exists
- [x] Verify qwen3-vl-8b-ctx32k-trading exists
- [x] Test both models with simple prompts
- [x] Document model performance baseline

## Phase 2: Data Layer ✅ COMPLETE

### Step 2.1: CCXT Integration ✅
- [x] Create ccxt_client.py with Binance default
- [x] Implement fetch_ohlcv() function
- [x] Add exchange switching capability
- [x] Test with BTC/USDT, ETH/USDT
- [x] Error handling and rate limiting

### Step 2.2: CSV Data Loader ✅
- [x] Create csv_loader.py
- [x] Parse TradingView CSV format
- [x] Validate data columns and types
- [x] Handle missing data/gaps
- [x] Test with sample CSV files

### Step 2.3: Data Manager ✅
- [x] Create data_manager.py
- [x] Unified interface for CCXT + CSV
- [x] Data validation and normalization
- [x] Caching strategy (implemented)
- [x] CLI tool: fetch_data.py

## Phase 3: Analysis Layer ✅ COMPLETE

### Step 3.1: Ollama Client ✅
- [x] Port ollama_client.py from qwen3-vl
- [x] Adapt for both text and vision models
- [x] Add retry logic and error handling
- [x] Test with both models
- [x] Response parsing utilities

### Step 3.2: Quantitative Analyzer ✅
- [x] Create quant_analyzer.py
- [x] Implement analyze_raw_data() function
- [x] Prompt engineering for Qwen-Coder
- [x] Extract numerical insights from response
- [x] Unit tests with sample data

### Step 3.3: Visual Analyzer ✅
- [x] Create visual_analyzer.py
- [x] Implement analyze_chart() function
- [x] Prompt engineering for Qwen-VL
- [x] Context injection from quant analysis
- [x] Parse trade setups from response

### Step 3.4: Analysis Pipeline ✅
- [x] Create pipeline.py
- [x] Orchestrate two-model workflow
- [x] Divergence detection logic
- [x] Confidence scoring algorithm
- [x] JSON output formatting

## Phase 4: CLI Tools ✅ COMPLETE

### Step 4.1: Single Analysis CLI ✅
- [x] Create analyze.py
- [x] Command-line argument parsing
- [x] Data source selection (CCXT/CSV)
- [x] Chart path input
- [x] Pretty-print results

### Step 4.2: Batch Analysis CLI ✅
- [x] Create batch_analyze.py
- [x] Multiple symbols processing
- [x] Parallel processing (optional)
- [x] Progress tracking
- [x] Consolidated reports

### Step 4.3: Utility Scripts ✅
- [x] setup_ccxt.py - Test exchange connectivity
- [x] validate_csv.py - Validate TradingView CSVs
- [x] test_models.py - Quick model health check

## Phase 5: Chart Automation (Future)

### Step 5.1: Manual Workflow
- [ ] Document screenshot process
- [ ] File naming conventions
- [ ] Chart quality guidelines
- [ ] Indicator checklist

### Step 5.2: Automated Generation (Later)
- [ ] Research Playwright for TradingView
- [ ] Matplotlib/mplfinance chart generation
- [ ] Evaluate trade-offs
- [ ] Implement chosen approach

## Phase 6: Integration & Testing

### Step 6.1: End-to-End Testing
- [ ] Test full pipeline with real data
- [ ] Validate JSON output format
- [ ] Test divergence detection
- [ ] Performance benchmarking

### Step 6.2: Documentation
- [ ] Update README.md
- [ ] Create usage examples
- [ ] Document configuration options
- [ ] Troubleshooting guide

### Step 6.3: Future Integrations
- [ ] Analyze BacktestingMCP integration points
- [ ] Analyze BackTestingSignals integration
- [ ] Analyze Trading-WebHook-Bot integration
- [ ] Design integration architecture

## Phase 7: Enhancements (Future)

### Step 7.1: Interactive Dashboard
- [ ] Evaluate Plotly Dash vs Streamlit
- [ ] Design UI mockups
- [ ] Implement real-time monitoring
- [ ] Portfolio aggregation views

### Step 7.2: Advanced Features
- [ ] Multi-timeframe analysis automation
- [ ] Alert system for high-confidence setups
- [ ] Historical analysis archive
- [ ] Performance tracking

---

## Current Status: Phase 1-4 COMPLETE ✅

### ✅ MVP READY - All Core Features Implemented

**Completed:**
1. ✅ Complete project structure
2. ✅ Virtual environment with all dependencies
3. ✅ CCXT integration for exchange data
4. ✅ CSV loader for TradingView exports
5. ✅ Two-model analysis pipeline (Quant + Visual)
6. ✅ CLI tools (fetch, analyze, batch, validate)
7. ✅ JSON output with divergence detection
8. ✅ Ollama models verified and tested

**Ready to Use:**
- Fetch data from Binance (or other exchanges)
- Analyze single symbols with two-model pipeline
- Batch analyze multiple symbols
- Detect divergences between models
- Export results to JSON

**Next: User Testing & Real-World Analysis**

---

## Development Principles

1. **Incremental Progress**: Complete one step before moving to next
2. **Test Early**: Validate each component with sample data
3. **Config-Driven**: Minimize hardcoded values
4. **Error Handling**: Graceful failures with clear messages
5. **Documentation**: Update docs as code evolves

## Timeline Estimate

- **Phase 1**: 1-2 hours
- **Phase 2**: 3-4 hours
- **Phase 3**: 5-6 hours
- **Phase 4**: 2-3 hours
- **Phase 5**: Future (TBD)
- **Phase 6**: 2-3 hours

**Total MVP**: ~15-20 hours of focused development
