from pathlib import Path

from PyQt6.QtWidgets import QApplication

from rhythm_trainer.gui.main_window import STYLE_FILE, MainWindow


def main() -> None:
    app = QApplication([])

    style_file_path = Path(__file__).parent / "gui" / STYLE_FILE
    with style_file_path.open("r") as style_file:
        _style = style_file.read()
        app.setStyleSheet(_style)

    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
