import csv
import random
import subprocess
import sys
from itertools import islice
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path("config.yaml")
MAX_EXERCISES = 90  # Maximum number of exercises supported


def main() -> None:
    config = parse_config()

    exercises, weights = get_exercises_and_weights(
        config["csv_path"],
        config["first_exercise"],
        config["last_exercise"],
    )

    random_mode = config.get("random_mode")

    while True:
        if random_mode:
            exercise = pick_random_exercise(exercises, weights)
        else:
            exercise = get_number_input(
                "Enter the exercise number to play: ",
                config["first_exercise"],
                config["last_exercise"],
            )
            print()

        print(f"Play exercise {exercise}")
        if config["backing_tracks_dir"]:
            input("Press Enter to play the backing track for this exercise...")
            play_backing_track(exercise, config["backing_tracks_dir"])

        response = get_valid_input("Did you play it well? (y/n/q): ", ["y", "n", "q"])

        if response == "q":
            save_exercises_and_weights(config["csv_path"], exercises, weights)
            sys.exit(0)

        print()
        if response == "y":
            if weights[exercise - config["first_exercise"]] > 1:
                weights[exercise - config["first_exercise"]] -= 1
        elif response == "n":
            weights[exercise - config["first_exercise"]] += 1
        else:
            raise ValueError("Unexpected response.")


def parse_config() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r") as file:
            config: dict[str, Any] = yaml.safe_load(file)
    else:
        raise FileNotFoundError(
            f"Configuration file {CONFIG_FILE} not found. Write a configuration file to"
            f" use the app. For help on how to do that, see the README at "
            f"https://github.com/marchfra/caged-trainer.",
        )

    if "csv_path" not in config:
        raise KeyError(
            "Configuration file is missing the 'csv_path' key. Please add it to the "
            "config file.",
        )
    config["csv_path"] = Path(config["csv_path"])

    if "first_exercise" not in config:
        config["first_exercise"] = 1
    if "last_exercise" not in config:
        config["last_exercise"] = MAX_EXERCISES

    if "backing_tracks_dir" not in config:
        config["backing_tracks_dir"] = None
    else:
        config["backing_tracks_dir"] = Path(config["backing_tracks_dir"])
        if not config["backing_tracks_dir"].is_dir():
            raise FileNotFoundError(
                f"Backing track file '{config['backing_tracks_dir']}' does not exist.",
            )

    if "random_mode" not in config:
        config["random_mode"] = True

    return config


def get_exercises_and_weights(
    csv_path: Path,
    first_exercise: int,
    last_exercise: int,
) -> tuple[list[int], list[int]]:
    """Read exercises and their weights from a CSV file within a specified range.

    If the CSV file exists, extracts exercise IDs and weights from the file between the
    given indices, with the minimum weight set to 1.
    If the file does not exist, generates a default list of exercise IDs and assigns a
    weight of 1 to each.
    """
    if csv_path.exists():
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
    print(
        f"No CSV file found at {csv_path}. Generating default exercises and weights.",
    )
    num_exercises = last_exercise - first_exercise + 1
    return list(range(1, last_exercise + 1)), [0] * (first_exercise - 1) + [
        1,
    ] * num_exercises


def save_exercises_and_weights(
    csv_path: Path,
    exercises: list[int],
    weights: list[int],
    total_exercises: int = MAX_EXERCISES,
) -> None:
    """Save the weights of the exercises to a CSV file.

    If the CSV file exists, it reads the current weights and updates them with the
    provided values.
    If the CSV file does not exist, it initializes all exercise weights to 0 and sets
    the provided weights.
    The CSV file will contain all exercises from 1 to `total_exercises`, each with their
    corresponding weight.
    """
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


def pick_random_exercise(
    exercises: list[int],
    weights: list[int],
    ex_buffer: int = 10,
    buffer: list[int] = [],  # noqa: B006 - This is intended behavior
) -> int:
    """Select a single exercise from a list of exercises based on provided weights."""
    if not exercises:
        raise ValueError("The exercise list is empty.")

    exercise = random.choices(exercises, weights=weights, k=1)[0]
    while exercise in buffer:
        exercise = random.choices(exercises, weights=weights, k=1)[0]
    buffer.append(exercise)
    if len(buffer) > ex_buffer:
        buffer.pop(0)

    return exercise


def play_backing_track(exercise: int, backing_tracks_dir: Path) -> None:
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

    folder = backing_tracks_dir / subdirs[(exercise - 1) // 10]
    if not folder.is_dir():
        raise FileNotFoundError(
            f"Backing track folder '{folder}' does not exist. Please check your "
            "configuration.",
        )

    track_path = folder / f"BK {folder.name} {exercise:02d}.mp3"
    if not track_path.is_file():
        raise FileNotFoundError(
            f"Backing track file '{track_path}' does not exist. Please check your "
            "configuration.",
        )

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
