"""
Spinner and progress utilities for visual feedback.
Provides spinners, progress bars, and status indicators.
"""

import sys
import time
import threading
from typing import Optional
from contextlib import contextmanager


class Spinner:
    """Console spinner for indicating ongoing operations."""
    
    SPINNER_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str = "Processing", stream=None):
        """Initialize spinner.
        
        Args:
            message: Message to display
            stream: Output stream (defaults to sys.stderr)
        """
        self.message = message
        self.stream = stream or sys.stderr
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._idx = 0
    
    def _spin(self):
        """Internal method to animate spinner."""
        while not self._stop_event.is_set():
            char = self.SPINNER_CHARS[self._idx % len(self.SPINNER_CHARS)]
            self.stream.write(f'\r{char} {self.message}')
            self.stream.flush()
            self._idx += 1
            time.sleep(0.1)
    
    def start(self):
        """Start the spinner."""
        if self._thread is not None:
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
    
    def stop(self, final_message: Optional[str] = None):
        """Stop the spinner.
        
        Args:
            final_message: Optional final message to display
        """
        if self._thread is None:
            return
        
        self._stop_event.set()
        self._thread.join()
        self._thread = None
        
        # Clear the line and print final message
        self.stream.write('\r' + ' ' * (len(self.message) + 3) + '\r')
        if final_message:
            self.stream.write(final_message + '\n')
        self.stream.flush()
    
    def update_message(self, message: str):
        """Update the spinner message.
        
        Args:
            message: New message to display
        """
        self.message = message


@contextmanager
def spinner(message: str = "Processing", success_message: str = "✓ Done", error_message: str = "✗ Failed"):
    """Context manager for spinner.
    
    Args:
        message: Message to display during processing
        success_message: Message to display on success
        error_message: Message to display on error
    
    Usage:
        with spinner("Loading data"):
            # do work
            pass
    """
    spin = Spinner(message)
    spin.start()
    
    try:
        yield spin
        spin.stop(success_message)
    except Exception:
        spin.stop(error_message)
        raise


class ProgressIndicator:
    """Simple progress indicator without tqdm dependency."""
    
    def __init__(self, total: int, description: str = "Progress", bar_length: int = 40):
        """Initialize progress indicator.
        
        Args:
            total: Total number of items
            description: Description of the task
            bar_length: Length of progress bar
        """
        self.total = total
        self.description = description
        self.bar_length = bar_length
        self.current = 0
        self.start_time = time.time()
    
    def update(self, n: int = 1):
        """Update progress by n items.
        
        Args:
            n: Number of items to increment
        """
        self.current += n
        self._display()
    
    def _display(self):
        """Display progress bar."""
        if self.total == 0:
            return
        
        percent = min(100, (self.current / self.total) * 100)
        filled = int(self.bar_length * self.current / self.total)
        bar = '█' * filled + '░' * (self.bar_length - filled)
        
        elapsed = time.time() - self.start_time
        items_per_sec = self.current / elapsed if elapsed > 0 else 0
        
        sys.stderr.write(
            f'\r{self.description}: [{bar}] {percent:.1f}% '
            f'({self.current}/{self.total}) | {items_per_sec:.1f} items/s'
        )
        sys.stderr.flush()
        
        if self.current >= self.total:
            sys.stderr.write('\n')
            sys.stderr.flush()
    
    def close(self):
        """Close the progress indicator."""
        if self.current < self.total:
            self.current = self.total
            self._display()


def progress_indicator(total: int, description: str = "Progress"):
    """Create a progress indicator.
    
    Args:
        total: Total number of items
        description: Description of the task
    
    Returns:
        ProgressIndicator instance
    
    Usage:
        progress = progress_indicator(100, "Loading items")
        for i in range(100):
            # do work
            progress.update()
        progress.close()
    """
    return ProgressIndicator(total, description)


class StatusLogger:
    """Logger for status updates with emoji indicators."""
    
    @staticmethod
    def info(message: str):
        """Log info message."""
        print(f"ℹ️  {message}")
    
    @staticmethod
    def success(message: str):
        """Log success message."""
        print(f"✅ {message}")
    
    @staticmethod
    def warning(message: str):
        """Log warning message."""
        print(f"⚠️  {message}")
    
    @staticmethod
    def error(message: str):
        """Log error message."""
        print(f"❌ {message}")
    
    @staticmethod
    def working(message: str):
        """Log working message."""
        print(f"⚙️  {message}")


# Singleton instance
status = StatusLogger()
