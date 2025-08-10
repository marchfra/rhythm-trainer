import locale
from collections.abc import Callable

import pytest
from pytestqt.qtbot import QtBot

from rhythm_trainer.gui.main_window import MainWindow

type AppFactory = Callable[[str | None], MainWindow]


@pytest.fixture
def app_factory(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[str | None], MainWindow]:
    def _app(lang: str | None) -> MainWindow:
        monkeypatch.setattr("locale.getlocale", lambda: (lang, "UTF-8"))

        app = MainWindow()
        qtbot.addWidget(app)
        return app

    return _app


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en_US", "Rhythm Trainer"),
        ("it_IT", "Rhythm Trainer"),
        ("fr_FR", "Rhythm Trainer"),
        (None, "Rhythm Trainer"),
    ],
)
def test_window_title(
    app_factory: Callable[[str | None], MainWindow],
    lang: str | None,
    expected: str,
) -> None:
    app = app_factory(lang)
    assert app.windowTitle() == expected


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en_US", "Play backing track"),
        ("it_IT", "Suona backing track"),
        ("fr_FR", "Play backing track"),
        (None, "Play backing track"),
    ],
)
def test_bk_tracks_button(
    app_factory: AppFactory,
    lang: str | None,
    expected: str,
) -> None:
    app = app_factory(lang)
    assert locale.getlocale()[0] == lang
    assert app.bk_tracks_button.text() == expected


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en_US", "Good"),
        ("it_IT", "Bene"),
        ("fr_FR", "Good"),
        (None, "Good"),
    ],
)
def test_good_button(
    app_factory: AppFactory,
    lang: str | None,
    expected: str,
) -> None:
    app = app_factory(lang)
    assert app.good_button.text() == expected


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en_US", "Bad"),
        ("it_IT", "Male"),
        ("fr_FR", "Bad"),
        (None, "Bad"),
    ],
)
def test_bad_button(
    app_factory: AppFactory,
    lang: str | None,
    expected: str,
) -> None:
    app = app_factory(lang)
    assert app.bad_button.text() == expected


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en_US", "Random Exercise"),
        ("it_IT", "Esercizio Casuale"),
        ("fr_FR", "Random Exercise"),
        (None, "Random Exercise"),
    ],
)
def test_random_tab(
    app_factory: AppFactory,
    lang: str | None,
    expected: str,
) -> None:
    app = app_factory(lang)
    assert app.tabs.tabText(0) == expected


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en_US", "Manual Input"),
        ("it_IT", "Input Manuale"),
        ("fr_FR", "Manual Input"),
        (None, "Manual Input"),
    ],
)
def test_manual_tab(
    app_factory: AppFactory,
    lang: str | None,
    expected: str,
) -> None:
    app = app_factory(lang)
    assert app.tabs.tabText(1) == expected
