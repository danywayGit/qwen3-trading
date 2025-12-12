"""
Merge CSV Files - Combine multiple TradingView exports for same timeframe

Handles multiple CSV exports of the same symbol/timeframe and:
- Concatenates all data
- Removes duplicate timestamps
- Sorts by timestamp
- Saves merged file
"""

import sys
import os
import argparse
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.csv_loader import CSVLoader
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def merge_csv_files(csv_files, output_file):
    """
    Merge multiple CSV files into one
    
    Args:
        csv_files: List of CSV file paths
        output_file: Output merged file path
        
    Returns:
        Merged DataFrame
    """
    logger.info(f"Merging {len(csv_files)} CSV files...")
    
    loader = CSVLoader()
    all_data = []
    
    # Load all CSV files
    for csv_file in csv_files:
        try:
            df = loader.load_csv(csv_file)
            logger.info(f"  ✓ Loaded {csv_file}: {len(df)} rows")
            all_data.append(df)
        except Exception as e:
            logger.error(f"  ❌ Failed to load {csv_file}: {e}")
    
    if not all_data:
        raise ValueError("No valid CSV files loaded")
    
    # Concatenate all DataFrames
    merged = pd.concat(all_data, ignore_index=False)
    logger.info(f"Combined total: {len(merged)} rows")
    
    # Remove duplicates based on timestamp (index)
    original_count = len(merged)
    merged = merged[~merged.index.duplicated(keep='first')]
    duplicates_removed = original_count - len(merged)
    
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate timestamps")
    
    # Sort by timestamp
    merged = merged.sort_index()
    
    # Save to output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    merged.to_csv(output_file, index=True)
    logger.info(f"✓ Saved merged file: {output_file}")
    logger.info(f"  Final: {len(merged)} unique rows")
    logger.info(f"  Range: {merged.index[0]} to {merged.index[-1]}")
    
    return merged


def auto_merge_by_pattern(folder, symbol, timeframe):
    """
    Auto-merge CSV files matching pattern
    
    Args:
        folder: Folder to search
        symbol: Symbol pattern (e.g., 'BTC_USDT', 'BTCUSDT')
        timeframe: Timeframe (e.g., '1h', '4h', '1d')
        
    Returns:
        List of matching files
    """
    logger.info(f"Searching for {symbol} {timeframe} CSV files in {folder}...")
    
    # Normalize patterns
    symbol_patterns = [
        symbol.upper(),
        symbol.lower(),
        symbol.replace('_', ''),
        symbol.replace('_', '-'),
        symbol.replace('/', '_')
    ]
    
    timeframe_patterns = [
        timeframe.upper(),
        timeframe.lower(),
        timeframe.replace('h', 'H'),
        timeframe.replace('d', 'D')
    ]
    
    # Find matching files
    matching_files = []
    
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if not file.endswith('.csv'):
                continue
            
            file_upper = file.upper()
            
            # Check if file matches symbol and timeframe patterns
            symbol_match = any(p.upper() in file_upper for p in symbol_patterns)
            timeframe_match = any(t.upper() in file_upper for t in timeframe_patterns)
            
            if symbol_match and timeframe_match:
                matching_files.append(os.path.join(folder, file))
    
    logger.info(f"Found {len(matching_files)} matching files")
    for f in matching_files:
        logger.info(f"  - {os.path.basename(f)}")
    
    return matching_files


def main():
    parser = argparse.ArgumentParser(
        description='Merge multiple TradingView CSV exports into one file'
    )
    
    parser.add_argument(
        '--files', '-f',
        type=str,
        nargs='+',
        help='List of CSV files to merge'
    )
    
    parser.add_argument(
        '--folder',
        type=str,
        default='data/csv_imports',
        help='Folder to search for CSV files (default: data/csv_imports)'
    )
    
    parser.add_argument(
        '--symbol', '-s',
        type=str,
        help='Symbol to auto-detect files (e.g., BTC_USDT, BTCUSDT)'
    )
    
    parser.add_argument(
        '--timeframe', '-t',
        type=str,
        help='Timeframe to auto-detect files (e.g., 1h, 4h, 1d)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: auto-generated)'
    )
    
    parser.add_argument(
        '--list-only',
        action='store_true',
        help='Only list matching files, do not merge'
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("CSV MERGE TOOL")
    print(f"{'='*60}\n")
    
    # Determine files to merge
    if args.files:
        # User specified files
        csv_files = args.files
    elif args.symbol and args.timeframe:
        # Auto-detect files
        csv_files = auto_merge_by_pattern(args.folder, args.symbol, args.timeframe)
        
        if not csv_files:
            print(f"❌ No files found matching {args.symbol} {args.timeframe}")
            print(f"\nSearched in: {args.folder}")
            print("\nTip: Use --files to specify files manually")
            sys.exit(1)
    else:
        print("❌ Error: Must provide either:")
        print("  --files file1.csv file2.csv ...")
        print("  OR")
        print("  --symbol SYMBOL --timeframe TIMEFRAME")
        sys.exit(1)
    
    # List only mode
    if args.list_only:
        print(f"Found {len(csv_files)} files:\n")
        for f in csv_files:
            print(f"  {f}")
        print(f"\n{'='*60}\n")
        sys.exit(0)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        # Auto-generate output filename
        if args.symbol and args.timeframe:
            symbol_clean = args.symbol.replace('/', '_')
            output_file = os.path.join(
                args.folder,
                f"{symbol_clean}_{args.timeframe}_merged.csv"
            )
        else:
            output_file = os.path.join(args.folder, "merged_output.csv")
    
    print(f"Input files:  {len(csv_files)}")
    print(f"Output file:  {output_file}\n")
    
    try:
        # Merge files
        merged_df = merge_csv_files(csv_files, output_file)
        
        print(f"\n{'='*60}")
        print("✓ MERGE COMPLETE")
        print(f"{'='*60}")
        print(f"Merged {len(csv_files)} files into:")
        print(f"  {output_file}")
        print(f"\nTotal rows: {len(merged_df)}")
        print(f"Date range: {merged_df.index[0]} to {merged_df.index[-1]}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
