# src/logging_setup.py
# Structured JSON logs with a request ID (REQ-N-009). Deliberately does
# NOT log the full question/answer text at default level (REQ-N-008 —
# customer content treated as sensitive by default).
import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "route", "latency_ms", "status_code",
                    "provider", "similarity", "evidence_found"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("shopbot")
    if logger.handlers:
        return logger  # already configured (e.g. re-imported under uvicorn --reload)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


logger = configure_logging()
