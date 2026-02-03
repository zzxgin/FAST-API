"""
Logger configuration for SkyrisReward backend.
Supports text and JSON formatting, configurable via environment variables.
Designed for containerized environments (Docker/K8s) outputting to stdout.
"""
import logging
import sys
import json
import os
from datetime import datetime, timedelta
from typing import Any
from app.core.config import LOG_LEVEL, LOG_FORMAT

class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
            
        return json.dumps(log_obj, ensure_ascii=False)

class DailyDateFileHandler(logging.FileHandler):
    """
    Custom FileHandler that writes to a file named with the current date (YYYY-MM-DD.log).
    Rotates automatically at midnight (by checking date on emit).
    Keeps a configurable number of past log files.
    """
    def __init__(self, log_dir: str, backup_count: int = 30, encoding: str = "utf-8"):
        self.log_dir = log_dir
        self.backup_count = backup_count
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        filename = os.path.join(log_dir, f"{self.current_date}.log")
        super().__init__(filename, encoding=encoding)
        self.cleanup()

    def emit(self, record):
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            self.current_date = new_date
            new_filename = os.path.join(self.log_dir, f"{self.current_date}.log")
            self.close()
            self.baseFilename = new_filename
            self.stream = self._open()
            self.cleanup()
        super().emit(record)

    def cleanup(self):
        """Delete log files older than backup_count days."""
        if self.backup_count > 0:
            cutoff = datetime.now() - timedelta(days=self.backup_count)
            for file in os.listdir(self.log_dir):
                if file.endswith(".log"):
                    try:
                        # Expect filename format: YYYY-MM-DD.log
                        file_date_str = file.replace(".log", "")
                        file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                        if file_date < cutoff:
                            os.remove(os.path.join(self.log_dir, file))
                    except ValueError:
                        pass  # Skip files that don't match the date format

def setup_logging():
    """Configure root logger and handlers."""
    if LOG_FORMAT.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    handlers = []

    # Stream Handler (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    handlers.append(stream_handler)

    # File Handler (Custom Daily Date)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = DailyDateFileHandler(
        log_dir=log_dir,
        backup_count=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    if root_logger.handlers:
        for h in root_logger.handlers:
            root_logger.removeHandler(h)
            
    for h in handlers:
        root_logger.addHandler(h)

    logging.getLogger("uvicorn.access").handlers = handlers
    logging.getLogger("uvicorn.error").handlers = handlers

setup_logging()

logger = logging.getLogger("skyrisreward")
