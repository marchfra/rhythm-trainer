from pathlib import Path

import pytest
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from rhythm_trainer import dirs
from rhythm_trainer.config import MAX_EXERCISES, Config
from rhythm_trainer.gui.settings_dialog import SettingsDialog


@pytest.fixture
def dialog(qtbot: QtBot) -> SettingsDialog:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_construction(dialog: SettingsDialog) -> None:
    assert dialog.windowTitle() == "Settings"
    assert dialog.size() == QSize(483, 201)

    assert dialog.csv_file_line.isReadOnly()
    assert dialog.csv_file_line.minimumWidth() == 135

    assert dialog.bk_tracks_line.isReadOnly()
    assert dialog.bk_tracks_line.minimumWidth() == 200

    assert dialog.range_min_spin.value() == 1
    assert dialog.range_max_spin.value() == MAX_EXERCISES


def test_new_csv(
    dialog: SettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QFileDialog, "exec", lambda self: 1)
    csv_path = Path(dirs.user_data_dir) / "file.csv"
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(csv_path)])
    dialog._new_csv()
    assert dialog.csv_file_line.text() == csv_path.name
    assert dialog.csv_file_line.toolTip() == csv_path.as_posix()
    assert dialog.csv_path == csv_path

    non_csv_path = Path(dirs.user_data_dir) / "file"
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(non_csv_path)])
    dialog._new_csv()
    assert dialog.csv_file_line.text() == non_csv_path.name
    assert dialog.csv_file_line.toolTip() == non_csv_path.as_posix()
    assert dialog.csv_path == csv_path


def test_browse_csv(
    dialog: SettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QFileDialog, "exec", lambda self: 1)
    csv_path = Path(dirs.user_data_dir) / "file.csv"
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(csv_path)])
    dialog._browse_csv()
    assert dialog.csv_file_line.text() == csv_path.name
    assert dialog.csv_file_line.toolTip() == csv_path.as_posix()
    assert dialog.csv_path == csv_path

    non_csv_path = Path(dirs.user_data_dir) / "file"
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(non_csv_path)])
    dialog._browse_csv()
    assert dialog.csv_file_line.text() == non_csv_path.name
    assert dialog.csv_file_line.toolTip() == non_csv_path.as_posix()
    assert dialog.csv_path == csv_path


def test_browse_bk_tracks_dir(
    dialog: SettingsDialog,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QFileDialog, "exec", lambda self: 1)
    bk_dir_path = tmp_path / "bk_tracks"
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(bk_dir_path)])
    dialog._browse_bk_tracks_dir()
    assert dialog.bk_tracks_line.text() == bk_dir_path.name
    assert dialog.bk_tracks_line.toolTip() == bk_dir_path.as_posix()
    assert dialog.bk_tracks_dir == bk_dir_path


@pytest.mark.parametrize("value", [1, 13, 17, 21, 42, 90])
def test_set_first_exercise(dialog: SettingsDialog, value: int) -> None:
    dialog.range_min_spin.setValue(value)
    assert dialog.range_max_spin.minimum() == value
    assert dialog.range_max_spin.maximum() == MAX_EXERCISES


@pytest.mark.parametrize("value", [1, 13, 17, 21, 42, 90])
def test_set_last_exercise(dialog: SettingsDialog, value: int) -> None:
    dialog.range_max_spin.setValue(value)
    assert dialog.range_min_spin.minimum() == 1
    assert dialog.range_min_spin.maximum() == value


def test_read_config_with_bk_dir(dialog: SettingsDialog) -> None:
    csv_path = Path(dirs.user_data_dir) / "test.csv"
    bk_tracks_dir = Path(dirs.user_downloads_dir) / "tracks"
    config = Config(
        csv_path=csv_path,
        backing_tracks_dir=bk_tracks_dir,
        first_exercise=13,
        last_exercise=27,
    )
    dialog.read_config(config)

    assert dialog.csv_path == csv_path
    assert dialog.csv_file_line.text() == csv_path.name
    assert dialog.csv_file_line.toolTip() == csv_path.as_posix()

    assert dialog.bk_tracks_dir == bk_tracks_dir
    assert dialog.bk_tracks_line.text() == bk_tracks_dir.name
    assert dialog.bk_tracks_line.toolTip() == bk_tracks_dir.as_posix()

    assert dialog.first_exercise == 13
    assert dialog.last_exercise == 27
    assert dialog.range_min_spin.value() == 13
    assert dialog.range_max_spin.value() == 27


def test_read_config_without_bk_dir(dialog: SettingsDialog) -> None:
    csv_path = Path(dirs.user_data_dir) / "test.csv"
    config = Config(
        csv_path=csv_path,
        first_exercise=13,
        last_exercise=27,
    )
    dialog.read_config(config)

    assert dialog.csv_path == csv_path
    assert dialog.csv_file_line.text() == csv_path.name
    assert dialog.csv_file_line.toolTip() == csv_path.as_posix()

    assert dialog.bk_tracks_line.text() == ""
    assert dialog.bk_tracks_line.toolTip() == ""

    assert dialog.first_exercise == 13
    assert dialog.last_exercise == 27
    assert dialog.range_min_spin.value() == 13
    assert dialog.range_max_spin.value() == 27
