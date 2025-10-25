"""
Enhanced Logging Utility for XMRT DAO System
Provides consistent, properly formatted logging across all components
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

class XMRTLogger:
    """Enhanced logger with structured formatting and multiple outputs"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler with color formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            self.log_dir / f"{name}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # JSON handler for structured logs
        json_handler = logging.FileHandler(
            self.log_dir / f"{name}_structured.jsonl",
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(json_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        self.logger.info(message, extra={'context': kwargs})
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        self.logger.warning(message, extra={'context': kwargs})
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context"""
        self.logger.error(message, extra={'context': kwargs})
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        self.logger.debug(message, extra={'context': kwargs})
    
    def success(self, message: str, **kwargs):
        """Log success message (custom level)"""
        self.logger.info(f"SUCCESS: {message}", extra={'context': kwargs})
    
    def edge_function_call(self, function_name: str, status: str, duration: float, **kwargs):
        """Log edge function calls with structured data"""
        self.info(
            f"Edge function call: {function_name}",
            function=function_name,
            status=status,
            duration_ms=duration,
            **kwargs
        )
    
    def task_event(self, task_id: str, event_type: str, **kwargs):
        """Log task-related events"""
        self.info(
            f"Task {event_type}: {task_id}",
            task_id=task_id,
            event_type=event_type,
            **kwargs
        )
    
    def system_metric(self, metric_name: str, value: Any, unit: str = ""):
        """Log system metrics"""
        self.info(
            f"Metric: {metric_name} = {value} {unit}",
            metric=metric_name,
            value=value,
            unit=unit
        )


class ColoredFormatter(logging.Formatter):
    """Formatter with ANSI color codes for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formatter that outputs structured JSON logs"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add context if available
        if hasattr(record, 'context'):
            log_data['context'] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class CycleLogger:
    """Logger specifically for cycle-based markdown logs"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.cycle_number = self._get_next_cycle_number()
    
    def _get_next_cycle_number(self) -> int:
        """Determine the next cycle number"""
        existing_cycles = list(self.log_dir.glob("cycle-*.md"))
        if not existing_cycles:
            return 0
        
        numbers = []
        for cycle_file in existing_cycles:
            try:
                num = int(cycle_file.stem.split('-')[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue
        
        return max(numbers) + 1 if numbers else 0
    
    def log_cycle(self, prompt: str, response: str, feedback: Optional[str] = None):
        """Log a complete cycle with proper formatting"""
        cycle_file = self.log_dir / f"cycle-{self.cycle_number:05d}.md"
        
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        content = f"""# Cycle {self.cycle_number}

**Timestamp:** {timestamp}  
**Prompt:** {prompt}

**Response:**  
{response}

---

"""
        
        if feedback:
            content += f"""**Feedback:**  
{feedback}

---

"""
        else:
            content += "**Feedback:** Not enough data for self-feedback yet.\n\n---\n\n"
        
        with open(cycle_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.cycle_number += 1
        
        return cycle_file


def get_logger(name: str) -> XMRTLogger:
    """Get or create a logger instance"""
    return XMRTLogger(name)


# Global logger instances
system_logger = get_logger('system')
edge_logger = get_logger('edge_functions')
task_logger = get_logger('tasks')
mining_logger = get_logger('mining')

__all__ = [
    'XMRTLogger',
    'CycleLogger',
    'get_logger',
    'system_logger',
    'edge_logger',
    'task_logger',
    'mining_logger'
]
