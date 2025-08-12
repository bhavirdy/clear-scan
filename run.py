#!/usr/bin/env python3
"""
ClearScan - AI-driven diagnostic platform for chest X-ray analysis
Entry point for the Flask application
"""

from app import app

if __name__ == '__main__':
    # Configure application for development
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5050
    )