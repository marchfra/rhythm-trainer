import csv
import random
from itertools import islice
from pathlib import Path

from rhythm_trainer.config import MAX_EXERCISES
from rhythm_trainer.logger import get_logger

logger = get_logger(__name__)


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
        logger.info(f"Found existing CSV file at {csv_path}.")
        exercises: list[int] = []
        weights: list[int] = []
        with csv_path.open("r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in islice(reader, first_exercise - 1, last_exercise):
                exercises.append(int(row[0]))
                weights.append(max(int(row[1]), 1))

        return exercises, weights

    logger.info(
        f"No CSV file found at {csv_path}. Generating default exercises and weights.",
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
) -> None:
    """Save the weights of the exercises to a CSV file.

    If the CSV file exists, it reads the current weights and updates them with the
    provided values.
    If the CSV file does not exist, it creates it and then initializes all exercise
    weights to 0 and sets the provided weights.
    The created CSV file will contain all exercises from 1 to `total_exercises`, each
    with their corresponding weight.
    """
    logger.info(f"Saving exercises and weights to CSV file {csv_path}")
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

    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        exercise = random.choices(exercises, weights=weights, k=1)[0]
        if exercise not in buffer:
            buffer.append(exercise)
            return exercise
        if len(buffer) >= buffer_size:
            buffer.pop(0)
        attempts += 1

    error_message = f"Failed to select a unique exercise after {max_attempts} attempts."
    logger.error(error_message)
    raise RuntimeError(error_message)
