"""
Alembic environment file for SmartCare-AI
Handles migrations for MSSQL and app models
"""
import sys
import os
from logging.config import fileConfig
from dotenv import load_dotenv  # Add this import

from sqlalchemy import engine_from_config, pool
from alembic import context

# Load environment variables FIRST
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Make App package importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your BaseConfig and models
from App.config.base import BaseConfig
from App.models.vector_sync_state import Base  # your model Base

# this is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Setup Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata for 'autogenerate' support
target_metadata = Base.metadata


def get_url():
    """Return the database URL from BaseConfig"""
    # Try to get directly from environment first
    url = os.getenv("MSSQL_CONNECTION_STRING")
    if not url:
        # Fall back to BaseConfig
        url = BaseConfig.MSSQL_CONNECTION_STRING
    if not url:
        raise ValueError("MSSQL_CONNECTION_STRING is not set in environment or BaseConfig")
    return url


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Add this function BEFORE the run_migrations_online() function
def include_object(object, name, type_, reflected, compare_to):
    """
    Exclude existing tables from alembic comparison.
    Only include new tables we define in our models.
    """
    # If it's a reflected table (already in database) and not in our models
    if type_ == "table" and reflected and name != "vector_sync_state":
        return False
    return True

# Then update the run_migrations_online() function:
def run_migrations_online():
    configuration = config.get_section(config.config_ini_section, {})
    configuration['sqlalchemy.url'] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,  # Add this line
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()