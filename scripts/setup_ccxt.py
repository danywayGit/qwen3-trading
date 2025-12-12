"""
Setup and test CCXT exchange connectivity

Run this script to verify your CCXT setup and exchange access
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ccxt
from src.utils.config_loader import load_config


def test_exchange_connection(exchange_name: str = 'binance'):
    """
    Test connection to exchange and fetch sample data
    
    Args:
        exchange_name: Name of exchange to test
    """
    print(f"\n{'='*60}")
    print(f"Testing CCXT Connection: {exchange_name.upper()}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'enableRateLimit': True,
            'timeout': 30000
        })
        
        print(f"✓ Exchange initialized: {exchange.name}")
        print(f"✓ Has fetchOHLCV: {exchange.has['fetchOHLCV']}")
        print(f"✓ Has fetchTicker: {exchange.has['fetchTicker']}")
        
        # Load markets
        print("\nLoading markets...")
        markets = exchange.load_markets()
        print(f"✓ Markets loaded: {len(markets)} trading pairs")
        
        # Test symbols
        test_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        available_symbols = [s for s in test_symbols if s in markets]
        
        print(f"\nAvailable test symbols: {', '.join(available_symbols)}")
        
        if not available_symbols:
            print("⚠ No test symbols available")
            return
        
        # Fetch sample OHLCV data
        symbol = available_symbols[0]
        print(f"\nFetching OHLCV data for {symbol}...")
        
        ohlcv = exchange.fetch_ohlcv(symbol, '4h', limit=10)
        
        print(f"✓ Fetched {len(ohlcv)} candles")
        print("\nSample data (latest candle):")
        latest = ohlcv[-1]
        print(f"  Timestamp: {latest[0]}")
        print(f"  Open:      {latest[1]}")
        print(f"  High:      {latest[2]}")
        print(f"  Low:       {latest[3]}")
        print(f"  Close:     {latest[4]}")
        print(f"  Volume:    {latest[5]}")
        
        # Fetch ticker
        print(f"\nFetching ticker for {symbol}...")
        ticker = exchange.fetch_ticker(symbol)
        print(f"✓ Current price: ${ticker['last']:,.2f}")
        print(f"  24h Volume:    ${ticker['quoteVolume']:,.0f}")
        print(f"  24h Change:    {ticker['percentage']:.2f}%")
        
        print(f"\n{'='*60}")
        print("✓ CCXT SETUP SUCCESSFUL")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure internet connection is active")
        print("2. Check if exchange is operational")
        print("3. Verify CCXT version: pip install --upgrade ccxt")
        print(f"{'='*60}\n")
        return False


def test_ollama_models():
    """Test Ollama models availability"""
    print(f"\n{'='*60}")
    print("Testing Ollama Models")
    print(f"{'='*60}\n")
    
    try:
        from src.utils.ollama_client import OllamaClient
        
        client = OllamaClient()
        models = client.list_models()
        
        print(f"✓ Ollama is running")
        print(f"✓ Found {len(models)} models\n")
        
        # Check for required models
        required_models = [
            'qwen3-coder-30b-ctx32k-quant:latest',
            'qwen3-vl-8b-ctx32k-trading:latest'
        ]
        
        for model in required_models:
            exists = model in models
            status = "✓" if exists else "❌"
            print(f"{status} {model}")
        
        all_exist = all(model in models for model in required_models)
        
        if all_exist:
            print(f"\n{'='*60}")
            print("✓ ALL REQUIRED MODELS AVAILABLE")
            print(f"{'='*60}\n")
        else:
            print("\n⚠ Some models are missing")
            print("Create them in OllamaTools repo:")
            print("  cd C:\\Users\\danyw\\Documents\\Git\\DanywayGit\\OllamaTools\\ollama")
            print("  ollama create qwen3-coder-30b-ctx32k-quant -f Modelfile.qwen3-coder-30b-ctx32k-quant")
            print("  ollama create qwen3-vl-8b-ctx32k-trading -f Modelfile.qwen3-vl-8b-ctx32k-trading")
            print(f"{'='*60}\n")
        
        return all_exist
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nEnsure Ollama is running: ollama serve")
        print(f"{'='*60}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Qwen3 Trading - Setup Verification")
    print("="*60)
    
    # Load config
    try:
        config = load_config()
        default_exchange = config['exchanges']['default']
        print(f"✓ Configuration loaded")
        print(f"  Default exchange: {default_exchange}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)
    
    # Test CCXT
    ccxt_ok = test_exchange_connection(default_exchange)
    
    # Test Ollama
    ollama_ok = test_ollama_models()
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    print(f"CCXT Exchange Access:  {'✓ OK' if ccxt_ok else '❌ FAILED'}")
    print(f"Ollama Models:         {'✓ OK' if ollama_ok else '❌ FAILED'}")
    print("="*60 + "\n")
    
    if ccxt_ok and ollama_ok:
        print("🎉 Setup complete! Ready to analyze trades.")
        print("\nNext steps:")
        print("  1. Take a chart screenshot and save to charts/manual/")
        print("  2. Run: python src/cli/analyze.py --symbol BTC/USDT --timeframe 4h")
        sys.exit(0)
    else:
        print("⚠ Setup incomplete. Fix errors above before proceeding.")
        sys.exit(1)
