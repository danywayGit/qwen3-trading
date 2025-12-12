"""
Visual Analyzer - Step 2 of two-model pipeline

Analyzes chart images using Qwen3-VL model and integrates with quantitative context
"""

import os
from typing import Dict, Any, Optional
import logging

from ..utils.ollama_client import OllamaClient
from ..utils.config_loader import load_config

logger = logging.getLogger(__name__)


class VisualAnalyzer:
    """Visual chart analysis using Qwen3-VL model"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize visual analyzer
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.model_config = self.config['models']['visual']
        
        # Initialize Ollama client
        ollama_config = self.config['ollama']
        self.client = OllamaClient(
            base_url=ollama_config['base_url'],
            timeout=ollama_config['timeout'],
            retry_attempts=ollama_config['retry_attempts']
        )
        
        logger.info(f"Initialized VisualAnalyzer with model: {self.model_config['name']}")
    
    def analyze(
        self,
        chart_path: str,
        symbol: str,
        timeframe: str,
        quant_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform visual chart analysis with optional quantitative context
        
        Args:
            chart_path: Path to chart image
            symbol: Trading pair symbol
            timeframe: Timeframe of chart
            quant_context: Optional quantitative analysis context
            
        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(chart_path):
            raise FileNotFoundError(f"Chart image not found: {chart_path}")
        
        logger.info(f"Starting visual analysis for {symbol} {timeframe}")
        logger.info(f"Chart image: {chart_path}")
        
        # Build prompt
        prompt = self._build_prompt(symbol, timeframe, quant_context)
        
        # Get analysis from model with image
        try:
            response = self.client.generate(
                model=self.model_config['name'],
                prompt=prompt,
                temperature=self.model_config['temperature'],
                top_p=self.model_config['top_p'],
                top_k=self.model_config.get('top_k', 40),
                max_tokens=self.model_config['max_tokens'],
                image_path=chart_path
            )
            
            logger.info("Visual analysis completed")
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'chart_path': chart_path,
                'has_quant_context': quant_context is not None,
                'analysis': response
            }
            
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            raise
    
    def _build_prompt(
        self,
        symbol: str,
        timeframe: str,
        quant_context: Optional[str]
    ) -> str:
        """Build analysis prompt for visual model"""
        
        prompt = f"""{symbol} {timeframe} TRADING CHART ANALYSIS

"""
        
        # Add quantitative context if available
        if quant_context:
            prompt += f"""QUANTITATIVE DATA CONTEXT:
{quant_context}

"""
        
        prompt += f"""Analyze the attached chart image and provide a comprehensive trading setup.

ANALYSIS REQUIRED:

1. TREND ANALYSIS
   - Overall trend direction (uptrend, downtrend, sideways)
   - Trend strength (strong, moderate, weak)
   - Market structure (higher highs/lows, lower highs/lows)

2. KEY LEVELS
   - Support levels with specific prices
   - Resistance levels with specific prices
   - Critical zones to watch

3. CHART PATTERNS
   - Identify any patterns forming (triangles, H&S, flags, etc.)
   - Pattern completion status
   - Breakout or breakdown potential

4. TECHNICAL INDICATORS (visible on chart)
   - RSI reading and interpretation
   - MACD signal (bullish/bearish, crossovers)
   - Moving averages position and crossovers
   - Volume analysis and confirmation

5. TRADE SETUP
   - Direction: LONG, SHORT, or NEUTRAL
   - Entry price (specific level)
   - Stop loss (specific price and % from entry)
   - Take profit 1 (conservative target)
   - Take profit 2 (extended target)
   - Risk-reward ratio for both TPs

6. INTEGRATED ASSESSMENT"""
        
        if quant_context:
            prompt += """
   - Does visual analysis align with quantitative data?
   - Any divergences between chart and numerical analysis?
   - Which signals are confirmed by both models?
   - Conflicting signals to be aware of?
"""
        
        prompt += """
7. CONFIDENCE & RISK
   - Confidence level (1-10) based on setup quality
   - Key risks or invalidation points
   - Market conditions affecting the setup

OUTPUT:
Provide specific prices, percentages, and actionable trade signals.
Be precise with entry, stop, and target levels.
"""
        
        if quant_context:
            prompt += "Explicitly state when visual and quantitative analyses agree or disagree."
        
        return prompt
