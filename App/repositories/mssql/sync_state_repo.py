# App/repositories/mssql/sync_state_repo.py
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from App.repositories.mssql.connection import get_session  # SQLAlchemy session factory
from App.models.vector_sync_state import VectorSyncState  # <-- ORM model
from App.observability.logger import get_logger

logger = get_logger(__name__)


class VectorSyncStateRepository:
    """Repository for handling VectorSyncState table in MSSQL"""

    def __init__(self):
        self.session: Session = get_session()

    def get_last_sync(self, entity_name: str) -> Optional[datetime]:
        """Get the last sync timestamp for a given entity"""
        try:
            state: Optional[VectorSyncState] = (
                self.session.query(VectorSyncState)
                .filter(VectorSyncState.entity_name == entity_name)
                .first()
            )
            if state:
                return state.last_synced_at
            return None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get last sync for '{entity_name}': {e}", exc_info=True)
            return None

    def update_last_sync(self, entity_name: str, synced_at: datetime):
        """Update the last sync timestamp (or insert if it doesn't exist)"""
        try:
            state: Optional[VectorSyncState] = (
                self.session.query(VectorSyncState)
                .filter(VectorSyncState.entity_name == entity_name)
                .first()
            )

            if state:
                state.last_synced_at = synced_at
                logger.info(f"Updated last sync for '{entity_name}' to {synced_at}")
            else:
                state = VectorSyncState(
                    entity_name=entity_name,
                    last_synced_at=synced_at
                )
                self.session.add(state)
                logger.info(f"Inserted new sync state for '{entity_name}' with {synced_at}")

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update last sync for '{entity_name}': {e}", exc_info=True)

    def insert_new(self, entity_name: str):
        """Insert a new entity record if not exists"""
        try:
            state_exists = (
                self.session.query(VectorSyncState)
                .filter(VectorSyncState.entity_name == entity_name)
                .first()
            )
            if not state_exists:
                new_state = VectorSyncState(entity_name=entity_name)
                self.session.add(new_state)
                self.session.commit()
                logger.info(f"Created new VectorSyncState record for '{entity_name}'")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to insert new sync state for '{entity_name}': {e}", exc_info=True)
