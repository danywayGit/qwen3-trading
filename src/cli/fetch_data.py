"""
Fetch Data CLI - Download OHLCV data via CCXT

Command-line tool to fetch trading data from exchanges
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.ccxt_client import CCXTClient
from src.utils.config_loader import load_config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch OHLCV data from crypto exchanges'
    )
    
    parser.add_argument(
        'symbol',
        type=str,
        help='Trading pair (e.g., BTC/USDT)'
    )
    
    parser.add_argument(
        '--timeframe', '-t',
        type=str,
        default='4h',
        help='Timeframe (default: 4h)'
    )
    
    parser.add_argument(
        '--periods', '-p',
        type=int,
        default=200,
        help='Number of candles to fetch (default: 200)'
    )
    
    parser.add_argument(
        '--exchange', '-e',
        type=str,
        default=None,
        help='Exchange name (default: from config)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output CSV file path'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    exchange = args.exchange or config['exchanges']['default']
    
    print(f"\n{'='*60}")
    print(f"Fetching Data: {args.symbol}")
    print(f"{'='*60}")
    print(f"Exchange:  {exchange}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Periods:   {args.periods}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize client
        client = CCXTClient(exchange)
        
        # Fetch data
        df = client.fetch_ohlcv(
            symbol=args.symbol,
            timeframe=args.timeframe,
            limit=args.periods
        )
        
        print(f"✓ Fetched {len(df)} candles")
        print(f"\nData range: {df.index[0]} to {df.index[-1]}")
        print(f"Latest close: ${df['close'].iloc[-1]:,.2f}")
        print(f"Latest volume: {df['volume'].iloc[-1]:,.0f}")
        
        # Save to file
        if args.output:
            output_path = args.output
        else:
            # Auto-generate filename
            symbol_safe = args.symbol.replace('/', '_')
            output_path = f"data/ccxt/{symbol_safe}_{args.timeframe}.csv"
            os.makedirs('data/ccxt', exist_ok=True)
        
        client.save_to_csv(df, output_path)
        print(f"\n✓ Saved to: {output_path}")
        
        print(f"\n{'='*60}")
        print("SUCCESS")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
