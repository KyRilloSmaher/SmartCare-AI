"""create vector_sync_state 

Revision ID: 5d8ec74ac5b4
Revises: 
Create Date: 2026-01-23 17:27:59.904194

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision = '5d8ec74ac5b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Check if table exists first
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'vector_sync_state' not in inspector.get_table_names():
        op.create_table('vector_sync_state',
            sa.Column('id', mssql.UNIQUEIDENTIFIER(), nullable=False),
            sa.Column('entity_name', sa.String(length=255), nullable=False),
            sa.Column('last_synced_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('GETUTCDATE()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('GETUTCDATE()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('entity_name', name='uq_vector_sync_state_entity_name')
        )
        
        op.create_index('ix_vector_sync_state_entity_name', 'vector_sync_state', ['entity_name'], unique=True)
        print(' Created vector_sync_state table')
    else:
        print(' vector_sync_state table already exists')


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'vector_sync_state' in inspector.get_table_names():
        indexes = inspector.get_indexes('vector_sync_state')
        index_names = [idx.get('name') for idx in indexes if idx.get('name')]
        
        if 'ix_vector_sync_state_entity_name' in index_names:
            op.drop_index('ix_vector_sync_state_entity_name', table_name='vector_sync_state')
        
        op.drop_table('vector_sync_state')
        print(' Dropped vector_sync_state table')
