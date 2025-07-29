from pathlib import Path

import pytest

from rhythm_trainer import dirs
from rhythm_trainer.config import (
    Config,
    FileFormat,
    NamingScheme,
    get_config_path,
    parse_config,
    save_config,
)


def patch_user_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the user config directory for testing."""
    monkeypatch.setattr(
        type(dirs),
        "user_config_dir",
        property(lambda _: str(tmp_path)),
    )


def patch_user_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the user data directory for testing."""
    monkeypatch.setattr(
        type(dirs),
        "user_data_dir",
        property(lambda _: str(tmp_path)),
    )


def test_config_to_dict_with_backing_tracks() -> None:
    config = Config(
        csv_path=Path("foo.csv"),
        backing_tracks_dir=Path("/tmp/bk"),
    )
    config_dict = config.to_dict()
    assert config_dict["csv_path"] == "foo.csv"
    assert config_dict["backing_tracks_dir"] == "/tmp/bk"
    assert config_dict["naming_scheme"] == "default"
    assert config_dict["file_format"] == "wav"


def test_config_to_dict_without_backing_tracks() -> None:
    config = Config(csv_path=Path("foo.csv"))
    config_dict = config.to_dict()
    assert config_dict["backing_tracks_dir"] is None


def test_get_config_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the config path is created correctly."""
    config_filename = "test_config.yaml"
    expected_path = tmp_path / config_filename

    patch_user_config_dir(tmp_path, monkeypatch)
    assert get_config_path(config_filename) == expected_path


def test_save_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving a configuration to a file."""
    config = Config(csv_path=Path("foo.csv"))
    config_filename = "test_config.yaml"
    expected_path = tmp_path / config_filename

    patch_user_config_dir(tmp_path, monkeypatch)
    save_config(config, config_filename)

    assert expected_path.exists()
    with expected_path.open("r") as file:
        content = file.read()
        assert "foo.csv" in content


def test_parse_config_creates_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the config is created with default values."""
    patch_user_config_dir(tmp_path, monkeypatch)
    patch_user_data_dir(tmp_path, monkeypatch)
    config_filename = "test_config.yaml"
    config_path = get_config_path(config_filename)

    assert not config_path.exists()  # Ensure the file does not exist
    config = parse_config(config_filename)
    assert isinstance(config, Config)
    assert config.csv_path == Path(tmp_path / "exercises.csv")
    assert config_path.exists()  # Ensure the file was created


def test_parse_config_reads_existing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the config is read from an existing file."""
    patch_user_config_dir(tmp_path, monkeypatch)
    patch_user_data_dir(tmp_path, monkeypatch)
    config_filename = "test_config.yaml"

    csv_path = tmp_path / "sample.csv"
    bk_dir = tmp_path / "backing_tracks"
    bk_dir.mkdir(parents=True, exist_ok=True)

    # Create a sample config file
    sample_config = Config(
        csv_path=csv_path,
        backing_tracks_dir=bk_dir,
        naming_scheme=NamingScheme.DEFAULT,
        file_format=FileFormat.MP3,
    )
    save_config(sample_config, config_filename)

    config = parse_config(config_filename)
    assert isinstance(config, Config)
    assert config.csv_path == csv_path
    assert config.backing_tracks_dir == bk_dir
    assert config.naming_scheme == NamingScheme.DEFAULT
    assert config.file_format == FileFormat.MP3


def test_parse_config_invalid_backing_tracks_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that an error is raised if the backing tracks directory does not exist."""
    patch_user_config_dir(tmp_path, monkeypatch)
    patch_user_data_dir(tmp_path, monkeypatch)
    config_filename = "test_config.yaml"

    csv_path = tmp_path / "sample.csv"
    bk_dir = tmp_path / "backing_tracks"
    assert not bk_dir.exists()  # Ensure the directory does not exist

    # Create a config file with a non-existent backing tracks directory
    sample_config = Config(
        csv_path=csv_path,
        backing_tracks_dir=bk_dir,
    )
    save_config(sample_config, config_filename)

    with pytest.raises(FileNotFoundError, match="does not exist"):
        parse_config(config_filename)
