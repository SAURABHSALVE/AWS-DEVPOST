"""
API routes for Multi-Lingual Content Creation Agent
"""
from flask import jsonify
from app.api import api_bp


@api_bp.route('/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Multi-Lingual Content Creation Agent API is running'
    })