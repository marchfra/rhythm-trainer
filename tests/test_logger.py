import logging
from pathlib import Path

import pytest

from rhythm_trainer import dirs
from rhythm_trainer.logger import get_logger


def patch_user_log_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Patch the user log directory to a temporary path for testing."""
    monkeypatch.setattr(type(dirs), "user_log_dir", property(lambda _: str(tmp_path)))


def test_get_logger_returns_logger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_user_log_dir(monkeypatch, tmp_path)
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)


def test_logger_has_console_and_file_handlers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_user_log_dir(monkeypatch, tmp_path)
    logger = get_logger("test_logger_handlers")
    handler_types = {type(h) for h in logger.handlers}
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types


def test_logger_creates_log_file_and_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_user_log_dir(monkeypatch, tmp_path)
    logger = get_logger("test_logger_file")
    log_file = tmp_path / "rhythm_trainer.log"
    logger.info("Hello log!")
    logger.handlers[1].flush()  # Ensure file handler flushes
    assert log_file.exists()
    content = log_file.read_text()
    assert "Hello log!" in content
    assert "test_logger_file" in content


def test_logger_format_in_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    patch_user_log_dir(monkeypatch, tmp_path)
    logger = get_logger("test_logger_format")
    log_file = tmp_path / "rhythm_trainer.log"
    logger.error("Format test")
    logger.handlers[1].flush()
    content = log_file.read_text()
    # Check for timestamp, logger name, level, and message
    assert "test_logger_format" in content
    assert "ERROR" in content
    assert "Format test" in content
