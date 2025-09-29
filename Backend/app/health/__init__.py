"""
Health check blueprint for Multi-Lingual Content Creation Agent
"""
from flask import Blueprint

health_bp = Blueprint('health', __name__)

# Import routes to register them with the blueprint
from app.health import routes