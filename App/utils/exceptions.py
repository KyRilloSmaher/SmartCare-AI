"""
Custom exceptions for SmartCare-AI
"""


class SmartCareException(Exception):
    """Base exception for SmartCare-AI"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(SmartCareException):
    """Validation error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class VectorStoreError(SmartCareException):
    """Vector store operation error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ConfigurationError(SmartCareException):
    """Configuration error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
