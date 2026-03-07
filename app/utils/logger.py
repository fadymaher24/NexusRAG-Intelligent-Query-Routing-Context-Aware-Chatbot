"""
Logging configuration for NexusRAG application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Logger class using Singleton pattern."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is not None:
            return
        
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file and console handlers."""
        from app.config import config
        
        # Create logs directory if it doesn't exist
        log_dir = config.LOG_FILE.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger('nexusrag')
        self._logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        console_handler.setFormatter(simple_formatter)
        self._logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None, "Logger failed to initialize"
        return self._logger
    
    def debug(self, message: str):
        """Log debug message."""
        if self._logger is not None:
            self._logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        if self._logger is not None:
            self._logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        if self._logger is not None:
            self._logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        if self._logger is not None:
            self._logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Log critical message."""
        if self._logger is not None:
            self._logger.critical(message, exc_info=exc_info)


# Create a global logger instance
logger = Logger()
