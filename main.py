import csv
import random
from pathlib import Path

CSV_NAME = Path("exercises-and-weights.csv")
NUM_EXERCISES = 90


def get_exercises_and_weights() -> tuple[list[int], list[int]]:
    """
    Reads exercise numbers and their corresponding weights from a CSV file.

    Returns:
        tuple[list[int], list[int]]: A tuple containing two lists:
            - The first list contains exercise numbers as integers.
            - The second list contains the corresponding weights as integers.

    If the CSV file is not found, returns a default list of exercise numbers from 1 to
    NUM_EXERCISES, each with a weight of 1.
    """
    try:
        exercises: list[int] = []
        weights: list[int] = []
        with open(CSV_NAME, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row:  # Skip empty rows
                    exercises.append(int(row[0]))
                    weights.append(int(row[1]))

        return exercises, weights
    except FileNotFoundError:
        return list(range(1, NUM_EXERCISES + 1)), [1] * NUM_EXERCISES


def save_exercises_and_weights(exercises: list[int], weights: list[int]) -> None:
    """
    Saves a list of exercises and their corresponding weights to a CSV file.

    The function writes the exercises and weights to a CSV file specified by the global
    variable CSV_NAME. Each row in the file contains an exercise and its associated
    weight.
    """
    with open(CSV_NAME, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Exercise", "Weight"])  # Write header
        for exercise, weight in zip(exercises, weights):
            writer.writerow([exercise, weight])


def pick_exercise(exercises: list[int], weights: list[int]) -> int:
    """
    Selects a single exercise from a list of exercises based on provided weights.
    """
    if not exercises:
        raise ValueError("The exercise list is empty.")

    return random.choices(exercises, weights=weights, k=1)[0]


def main():  # TODO: Automatically open the backing track for the selected exercise
    exercises, weights = get_exercises_and_weights()

    while True:
        exercise = pick_exercise(exercises, weights)
        print(f"Play exercise {exercise}")
        response = input("Did you play it well? (y/n/yq/nq): ").strip().lower()

        if response[0] == "y":
            if weights[exercise - 1] > 1:
                weights[exercise - 1] -= 1
        elif response[0] == "n":
            weights[exercise - 1] += 1
        else:
            print("Invalid response. Please enter 'y', 'n', 'yq', or 'nq'.")
            continue

        if "q" in response:
            save_exercises_and_weights(exercises, weights)
            exit(0)
        else:
            print()


if __name__ == "__main__":
    main()
