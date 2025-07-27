import csv
import math
import random
import subprocess
from dataclasses import dataclass
from enum import Enum
from itertools import islice
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path(".config.yaml")
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


def main() -> None:
    ...
    # config = parse_config()

    # exercises, weights = get_exercises_and_weights(
    #     config.csv_path,
    #     config.first_exercise,
    #     config.last_exercise,
    #     verbose=True,
    # )

    # buffer: list[int] = []

    # while True:
    #     if config.random_mode:
    #         exercise = pick_random_exercise(exercises, weights, buffer)
    #     else:
    #         exercise = get_number_input(
    #             "Enter the exercise number to play: ",
    #             config.first_exercise,
    #             config.last_exercise,
    #         )
    #         print()

    #     print(f"Play exercise {exercise}")
    #     if config.backing_tracks_dir:
    #         input("Press Enter to play the backing track for this exercise...")
    #         play_backing_track(
    #             exercise,
    #             config.backing_tracks_dir,
    #             NamingScheme.LOGICAL,
    #             "mp3",
    #         )

    #     response = get_valid_input("Did you play it well? (y/n/q): ", ["y", "n", "q"])

    #     if response == "q":
    #         save_exercises_and_weights(
    #             config.csv_path,
    #             exercises,
    #             weights,
    #             verbose=True,
    #         )
    #         sys.exit(0)

    #     print()
    #     if response == "y":
    #         if weights[exercise - config.first_exercise] > 1:
    #             weights[exercise - config.first_exercise] -= 1
    #     elif response == "n":
    #         weights[exercise - config.first_exercise] += 1
    #     else:
    #         raise ValueError("Unexpected response.")

    #     save_exercises_and_weights(config.csv_path, exercises, weights)


def parse_config(config_path: Path = CONFIG_FILE) -> Config:
    if not config_path.exists():
        print("Configuration file not found. Creating a default one.")
        default_config = Config(csv_path=Path("exercises.csv"))
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


