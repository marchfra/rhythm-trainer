from pathlib import Path

from rhythm_trainer.config import FileFormat, NamingScheme
from rhythm_trainer.logger import get_logger

logger = get_logger(__name__)


def get_valid_input(prompt: str, valid_responses: list[str]) -> str:
    """Validate user input against a list of valid responses."""
    while True:
        response = input(prompt).strip().lower()
        if response in valid_responses:
            return response
        print(
            "Invalid input. Please enter one of the following: "
            f"{', '.join(valid_responses)}.",
        )


def get_number_input(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Prompt the user for a number input."""
    while True:
        response = input(prompt).strip()
        if response.isdigit():
            response = int(response)
            if (min_value is None or response >= min_value) and (
                max_value is None or response <= max_value
            ):
                return response
        print("Invalid input.", end=" ")
        if min_value is not None and max_value is not None:
            print(f"Please enter a number between {min_value} and {max_value}.")
        elif min_value is not None:
            print(f"Please enter a number greater than or equal to {min_value}.")
        elif max_value is not None:
            print(f"Please enter a number less than or equal to {max_value}.")
        else:
            print("Please enter a valid number.")


def infer_file_format(bk_tracks_dir: Path) -> FileFormat:
    """Infer the file format from the file extension."""
    acoustic_dir = bk_tracks_dir / "Acoustic"
    if not acoustic_dir.is_dir():
        error_message = (
            f"Backing tracks directory {bk_tracks_dir} does not contain an 'Acoustic' "
            f"subdirectory.",
        )
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    for file in acoustic_dir.iterdir():
        if file.is_file():
            if file.suffix.lower() == ".mp3":
                return FileFormat.MP3
            if file.suffix.lower() == ".wav":
                return FileFormat.WAV

            error_message = (
                f"Unsupported file format: {file.suffix}. "
                f"Supported formats are {[f'.{e.value}' for e in FileFormat]}",
            )
            logger.error(error_message)
            raise ValueError(error_message)

    error_message = (
        f"No backing tracks found in {bk_tracks_dir} with a recognizable file format.",
    )
    logger.error(error_message)
    raise FileNotFoundError(error_message)


def infer_naming_scheme(bk_tracks_dir: Path) -> NamingScheme:
    """Infer the naming scheme from the file name.

    Default:
        - {chapter} {exercise} BK.{file_format}
    Logical:
        - BK {chapter} {exercise:02d}.{file_format}
    """
    acoustic_dir = bk_tracks_dir / "Acoustic"
    if not acoustic_dir.is_dir():
        raise FileNotFoundError(
            f"Backing tracks directory {bk_tracks_dir} does not contain an 'Acoustic' "
            f"subdirectory.",
        )

    for file in acoustic_dir.iterdir():
        if "BK" in file.name:
            if file.name.startswith("BK "):
                return NamingScheme.LOGICAL
            if " BK." in file.name:
                return NamingScheme.DEFAULT

    raise FileNotFoundError(
        f"No backing tracks found in {bk_tracks_dir} with a recognizable name.",
    )
