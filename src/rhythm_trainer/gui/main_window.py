from collections.abc import Callable
from functools import partial
from pathlib import Path

from PyQt6.QtCore import QObject, QSize, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rhythm_trainer.config import Config, parse_config, save_config
from rhythm_trainer.exercises import (
    get_exercises_and_weights,
    save_exercises_and_weights,
)
from rhythm_trainer.gui.settings_dialog import SettingsDialog
from rhythm_trainer.tracks import play_backing_track
from rhythm_trainer.utils import infer_file_format, infer_naming_scheme

from .modes import BaseModeWidget, ManualModeWidget, RandomModeWidget

TEST_MODE = True

# --- UI Constants ---
WINDOW_TITLE = "Rhythm Trainer"
WINDOW_SIZE = (350, 425)
MARGIN = 30
BK_BUTTON_TEXT = "Play backing track"
BK_BUTTON_SIZE = (250, 50)
TAB_RANDOM = "Random Exercise"
TAB_MANUAL = "Manual Input"
FEEDBACK_LABEL = "How did it go?"
GOOD_BUTTON_TEXT = "Good"
BAD_BUTTON_TEXT = "Bad"
FEEDBACK_BUTTON_SIZE = 100, 50
STYLE_FILE = "style.qss"
SHORTCUT_TAB1 = "Ctrl+1"
SHORTCUT_TAB2 = "Ctrl+2"


