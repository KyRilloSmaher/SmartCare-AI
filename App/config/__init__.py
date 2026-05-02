"""
Configuration module for SmartCare-AI
"""
import os
from typing import Type

from .base import BaseConfig
from .dev import DevConfig
from .prod import ProdConfig
from .test import TestConfig


def get_config() -> Type[BaseConfig]:
    """
    Get configuration class based on ENV variable
    
    Returns:
        Configuration class (DevConfig, ProdConfig, or TestConfig)
    """
    env = os.getenv('ENV', 'development').lower()
    
    if env == 'production':
        return ProdConfig
    if env == 'testing':
        return TestConfig
    return DevConfig
