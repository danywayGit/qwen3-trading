"""
Analysis Pipeline - Orchestrates two-model trading analysis

Coordinates quantitative data analysis with visual chart analysis
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .quant_analyzer import QuantitativeAnalyzer
from .visual_analyzer import VisualAnalyzer
from ..data.data_manager import DataManager

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Two-model analysis pipeline coordinator"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize analysis pipeline
        
        Args:
            config_path: Path to configuration file
        """
        self.quant_analyzer = QuantitativeAnalyzer(config_path)
        self.visual_analyzer = VisualAnalyzer(config_path)
        self.data_manager = DataManager()
        
        # Load config for output settings
        from ..utils.config_loader import load_config
        self.config = load_config(config_path)
        
        logger.info("Initialized AnalysisPipeline")
    
    def analyze(
        self,
        symbol: str,
        timeframe: str,
        chart_path: str,
        data_source: str = 'ccxt',
        csv_file: Optional[str] = None,
        periods: int = 200,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete two-model analysis pipeline
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (e.g., '4h')
            chart_path: Path to chart image
            data_source: 'ccxt' or 'csv'
            csv_file: CSV file path (if data_source='csv')
            periods: Number of periods to analyze
            save_results: Save results to JSON file
            
        Returns:
            Complete analysis results dictionary
        """
        logger.info(f"Starting analysis pipeline for {symbol} {timeframe}")
        logger.info(f"Data source: {data_source}, Chart: {chart_path}")
        
        # Step 1: Load data
        logger.info("Step 1: Loading OHLCV data...")
        df = self.data_manager.load_data(
            symbol=symbol,
            timeframe=timeframe,
            source=data_source,
            periods=periods,
            csv_file=csv_file
        )
        
        data_summary = self.data_manager.get_summary(df)
        logger.info(f"Loaded {len(df)} candles")
        
        # Step 2: Quantitative analysis
        logger.info("Step 2: Running quantitative analysis...")
        quant_result = self.quant_analyzer.analyze(
            df=df,
            symbol=symbol,
            timeframe=timeframe,
            periods=min(periods, len(df))
        )
        
        logger.info("Quantitative analysis complete")
        
        # Step 3: Visual analysis with quant context
        logger.info("Step 3: Running visual chart analysis...")
        visual_result = self.visual_analyzer.analyze(
            chart_path=chart_path,
            symbol=symbol,
            timeframe=timeframe,
            quant_context=quant_result['analysis']
        )
        
        logger.info("Visual analysis complete")
        
        # Step 4: Integrate results
        logger.info("Step 4: Integrating results...")
        integrated = self._integrate_results(
            quant_result, visual_result, data_summary
        )
        
        # Save results if requested
        if save_results:
            output_path = self._save_results(integrated)
            integrated['output_file'] = output_path
            logger.info(f"Results saved to: {output_path}")
        
        logger.info("Analysis pipeline complete")
        
        return integrated
    
    def _integrate_results(
        self,
        quant: Dict[str, Any],
        visual: Dict[str, Any],
        data_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate quantitative and visual analysis results
        
        Args:
            quant: Quantitative analysis results
            visual: Visual analysis results
            data_summary: Data summary statistics
            
        Returns:
            Integrated analysis dictionary
        """
        # Detect divergences (simplified - check for opposite signals)
        quant_text = quant['analysis'].lower()
        visual_text = visual['analysis'].lower()
        
        divergence_detected = self._detect_divergence(quant_text, visual_text)
        
        integrated = {
            'metadata': {
                'symbol': quant['symbol'],
                'timeframe': quant['timeframe'],
                'timestamp': datetime.now().isoformat(),
                'data_source': 'integrated',
                'chart_image': visual['chart_path']
            },
            'data_summary': data_summary,
            'quantitative_analysis': {
                'model': self.quant_analyzer.model_config['name'],
                'periods_analyzed': quant['periods_analyzed'],
                'latest_price': quant['latest_price'],
                'latest_volume': quant['latest_volume'],
                'analysis': quant['analysis']
            },
            'visual_analysis': {
                'model': self.visual_analyzer.model_config['name'],
                'chart_path': visual['chart_path'],
                'analysis': visual['analysis']
            },
            'integration': {
                'divergence_detected': divergence_detected,
                'alignment_status': 'low' if divergence_detected else 'high',
                'notes': self._generate_integration_notes(quant_text, visual_text, divergence_detected)
            }
        }
        
        return integrated
    
    def _detect_divergence(self, quant_text: str, visual_text: str) -> bool:
        """
        Detect divergences between quantitative and visual analysis
        
        Simple keyword-based detection
        """
        # Bullish/bearish keywords
        bullish_words = ['bullish', 'uptrend', 'long', 'buy', 'support holding']
        bearish_words = ['bearish', 'downtrend', 'short', 'sell', 'resistance']
        
        quant_bullish = any(word in quant_text for word in bullish_words)
        quant_bearish = any(word in quant_text for word in bearish_words)
        
        visual_bullish = any(word in visual_text for word in bullish_words)
        visual_bearish = any(word in visual_text for word in bearish_words)
        
        # Divergence if opposite signals
        divergence = (
            (quant_bullish and visual_bearish) or
            (quant_bearish and visual_bullish)
        )
        
        return divergence
    
    def _generate_integration_notes(
        self,
        quant_text: str,
        visual_text: str,
        divergence: bool
    ) -> str:
        """Generate notes about integration quality"""
        
        if divergence:
            return (
                "⚠️ DIVERGENCE DETECTED: Quantitative and visual analyses show "
                "conflicting signals. This may indicate a market transition or "
                "setup requiring extra caution. Consider waiting for alignment "
                "before taking positions."
            )
        else:
            return (
                "✓ ALIGNMENT: Both quantitative and visual analyses support "
                "similar conclusions. This increases confidence in the trade setup."
            )
    
    def _save_results(self, results: Dict[str, Any]) -> str:
        """
        Save results to JSON file
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Path to saved file
        """
        # Create output directory
        output_dir = self.config['results']['json_folder']
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol = results['metadata']['symbol'].replace('/', '_')
        timeframe = results['metadata']['timeframe']
        
        filename = f"{symbol}_{timeframe}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable text report
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Formatted report string
        """
        meta = results['metadata']
        quant = results['quantitative_analysis']
        visual = results['visual_analysis']
        integration = results['integration']
        
        report = f"""
{'='*70}
QWEN3 TRADING ANALYSIS REPORT
{'='*70}

Symbol: {meta['symbol']}
Timeframe: {meta['timeframe']}
Analysis Date: {meta['timestamp']}
Chart Image: {meta['chart_image']}

{'='*70}
QUANTITATIVE ANALYSIS (Data-Driven)
{'='*70}

Model: {quant['model']}
Periods Analyzed: {quant['periods_analyzed']}
Latest Price: ${quant['latest_price']:,.2f}
Latest Volume: {quant['latest_volume']:,.0f}

{quant['analysis']}

{'='*70}
VISUAL ANALYSIS (Chart-Based)
{'='*70}

Model: {visual['model']}

{visual['analysis']}

{'='*70}
INTEGRATION ASSESSMENT
{'='*70}

Alignment Status: {integration['alignment_status'].upper()}
Divergence Detected: {'YES ⚠️' if integration['divergence_detected'] else 'NO ✓'}

{integration['notes']}

{'='*70}
"""
        
        return report