def get_exercises_and_weights(
    csv_path: Path,
    first_exercise: int,
    last_exercise: int,
    *,
    verbose: bool = False,
) -> tuple[list[int], list[int]]:
    """Read exercises and their weights from a CSV file within a specified range.

    If the CSV file exists, extracts exercise IDs and weights from the file between the
    given indices, with the minimum weight set to 1.
    If the file does not exist, generates a default list of exercise IDs and assigns a
    weight of 1 to each.
    """
    if csv_path.exists():
        if verbose:
            print(f"Found existing CSV file at {csv_path}.")
        exercises: list[int] = []
        weights: list[int] = []
        with csv_path.open("r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in islice(reader, first_exercise - 1, last_exercise):
                exercises.append(int(row[0]))
                weights.append(max(int(row[1]), 1))

        return exercises, weights

    if verbose:
        print(
            f"No CSV file found at {csv_path}. "
            f"Generating default exercises and weights.",
        )
    num_exercises = last_exercise - first_exercise + 1
    exercises = list(range(1, last_exercise + 1))
    weights = [0] * (first_exercise - 1) + [1] * num_exercises
    return exercises, weights


def save_exercises_and_weights(
    csv_path: Path,
    exercises: list[int],
    weights: list[int],
    total_exercises: int = MAX_EXERCISES,
    *,
    verbose: bool = False,
) -> None:
    """Save the weights of the exercises to a CSV file.

    If the CSV file exists, it reads the current weights and updates them with the
    provided values.
    If the CSV file does not exist, it creates it and then initializes all exercise
    weights to 0 and sets the provided weights.
    The created CSV file will contain all exercises from 1 to `total_exercises`, each
    with their corresponding weight.
    """
    if verbose:
        print(f"Saving exercises and weights to CSV file {csv_path}")
    # Initialize all weights to 0 for exercises not in the CSV and read existing weights
    all_weights = dict.fromkeys(range(1, total_exercises + 1), 0)
    if csv_path.exists():
        with csv_path.open("r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    all_weights[int(row[0])] = int(row[1])

    # Update weights for the exercises being saved
    for i, exercise in enumerate(exercises):
        all_weights[exercise] = weights[i]

    # Write the updated weights back to the CSV file
    with csv_path.open("w") as file:
        writer = csv.writer(file)
        writer.writerow(["Exercise", "Weight"])  # Write header
        for exercise, weight in all_weights.items():
            writer.writerow([exercise, weight])


def map_weights(weights: list[int], sensitivity: float) -> list[float]:
    """Apply exponential map to the weights, with parameter s.

    Returns
    -------
        list[float] : the new weights

    """
    return [(math.exp(weight / max(weights)) - 1) ** sensitivity for weight in weights]


def pick_random_exercise(
    exercises: list[int],
    weights: list[int],
    buffer: list[int] | None = None,
    buffer_size: int = 10,
) -> int:
    """Select a single exercise from a list of exercises based on provided weights.

    The selection is done randomly, with the probability of each exercise being
    proportional to its weight. The function ensures that the selected exercise is not
    already in the buffer, which is a list of recently selected exercises. If the
    buffer is full, the oldest exercise is removed to make space for the new one.
    """
    if buffer is None:
        buffer = []
    if not exercises:
        raise ValueError("The exercise list is empty.")

    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        exercise = random.choices(exercises, weights=weights, k=1)[0]
        if exercise not in buffer:
            buffer.append(exercise)
            if len(buffer) > buffer_size:
                buffer.pop(0)
            return exercise
        attempts += 1

    raise RuntimeError(
        f"Failed to select a unique exercise after {max_attempts} attempts.",
    )


def validate_backing_track(
    exercise: int,
    backing_tracks_dir: Path,
    naming_convention: NamingScheme = NamingScheme.DEFAULT,
    file_format: FileFormat = FileFormat.WAV,
) -> Path | None:
    """Check if the backing track for a given exercise exists.

    Returns the backing track's Path if it exists, None otherwise.
    """
    subdirs = [
        "Acoustic",
        "Classic Blues",
        "Classic Rock",
        "Funk",
        "Fusion",
        "Hard Rock & Heavy Metal",
        "Jazz",
        "Pop",
        "Soul",
    ]

    chapter_folder = backing_tracks_dir / subdirs[(exercise - 1) // 10]
    if not chapter_folder.is_dir():
        return None

    if naming_convention == NamingScheme.LOGICAL:
        track_path = (
            chapter_folder
            / f"BK {chapter_folder.name} {exercise:02d}.{file_format.value}"
        )
    elif naming_convention == NamingScheme.DEFAULT:
        track_path = (
            chapter_folder
            / f"{chapter_folder.name} {exercise:02d} BK.{file_format.value}"
        )
    else:
        raise ValueError(
            f"Unsupported naming convention: {naming_convention}. "
            f"Use one of {[f'NamingConvention.{e.name}' for e in NamingScheme]}",
        )

    return track_path if track_path.is_file() else None


def play_backing_track(
    exercise: int,
    backing_tracks_dir: Path,
    naming_convention: NamingScheme = NamingScheme.DEFAULT,
    file_format: FileFormat = FileFormat.WAV,
    *,
    verbose: bool = False,
) -> None:
    """Play the backing track for a given exercise.

    This function locates the backing track file based on the exercise number,
    backing tracks directory, naming convention, and file type. If the file is found,
    it opens the track using the system's default application, otherwise it raises a
    FileNotFoundError.
    """
    track_path = validate_backing_track(
        exercise,
        backing_tracks_dir,
        naming_convention,
        file_format,
    )

    if track_path is None:
        raise FileNotFoundError(
            f"Backing track {track_path} for exercise {exercise} not found in directory"
            f" {backing_tracks_dir}. Please check your configuration.",
        )

    if verbose:
        print(f"Playing backing track '{track_path.name}'")
    subprocess.Popen(  # noqa: S603
        ["/usr/bin/open", str(track_path)],
        stdout=subprocess.DEVNULL,
    )


def get_valid_input(prompt: str, valid_responses: list[str]) -> str:
    """Validate user input against a list of valid responses."""
    while True:
        response = input(prompt).strip().lower()
        if response in valid_responses:
            return response
        print(
            "Invalid input. Please enter one of the following: "
            f"{', '.join(valid_responses)}.",
        )


def get_number_input(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Prompt the user for a number input."""
    while True:
        response = input(prompt).strip()
        if response.isdigit():
            response = int(response)
            if (min_value is None or response >= min_value) and (
                max_value is None or response <= max_value
            ):
                return response
        print("Invalid input.", end=" ")
        if min_value is not None and max_value is not None:
            print(f"Please enter a number between {min_value} and {max_value}.")
        elif min_value is not None:
            print(f"Please enter a number greater than or equal to {min_value}.")
        elif max_value is not None:
            print(f"Please enter a number less than or equal to {max_value}.")
        else:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()
