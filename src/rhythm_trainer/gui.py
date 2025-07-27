from collections.abc import Callable
from pathlib import Path

from main import (
    MAX_EXERCISES,
    FileFormat,
    NamingScheme,
    get_exercises_and_weights,
    parse_config,
    pick_random_exercise,
    play_backing_track,
    save_exercises_and_weights,
    validate_backing_track,
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIntValidator, QKeyEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

TEST_MODE = True


def main() -> None:
    app = QApplication([])

    with Path("src/rhythm_trainer/style.qss").open("r") as style_file:
        _style = style_file.read()
        app.setStyleSheet(_style)

    main_window = MainWindow()
    main_window.show()
    app.exec()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rhythm Trainer")
        self.setFixedSize(QSize(350, 400))

        self._load_config_and_exercises()

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        # layout.setSpacing(100)
        self.setCentralWidget(central_widget)

        bk_tracks_button_layout = QHBoxLayout()

        self.bk_tracks_button = QPushButton("Play backing track")
        self.bk_tracks_button.setObjectName("bk_tracks_button")
        self.bk_tracks_button.setFixedSize(QSize(250, 50))
        self.bk_tracks_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bk_tracks_button.clicked.connect(self.play_backing_track)
        bk_tracks_button_layout.addWidget(self.bk_tracks_button)

        self.create_modes_tab(layout, self.bk_tracks_button)

        layout.addLayout(bk_tracks_button_layout)

        feedback_label = QLabel("How did it go?")
        feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feedback_label.setFixedHeight(50)
        layout.addWidget(feedback_label)

        feedback_buttons_layout = QHBoxLayout()
        self.good_button = QPushButton("Good")
        self.good_button.setFocus()
        self.good_button.setObjectName("good_button")
        self.good_button.setMinimumSize(QSize(100, 50))
        self.good_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.good_button.clicked.connect(self.good_feedback)
        feedback_buttons_layout.addWidget(self.good_button)
        self.bad_button = QPushButton("Bad")
        self.bad_button.setObjectName("bad_button")
        self.bad_button.setMinimumSize(QSize(100, 50))
        self.bad_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bad_button.clicked.connect(self.bad_feedback)
        feedback_buttons_layout.addWidget(self.bad_button)
        layout.addLayout(feedback_buttons_layout)

        self.manual_mode.exercise_input.set_shortcut_callbacks(
            self.good_button.click,
            self.bad_button.click,
        )

        self._init_shortcuts()
        self.buffer: list[int] = []
        self.next_exercise()

    def _init_shortcuts(self) -> None:
        self.play_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.play_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.play_shortcut.activated.connect(self.bk_tracks_button.click)

        self.play_shortcut_alt = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.play_shortcut_alt.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.play_shortcut_alt.activated.connect(self.bk_tracks_button.click)

        self.good_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Plus), self)
        self.good_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.good_shortcut.activated.connect(self.good_button.click)

        self.bad_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Minus), self)
        self.bad_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.bad_shortcut.activated.connect(self.bad_button.click)

        self.tab_shortcut_ctrl_1 = QShortcut(QKeySequence("Ctrl+1"), self)
        self.tab_shortcut_ctrl_1.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.tab_shortcut_ctrl_1.activated.connect(lambda: self.tabs.setCurrentIndex(0))
        self.tab_shortcut_ctrl_1.activated.connect(
            lambda: self.bk_tracks_button.setEnabled(True),
        )

        self.tab_shortcut_ctrl_2 = QShortcut(QKeySequence("Ctrl+2"), self)
        self.tab_shortcut_ctrl_2.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.tab_shortcut_ctrl_2.activated.connect(lambda: self.tabs.setCurrentIndex(1))
        self.tab_shortcut_ctrl_2.activated.connect(
            lambda: self.bk_tracks_button.setEnabled(False),
        )
        self.tab_shortcut_ctrl_2.activated.connect(
            lambda: self.manual_mode.exercise_input.setFocus(),
        )

        self.tab_shortcut_cmd_1 = QShortcut(QKeySequence("Meta+1"), self)
        self.tab_shortcut_cmd_1.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.tab_shortcut_cmd_1.activated.connect(lambda: self.tabs.setCurrentIndex(0))
        self.tab_shortcut_cmd_1.activated.connect(
            lambda: self.bk_tracks_button.setEnabled(True),
        )

        self.tab_shortcut_cmd_2 = QShortcut(QKeySequence("Meta+2"), self)
        self.tab_shortcut_cmd_2.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.tab_shortcut_cmd_2.activated.connect(lambda: self.tabs.setCurrentIndex(1))
        self.tab_shortcut_cmd_2.activated.connect(
            lambda: self.bk_tracks_button.setEnabled(False),
        )
        self.tab_shortcut_cmd_2.activated.connect(
            lambda: self.manual_mode.exercise_input.setFocus(),
        )

    def _load_config_and_exercises(self) -> None:
        self.config = parse_config()
        self.exercises, self.weights = get_exercises_and_weights(
            self.config.csv_path,
            self.config.first_exercise,
            self.config.last_exercise,
        )

    def create_modes_tab(self, layout: QLayout, bk_tracks_button: QPushButton) -> None:
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")
        self.tabs.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.random_mode = RandomModeWidget(bk_tracks_button)
        self.manual_mode = ManualModeWidget(
            bk_tracks_button,
            self.config.first_exercise,
            self.config.last_exercise,
        )

        self.manual_mode.exercise_input.textChanged.connect(
            self.get_exercise_from_manual_mode,
        )

        if self.config.backing_tracks_dir is not None:
            self.manual_mode.exercise_input.textChanged.connect(
                lambda: self.manual_mode.enable_bk_track_button(
                    self.config.backing_tracks_dir,
                    self.config.naming_scheme,
                    self.config.file_format,
                )
                if self.config.backing_tracks_dir
                else None,
            )
        self.tabs.addTab(self.random_mode, "Random Exercise")
        self.tabs.addTab(self.manual_mode, "Manual Input")

        layout.addWidget(self.tabs)

    def play_backing_track(self) -> None:
        print(f"Playing backing track for exercise {self.current_exercise}.")
        self.bk_tracks_button.setEnabled(False)

        if (
            self.config.backing_tracks_dir
            and self.current_exercise is not None
            and not TEST_MODE
        ):
            play_backing_track(
                self.current_exercise,
                self.config.backing_tracks_dir,
                self.config.naming_scheme,
                self.config.file_format,
            )

        self.good_button.setEnabled(True)
        self.bad_button.setEnabled(True)

    def good_feedback(self) -> None:
        print(f"Good feedback received on exercise {self.current_exercise}.")
        if self.current_exercise is not None:
            if self.weights[self.current_exercise - self.config.first_exercise] > 1:
                self.weights[self.current_exercise - self.config.first_exercise] -= 1
            save_exercises_and_weights(
                self.config.csv_path,
                self.exercises,
                self.weights,
            )
            self.next_exercise()

    def bad_feedback(self) -> None:
        print(f"Bad feedback received on exercise {self.current_exercise}.")
        if self.current_exercise is not None:
            self.weights[self.current_exercise - self.config.first_exercise] += 1
            save_exercises_and_weights(
                self.config.csv_path,
                self.exercises,
                self.weights,
            )
            self.next_exercise()

    def reset_interface(self) -> None:
        self.good_button.setEnabled(False)
        self.bad_button.setEnabled(False)
        self.bk_tracks_button.setEnabled(False)

        self.manual_mode.exercise_input.setText("")

    def next_exercise(self) -> None:
        self.reset_interface()

        if self.tabs.currentIndex() == 0:
            self.current_exercise = self.random_mode.pick_exercise(
                self.exercises,
                self.weights,
                self.buffer,
            )

            if self.config.backing_tracks_dir:
                self.random_mode.enable_bk_track_button(
                    self.config.backing_tracks_dir,
                    self.config.naming_scheme,
                    self.config.file_format,
                )
            else:
                self.bk_tracks_button.setEnabled(False)
                self.good_button.setEnabled(True)
                self.bad_button.setEnabled(True)
        elif self.tabs.currentIndex() == 1:
            self.current_exercise = self.manual_mode.get_exercise()

            if self.current_exercise is not None:
                if self.config.backing_tracks_dir:
                    self.manual_mode.enable_bk_track_button(
                        self.config.backing_tracks_dir,
                        self.config.naming_scheme,
                        self.config.file_format,
                    )
                else:
                    self.bk_tracks_button.setEnabled(False)
                    self.good_button.setEnabled(True)
                    self.bad_button.setEnabled(True)
        else:
            raise ValueError("Invalid tab index. This should never happen.")

    def get_exercise_from_manual_mode(self) -> None:
        exercise = self.manual_mode.get_exercise()
        if exercise is not None:
            self.current_exercise = exercise


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


type ButtonClickFn = Callable[[], None]


class NumberOnlyLineEdit(QLineEdit):
    def __init__(
        self,
        first_exercise: int = 1,
        last_exercise: int = MAX_EXERCISES,
        contents: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(contents if contents is not None else "", parent)
        validator = QIntValidator()
        validator.setRange(first_exercise, last_exercise)
        self.setValidator(validator)
        self._good_callback: ButtonClickFn | None = None
        self._bad_callback: ButtonClickFn | None = None

    def set_shortcut_callbacks(
        self,
        good_callback: ButtonClickFn,
        bad_callback: ButtonClickFn,
    ) -> None:
        self._good_callback = good_callback
        self._bad_callback = bad_callback

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:  # noqa: N802
        if a0 is None:
            return
        if a0.key() == Qt.Key.Key_Plus and self._good_callback:
            self._good_callback()
        elif a0.key() == Qt.Key.Key_Minus and self._bad_callback:
            self._bad_callback()
        else:
            super().keyPressEvent(a0)


if __name__ == "__main__":
    main()
