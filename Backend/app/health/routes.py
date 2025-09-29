"""
Health check routes for Multi-Lingual Content Creation Agent
"""
from flask import jsonify
from app.health import health_bp
import datetime


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'multi-lingual-content-agent',
        'version': '1.0.0'
    })


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint for deployment"""
    # TODO: Add checks for database connectivity, external services, etc.
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'checks': {
            'database': 'not_implemented',
            'aws_bedrock': 'not_implemented'
        }
    })