"""
Feature flags configuration
Centralized feature toggle management using environment variables
"""

import os
from typing import Dict


class FeatureFlags:
    """
    Feature flags manager.

    All features are controlled via environment variables.
    Default value is False unless explicitly enabled.
    """

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    @staticmethod
    def _get_flag(env_key: str, default: str = "false") -> bool:
        """
        Read boolean flag from environment.

        Accepts: true / false (case insensitive)
        """
        return os.getenv(env_key, default).lower() == "true"

    # ---------------------------------------------------------
    # Feature Definitions
    # ---------------------------------------------------------

    SEMANTIC_SEARCH: bool = _get_flag.__func__("FEATURE_SEMANTIC_SEARCH", "true")
    DRUG_INTELLIGENCE: bool = _get_flag.__func__("FEATURE_DRUG_INTELLIGENCE", "true")
    CONTRAINDICATIONS: bool = _get_flag.__func__("FEATURE_CONTRAINDICATIONS", "true")
    VOICE_SEARCH: bool = _get_flag.__func__("FEATURE_VOICE_SEARCH", "true")

    CHAT: bool = _get_flag.__func__("FEATURE_CHAT", "true")
    DRUG_EXTRACTION: bool = _get_flag.__func__("FEATURE_DRUG_EXTRACTION", "true")

    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------

    @classmethod
    def is_enabled(cls, feature: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature name (case-insensitive)

        Returns:
            bool
        """

        feature_map: Dict[str, bool] = {
            "semantic_search": cls.SEMANTIC_SEARCH,
            "drug_intelligence": cls.DRUG_INTELLIGENCE,
            "contraindications": cls.CONTRAINDICATIONS,
            "voice_search": cls.VOICE_SEARCH,
            "chat": cls.CHAT,
            "drug_extraction": cls.DRUG_EXTRACTION,
        }

        return feature_map.get(feature.lower().strip(), False)

    @classmethod
    def get_all(cls) -> Dict[str, bool]:
        """
        Return all feature flags.
        Useful for debugging or admin dashboard.
        """
        return {
            "semantic_search": cls.SEMANTIC_SEARCH,
            "drug_intelligence": cls.DRUG_INTELLIGENCE,
            "contraindications": cls.CONTRAINDICATIONS,
            "voice_search": cls.VOICE_SEARCH,
            "chat": cls.CHAT,
            "drug_extraction": cls.DRUG_EXTRACTION,
        }