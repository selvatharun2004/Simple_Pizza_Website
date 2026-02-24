"""
Error handlers - Custom error pages
"""
import logging
from flask import render_template, request

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Register error handlers with the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors with custom error page"""
        logger.warning(f"404 error: {request.url}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 errors with custom error page"""
        logger.error(f"500 error: {str(e)}")
        return render_template('500.html'), 500
