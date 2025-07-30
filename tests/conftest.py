from pathlib import Path

import pytest

from rhythm_trainer import dirs

# @pytest.fixture(autouse=True)
# def user_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
#     """Patch the user config directory for testing."""
#     monkeypatch.setattr(
#         type(dirs),
#         "user_config_dir",
#         property(lambda _: str(tmp_path / "config")),
#     )
#     if hasattr(dirs, "__dict__") and "user_config_dir" in dirs.__dict__:
#         del dirs.__dict__["user_config_dir"]

#     print(f"User config directory: {dirs.user_config_dir}")


# @pytest.fixture(autouse=True)
# def user_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
#     """Patch the user data directory for testing."""
#     monkeypatch.setattr(
#         type(dirs),
#         "user_data_dir",
#         property(lambda _: str(tmp_path / "data")),
#     )


# @pytest.fixture(autouse=True)
# def user_log_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
#     """Patch the user log directory to a temporary path for testing."""
#     monkeypatch.setattr(
#         type(dirs),
#         "user_log_dir",
#         property(lambda _: str(tmp_path / "logs")),
#     )


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
