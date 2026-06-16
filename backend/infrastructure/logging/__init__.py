import logging
import json
from pythonjsonlogger import jsonlogger


def get_logger(name):
    """Get a logger configured for JSON output."""
    return logging.getLogger(name)


class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['timestamp'] = self.formatTime(record, self.datefmt)


def configure_logging():
    """Configure structured JSON logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # JSON handler
    json_handler = logging.StreamHandler()
    formatter = JSONFormatter()
    json_handler.setFormatter(formatter)
    root_logger.addHandler(json_handler)

    # Silence noisy loggers
    logging.getLogger('django.db').setLevel(logging.WARNING)
    logging.getLogger('django.request').setLevel(logging.WARNING)


__all__ = ['get_logger', 'configure_logging']
