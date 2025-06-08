import csv
import random
from itertools import islice
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path("config.yaml")
MAX_EXERCISES = 90  # Maximum number of exercises supported


def parse_config() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            config: dict[str, Any] = yaml.safe_load(file)
    else:
        raise FileNotFoundError(
            f"Configuration file {CONFIG_FILE} not found. Write a configuration file to "
            f"use the app. For help on how to do that, see the README at "
            f"https://github.com/marchfra/caged-trainer."
        )

    if "csv_path" not in config:
        raise KeyError(
            "Configuration file is missing the 'csv_path' key. Please add it to the config file."
        )

    if "first_exercise" not in config:
        config["first_exercise"] = 1
    if "last_exercise" not in config:
        config["last_exercise"] = MAX_EXERCISES

    return config


def get_exercises_and_weights(
    csv_path: Path, first_exercise: int, last_exercise: int
) -> tuple[list[int], list[int]]:
    """
    Reads exercises and their corresponding weights from a CSV file within a specified range.

    If the CSV file exists, extracts exercise IDs and weights from the file between the given indices,
    with the minimum weight set to 1.
    If the file does not exist, generates a default list of exercise IDs and assigns a weight of 1 to each.
    """
    if csv_path.exists():
        print(f"Found existing CSV file at {csv_path}.")
        exercises: list[int] = []
        weights: list[int] = []
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in islice(reader, first_exercise - 1, last_exercise):
                exercises.append(int(row[0]))
                weights.append(max(int(row[1]), 1))

        return exercises, weights
    else:
        print(
            f"No CSV file found at {csv_path}. Generating default exercises and weights."
        )
        num_exercises = last_exercise - first_exercise + 1
        return list(range(1, last_exercise + 1)), [0] * (first_exercise - 1) + [
            1
        ] * num_exercises


def save_exercises_and_weights(
    csv_path: Path,
    exercises: list[int],
    weights: list[int],
    total_exercises: int = MAX_EXERCISES,
) -> None:
    """
    Saves the weights of the exercises to a CSV file.

    If the CSV file exists, it reads the current weights and updates them with the provided values.
    If the CSV file does not exist, it initializes all exercise weights to 0 and sets the provided weights.
    The CSV file will contain all exercises from 1 to `total_exercises`, each with their corresponding weight.
    """
    # Initialize all weights to 0 for exercises not in the CSV and read existing weights
    all_weights = {i: 0 for i in range(1, total_exercises + 1)}
    if csv_path.exists():
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    all_weights[int(row[0])] = int(row[1])

    # Update weights for the exercises being saved
    for i, exercise in enumerate(exercises):
        all_weights[exercise] = weights[i]

    # Write the updated weights back to the CSV file
    with open(csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Exercise", "Weight"])  # Write header
        for exercise, weight in all_weights.items():
            writer.writerow([exercise, weight])


def pick_exercise(exercises: list[int], weights: list[int]) -> int:
    """
    Selects a single exercise from a list of exercises based on provided weights.
    """
    if not exercises:
        raise ValueError("The exercise list is empty.")

    return random.choices(exercises, weights=weights, k=1)[0]


# TODO: Automatically open the backing track for the selected exercise
def main() -> None:
    config = parse_config()

    exercises, weights = get_exercises_and_weights(
        config["csv_path"], config["first_exercise"], config["last_exercise"]
    )

    while True:
        exercise = pick_exercise(exercises, weights)
        print(f"Play exercise {exercise}")

        while True:
            response = input("Did you play it well? (y/n/q): ").strip().lower()
            if response in ["y", "n", "q"]:
                break
            print("Invalid response. Please enter 'y' (yes), 'n' (no), or 'q' (quit).")

        if response == "q":
            print(f"Saving exercises and weights to CSV file {config['csv_path']}")
            save_exercises_and_weights(config["csv_path"], exercises, weights)
            exit(0)

        print()
        if response == "y":
            if weights[exercise - 1] > 1:
                weights[exercise - 1] -= 1
        elif response == "n":
            weights[exercise - 1] += 1
        else:
            raise ValueError("Unexpected response. This should never happen.")


if __name__ == "__main__":
    main()
