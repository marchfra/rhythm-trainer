import logging
from pathlib import Path

from rhythm_trainer import dirs


def get_logger(
    name: str,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """Create and configure a logger with the specified name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter("{name} - {levelname} - {message}", style="{")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    log_path = Path(dirs.user_log_dir) / "rhythm_trainer.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
