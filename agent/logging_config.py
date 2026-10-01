import logging
from datetime import datetime
from pathlib import Path


LOGGER_NAME = "agent"
LOG_DIRECTORY = Path(__file__).resolve().parent.parent / "logs"
_active_log_path = None
_message_number = 0


def start_run_logging() -> Path:
    # Reuse one file while a chat session is active.
    global _active_log_path, _message_number
    logger = logging.getLogger(LOGGER_NAME)
    if _active_log_path is not None and logger.handlers:
        return _active_log_path
    LOG_DIRECTORY.mkdir(exist_ok=True)
    log_path = LOG_DIRECTORY / datetime.now().strftime("run_%Y%m%d_%H%M%S_%f.log")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stop_run_logging()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)
    _active_log_path = log_path
    _message_number = 0
    return log_path


def stop_run_logging() -> None:
    global _active_log_path
    logger = logging.getLogger(LOGGER_NAME)
    for handler in logger.handlers[:]:
        handler.flush()
        handler.close()
        logger.removeHandler(handler)
    _active_log_path = None


def is_run_logging_active() -> bool:
    return _active_log_path is not None


def next_message_number() -> int:
    global _message_number
    if not is_run_logging_active():
        start_run_logging()
    _message_number += 1
    return _message_number


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{LOGGER_NAME}.{name}")