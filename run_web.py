#!/usr/bin/env python3
"""
Flask application runner for the HAR Event Parser web interface.
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the Flask app
from web.app import app

if __name__ == "__main__":
    print("Starting HAR Event Parser Web Interface...")
    print("Visit: http://localhost:5000")
    print("API docs: http://localhost:5000/api/docs")
    print("\nPress Ctrl+C to stop the server")

    app.run(debug=True, host="0.0.0.0", port=5000)
