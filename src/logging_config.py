import logging
from pathlib import Path
from typing import List

DEFAULT_LOG_FILE = "logs/app.log"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_owned_handlers: List[logging.Handler] = []


def setup_logging(
    log_file: str = DEFAULT_LOG_FILE,
    level: int = logging.INFO,
) -> logging.Logger:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in _owned_handlers:
        root_logger.removeHandler(handler)
        handler.close()
    _owned_handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    _owned_handlers.append(console_handler)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    _owned_handlers.append(file_handler)

    return root_logger
