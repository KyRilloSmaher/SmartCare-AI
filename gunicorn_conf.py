from Jobs.sync_products import start_vector_sync_scheduler

def on_starting(server):
    """
    Runs ONCE in master process
    """
    start_vector_sync_scheduler()