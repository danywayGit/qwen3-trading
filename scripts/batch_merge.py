#!/usr/bin/env python3
"""
Batch CSV Merge Script
Automatically detects and merges all CSV files by timeframe pattern.
Handles TradingView export format with numbered duplicates.
"""

import os
import re
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from collections import defaultdict

def detect_csv_groups(folder: str) -> dict:
    """
    Detect CSV files and group them by timeframe.
    
    Args:
        folder: Path to folder containing CSV files
        
    Returns:
        Dictionary mapping timeframe -> list of file paths
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder}")
        return {}
    
    # Pattern to match TradingView CSV exports
    # Examples: "CRYPTO_BTCUSD, 60.csv", "CRYPTO_BTCUSD, 60 (1).csv"
    pattern = re.compile(r'.*,\s*(\d+|1D)(?:\s*\(\d+\))?\.csv$', re.IGNORECASE)
    
    groups = defaultdict(list)
    
    for file_path in folder_path.glob('*.csv'):
        match = pattern.match(file_path.name)
        if match:
            timeframe = match.group(1)
            groups[timeframe].append(file_path)
    
    # Sort files within each group (base file first, then numbered)
    for timeframe in groups:
        groups[timeframe].sort(key=lambda p: (
            ' (' in p.name,  # Files without (N) come first
            p.name  # Then alphabetical
        ))
    
    return dict(groups)

def merge_csv_files(file_paths: list, timeframe: str, output_folder: str) -> dict:
    """
    Merge multiple CSV files, remove duplicates, and save result.
    
    Args:
        file_paths: List of Path objects to merge
        timeframe: Timeframe identifier (e.g., '60', '240', '1D')
        output_folder: Where to save merged file
        
    Returns:
        Dictionary with merge statistics
    """
    print(f"\n📊 Processing {timeframe}min files...")
    
    # Read all CSVs
    dfs = []
    total_rows_before = 0
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"  [{i}/{len(file_paths)}] Reading {file_path.name}...")
        try:
            df = pd.read_csv(file_path)
            rows = len(df)
            total_rows_before += rows
            print(f"      ✓ Loaded {rows:,} rows")
            dfs.append(df)
        except Exception as e:
            print(f"      ❌ Error reading {file_path.name}: {e}")
            continue
    
    if not dfs:
        print(f"  ❌ No valid data loaded for {timeframe}")
        return None
    
    # Concatenate all dataframes
    print(f"  🔗 Merging {len(dfs)} files...")
    merged = pd.concat(dfs, ignore_index=True)
    
    # Detect time column (TradingView uses 'time' or 'timestamp')
    time_col = None
    for col in ['time', 'timestamp', 'Time', 'Timestamp']:
        if col in merged.columns:
            time_col = col
            break
    
    if not time_col:
        print(f"  ❌ No time column found in CSV. Columns: {merged.columns.tolist()}")
        return None
    
    # Parse timestamps and remove duplicates
    print(f"  📅 Parsing timestamps...")
    try:
        # TradingView exports Unix timestamps in seconds
        merged[time_col] = pd.to_datetime(merged[time_col], unit='s')
    except Exception as e:
        print(f"  ❌ Error parsing timestamps: {e}")
        return None
    
    # Remove duplicates based on timestamp
    before_dedup = len(merged)
    merged = merged.drop_duplicates(subset=[time_col], keep='first')
    after_dedup = len(merged)
    duplicates_removed = before_dedup - after_dedup
    
    # Sort by timestamp
    merged = merged.sort_values(time_col)
    
    # Generate output filename
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Map timeframe to human-readable format
    timeframe_map = {
        '15': '15min',
        '60': '1H',
        '240': '4H',
        '720': '12H',
        '1D': 'Daily'
    }
    tf_name = timeframe_map.get(timeframe, f'{timeframe}min')
    
    output_file = output_path / f'BTC_USDT_{tf_name}_merged.csv'
    
    # Save merged data
    print(f"  💾 Saving to {output_file.name}...")
    merged.to_csv(output_file, index=False)
    
    # Get date range
    start_date = merged[time_col].min()
    end_date = merged[time_col].max()
    
    # Statistics
    stats = {
        'timeframe': tf_name,
        'files_merged': len(file_paths),
        'total_rows_before': total_rows_before,
        'rows_after_merge': after_dedup,
        'duplicates_removed': duplicates_removed,
        'start_date': start_date,
        'end_date': end_date,
        'output_file': str(output_file),
        'file_size_mb': output_file.stat().st_size / (1024 * 1024)
    }
    
    print(f"  ✅ SUCCESS!")
    print(f"     • Merged {stats['files_merged']} files")
    print(f"     • Total input rows: {stats['total_rows_before']:,}")
    print(f"     • After deduplication: {stats['rows_after_merge']:,}")
    print(f"     • Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"     • Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"     • Output size: {stats['file_size_mb']:.2f} MB")
    print(f"     • Saved to: {output_file}")
    
    return stats

def main():
    """Main execution flow"""
    # Configuration
    input_folder = 'data/csv_imports'
    output_folder = 'data/csv_imports/merged'
    
    print("=" * 70)
    print("📦 Batch CSV Merge - TradingView Export Consolidation")
    print("=" * 70)
    
    # Detect CSV groups
    print(f"\n🔍 Scanning {input_folder} for CSV files...")
    groups = detect_csv_groups(input_folder)
    
    if not groups:
        print(f"❌ No CSV files found matching TradingView pattern in {input_folder}")
        sys.exit(1)
    
    print(f"\n✅ Found {len(groups)} timeframe(s):")
    for timeframe, files in sorted(groups.items()):
        print(f"   • {timeframe:>3} → {len(files)} file(s)")
    
    # Merge each group
    all_stats = []
    for timeframe, files in sorted(groups.items()):
        stats = merge_csv_files(files, timeframe, output_folder)
        if stats:
            all_stats.append(stats)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 MERGE SUMMARY")
    print("=" * 70)
    
    if all_stats:
        total_input = sum(s['total_rows_before'] for s in all_stats)
        total_output = sum(s['rows_after_merge'] for s in all_stats)
        total_duplicates = sum(s['duplicates_removed'] for s in all_stats)
        total_size = sum(s['file_size_mb'] for s in all_stats)
        
        print(f"\n✅ Successfully merged {len(all_stats)} timeframe(s):")
        for stats in all_stats:
            print(f"\n   {stats['timeframe']:>6} | {stats['rows_after_merge']:>7,} rows | "
                  f"{stats['file_size_mb']:>6.2f} MB")
            print(f"          └─ {stats['start_date'].strftime('%Y-%m-%d')} to "
                  f"{stats['end_date'].strftime('%Y-%m-%d')}")
        
        print(f"\n📈 Overall Statistics:")
        print(f"   • Total input rows: {total_input:,}")
        print(f"   • Total output rows: {total_output:,}")
        print(f"   • Duplicates removed: {total_duplicates:,}")
        print(f"   • Deduplication rate: {(total_duplicates/total_input*100):.1f}%")
        print(f"   • Total output size: {total_size:.2f} MB")
        print(f"\n📁 All merged files saved to: {output_folder}/")
        
        print("\n🚀 Next Steps:")
        print("   1. Validate merged data:")
        print(f"      python scripts/validate_csv.py {output_folder}/BTC_USDT_4H_merged.csv")
        print("\n   2. Run analysis:")
        print(f"      python src/cli/analyze.py BTC/USDT -t 4H \\")
        print(f"        -c charts/manual/BTC_USDT_multi_timeframe.png \\")
        print(f"        --data-source csv \\")
        print(f"        --csv-file {output_folder}/BTC_USDT_4H_merged.csv \\")
        print(f"        --report")
    else:
        print("\n❌ No files were successfully merged.")
        sys.exit(1)
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
