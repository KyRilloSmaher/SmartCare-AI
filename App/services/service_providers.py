# service_providers.py
"""
DI container — the ONLY place that imports concrete service classes.

Routes call get_*_service() and receive the interface type.
Swap implementations here (e.g. for tests) without touching any endpoint.
"""
from functools import lru_cache
from App.services.interfaces import ISemanticSearchService, ISimilarityService, IContradictionService
from App.services.drug_similars_service import SimilarityService
from App.services.semantic_search_service import SemanticSearchService
from App.services.drug_Contradiction_service import ContradictionService

from App.services.interfaces import (
    IContradictionService,
    ISemanticSearchService,
    ISimilarityService,
)
@lru_cache(maxsize=1)
def get_similarity_service() -> ISimilarityService:
    return SimilarityService()

@lru_cache(maxsize=1)
def get_semantic_search_service() -> ISemanticSearchService:
    return SemanticSearchService()

@lru_cache(maxsize=1)
def get_contradiction_service() -> IContradictionService:
    return ContradictionService()