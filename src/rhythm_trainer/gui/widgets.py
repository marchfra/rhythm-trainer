from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QKeyEvent
from PyQt6.QtWidgets import QLineEdit, QWidget

from rhythm_trainer.main import MAX_EXERCISES

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
