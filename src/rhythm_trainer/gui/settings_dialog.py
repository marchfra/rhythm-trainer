from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
)

from rhythm_trainer import dirs
from rhythm_trainer.config import MAX_EXERCISES, Config


class SettingsDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(QSize(483, 201))

        layout = QFormLayout(self)
        self._add_csv_section(layout)
        self._add_bk_tracks_section(layout)
        self._add_range_section(layout)
        self._add_buttons_section(layout)

        layout.setVerticalSpacing(15)

    def _add_csv_section(self, layout: QFormLayout) -> None:
        file_layout = QHBoxLayout()
        self.csv_file_line = QLineEdit()
        self.csv_file_line.setReadOnly(True)
        self.csv_file_line.setMinimumWidth(135)
        csv_new_button = QPushButton("New", self)
        csv_new_button.setToolTip("Create new CSV file")
        csv_new_button.clicked.connect(self._new_csv)
        csv_browse_button = QPushButton("Browse", self)
        csv_browse_button.setToolTip("Browse for CSV file")
        csv_browse_button.clicked.connect(self._browse_csv)
        file_layout.addWidget(self.csv_file_line)
        file_layout.addWidget(csv_new_button)
        file_layout.addWidget(csv_browse_button)
        file_layout.setSpacing(8)
        layout.addRow("CSV Path:", file_layout)

    def _add_bk_tracks_section(self, layout: QFormLayout) -> None:
        bk_tracks_layout = QHBoxLayout()
        self.bk_tracks_line = QLineEdit()
        self.bk_tracks_line.setReadOnly(True)
        self.bk_tracks_line.setMinimumWidth(200)
        bk_tracks_browse_button = QPushButton("Browse", self)
        bk_tracks_browse_button.setToolTip("Browse for backing tracks directory")
        bk_tracks_browse_button.clicked.connect(self._browse_bk_tracks_dir)
        bk_tracks_layout.addWidget(self.bk_tracks_line)
        bk_tracks_layout.addWidget(bk_tracks_browse_button)
        layout.addRow("Backing Tracks Directory:", bk_tracks_layout)

    def _add_range_section(self, layout: QFormLayout) -> None:
        range_layout = QHBoxLayout()
        self.range_min_spin = QSpinBox()
        self.range_min_spin.setValue(1)
        self.range_min_spin.setRange(1, MAX_EXERCISES)
        self.range_min_spin.setFixedWidth(50)
        self.range_max_spin = QSpinBox()
        self.range_max_spin.setValue(MAX_EXERCISES)
        self.range_max_spin.setRange(1, MAX_EXERCISES)
        self.range_max_spin.setFixedWidth(50)

        self.range_min_spin.valueChanged.connect(self._set_first_exercise)
        self.range_max_spin.valueChanged.connect(self._set_last_exercise)

        range_layout.addWidget(self.range_min_spin)
        range_layout.addWidget(QLabel("-"))
        range_layout.addWidget(self.range_max_spin)
        layout.addRow("Exercise Range:", range_layout)

    def _add_buttons_section(self, layout: QFormLayout) -> None:
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _new_csv(self) -> None:
        file_dialog = QFileDialog(
            self,
            caption="Create new CSV file",
            directory=dirs.user_data_dir,
            filter="CSV Files (*.csv)",
        )
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setOption(QFileDialog.Option.DontConfirmOverwrite, True)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        if file_dialog.exec():
            file_path = Path(file_dialog.selectedFiles()[0])
            self.csv_file_line.setText(file_path.name)
            self.csv_file_line.setToolTip(file_path.as_posix())
            if file_path.suffix == ".csv":
                self.csv_path = file_path
            else:
                self.csv_path = file_path.with_suffix(".csv")

    def _browse_csv(self) -> None:
        file_dialog = QFileDialog(
            self,
            caption="Select or enter CSV file",
            directory=dirs.user_data_dir,
            filter="CSV Files (*.csv)",
        )
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setOption(QFileDialog.Option.DontConfirmOverwrite, True)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        if file_dialog.exec():
            file_path = Path(file_dialog.selectedFiles()[0])
            self.csv_file_line.setText(file_path.name)
            self.csv_file_line.setToolTip(file_path.as_posix())
            if file_path.suffix == ".csv":
                self.csv_path = file_path
            else:
                self.csv_path = file_path.with_suffix(".csv")

    def _browse_bk_tracks_dir(self) -> None:
        dir_dialog = QFileDialog(
            self,
            caption="Select or enter backing tracks directory",
            directory=dirs.user_downloads_dir,
            filter="Directories",
        )
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dir_dialog.exec():
            self.bk_tracks_dir = Path(dir_dialog.selectedFiles()[0])
            self.bk_tracks_line.setText(self.bk_tracks_dir.name)
            self.bk_tracks_line.setToolTip(self.bk_tracks_dir.as_posix())
            self.bk_tracks_line.setCursorPosition(0)

    def _set_first_exercise(self, value: int) -> None:
        self.range_max_spin.setRange(value, MAX_EXERCISES)
        self.first_exercise = value

    def _set_last_exercise(self, value: int) -> None:
        self.range_min_spin.setRange(1, value)
        self.last_exercise = value

    def read_config(self, config: Config) -> None:
        """Read configuration from the provided Config object."""
        self.csv_path = config.csv_path
        self.csv_file_line.setText(self.csv_path.name)
        self.csv_file_line.setToolTip(self.csv_path.as_posix())

        if config.backing_tracks_dir:
            self.bk_tracks_dir = config.backing_tracks_dir
            self.bk_tracks_line.setText(self.bk_tracks_dir.name)
            self.bk_tracks_line.setToolTip(self.bk_tracks_dir.as_posix())

        self.first_exercise = config.first_exercise
        self.last_exercise = config.last_exercise
        self.range_min_spin.setValue(self.first_exercise)
        self.range_max_spin.setValue(self.last_exercise)
