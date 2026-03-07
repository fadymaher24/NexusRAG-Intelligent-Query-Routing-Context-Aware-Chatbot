"""
Configuration module for NexusRAG application.
Implements Singleton pattern for configuration management.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration class using Singleton pattern."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables or defaults."""
        # Load environment variables from .env file
        load_dotenv()
        
        # Project paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "dataset"
        
        # Weaviate configuration
        self.WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
        self.WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", "8079"))
        self.WEAVIATE_GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", "50050"))
        
        # LLM Configuration
        self.LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Llama-3.2-3B-Instruct-Turbo")
        self.LLM_API_KEY = os.getenv("LLM_API_KEY", "")
        self.LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "")
        
        # Application settings
        self.MAX_TOKENS_DEFAULT = int(os.getenv("MAX_TOKENS_DEFAULT", "500"))
        self.TEMPERATURE_DEFAULT = float(os.getenv("TEMPERATURE_DEFAULT", "0.3"))
        self.TOP_P_DEFAULT = float(os.getenv("TOP_P_DEFAULT", "0.8"))
        
        # Query routing parameters
        self.CREATIVE_TEMPERATURE = float(os.getenv("CREATIVE_TEMPERATURE", "1.0"))
        self.CREATIVE_TOP_P = float(os.getenv("CREATIVE_TOP_P", "0.9"))
        self.TECHNICAL_TEMPERATURE = float(os.getenv("TECHNICAL_TEMPERATURE", "0.3"))
        self.TECHNICAL_TOP_P = float(os.getenv("TECHNICAL_TOP_P", "0.8"))
        
        # Product retrieval settings
        self.PRODUCT_LIMIT = int(os.getenv("PRODUCT_LIMIT", "20"))
        self.MIN_RESULTS_THRESHOLD = int(os.getenv("MIN_RESULTS_THRESHOLD", "5"))
        
        # Flask settings
        self.FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
        self.FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
        self.FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = self.BASE_DIR / "logs" / "app.log"
    
    def get_llm_params(self, task_type: str = "default") -> Dict[str, Any]:
        """Get LLM parameters based on task type.
        
        Args:
            task_type: Type of task ('creative', 'technical', 'default')
            
        Returns:
            Dictionary with temperature and top_p values
        """
        params = {
            "creative": {
                "temperature": self.CREATIVE_TEMPERATURE,
                "top_p": self.CREATIVE_TOP_P
            },
            "technical": {
                "temperature": self.TECHNICAL_TEMPERATURE,
                "top_p": self.TECHNICAL_TOP_P
            },
            "default": {
                "temperature": self.TEMPERATURE_DEFAULT,
                "top_p": self.TOP_P_DEFAULT
            }
        }
        return params.get(task_type, params["default"])


# Create a global config instance
config = Config()
