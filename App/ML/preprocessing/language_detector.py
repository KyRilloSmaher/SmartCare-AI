from langdetect import detect, DetectorFactory
from App.observability.logger import get_logger

DetectorFactory.seed = 0  # For reproducible results
logger = get_logger(__name__)

class LanguageDetector:
    """
    Detects the language of a text string.
    """

    def detect_language(self, text: str) -> str:
        if not text:
            return "unknown"
        try:
            lang = detect(text)
            logger.debug(f"Detected language: {lang}")
            return lang
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "unknown"
