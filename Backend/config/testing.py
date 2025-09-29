"""
Testing configuration for Multi-Lingual Content Creation Agent
"""
import os
from config.base import BaseConfig


class TestingConfig(BaseConfig):
    """Testing configuration"""
    
    DEBUG = False
    TESTING = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False
    
    # Testing-specific settings
    FLASK_ENV = 'testing'
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        
        # Testing-specific initialization
        import logging
        logging.disable(logging.CRITICAL)