class MainWindow(QMainWindow):
    # --- Initialization ---

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(QSize(*WINDOW_SIZE))

        self._load_config_and_exercises()
        self._setup_ui()
        self._setup_shortcuts()
        self._buffer: list[int] = []
        self.next_exercise()

    def _load_config_and_exercises(self) -> None:
        """Load the application configuration and exercises."""
        self.config = parse_config()
        if self.config.backing_tracks_dir:
            file_format = infer_file_format(self.config.backing_tracks_dir)
            naming_scheme = infer_naming_scheme(self.config.backing_tracks_dir)

            self.config.file_format = file_format
            self.config.naming_scheme = naming_scheme

            save_config(self.config)

        self.exercises, self.weights = get_exercises_and_weights(
            self.config.csv_path,
            self.config.first_exercise,
            self.config.last_exercise,
        )

    def _setup_ui(self) -> None:
        """Initialize and arrange the main window's user interface components.

        This method sets up the central widget and its layout, applies margins,
        adds the backing tracks button, modes tab, and feedback section to the layout.
        It also configures shortcut callbacks for the manual mode exercise input,
        linking them to the good and bad buttons.
        """
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.setCentralWidget(central_widget)

        cog_button = QPushButton("⚙️")
        cog_button.setObjectName("cog_button")
        # cog_button.setIcon(QIcon.fromTheme("preferences-system"))
        cog_button.setFixedSize(QSize(32, 32))
        cog_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        cog_button.clicked.connect(self._settings)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(cog_button)
        layout.addLayout(top_layout)

        bk_tracks_button_layout = self._add_bk_tracks_button()
        self._add_modes_tab(layout, self.bk_tracks_button)
        layout.addLayout(bk_tracks_button_layout)
        self._add_feedback_section(layout)

        self.manual_mode.exercise_input.set_shortcut_callbacks(
            self.good_button.click,
            self.bad_button.click,
        )

    def _add_bk_tracks_button(self) -> QHBoxLayout:
        """Create and return a horizontal layout containing the backing tracks button.

        The button is configured with a fixed size, no focus policy, and is connected to
        the `play_backing_track` slot when clicked. The button is added to a
        QHBoxLayout, which is returned.

        Returns:
            QHBoxLayout: The layout containing the configured backing tracks button.

        """
        bk_tracks_button_layout = QHBoxLayout()

        self.bk_tracks_button = QPushButton(BK_BUTTON_TEXT)
        self.bk_tracks_button.setObjectName("bk_tracks_button")
        self.bk_tracks_button.setFixedSize(QSize(*BK_BUTTON_SIZE))
        self.bk_tracks_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bk_tracks_button.clicked.connect(self.play_backing_track)
        bk_tracks_button_layout.addWidget(self.bk_tracks_button)

        return bk_tracks_button_layout

    def _add_modes_tab(self, layout: QLayout, bk_tracks_button: QPushButton) -> None:
        """Add the modes tab widget to the layout, initializing random and manual modes.

        This method creates a QTabWidget containing two tabs: one for random mode and
        one for manual mode. It sets up the necessary connections for the manual mode's
        exercise input to update the exercise and background tracks button state. The
        tabs are then added to the provided layout.

        Args:
            layout : QLayout
                The layout to which the tab widget will be added.
            bk_tracks_button : QPushButton
                The button used for background tracks, passed to the mode widgets.

        """
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
            self._get_exercise_from_manual_mode,
        )
        self.manual_mode.exercise_input.textChanged.connect(
            self._update_manual_mode_bk_button,
        )

        self.tabs.addTab(self.random_mode, TAB_RANDOM)
        self.tabs.addTab(self.manual_mode, TAB_MANUAL)

        layout.addWidget(self.tabs)

    def _add_feedback_section(self, layout: QVBoxLayout) -> None:
        """Add the feedback section to the given layout.

        The feedback section includes a centered label and two feedback buttons ("Good"
        and "Bad"). The buttons are connected to their respective feedback handlers.

        Args:
            layout : QVBoxLayout
                The layout to which the feedback section is added.

        """
        feedback_label = QLabel(FEEDBACK_LABEL)
        feedback_label.setObjectName("feedback_label")
        feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feedback_label.setFixedHeight(50)
        layout.addWidget(feedback_label)

        feedback_buttons_layout = QHBoxLayout()
        self.good_button = QPushButton(GOOD_BUTTON_TEXT)
        self.good_button.setFocus()
        self.good_button.setObjectName("good_button")
        self.good_button.setMinimumSize(QSize(*FEEDBACK_BUTTON_SIZE))
        self.good_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.good_button.clicked.connect(self.good_feedback)
        feedback_buttons_layout.addWidget(self.good_button)

        self.bad_button = QPushButton(BAD_BUTTON_TEXT)
        self.bad_button.setObjectName("bad_button")
        self.bad_button.setMinimumSize(QSize(*FEEDBACK_BUTTON_SIZE))
        self.bad_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bad_button.clicked.connect(self.bad_feedback)
        feedback_buttons_layout.addWidget(self.bad_button)

        layout.addLayout(feedback_buttons_layout)

    # --- Shortcuts ---

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts for main window actions."""
        make_shortcut = partial(self._make_shortcut, parent=self)

        self.play_shortcut = make_shortcut(
            QKeySequence(Qt.Key.Key_Return),
            self.bk_tracks_button.click,
        )
        self.play_shortcut_alt = make_shortcut(
            QKeySequence(Qt.Key.Key_Enter),
            self.bk_tracks_button.click,
        )

        self.good_shortcut = make_shortcut(
            QKeySequence(Qt.Key.Key_Plus),
            self.good_button.click,
        )
        self.bad_shortcut = make_shortcut(
            QKeySequence(Qt.Key.Key_Minus),
            self.bad_button.click,
        )

        self.tab_shortcut_1 = make_shortcut(
            QKeySequence(SHORTCUT_TAB1),
            self._activate_tab_1,
        )

        self.tab_shortcut_ctrl_2 = make_shortcut(
            QKeySequence(SHORTCUT_TAB2),
            self._activate_tab_2,
        )

    def _make_shortcut(
        self,
        keyseq: QKeySequence,
        slot: Callable[[], None],
        parent: QObject,
        context: Qt.ShortcutContext = Qt.ShortcutContext.ApplicationShortcut,
    ) -> QShortcut:
        """Create and return a QShortcut.

        Args:
            keyseq : QKeySequence
                The key sequence for the shortcut.
            slot : Callable[[], None]
                The function to call when the shortcut is activated.
            parent : QObject
                The parent object for the shortcut.
            context : Qt.ShortcutContext, optional
                The shortcut context. Defaults to
                Qt.ShortcutContext.ApplicationShortcut.

        Returns:
            QShortcut: The created shortcut object.

        """
        shortcut = QShortcut(keyseq, parent)
        shortcut.setContext(context)
        shortcut.activated.connect(slot)
        return shortcut

    def _activate_tab_1(self) -> None:
        """Activate the first tab (random mode)."""
        self.tabs.setCurrentIndex(0)
        self.manual_mode.exercise_input.setText("")
        if self.config.backing_tracks_dir:
            self.random_mode.enable_bk_track_button(
                self.config.backing_tracks_dir,
                self.config.naming_scheme,
                self.config.file_format,
            )
        else:
            self.bk_tracks_button.setEnabled(False)

    def _activate_tab_2(self) -> None:
        """Activate the second tab (manual mode)."""
        self.tabs.setCurrentIndex(1)
        self.manual_mode.exercise_input.setFocus()
        if self.config.backing_tracks_dir:
            self.manual_mode.enable_bk_track_button(
                self.config.backing_tracks_dir,
                self.config.naming_scheme,
                self.config.file_format,
            )
        else:
            self.bk_tracks_button.setEnabled(False)

    # --- Core Logic ---
    # ! app doesn't behave properly with non-standard exercise range
    # TODO: app doesn't behave properly with non-standard exercise range

    def play_backing_track(self) -> None:
        """Play the backing track for the current exercise, if available.

        This method also disables the backing tracks button during playback and enables
        the 'good' and 'bad' buttons afterwards. Does nothing if TEST_MODE is active or
        no exercise is selected.
        """
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
        """Handle positive feedback for the current exercise.

        Decreases the weight of the current exercise if possible, saves the updated
        weights and exercises to the CSV file, and advances to the next exercise.
        """
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
        """Handle negative feedback for the current exercise.

        Increments the weight for the current exercise, saves the updated exercises and
        weights to the CSV file, and advances to the next exercise.
        """
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
        """Reset the main window interface to get ready for a new exercise."""
        self.good_button.setEnabled(False)
        self.bad_button.setEnabled(False)
        self.bk_tracks_button.setEnabled(False)

        self.manual_mode.exercise_input.setText("")

    def next_exercise(self) -> None:
        """Advance to the next exercise based on the selected tab."""
        self.reset_interface()

        if self.tabs.currentIndex() == 0:
            self.current_exercise = self.random_mode.pick_exercise(
                self.exercises,
                self.weights,
                self._buffer,
            )
            self._enable_buttons(self.random_mode)
        elif self.tabs.currentIndex() == 1:
            self.current_exercise = self.manual_mode.get_exercise()
            if self.current_exercise is not None:
                self._enable_buttons(self.manual_mode)
        else:
            raise ValueError("Invalid tab index. This should never happen.")

    def _settings(self) -> None:
        settings = SettingsDialog()
        settings.read_config(self.config)
        if settings.exec() == QDialog.DialogCode.Accepted:
            config = Config(
                csv_path=Path(settings.csv_path),
                first_exercise=settings.first_exercise,
                last_exercise=settings.last_exercise,
                backing_tracks_dir=Path(settings.bk_tracks_dir)
                if settings.bk_tracks_dir
                else None,
            )
            save_config(config)
            self._load_config_and_exercises()
            self.next_exercise()

    def _enable_buttons(self, mode_widget: BaseModeWidget) -> None:
        """Enable or disable buttons in the mode widget.

        If a backing tracks directory is set, enables the backing track button with the
        current configuration. Otherwise, disables the backing track button and enables
        the good and bad buttons.

        Args:
            mode_widget : BaseModeWidget
                The mode widget whose buttons are to be enabled or disabled.

        """
        if self.config.backing_tracks_dir:
            mode_widget.enable_bk_track_button(
                self.config.backing_tracks_dir,
                self.config.naming_scheme,
                self.config.file_format,
            )
        else:
            self.bk_tracks_button.setEnabled(False)
            self.good_button.setEnabled(True)
            self.bad_button.setEnabled(True)

    def _get_exercise_from_manual_mode(self) -> None:
        """Retrieve the exercise from the manual mode input field."""
        exercise = self.manual_mode.get_exercise()
        if exercise is not None:
            self.current_exercise = exercise

    def _update_manual_mode_bk_button(self) -> None:
        """Update the backing track button state in manual mode based on input."""
        if self.config.backing_tracks_dir:
            self.manual_mode.enable_bk_track_button(
                self.config.backing_tracks_dir,
                self.config.naming_scheme,
                self.config.file_format,
            )
        else:
            self.bk_tracks_button.setEnabled(False)
