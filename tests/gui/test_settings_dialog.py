from pathlib import Path

import pytest
from PyQt6.QtCore import QSize
from pytestqt.qtbot import QtBot

from rhythm_trainer.config import Config
from rhythm_trainer.gui.settings_dialog import SettingsDialog


@pytest.fixture
def dialog(qtbot: QtBot) -> SettingsDialog:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    return dialog


@pytest.fixture
def config(tmp_path: Path) -> Config:
    csv_path = tmp_path / "test.csv"
    config = Config(csv_path=csv_path, backing_tracks_dir=tmp_path / "tracks")
    return config


def test_dialog_construction(dialog: SettingsDialog) -> None:
    assert dialog.windowTitle() == "Settings"
    assert dialog.size() == QSize(483, 201)

    assert dialog.csv_file_line.isReadOnly()
    assert dialog.csv_file_line.minimumWidth() == 135

    assert dialog.bk_tracks_line.isReadOnly()
    assert dialog.bk_tracks_line.minimumWidth() == 200

    assert dialog.range_min_spin.value() == 1
    assert dialog.range_max_spin.value() == 90
