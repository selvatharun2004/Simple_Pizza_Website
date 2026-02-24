"""
Main routes - Homepage and menu display
"""
import logging
from flask import Blueprint, render_template
from services import MenuService

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Display homepage with pizza menu"""
    try:
        pizzas = MenuService.get_all_pizzas()
        return render_template('index.html', pizzas=pizzas)
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        return render_template('500.html'), 500
