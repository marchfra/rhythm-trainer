from pathlib import Path

import pytest

from rhythm_trainer import dirs


@pytest.fixture(autouse=True)
def patch_locale(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("locale.getlocale", lambda: ("en_US", "UTF-8"))


@pytest.fixture(autouse=True)
def patch_platformdirs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Patch the user directories to temporary paths for testing."""
    monkeypatch.setattr(
        type(dirs),
        "user_config_dir",
        property(lambda _: str(tmp_path / "config")),
    )
    monkeypatch.setattr(
        type(dirs),
        "user_data_dir",
        property(lambda _: str(tmp_path / "data")),
    )
    monkeypatch.setattr(
        type(dirs),
        "user_log_dir",
        property(lambda _: str(tmp_path / "logs")),
    )
    monkeypatch.setattr(
        type(dirs),
        "user_downloads_dir",
        property(lambda _: str(tmp_path / "downloads")),
    )
