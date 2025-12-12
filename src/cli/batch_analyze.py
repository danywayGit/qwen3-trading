"""
Batch Analyze CLI - Analyze multiple symbols

Command-line tool for batch trading analysis
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.analysis.pipeline import AnalysisPipeline
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_symbols_file(filepath: str) -> list:
    """Load symbols from text file (one per line)"""
    with open(filepath, 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols


def find_chart_for_symbol(symbol: str, timeframe: str, chart_folder: str) -> str:
    """Find chart image for symbol"""
    symbol_norm = symbol.replace('/', '_').replace('-', '_')
    patterns = [
        f"{symbol_norm}_{timeframe}.png",
        f"{symbol_norm}_{timeframe.upper()}.png",
        f"{symbol_norm}_{timeframe.lower()}.png",
        f"{symbol_norm}.png"
    ]
    
    for pattern in patterns:
        path = os.path.join(chart_folder, pattern)
        if os.path.exists(path):
            return path
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Batch trading analysis for multiple symbols'
    )
    
    parser.add_argument(
        '--symbols', '-s',
        type=str,
        nargs='+',
        help='List of symbols (e.g., BTC/USDT ETH/USDT)'
    )
    
    parser.add_argument(
        '--symbols-file', '-f',
        type=str,
        help='File with symbols (one per line)'
    )
    
    parser.add_argument(
        '--timeframe', '-t',
        type=str,
        default='4h',
        help='Timeframe (default: 4h)'
    )
    
    parser.add_argument(
        '--chart-folder',
        type=str,
        default='charts/manual',
        help='Folder containing chart images (default: charts/manual)'
    )
    
    parser.add_argument(
        '--data-source', '-d',
        type=str,
        choices=['ccxt', 'csv'],
        default='ccxt',
        help='Data source (default: ccxt)'
    )
    
    parser.add_argument(
        '--periods', '-p',
        type=int,
        default=200,
        help='Number of periods (default: 200)'
    )
    
    args = parser.parse_args()
    
    # Get symbol list
    if args.symbols:
        symbols = args.symbols
    elif args.symbols_file:
        symbols = load_symbols_file(args.symbols_file)
    else:
        print("Error: Must provide either --symbols or --symbols-file")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"BATCH TRADING ANALYSIS")
    print(f"{'='*70}")
    print(f"Symbols:      {len(symbols)}")
    print(f"Timeframe:    {args.timeframe}")
    print(f"Data Source:  {args.data_source}")
    print(f"Chart Folder: {args.chart_folder}")
    print(f"{'='*70}\n")
    
    # Initialize pipeline
    pipeline = AnalysisPipeline()
    
    # Track results
    all_results = []
    successful = 0
    failed = 0
    
    # Analyze each symbol
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Analyzing {symbol}...")
        
        # Find chart
        chart_path = find_chart_for_symbol(symbol, args.timeframe, args.chart_folder)
        
        if not chart_path:
            print(f"  ⚠️  Chart not found for {symbol}, skipping")
            failed += 1
            continue
        
        try:
            results = pipeline.analyze(
                symbol=symbol,
                timeframe=args.timeframe,
                chart_path=chart_path,
                data_source=args.data_source,
                periods=args.periods,
                save_results=True
            )
            
            all_results.append({
                'symbol': symbol,
                'status': 'success',
                'output_file': results.get('output_file'),
                'alignment': results['integration']['alignment_status'],
                'divergence': results['integration']['divergence_detected']
            })
            
            print(f"  ✓ Complete - Alignment: {results['integration']['alignment_status']}")
            successful += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            all_results.append({
                'symbol': symbol,
                'status': 'failed',
                'error': str(e)
            })
            failed += 1
    
    # Save batch summary
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_path = f"results/json/batch_summary_{timestamp}.json"
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_symbols': len(symbols),
        'successful': successful,
        'failed': failed,
        'timeframe': args.timeframe,
        'data_source': args.data_source,
        'results': all_results
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n{'='*70}")
    print("BATCH ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"Total:      {len(symbols)}")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"\nSummary saved to: {summary_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
