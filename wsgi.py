

"""
SmartCare-AI entry point (Gunicorn target)
"""

from App import create_app

app = create_app()

application = app   
