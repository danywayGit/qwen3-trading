"""
Qwen3 Trading Analysis Package

Two-model AI trading analysis system combining quantitative data analysis 
with visual chart recognition.
"""

__version__ = "0.1.0"
__author__ = "Qwen3 Trading Team"

from src.utils.config_loader import load_config

# Package metadata
PACKAGE_NAME = "qwen3-trading"
DEFAULT_CONFIG_PATH = "config.json"

# Load default configuration
config = load_config(DEFAULT_CONFIG_PATH)
