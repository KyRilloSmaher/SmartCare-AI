"""
Application entry point for SmartCare-AI
"""
import os
from dotenv import load_dotenv

load_dotenv()

from App import create_app
from Jobs.sync_products import start_vector_sync_scheduler

app = create_app()

if __name__ == "__main__":
    # 🔥 START BACKGROUND JOBS ONCE
    # start_vector_sync_scheduler()

    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app.run(host="0.0.0.0", port=port, debug=debug)


