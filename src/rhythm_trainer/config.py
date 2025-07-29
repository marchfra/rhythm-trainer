from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from platformdirs import user_config_dir, user_data_dir

APP_NAME = "rhythm_trainer"
CONFIG_FILENAME = "config.yaml"
MAX_EXERCISES = 90  # Default maximum number of exercises supported


class NamingScheme(Enum):
    """Enum for naming conventions of backing tracks."""

    DEFAULT = "default"
    LOGICAL = "logical"


class FileFormat(Enum):
    """Enum for file formats of backing tracks."""

    WAV = "wav"
    MP3 = "mp3"


@dataclass
class Config:
    csv_path: Path
    first_exercise: int = 1
    last_exercise: int = MAX_EXERCISES
    backing_tracks_dir: Path | None = None
    naming_scheme: NamingScheme = NamingScheme.DEFAULT
    file_format: FileFormat = FileFormat.WAV

    def to_dict(self) -> dict[str, str | int | None]:
        """Convert the configuration to a dictionary with string representations."""
        return {
            "csv_path": str(self.csv_path),
            "first_exercise": self.first_exercise,
            "last_exercise": self.last_exercise,
            "backing_tracks_dir": str(self.backing_tracks_dir)
            if self.backing_tracks_dir
            else None,
            "naming_scheme": self.naming_scheme.value,
            "file_format": self.file_format.value,
        }


def get_config_path(config_filename: str) -> Path:
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / config_filename


def parse_config(config_filename: str = CONFIG_FILENAME) -> Config:
    config_path = get_config_path(config_filename)
    if not config_path.exists():
        print("Configuration file not found. Creating a default one.")
        default_config = Config(csv_path=Path(user_data_dir() + "/exercises.csv"))
        with config_path.open("w") as file:
            yaml.safe_dump(default_config.to_dict(), file)
        return default_config

    print(f"Reading configuration from {config_path}")
    with config_path.open("r") as file:
        config_data: dict[str, Any] = yaml.safe_load(file)
        if "csv_path" in config_data:
            config_data["csv_path"] = Path(config_data["csv_path"])
        if (
            "backing_tracks_dir" in config_data
            and config_data["backing_tracks_dir"] is not None
        ):
            config_data["backing_tracks_dir"] = Path(config_data["backing_tracks_dir"])
        if "naming_scheme" in config_data:
            config_data["naming_scheme"] = NamingScheme(
                config_data["naming_scheme"].lower(),
            )
        if "file_format" in config_data:
            config_data["file_format"] = FileFormat(
                config_data["file_format"].lower(),
            )
        config = Config(**config_data)

    if (
        config_data["backing_tracks_dir"]
        and not config_data["backing_tracks_dir"].is_dir()
    ):
        raise FileNotFoundError(
            f"Backing track directory '{config_data['backing_tracks_dir']}' "
            f"does not exist.",
        )

    return config


def save_config(config: Config, config_filename: str = CONFIG_FILENAME) -> None:
    config_path = get_config_path(config_filename)
    with config_path.open("w") as file:
        yaml.safe_dump(config.to_dict(), file)
