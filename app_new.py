"""
Pizza Shop Web Application - Main application file

This is the refactored version with modular structure.
The application is organized into separate modules:
- config.py: Configuration settings
- database.py: Database connection and initialization
- services/: Business logic (MenuService, CartManager, OrderProcessor)
- routes/: Route handlers (main, cart, order routes)
"""
import logging
from flask import Flask
from config import config
from database import init_db
from routes import main_bp, cart_bp, order_bp, manager_bp, register_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use ('development', 'production', 'testing')
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    database_path = app.config.get('DATABASE', 'pizza_shop.db')
    init_db(database_path)
    logger.info(f"Application initialized with {config_name} configuration")
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(manager_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


# Create application instance
app = create_app('development')


if __name__ == '__main__':
    app.run(debug=True)
