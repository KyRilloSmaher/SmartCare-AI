

"""
Sync products from MSSQL into Vector DB As Background Job
"""

# App/jobs/vector_sync_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from App.services.sync_db_service import SyncService
from App.observability.logger import get_logger
import atexit

logger = get_logger(__name__)

def start_vector_sync_scheduler():
    """
    Starts the background scheduler for product vector sync.
    Runs once immediately, then daily at 2 AM UTC.
    """
    scheduler = BackgroundScheduler(timezone="UTC")

    def sync_job():
        logger.info("🔄 Starting product vector sync job")
        try:
            service = SyncService()
            stats = service.sync_products()
            logger.info("✅ Product vector sync completed", extra=stats)
        except Exception as e:
            logger.exception(f"❌ Vector sync job failed: {e}")

    # Run once immediately
    logger.info("⏱ Running initial sync on startup...")
    sync_job()

    # Schedule daily at 2:00 AM UTC
    scheduler.add_job(sync_job, 'cron', hour=2, minute=0, id='daily_vector_sync')
    scheduler.start()
    logger.info("📅 Vector sync scheduler started")

    # Graceful shutdown
    atexit.register(lambda: scheduler.shutdown())
