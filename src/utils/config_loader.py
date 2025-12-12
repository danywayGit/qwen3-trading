"""
Configuration loader utility

Loads and validates configuration from config.json
"""

import json
import os
from typing import Dict, Any


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to config.json file
        
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required sections
    required_sections = ['models', 'exchanges', 'data_sources', 'analysis', 'ollama']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
    
    return config


def get_model_config(config: Dict[str, Any], model_type: str) -> Dict[str, Any]:
    """
    Get configuration for specific model
    
    Args:
        config: Full configuration dictionary
        model_type: 'quantitative' or 'visual'
        
    Returns:
        Model configuration dictionary
    """
    if model_type not in config['models']:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return config['models'][model_type]


def get_exchange_config(config: Dict[str, Any], exchange: str = None) -> Dict[str, Any]:
    """
    Get exchange configuration
    
    Args:
        config: Full configuration dictionary
        exchange: Exchange name (defaults to config default)
        
    Returns:
        Exchange configuration dictionary
    """
    exchanges = config['exchanges']
    
    if exchange is None:
        exchange = exchanges['default']
    
    if exchange not in exchanges['available']:
        raise ValueError(f"Exchange {exchange} not in available exchanges")
    
    return {
        'name': exchange,
        **exchanges['ccxt_config']
    }
