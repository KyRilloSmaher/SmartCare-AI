"""
Central models registry for SQLAlchemy and Alembic
"""
from sqlalchemy.ext.declarative import declarative_base

# Create a SINGLE Base for all models
Base = declarative_base()

# Import all models here so alembic can discover them
# This must be done AFTER Base is created
from App.models.vector_sync_state import VectorSyncState

# Optional: Export for easy imports
__all__ = ['Base', 'VectorSyncState']