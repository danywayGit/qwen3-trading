"""
Ollama HTTP Client

Wrapper for Ollama API to interact with Qwen models
Adapted from qwen3-vl project
"""

import requests
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        retry_attempts: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2000,
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send chat request to Ollama
        
        Args:
            model: Model name (e.g., 'qwen3-coder-30b-ctx32k-quant:latest')
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum tokens to generate
            images: Optional list of image paths for vision models
            
        Returns:
            Response dictionary from Ollama
            
        Raises:
            requests.RequestException: On API errors
        """
        endpoint = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens
            },
            "stream": False
        }
        
        # Add images for vision models
        if images:
            # Convert image paths to base64
            encoded_images = []
            for img_path in images:
                if img_path:
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            encoded_images.append(img_data)
                    except Exception as e:
                        logger.error(f"Failed to encode image {img_path}: {e}")
            
            # Attach images to the last user message
            if encoded_images:
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        msg['images'] = encoded_images
                        break
        
        logger.debug(f"Sending request to {endpoint}")
        logger.debug(f"Model: {model}, Messages: {len(messages)}")
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Response received: {len(str(result))} characters")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2000,
        image_path: Optional[str] = None
    ) -> str:
        """
        Simplified generate method (single prompt)
        
        Args:
            model: Model name
            prompt: Text prompt
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum tokens to generate
            image_path: Optional image path for vision models
            
        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        images = [image_path] if image_path else None
        
        response = self.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_tokens=max_tokens,
            images=images
        )
        
        # Extract message content
        return response.get('message', {}).get('content', '')
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama
        
        Returns:
            List of model names
        """
        endpoint = f"{self.base_url}/api/tags"
        
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            
            logger.info(f"Found {len(models)} models")
            return models
            
        except requests.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def check_model_exists(self, model_name: str) -> bool:
        """
        Check if a specific model exists
        
        Args:
            model_name: Model name to check
            
        Returns:
            True if model exists, False otherwise
        """
        models = self.list_models()
        return model_name in models
