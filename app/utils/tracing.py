"""
Tracing utilities for request tracking and observability.
Provides trace context, request IDs, and span tracking.
"""

import time
import uuid
import contextvars
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager

from app.utils.logger import logger


# Context variable for trace ID
_trace_id_var = contextvars.ContextVar('trace_id', default=None)
_span_stack_var = contextvars.ContextVar('span_stack', default=[])


class TraceContext:
    """Trace context manager for tracking operations."""
    
    @staticmethod
    def generate_trace_id() -> str:
        """Generate a new trace ID."""
        return str(uuid.uuid4())
    
    @staticmethod
    def set_trace_id(trace_id: str):
        """Set current trace ID."""
        _trace_id_var.set(trace_id)
    
    @staticmethod
    def get_trace_id() -> Optional[str]:
        """Get current trace ID."""
        return _trace_id_var.get()
    
    @staticmethod
    def clear_trace_id():
        """Clear current trace ID."""
        _trace_id_var.set(None)
    
    @staticmethod
    def get_span_stack() -> list:
        """Get current span stack."""
        stack = _span_stack_var.get()
        return stack if stack else []
    
    @staticmethod
    def push_span(span_name: str):
        """Push a new span onto the stack."""
        stack = TraceContext.get_span_stack()
        stack.append(span_name)
        _span_stack_var.set(stack)
    
    @staticmethod
    def pop_span():
        """Pop the current span from the stack."""
        stack = TraceContext.get_span_stack()
        if stack:
            stack.pop()
            _span_stack_var.set(stack)
    
    @staticmethod
    def get_current_span() -> Optional[str]:
        """Get the current span name."""
        stack = TraceContext.get_span_stack()
        return stack[-1] if stack else None


@contextmanager
def trace_operation(operation_name: str, **attributes):
    """Context manager for tracing an operation.
    
    Args:
        operation_name: Name of the operation
        **attributes: Additional attributes to log
    
    Usage:
        with trace_operation("load_data", count=100):
            # do work
            pass
    """
    trace_id = TraceContext.get_trace_id()
    if not trace_id:
        trace_id = TraceContext.generate_trace_id()
        TraceContext.set_trace_id(trace_id)
    
    TraceContext.push_span(operation_name)
    
    start_time = time.time()
    
    # Build log message with attributes
    attrs_str = " ".join([f"{k}={v}" for k, v in attributes.items()])
    log_msg = f"[trace_id={trace_id}] [{operation_name}] Starting"
    if attrs_str:
        log_msg += f" | {attrs_str}"
    
    logger.info(log_msg)
    
    try:
        yield trace_id
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"[trace_id={trace_id}] [{operation_name}] Failed after {duration_ms:.2f}ms | error={str(e)}"
        )
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"[trace_id={trace_id}] [{operation_name}] Completed in {duration_ms:.2f}ms"
        )
        TraceContext.pop_span()


def traced(operation_name: Optional[str] = None):
    """Decorator for tracing function calls.
    
    Args:
        operation_name: Optional name for the operation. Defaults to function name.
    
    Usage:
        @traced("my_operation")
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with trace_operation(op_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


class Span:
    """Represents a traced span of execution."""
    
    def __init__(self, name: str, trace_id: str):
        """Initialize span.
        
        Args:
            name: Span name
            trace_id: Associated trace ID
        """
        self.name = name
        self.trace_id = trace_id
        self.start_time = time.time()
        self.attributes: Dict[str, Any] = {}
    
    def add_attribute(self, key: str, value: Any):
        """Add an attribute to the span."""
        self.attributes[key] = value
    
    def end(self):
        """End the span and log duration."""
        duration_ms = (time.time() - self.start_time) * 1000
        attrs_str = " ".join([f"{k}={v}" for k, v in self.attributes.items()])
        log_msg = f"[trace_id={self.trace_id}] [{self.name}] Duration: {duration_ms:.2f}ms"
        if attrs_str:
            log_msg += f" | {attrs_str}"
        logger.debug(log_msg)


def log_with_trace(level: str, message: str, **kwargs):
    """Log a message with trace context.
    
    Args:
        level: Log level (info, warning, error, debug)
        message: Log message
        **kwargs: Additional key-value pairs to include
    """
    trace_id = TraceContext.get_trace_id()
    span = TraceContext.get_current_span()
    
    prefix = ""
    if trace_id:
        prefix += f"[trace_id={trace_id}]"
    if span:
        prefix += f"[{span}]"
    
    if prefix:
        message = f"{prefix} {message}"
    
    if kwargs:
        attrs_str = " | " + " ".join([f"{k}={v}" for k, v in kwargs.items()])
        message += attrs_str
    
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)
