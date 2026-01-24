import re
from App.observability.logger import get_logger

logger = get_logger(__name__)

class Cleaner:
    """
    Cleans raw text for ML processing:
    - Removes HTML, extra spaces, special characters
    - Lowercases text
    """

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        logger.debug(f"Cleaning text: {text[:30]}...")
        # Remove HTML tags
        text = re.sub(r"<.*?>", " ", text)
        # Remove special characters except dots and commas
        text = re.sub(r"[^a-zA-Z0-9\s.,]", " ", text)
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        # Lowercase
        text = text.lower()
        return text
