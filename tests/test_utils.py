from pathlib import Path

import pytest

from rhythm_trainer.config import FileFormat, NamingScheme
from rhythm_trainer.utils import (
    get_number_input,
    get_valid_input,
    infer_file_format,
    infer_naming_scheme,
)


@pytest.mark.parametrize(
    ("valid_input", "expected_inputs"),
    [
        ("yes", ["yes", "no"]),
        ("no", ["yes", "no"]),
        ("42", ["42", "57", "12", "91"]),
    ],
)
def test_get_valid_input_valid(
    monkeypatch: pytest.MonkeyPatch,
    valid_input: str,
    expected_inputs: list[str],
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: valid_input)
    assert get_valid_input("Prompt: ", expected_inputs) == valid_input


def test_get_valid_input_invalid_then_valid(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    responses = iter(["maybe", "no"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = get_valid_input("Prompt: ", ["yes", "no"])
    assert result == "no"
    captured = capsys.readouterr()
    assert "Invalid input" in captured.out
    assert "yes, no" in captured.out


@pytest.mark.parametrize("valid_inputs", [42, 57, 12, 91])
def test_get_number_input_valid(
    monkeypatch: pytest.MonkeyPatch,
    valid_inputs: int,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: str(valid_inputs))
    assert get_number_input("Enter a number: ") == valid_inputs


def test_get_number_input_invalid_then_valid(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    responses = iter(["foo", "10"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = get_number_input("Enter a number: ")
    assert result == 10
    captured = capsys.readouterr()
    assert "Invalid input." in captured.out


def test_get_number_input_below_min(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    responses = iter(["2", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = get_number_input("Enter a number: ", min_value=5)
    assert result == 5
    captured = capsys.readouterr()
    assert "greater than or equal to 5" in captured.out


def test_get_number_input_above_max(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    responses = iter(["100", "7"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = get_number_input("Enter a number: ", max_value=7)
    assert result == 7
    captured = capsys.readouterr()
    assert "less than or equal to 7" in captured.out


def test_get_number_input_between_min_max(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    responses = iter(["1", "15", "8"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = get_number_input("Enter a number: ", min_value=5, max_value=10)
    assert result == 8
    captured = capsys.readouterr()
    assert "between 5 and 10" in captured.out


@pytest.mark.parametrize(
    ("file_extension", "expected_format"),
    [
        (".mp3", FileFormat.MP3),
        (".wav", FileFormat.WAV),
    ],
)
def test_infer_file_format(
    tmp_path: Path,
    file_extension: str,
    expected_format: FileFormat,
) -> None:
    acoustic_dir = tmp_path / "Acoustic"
    acoustic_dir.mkdir()
    (acoustic_dir / f"track{file_extension}").touch()

    assert infer_file_format(tmp_path) == expected_format


def test_infer_file_format_no_acoustic_dir(tmp_path: Path) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="does not contain an 'Acoustic' subdirectory",
    ):
        infer_file_format(tmp_path)


def test_infer_file_format_empty_acoustic_dir(tmp_path: Path) -> None:
    acoustic_dir = tmp_path / "Acoustic"
    acoustic_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="with a recognizable file format."):
        infer_file_format(tmp_path)


@pytest.mark.parametrize(
    "file_extension",
    [".txt", ".flac", ".ogg"],
)
def test_infer_file_format_invalid_extension(
    tmp_path: Path,
    file_extension: str,
) -> None:
    acoustic_dir = tmp_path / "Acoustic"
    acoustic_dir.mkdir()
    (acoustic_dir / f"track{file_extension}").touch()

    with pytest.raises(ValueError, match=f"Unsupported file format: {file_extension}"):
        infer_file_format(tmp_path)


@pytest.mark.parametrize(
    ("file_name", "expected_scheme"),
    [
        ("BK track.mp3", NamingScheme.LOGICAL),
        ("track BK.mp3", NamingScheme.DEFAULT),
    ],
)
def test_infer_naming_scheme(
    tmp_path: Path,
    file_name: str,
    expected_scheme: NamingScheme,
) -> None:
    acoustic_dir = tmp_path / "Acoustic"
    acoustic_dir.mkdir()
    (acoustic_dir / file_name).touch()

    assert infer_naming_scheme(tmp_path) == expected_scheme


def test_infer_naming_scheme_no_acoustic_dir(tmp_path: Path) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="does not contain an 'Acoustic' subdirectory",
    ):
        infer_naming_scheme(tmp_path)


def test_infer_naming_scheme_empty_acoustic_dir(tmp_path: Path) -> None:
    acoustic_dir = tmp_path / "Acoustic"
    acoustic_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="with a recognizable name."):
        infer_naming_scheme(tmp_path)
