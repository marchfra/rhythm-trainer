import subprocess
from pathlib import Path

from rhythm_trainer.config import FileFormat, NamingScheme
from rhythm_trainer.logger import get_logger

logger = get_logger(__name__)


def validate_backing_track(
    exercise: int,
    backing_tracks_dir: Path,
    naming_convention: NamingScheme = NamingScheme.DEFAULT,
    file_format: FileFormat = FileFormat.WAV,
) -> Path | None:
    """Check if the backing track for a given exercise exists.

    Returns the backing track's Path if it exists, None otherwise.
    """
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

    chapter_folder = backing_tracks_dir / subdirs[(exercise - 1) // 10]
    if not chapter_folder.is_dir():
        return None

    if naming_convention == NamingScheme.LOGICAL:
        track_path = (
            chapter_folder
            / f"BK {chapter_folder.name} {exercise:02d}.{file_format.value}"
        )
    elif naming_convention == NamingScheme.DEFAULT:
        track_path = (
            chapter_folder / f"{chapter_folder.name} {exercise} BK.{file_format.value}"
        )
    else:
        raise ValueError(
            f"Unsupported naming convention: {naming_convention}. "
            f"Use one of {[f'NamingConvention.{e.name}' for e in NamingScheme]}",
        )

    return track_path if track_path.is_file() else None


def play_backing_track(
    exercise: int,
    backing_tracks_dir: Path,
    naming_convention: NamingScheme = NamingScheme.DEFAULT,
    file_format: FileFormat = FileFormat.WAV,
) -> None:
    """Play the backing track for a given exercise.

    This function locates the backing track file based on the exercise number,
    backing tracks directory, naming convention, and file type. If the file is found,
    it opens the track using the system's default application, otherwise it raises a
    FileNotFoundError.
    """
    track_path = validate_backing_track(
        exercise,
        backing_tracks_dir,
        naming_convention,
        file_format,
    )

    if track_path is None:
        error_message = (
            f"Backing track for exercise {exercise} not found in directory "
            f"{backing_tracks_dir}. Please check your configuration."
        )
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    logger.info(f"Playing backing track '{track_path.name}'")
    subprocess.Popen(  # noqa: S603
        ["/usr/bin/open", str(track_path)],
        stdout=subprocess.DEVNULL,
    )
