from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from rhythm_trainer.config import FileFormat, NamingScheme
from rhythm_trainer.exercises import pick_random_exercise
from rhythm_trainer.gui.widgets import NumberOnlyLineEdit
from rhythm_trainer.tracks import validate_backing_track


class BaseModeWidget(QWidget):
    def __init__(
        self,
        bk_tracks_button: QPushButton,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.bk_tracks_button = bk_tracks_button
        self.current_exercise: int | None = None

    def enable_bk_track_button(
        self,
        backing_tracks_dir: Path,
        naming_scheme: NamingScheme,
        file_format: FileFormat,
    ) -> None:
        enable = False

        if self.current_exercise:
            enable = (
                validate_backing_track(
                    self.current_exercise,
                    backing_tracks_dir,
                    naming_scheme,
                    file_format,
                )
                is not None
            )

        self.bk_tracks_button.setEnabled(enable)


class RandomModeWidget(BaseModeWidget):
    def __init__(
        self,
        bk_tracks_button: QPushButton,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(bk_tracks_button, parent)

        layout = QVBoxLayout(self)
        self.exercise_label = QLabel()
        self.exercise_label.setObjectName("question")
        self.exercise_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exercise_label.setFixedHeight(30)
        layout.addWidget(self.exercise_label)

    def pick_exercise(
        self,
        exercises: list[int],
        weights: list[int],
        buffer: list[int],
    ) -> int:
        self.current_exercise = pick_random_exercise(exercises, weights, buffer)
        self.exercise_label.setText(f"Exercise #{self.current_exercise}")
        return self.current_exercise


class ManualModeWidget(BaseModeWidget):
    def __init__(
        self,
        bk_tracks_button: QPushButton,
        first_exercise: int,
        last_exercise: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(bk_tracks_button, parent)

        layout = QVBoxLayout(self)
        input_label = QLabel("Enter an exercise")
        input_label.setObjectName("input_label")
        input_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        input_label.setFixedHeight(30)
        layout.addWidget(input_label)

        self.exercise_input = NumberOnlyLineEdit(first_exercise, last_exercise)
        self.exercise_input.setObjectName("exercise_input")
        self.exercise_input.textChanged.connect(self._validate_exercise_input)
        self.exercise_input.setPlaceholderText(
            f"Exercise range: {first_exercise} - {last_exercise}",
        )
        layout.addWidget(self.exercise_input)

    def _validate_exercise_input(self, text: str) -> None:
        validator = self.exercise_input.validator()
        if not validator:
            return

        state = validator.validate(text, 0)[0]
        if state != QIntValidator.State.Acceptable:
            self.exercise_input.setStyleSheet("color: red;")
            self.is_valid = False
        else:
            self.current_exercise = int(text)
            self.exercise_input.setStyleSheet("")
            if text != "":
                self.is_valid = True

        if text == "":
            self.exercise_input.setStyleSheet("")
            self.current_exercise = None

    def get_exercise(self) -> int | None:
        if self.is_valid and self.current_exercise is not None:
            return self.current_exercise
        return None
