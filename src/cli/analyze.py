"""
Analyze CLI - Run two-model trading analysis

Command-line tool to analyze trading setups
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.analysis.pipeline import AnalysisPipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Run two-model trading analysis (Quantitative + Visual)'
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
        '--chart', '-c',
        type=str,
        required=True,
        help='Path to chart image (REQUIRED)'
    )
    
    parser.add_argument(
        '--data-source', '-d',
        type=str,
        choices=['ccxt', 'csv'],
        default='ccxt',
        help='Data source: ccxt or csv (default: ccxt)'
    )
    
    parser.add_argument(
        '--csv-file',
        type=str,
        default=None,
        help='CSV file path (if data-source=csv)'
    )
    
    parser.add_argument(
        '--periods', '-p',
        type=int,
        default=200,
        help='Number of periods to analyze (default: 200)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print human-readable report'
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"QWEN3 TRADING ANALYSIS")
    print(f"{'='*70}")
    print(f"Symbol:       {args.symbol}")
    print(f"Timeframe:    {args.timeframe}")
    print(f"Data Source:  {args.data_source}")
    print(f"Chart Image:  {args.chart}")
    if args.csv_file:
        print(f"CSV File:     {args.csv_file}")
    print(f"{'='*70}\n")
    
    try:
        # Initialize pipeline
        pipeline = AnalysisPipeline()
        
        # Run analysis
        results = pipeline.analyze(
            symbol=args.symbol,
            timeframe=args.timeframe,
            chart_path=args.chart,
            data_source=args.data_source,
            csv_file=args.csv_file,
            periods=args.periods,
            save_results=not args.no_save
        )
        
        # Print results
        if args.report:
            # Human-readable report
            report = pipeline.generate_report(results)
            print(report)
        else:
            # Summary output
            print(f"\n{'='*70}")
            print("ANALYSIS COMPLETE")
            print(f"{'='*70}\n")
            
            print("QUANTITATIVE ANALYSIS:")
            print(results['quantitative_analysis']['analysis'][:500] + "...\n")
            
            print("VISUAL ANALYSIS:")
            print(results['visual_analysis']['analysis'][:500] + "...\n")
            
            print(f"Alignment: {results['integration']['alignment_status'].upper()}")
            print(f"Divergence: {'YES ⚠️' if results['integration']['divergence_detected'] else 'NO ✓'}")
            print(f"\n{results['integration']['notes']}\n")
            
            if 'output_file' in results:
                print(f"Full results saved to: {results['output_file']}")
        
        print(f"\n{'='*70}")
        print("✓ SUCCESS")
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Verify both models exist: ollama list")
        print("3. Check chart image path is correct")
        print("4. Verify data source is accessible")
        sys.exit(1)


if __name__ == "__main__":
    main()
