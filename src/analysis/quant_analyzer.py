"""
Quantitative Analyzer - Step 1 of two-model pipeline

Analyzes raw OHLCV data using Qwen3-Coder model for numerical insights
"""

import pandas as pd
from typing import Dict, Any
import logging

from ..utils.ollama_client import OllamaClient
from ..utils.config_loader import load_config

logger = logging.getLogger(__name__)


class QuantitativeAnalyzer:
    """Quantitative analysis using Qwen3-Coder model"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize quantitative analyzer
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.model_config = self.config['models']['quantitative']
        
        # Initialize Ollama client
        ollama_config = self.config['ollama']
        self.client = OllamaClient(
            base_url=ollama_config['base_url'],
            timeout=ollama_config['timeout'],
            retry_attempts=ollama_config['retry_attempts']
        )
        
        logger.info(f"Initialized QuantitativeAnalyzer with model: {self.model_config['name']}")
    
    def analyze(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
        periods: int = 100
    ) -> Dict[str, Any]:
        """
        Perform quantitative analysis on OHLCV data
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol
            timeframe: Timeframe of data
            periods: Number of recent periods to analyze
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting quantitative analysis for {symbol} {timeframe}")
        
        # Take recent periods
        df_recent = df.tail(periods)
        
        # Build prompt with data
        prompt = self._build_prompt(df_recent, symbol, timeframe)
        
        # Get analysis from model
        try:
            response = self.client.generate(
                model=self.model_config['name'],
                prompt=prompt,
                temperature=self.model_config['temperature'],
                top_p=self.model_config['top_p'],
                max_tokens=self.model_config['max_tokens']
            )
            
            logger.info("Quantitative analysis completed")
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'periods_analyzed': len(df_recent),
                'analysis': response,
                'latest_price': float(df_recent['close'].iloc[-1]),
                'latest_volume': float(df_recent['volume'].iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"Quantitative analysis failed: {e}")
            raise
    
    def _build_prompt(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str
    ) -> str:
        """Build analysis prompt with OHLCV data"""
        
        # Extract data series
        closes = df['close'].tolist()
        highs = df['high'].tolist()
        lows = df['low'].tolist()
        volumes = df['volume'].tolist()
        
        # Take last 50 for prompt (balance between context and token limit)
        n = min(50, len(df))
        
        prompt = f"""Analyze {symbol} {timeframe} OHLCV data for quantitative trading insights.

RECENT DATA (Last {n} periods):
Closing Prices: {closes[-n:]}
High Prices: {highs[-n:]}
Low Prices: {lows[-n:]}
Volume: {volumes[-n:]}

Current Price: {closes[-1]}
Current Volume: {volumes[-1]}

ANALYSIS REQUIRED:

1. MOMENTUM ANALYSIS
   - Calculate 5-period, 10-period, and 20-period momentum (% change)
   - Identify acceleration or deceleration patterns
   - Rate of change trends

2. VOLATILITY METRICS
   - Estimate ATR (Average True Range)
   - Calculate volatility percentile (current vs recent history)
   - Identify volatility expansion/contraction

3. VOLUME ANALYSIS
   - Compare current volume to 20-period moving average (%)
   - Identify volume trend (increasing/decreasing)
   - Detect volume spikes or anomalies

4. KEY PRICE LEVELS
   - Recent swing highs and lows with specific prices
   - Support and resistance zones from price clusters
   - Pivot points if calculable

5. MOVING AVERAGES
   - Calculate 20, 50, 200-period MAs (or estimate from data)
   - Current price position relative to MAs
   - MA crossovers or convergence

6. STATISTICAL PATTERNS
   - RSI estimation (if sufficient data)
   - MACD signal (if calculable)
   - Price structure: higher highs/lows, lower highs/lows
   - Any statistical anomalies or outliers

OUTPUT FORMAT:
Provide precise numerical results with specific price levels and percentages.
Focus on what the numbers indicate, not visual patterns.
Be concise but thorough with exact values.
"""
        
        return prompt
    
    def get_data_summary(self, df: pd.DataFrame) -> str:
        """
        Get quick summary of dataset for logging
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Summary string
        """
        return (
            f"{len(df)} candles, "
            f"Range: {df.index[0]} to {df.index[-1]}, "
            f"Price: ${df['close'].iloc[-1]:,.2f}"
        )
