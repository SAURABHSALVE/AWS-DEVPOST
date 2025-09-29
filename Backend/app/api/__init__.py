"""
API blueprints package for Multi-Lingual Content Creation Agent
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.api import routes