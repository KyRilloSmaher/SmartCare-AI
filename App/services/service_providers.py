# service_providers.py
"""
DI container — the ONLY place that imports concrete service classes.

Routes call get_*_service() and receive the interface type.
Swap implementations here (e.g. for tests) without touching any endpoint.
"""
from functools import lru_cache
from App.services.Chat.ChatService import ChatService
from App.services.Chat.IChatService import IChatService
from App.services.DrugNameExtraction.DrugNameExtractionService import DrugNameExtractionService
from App.services.DrugNameExtraction.IDrugNameExtractionService import IDrugNameExtractionService
from App.services.VoiceSearch.IVoiceSearchService import IVoiceSearchService
from App.services.VoiceSearch.Voice_search_service import VoiceSearchService
from App.services.ContradictionService import IContradictionService
from App.services.SimilarityService import ISimilarityService
from App.services.SemanticSearchService import ISemanticSearchService
from App.services.SimilarityService.drug_similars_service import SimilarityService
from App.services.SemanticSearchService.semantic_search_service import SemanticSearchService
from App.services.ContradictionService.drug_Contradiction_service import ContradictionService

@lru_cache(maxsize=1)
def get_similarity_service() -> ISimilarityService:
    return SimilarityService()

@lru_cache(maxsize=1)
def get_semantic_search_service() -> ISemanticSearchService:
    return SemanticSearchService()

@lru_cache(maxsize=1)
def get_contradiction_service() -> IContradictionService:
    return ContradictionService()

@lru_cache(maxsize=1)
def get_voice_search_service() -> IVoiceSearchService:
    semantic = get_semantic_search_service()
    return VoiceSearchService(semantic)

@lru_cache(maxsize=1)
def get_chat_service() -> IChatService:
    return ChatService()

@lru_cache(maxsize=1)
def get_drug_name_extraction_service() -> IDrugNameExtractionService:
    return DrugNameExtractionService()