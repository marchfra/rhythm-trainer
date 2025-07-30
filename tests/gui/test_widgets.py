import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QKeyEvent
from pytestqt.qtbot import QtBot

from rhythm_trainer.gui.widgets import NumberOnlyLineEdit


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("7", True),
        ("10", True),
        ("90", False),
        ("0", False),
        ("1000", False),
        ("abc", False),
    ],
)
def test_validator_range(qtbot: QtBot, value: str, *, expected: bool) -> None:
    widget = NumberOnlyLineEdit(first_exercise=1, last_exercise=10)
    qtbot.addWidget(widget)
    widget.setText(value)
    if not widget.validator():
        pytest.fail("Validator should not be None.")

    state = widget.validator().validate(widget.text(), 0)[0]  # pyright: ignore[reportOptionalMemberAccess]
    assert (state == QIntValidator.State.Acceptable) == expected


def test_good_callback_invoked(qtbot: QtBot) -> None:
    widget = NumberOnlyLineEdit()
    qtbot.addWidget(widget)
    called = {"good": False, "bad": False}
    widget.set_shortcut_callbacks(
        lambda: called.update(good=True),
        lambda: called.update(bad=True),
    )
    event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Plus,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.keyPressEvent(event)
    assert called["good"]
    assert not called["bad"]


def test_bad_callback_invoked(qtbot: QtBot) -> None:
    widget = NumberOnlyLineEdit()
    qtbot.addWidget(widget)
    called = {"good": False, "bad": False}
    widget.set_shortcut_callbacks(
        lambda: called.update(good=True),
        lambda: called.update(bad=True),
    )
    event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Minus,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.keyPressEvent(event)
    assert not called["good"]
    assert called["bad"]


def test_other_key_calls_super(qtbot: QtBot, monkeypatch: pytest.MonkeyPatch) -> None:
    widget = NumberOnlyLineEdit()
    qtbot.addWidget(widget)
    called = {}

    def fake_super(_self: NumberOnlyLineEdit, _event: QKeyEvent | None) -> None:
        called["super"] = True

    monkeypatch.setattr("PyQt6.QtWidgets.QLineEdit.keyPressEvent", fake_super)
    # Now call the original method via super
    event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_A,
        Qt.KeyboardModifier.NoModifier,
    )
    # Call the real method via the parent class to trigger the monkeypatch
    widget.keyPressEvent(event)
    assert called.get("super")


def test_none_event_does_nothing(qtbot: QtBot) -> None:
    widget = NumberOnlyLineEdit()
    qtbot.addWidget(widget)
    # Should not raise
    widget.keyPressEvent(None)
