"""
Flask application factory for Multi-Lingual Content Creation Agent
"""
from flask import Flask
from flask_cors import CORS
from flask.logging import default_handler
import logging
import os


def create_app(config_name=None):
    """Create and configure Flask application instance"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        from config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config.testing import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Configure CORS for frontend communication
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure logging
    if not app.debug and not app.testing:
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(default_handler)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.health import health_bp
    app.register_blueprint(health_bp)
    
    # Add root route
    @app.route('/')
    def index():
        """Root endpoint with service information"""
        return {
            'service': 'Multi-Lingual Content Creation Agent',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'readiness': '/ready', 
                'api_status': '/api/status'
            }
        }
    

    
    return app