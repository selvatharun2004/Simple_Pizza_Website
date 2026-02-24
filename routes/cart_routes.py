"""
Cart routes - Shopping cart operations
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services import MenuService, CartManager

logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/add_to_cart/<int:pizza_id>', methods=['POST'])
def add_to_cart(pizza_id):
    """Add pizza to cart"""
    try:
        # Validate pizza_id exists in database
        pizza = MenuService.get_pizza_by_id(pizza_id)
        
        if pizza is None:
            logger.warning(f"Attempt to add invalid pizza ID: {pizza_id}")
            return jsonify({'success': False, 'error': 'Invalid pizza ID'}), 404
        
        # Add item to cart
        CartManager.add_item(pizza['id'], pizza['name'], pizza['price'])
        
        logger.info(f"Pizza {pizza['name']} (ID: {pizza_id}) added to cart")
        return jsonify({'success': True, 'message': f"{pizza['name']} added to cart"}), 200
    except Exception as e:
        logger.error(f"Error adding pizza {pizza_id} to cart: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred while adding to cart'}), 500


@cart_bp.route('/cart')
def cart():
    """Display cart contents"""
    try:
        cart_items = CartManager.get_cart()
        total = CartManager.get_cart_total()
        return render_template('cart.html', cart=cart_items, total=total)
    except Exception as e:
        logger.error(f"Error loading cart page: {str(e)}")
        return render_template('500.html'), 500


@cart_bp.route('/remove_from_cart/<int:pizza_id>', methods=['POST'])
def remove_from_cart(pizza_id):
    """Remove pizza from cart"""
    try:
        # Validate pizza_id exists before removal
        pizza = MenuService.get_pizza_by_id(pizza_id)
        if pizza is None:
            logger.warning(f"Attempt to remove invalid pizza ID: {pizza_id}")
        
        CartManager.remove_item(pizza_id)
        logger.info(f"Pizza ID {pizza_id} removed from cart")
        return redirect(url_for('cart.cart'))
    except Exception as e:
        logger.error(f"Error removing pizza {pizza_id} from cart: {str(e)}")
        return redirect(url_for('cart.cart'))
