from pathlib import Path
from typing import Literal

import pytest
from PyQt6.QtWidgets import QPushButton
from pytestqt.qtbot import QtBot

from rhythm_trainer.config import FileFormat, NamingScheme
from rhythm_trainer.gui.modes import BaseModeWidget, ManualModeWidget, RandomModeWidget


@pytest.fixture
def button(qtbot: QtBot) -> QPushButton:
    btn = QPushButton()
    qtbot.addWidget(btn)
    return btn


def test_button_disabled_when_no_exercise(button: QPushButton, tmp_path: Path) -> None:
    widget = BaseModeWidget(button)
    widget.current_exercise = None
    widget.enable_bk_track_button(tmp_path, NamingScheme.DEFAULT, FileFormat.WAV)
    assert not button.isEnabled()


def test_button_enabled_when_track_exists(
    button: QPushButton,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    widget = BaseModeWidget(button)
    widget.current_exercise = 5

    def fake_validate(
        _ex: int,
        _bk_dir: Path,
        _naming: NamingScheme,
        _fmt: FileFormat,
    ) -> Path:
        return tmp_path / "fake_track.wav"

    monkeypatch.setattr(
        "rhythm_trainer.gui.modes.validate_backing_track",
        fake_validate,
    )

    widget.enable_bk_track_button(tmp_path, NamingScheme.DEFAULT, FileFormat.WAV)
    assert button.isEnabled()


def test_button_disabled_when_track_missing(
    button: QPushButton,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    widget = BaseModeWidget(button)
    widget.current_exercise = 7

    monkeypatch.setattr(
        "rhythm_trainer.gui.modes.validate_backing_track",
        lambda *_args: None,
    )

    widget.enable_bk_track_button(tmp_path, NamingScheme.DEFAULT, FileFormat.WAV)
    assert not button.isEnabled()


def test_validate_backing_track_called_with_correct_args(
    button: QPushButton,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    widget = BaseModeWidget(button)
    widget.current_exercise = 42
    called = {}

    def fake_validate(
        ex: int,
        bk_dir: Path,
        naming: NamingScheme,
        fmt: FileFormat,
    ) -> None:
        called.update({"ex": ex, "bk_dir": bk_dir, "naming": naming, "fmt": fmt})

    monkeypatch.setattr(
        "rhythm_trainer.gui.modes.validate_backing_track",
        fake_validate,
    )

    widget.enable_bk_track_button(tmp_path, NamingScheme.LOGICAL, FileFormat.MP3)
    assert called["ex"] == 42
    assert called["bk_dir"] == tmp_path
    assert called["naming"] == NamingScheme.LOGICAL
    assert called["fmt"] == FileFormat.MP3


def test_widget_construction_sets_label(button: QPushButton) -> None:
    widget = RandomModeWidget(button)
    assert widget.exercise_label.objectName() == "question"
    assert widget.exercise_label.alignment()
    assert widget.exercise_label.text() == ""


def test_pick_exercise_sets_current_and_label(
    button: QPushButton,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    widget = RandomModeWidget(button)
    # Patch pick_random_exercise to return a known value
    monkeypatch.setattr(
        "rhythm_trainer.gui.modes.pick_random_exercise",
        lambda _exercises, _weights, _buffer: 42,
    )
    exercises = [1, 2, 3]
    weights = [1, 1, 1]
    buffer = []
    result = widget.pick_exercise(exercises, weights, buffer)
    assert widget.current_exercise == 42
    assert widget.exercise_label.text() == "Exercise #42"
    assert result == 42


def test_pick_exercise_passes_correct_args(
    button: QPushButton,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    widget = RandomModeWidget(button)
    called = {}

    def fake_picker(
        exercises: list[int],
        weights: list[int],
        buffer: list[int],
    ) -> Literal[7]:
        called["exercises"] = exercises
        called["weights"] = weights
        called["buffer"] = buffer
        return 7

    monkeypatch.setattr(
        "rhythm_trainer.gui.modes.pick_random_exercise",
        fake_picker,
    )
    exercises = [10, 20]
    weights = [2, 3]
    buffer = [99]
    widget.pick_exercise(exercises, weights, buffer)
    assert called["exercises"] == exercises
    assert called["weights"] == weights
    assert called["buffer"] == buffer


def test_widget_construction(button: QPushButton) -> None:
    widget = ManualModeWidget(button, 1, 10)
    assert widget.exercise_input.objectName() == "exercise_input"
    assert widget.exercise_input.placeholderText() == "Exercise range: 1 - 10"


def test_valid_input_sets_current_and_valid(qtbot: QtBot, button: QPushButton) -> None:
    widget = ManualModeWidget(button, 1, 10)
    qtbot.addWidget(widget)
    widget.exercise_input.setText("5")
    assert widget.current_exercise == 5
    assert widget.is_valid
    assert widget.exercise_input.styleSheet() == ""
    assert widget.get_exercise() == 5


def test_invalid_input_sets_invalid_and_red(qtbot: QtBot, button: QPushButton) -> None:
    widget = ManualModeWidget(button, 1, 10)
    qtbot.addWidget(widget)
    widget.exercise_input.setText("0")  # out of range
    assert widget.current_exercise is None
    assert not widget.is_valid
    assert "color: red" in widget.exercise_input.styleSheet()
    assert widget.get_exercise() is None


def test_non_integer_input(qtbot: QtBot, button: QPushButton) -> None:
    widget = ManualModeWidget(button, 1, 10)
    qtbot.addWidget(widget)
    widget.exercise_input.setText("abc")
    assert widget.current_exercise is None
    assert not widget.is_valid
    assert "color: red" in widget.exercise_input.styleSheet()
    assert widget.get_exercise() is None


def test_empty_input_resets_state(qtbot: QtBot, button: QPushButton) -> None:
    widget = ManualModeWidget(button, 1, 10)
    qtbot.addWidget(widget)
    widget.exercise_input.setText("5")
    assert widget.get_exercise() == 5
    widget.exercise_input.setText("")
    assert widget.current_exercise is None
    assert widget.exercise_input.styleSheet() == ""
    assert widget.get_exercise() is None


def test_edge_values(qtbot: QtBot, button: QPushButton) -> None:
    widget = ManualModeWidget(button, 1, 10)
    qtbot.addWidget(widget)
    widget.exercise_input.setText("1")
    assert widget.get_exercise() == 1
    widget.exercise_input.setText("10")
    assert widget.get_exercise() == 10


def test_validate_exercise_input_no_validator(
    qtbot: QtBot,
    button: QPushButton,
) -> None:
    widget = ManualModeWidget(button, 1, 10)
    qtbot.addWidget(widget)

    widget.exercise_input.validator = lambda: None

    widget.exercise_input.setText("5")
    assert widget.current_exercise is None
