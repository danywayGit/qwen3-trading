"""
Validate CSV - Check TradingView CSV file format

Command-line tool to validate CSV files before analysis
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.csv_loader import CSVLoader
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Validate TradingView CSV file format'
    )
    
    parser.add_argument(
        'csv_file',
        type=str,
        help='Path to CSV file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"CSV Validation: {args.csv_file}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(args.csv_file):
        print(f"❌ File not found: {args.csv_file}")
        sys.exit(1)
    
    try:
        # Load CSV
        loader = CSVLoader()
        df = loader.load_csv(args.csv_file)
        
        print(f"✓ CSV loaded successfully")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
        
        # Validate data quality
        print(f"\nValidating data quality...")
        report = loader.validate_data_quality(df)
        
        print(f"\nData Quality Report:")
        print(f"  Total rows: {report['total_rows']}")
        print(f"  Duplicates: {report['duplicates']}")
        
        # Check for missing values
        missing = report['missing_values']
        has_missing = any(v > 0 for v in missing.values())
        
        if has_missing:
            print(f"\n⚠️  Missing values detected:")
            for col, count in missing.items():
                if count > 0:
                    print(f"    {col}: {count}")
        else:
            print(f"  ✓ No missing values")
        
        # Check for gaps
        if report['gaps']:
            print(f"\n⚠️  Time gaps detected ({len(report['gaps'])} gaps):")
            for gap in report['gaps'][:5]:
                print(f"    {gap['timestamp']}: {gap['gap_duration']}")
            if len(report['gaps']) > 5:
                print(f"    ... and {len(report['gaps']) - 5} more")
        else:
            print(f"  ✓ No significant time gaps")
        
        # Show sample data
        if args.verbose:
            print(f"\nSample data (last 5 rows):")
            print(df.tail().to_string())
        else:
            print(f"\nLatest data:")
            latest = df.iloc[-1]
            print(f"  Close:  ${latest['close']:,.2f}")
            print(f"  Volume: {latest['volume']:,.0f}")
        
        print(f"\n{'='*60}")
        print("✓ VALIDATION PASSED")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        print(f"\n{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
