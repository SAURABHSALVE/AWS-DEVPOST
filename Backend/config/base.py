"""
Base configuration for Multi-Lingual Content Creation Agent
"""
import os
from datetime import timedelta


class BaseConfig:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # AWS settings
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # Bedrock settings
    BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    BEDROCK_MAX_TOKENS = int(os.environ.get('BEDROCK_MAX_TOKENS', '4000'))
    BEDROCK_TEMPERATURE = float(os.environ.get('BEDROCK_TEMPERATURE', '0.7'))
    
    # Content generation settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '10000'))
    DEFAULT_TIMEOUT = int(os.environ.get('DEFAULT_TIMEOUT', '30'))
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass