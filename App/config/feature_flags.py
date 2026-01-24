"""
Feature flags configuration
"""
import os
from typing import Dict


class FeatureFlags:
    """Feature flags manager"""
    
    # Feature flags from environment
    SEMANTIC_SEARCH: bool = os.getenv('FEATURE_SEMANTIC_SEARCH', 'true').lower() == 'true'
    DRUG_INTELLIGENCE: bool = os.getenv('FEATURE_DRUG_INTELLIGENCE', 'true').lower() == 'true'
    CONTRAINDICATIONS: bool = os.getenv('FEATURE_CONTRAINDICATIONS', 'true').lower() == 'true'
    
    @classmethod
    def is_enabled(cls, feature: str) -> bool:
        """
        Check if a feature is enabled
        
        Args:
            feature: Feature name (e.g., 'semantic_search')
            
        Returns:
            True if feature is enabled
        """
        feature_map: Dict[str, bool] = {
            'semantic_search': cls.SEMANTIC_SEARCH,
            'drug_intelligence': cls.DRUG_INTELLIGENCE,
            'contraindications': cls.CONTRAINDICATIONS,
        }
        
        return feature_map.get(feature.lower(), False)
    
    @classmethod
    def get_all(cls) -> Dict[str, bool]:
        """Get all feature flags"""
        return {
            'semantic_search': cls.SEMANTIC_SEARCH,
            'drug_intelligence': cls.DRUG_INTELLIGENCE,
            'contraindications': cls.CONTRAINDICATIONS,
        }
