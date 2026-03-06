"""
Application entry point for SmartCare-AI
"""
import os
from dotenv import load_dotenv

from App.tests.test_semantic_search import TestSemanticSearch
from App.tests.test_similars_drugs import TestSimilarDrugs

load_dotenv()

from App import create_app
from Jobs.sync_products import start_vector_sync_scheduler

app = create_app()

if __name__ == "__main__":
    # 🔥 START BACKGROUND JOBS ONCE
    # start_vector_sync_scheduler()
        # Optional manual tests
    from App.tests.test_similars_drugs import TestSimilarDrugs
    from App.tests.test_semantic_search import TestSemanticSearch

    test_similar = TestSimilarDrugs()
    test_similar.test_find_similar_by_id("00230eb5-aed2-490a-9642-7cba938790c8")

    test_semantic = TestSemanticSearch()
    test_semantic.test_search("Sexual")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "false"

    app.run(host="0.0.0.0", port=port, debug=debug)

