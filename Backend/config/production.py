"""
Production configuration for Multi-Lingual Content Creation Agent
"""
import os
from config.base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/content_agent_prod'
    SQLALCHEMY_ECHO = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # Production-specific settings
    FLASK_ENV = 'production'
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # File logging
            file_handler = RotatingFileHandler(
                'logs/content_agent.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Multi-Lingual Content Agent startup')