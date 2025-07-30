from pathlib import Path

import pytest

from rhythm_trainer import tracks
from rhythm_trainer.config import FileFormat, NamingScheme


def make_chapter_dir(
    tmp_path: Path,
    subdir: str,
    exercise: int,
    naming: NamingScheme,
    file_format: FileFormat,
) -> tuple[Path, Path]:
    chapter = tmp_path / subdir
    chapter.mkdir(parents=True)
    if naming == NamingScheme.LOGICAL:
        fname = f"BK {subdir} {exercise:02d}.{file_format.value}"
    else:
        fname = f"{subdir} {exercise} BK.{file_format.value}"
    track = chapter / fname
    track.touch()
    return chapter, track


def test_validate_backing_track_exists_default(tmp_path: Path) -> None:
    subdirs = [
        "Acoustic",
        "Classic Blues",
        "Classic Rock",
        "Funk",
        "Fusion",
        "Hard Rock & Heavy Metal",
        "Jazz",
        "Pop",
        "Soul",
    ]
    exercise = 1
    _, track = make_chapter_dir(
        tmp_path,
        subdirs[0],
        exercise,
        NamingScheme.DEFAULT,
        FileFormat.WAV,
    )
    result = tracks.validate_backing_track(
        exercise,
        tmp_path,
        NamingScheme.DEFAULT,
        FileFormat.WAV,
    )
    assert result == track


def test_validate_backing_track_exists_logical(tmp_path: Path) -> None:
    subdirs = [
        "Acoustic",
        "Classic Blues",
        "Classic Rock",
        "Funk",
        "Fusion",
        "Hard Rock & Heavy Metal",
        "Jazz",
        "Pop",
        "Soul",
    ]
    exercise = 11  # Should be in "Classic Blues"
    _, track = make_chapter_dir(
        tmp_path,
        subdirs[1],
        exercise,
        NamingScheme.LOGICAL,
        FileFormat.MP3,
    )
    result = tracks.validate_backing_track(
        exercise,
        tmp_path,
        NamingScheme.LOGICAL,
        FileFormat.MP3,
    )
    assert result == track


def test_validate_backing_track_not_exists(tmp_path: Path) -> None:
    exercise = 1
    # Create chapter dir but no file
    subdir = "Acoustic"
    chapter = tmp_path / subdir
    chapter.mkdir()
    assert not any(chapter.iterdir())  # Ensure it's empty
    result = tracks.validate_backing_track(
        exercise,
        tmp_path,
        NamingScheme.DEFAULT,
        FileFormat.WAV,
    )
    assert result is None


def test_validate_backing_track_no_chapter_dir(tmp_path: Path) -> None:
    exercise = 1
    # No chapter dir at all
    assert not any(tmp_path.iterdir())  # Ensure tmp_path is empty
    result = tracks.validate_backing_track(
        exercise,
        tmp_path,
        NamingScheme.DEFAULT,
        FileFormat.WAV,
    )
    assert result is None


def test_validate_backing_track_unsupported_naming(tmp_path: Path) -> None:
    exercise = 1
    subdir = "Acoustic"
    chapter = tmp_path / subdir
    chapter.mkdir()

    class FakeNaming:
        pass

    with pytest.raises(ValueError, match="Unsupported naming convention"):
        tracks.validate_backing_track(
            exercise,
            tmp_path,
            FakeNaming(),  # pyright: ignore[reportArgumentType]
            FileFormat.WAV,
        )


def test_play_backing_track_invalid_track(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "rhythm_trainer.tracks.validate_backing_track",
        lambda *_, **__: None,
    )

    with pytest.raises(FileNotFoundError, match="not found in directory"):
        tracks.play_backing_track(1, Path(), NamingScheme.DEFAULT, FileFormat.WAV)


def test_play_backing_track_valid_track(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "rhythm_trainer.tracks.validate_backing_track",
        lambda *_, **__: tmp_path / "valid_track.wav",
    )
    called = {}

    def mock_popen(args: list[str], stdout: int | None) -> None:
        called["args"] = args
        called["stdout"] = stdout

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    tracks.play_backing_track(1, tmp_path, NamingScheme.DEFAULT, FileFormat.WAV)
