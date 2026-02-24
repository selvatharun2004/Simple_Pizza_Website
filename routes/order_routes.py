"""
Order routes - Checkout and order confirmation
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for
from services import CartManager, OrderProcessor

logger = logging.getLogger(__name__)

order_bp = Blueprint('order', __name__)


@order_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Display checkout page with form and order summary, or process order submission"""
    if request.method == 'POST':
        # Handle form submission
        customer_name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validate all form fields are non-empty
        if not customer_name or not phone or not address:
            logger.warning("Checkout form validation failed: missing required fields")
            # Return to checkout page with error message
            cart_items = CartManager.get_cart()
            total = CartManager.get_cart_total()
            error_message = 'All fields are required. Please fill in your name, phone, and address.'
            return render_template('checkout.html', cart=cart_items, total=total, error=error_message), 400
        
        # Get cart data
        cart_items = CartManager.get_cart()
        total = CartManager.get_cart_total()
        
        # Check if cart is empty (edge case)
        if not cart_items:
            logger.warning("Checkout attempted with empty cart")
            return redirect(url_for('cart.cart'))
        
        try:
            # Create order in database
            order_id = OrderProcessor.create_order(customer_name, phone, address, cart_items, total)
            
            # Clear cart after successful order
            CartManager.clear_cart()
            
            # Redirect to confirmation page with order_id
            return redirect(url_for('order.confirmation', order_id=order_id))
        
        except Exception as e:
            # Handle database errors
            logger.error(f"Error processing checkout: {str(e)}")
            cart_items = CartManager.get_cart()
            total = CartManager.get_cart_total()
            error_message = 'An error occurred while processing your order. Please try again.'
            return render_template('checkout.html', cart=cart_items, total=total, error=error_message), 500
    
    # GET request - display checkout page
    try:
        # Check if cart is empty, redirect to cart if true
        if CartManager.is_empty():
            logger.info("Checkout page accessed with empty cart, redirecting")
            return redirect(url_for('cart.cart'))
        
        # Get cart data and total
        cart_items = CartManager.get_cart()
        total = CartManager.get_cart_total()
        
        # Render checkout page with cart summary
        return render_template('checkout.html', cart=cart_items, total=total)
    except Exception as e:
        logger.error(f"Error loading checkout page: {str(e)}")
        return render_template('500.html'), 500


@order_bp.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    """Display order confirmation page"""
    try:
        # Retrieve order details
        order = OrderProcessor.get_order_by_id(order_id)
        
        # Handle case where order_id doesn't exist
        if order is None:
            logger.warning(f"Confirmation page accessed with invalid order ID: {order_id}")
            return "Order not found", 404
        
        # Render confirmation page with order details
        return render_template('confirmation.html', order=order)
    except Exception as e:
        logger.error(f"Error loading confirmation page for order {order_id}: {str(e)}")
        return render_template('500.html'), 500
