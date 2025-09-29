"""
Main application entry point for Multi-Lingual Content Creation Agent
"""
import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Flask app on http://localhost:{port}")
    print("Available endpoints:")
    print(f"  Root: http://localhost:{port}/")
    print(f"  Health: http://localhost:{port}/health")
    print(f"  Ready: http://localhost:{port}/ready")
    print(f"  API Status: http://localhost:{port}/api/status")
    
    app.run(
        host='127.0.0.1',
        port=port,
        debug=debug
    )