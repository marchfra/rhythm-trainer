import gettext
import locale
from pathlib import Path

from rhythm_trainer import APP_NAME
from rhythm_trainer.logger import get_logger

logger = get_logger(__name__)


def _(text: str) -> str:
    """Translate the given text using the current locale."""
    lang = locale.getlocale()[0]
    if lang is None:
        lang = "en_US"  # Default to English if no locale is set

    logger.debug(f"Setting locale to {lang}")
    locale_dir = Path(__file__).parent / "locale"

    translate = gettext.translation(
        APP_NAME,
        locale_dir,
        languages=[lang],
        fallback=True,
    )
    return translate.gettext(text)
