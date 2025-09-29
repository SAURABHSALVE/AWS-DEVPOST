"""
Development configuration for Multi-Lingual Content Creation Agent
"""
import os
from config.base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dev_content_agent.db'
    SQLALCHEMY_ECHO = True
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific settings
    FLASK_ENV = 'development'
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        
        # Development-specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)