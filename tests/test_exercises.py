import csv
from pathlib import Path

import pytest

from rhythm_trainer.exercises import (
    get_exercises_and_weights,
    pick_random_exercise,
    save_exercises_and_weights,
)


def test_get_exercises_and_weights_from_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "exercises.csv"
    first_exercise = 3
    last_exercise = 7

    with csv_path.open("w") as file:
        writer = csv.writer(file)
        writer.writerow(["Exercise", "Weight"])
        for i in range(1, 11):
            writer.writerow([i, i])

    exercises, weights = get_exercises_and_weights(
        csv_path,
        first_exercise,
        last_exercise,
    )
    assert exercises == [3, 4, 5, 6, 7]
    assert weights == [3, 4, 5, 6, 7]


def test_get_exercises_and_weights_default(tmp_path: Path) -> None:
    csv_path = tmp_path / "exercises.csv"
    first_exercise = 3
    last_exercise = 7
    assert not csv_path.exists()

    exercises, weights = get_exercises_and_weights(
        csv_path,
        first_exercise,
        last_exercise,
    )
    assert exercises == [1, 2, 3, 4, 5, 6, 7]
    assert weights == [0, 0, 1, 1, 1, 1, 1]


def test_save_exercises_and_weights_to_existing_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "exercises.csv"
    exercises = [1, 2, 3, 4, 5, 6, 7]
    weights = [0, 0, 1, 1, 2, 1, 1]
    total_exercises = 10

    save_exercises_and_weights(csv_path, exercises, weights, total_exercises)

    weights = [1, 1, 3, 2, 2, 1, 5]
    save_exercises_and_weights(csv_path, exercises, weights, total_exercises)

    with csv_path.open("r") as file:
        reader = csv.reader(file)
        header = next(reader)
        assert header == ["Exercise", "Weight"]
        for i, row in enumerate(reader):
            if i < len(exercises):
                assert row == [str(exercises[i]), str(weights[i])]
            else:
                assert row == [str(i + 1), "0"]


def test_save_exercises_and_weights_to_new_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "exercises.csv"
    exercises = [1, 2, 3, 4, 5, 6, 7]
    weights = [0, 0, 1, 1, 2, 1, 1]
    total_exercises = 10

    assert not csv_path.exists()

    save_exercises_and_weights(csv_path, exercises, weights, total_exercises)

    with csv_path.open("r") as file:
        reader = csv.reader(file)
        header = next(reader)
        assert header == ["Exercise", "Weight"]
        for i, row in enumerate(reader):
            if i < len(exercises):
                assert row == [str(exercises[i]), str(weights[i])]
            else:
                assert row == [str(i + 1), "0"]


@pytest.mark.parametrize("expected", [1, 2, 3, 4, 5, 6, 7])
def test_pick_random_exercise_no_buffer(
    monkeypatch: pytest.MonkeyPatch,
    expected: int,
) -> None:
    monkeypatch.setattr("random.choices", lambda _, weights=None, k=1: [expected])

    exercise = pick_random_exercise(
        exercises=list(range(1, 11)),
        weights=list(range(1, 11)),
    )

    assert exercise == expected


def test_pick_random_exercise_buffer_full(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("random.choices", lambda _, weights=None, k=1: [1])

    buffer = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    exercise = pick_random_exercise(
        exercises=list(range(1, 11)),
        weights=list(range(1, 11)),
        buffer=buffer,
    )

    assert exercise == 1


def test_pick_random_exercise_max_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("random.choices", lambda _, weights=None, k=1: [1])

    buffer = [1, 2, 3]
    with pytest.raises(RuntimeError, match="Failed to select a unique"):
        pick_random_exercise(
            exercises=list(range(1, 11)),
            weights=list(range(1, 11)),
            buffer=buffer,
        )
