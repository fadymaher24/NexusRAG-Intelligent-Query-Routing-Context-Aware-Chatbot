"""
LLM client for interacting with language models.
Provides abstraction over different LLM providers.
"""

from typing import Dict, Any, Optional
import json
import requests

from app.config import config
from app.utils.logger import logger


class LLMClient:
    """Client for interacting with Language Models."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base_url: Optional[str] = None
    ):
        """Initialize LLM client.
        
        Args:
            model: Model name/identifier
            api_key: API key for authentication
            api_base_url: Base URL for API endpoint
        """
        self.model = model or config.LLM_MODEL
        self.api_key = api_key or config.LLM_API_KEY
        self.api_base_url = api_base_url or config.LLM_API_BASE_URL
        logger.info(f"Initialized LLM client with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.8,
        max_tokens: int = 500,
        role: str = 'user'
    ) -> Dict[str, Any]:
        """Generate response from LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            role: Role for the message
            
        Returns:
            Dictionary with 'content' key containing the response
        """
        try:
            logger.debug(f"Generating LLM response with temperature={temperature}, top_p={top_p}")
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": [{"role": role, "content": prompt}],
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                logger.debug(f"Using API key: {self.api_key[:15]}...{self.api_key[-4:]}")
            else:
                logger.warning("No API key configured")
            
            # Make API request
            if self.api_base_url:
                # Use custom API endpoint (e.g., Together AI, OpenAI-compatible)
                endpoint = f"{self.api_base_url}/chat/completions"
                response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                # Extract content from response
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                logger.debug("LLM response generated successfully")
                return {'content': content}
            else:
                # Fallback for testing without API
                logger.warning("No API base URL configured, returning mock response")
                return {
                    'content': f"[Mock Response] This is a placeholder response for: {prompt[:50]}...\n\nPlease configure LLM_API_BASE_URL and LLM_API_KEY in your .env file to use a real LLM provider."
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}", exc_info=True)
            return {'content': '', 'error': f'HTTP request failed: {str(e)}'}
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}", exc_info=True)
            return {'content': '', 'error': str(e)}
    
    def generate_single_token(
        self,
        prompt: str,
        temperature: float = 0.0
    ) -> str:
        """Generate a single token response (useful for classification).
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            
        Returns:
            Single token string response
        """
        response = self.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=1
        )
        return response.get('content', '').strip()
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1500
    ) -> Optional[Dict[str, Any]]:
        """Generate and parse JSON response.
        
        Args:
            prompt: Input prompt requesting JSON output
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        response = self.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.get('content', '').strip()
        
        try:
            # Clean up common JSON formatting issues
            content = content.replace("\n", '').replace("'", '').replace("}}", "}").replace("{{", "{")
            parsed = json.loads(content)
            logger.debug("Successfully parsed JSON response")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw content: {content}")
            return None


class LLMClientFactory:
    """Factory for creating LLM client instances."""
    
    _instance: Optional[LLMClient] = None
    
    @classmethod
    def get_client(cls) -> LLMClient:
        """Get or create LLM client instance.
        
        Returns:
            LLMClient instance
        """
        if cls._instance is None:
            cls._instance = LLMClient()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the client instance."""
        cls._instance = None
