"""
Cart Manager - Handles shopping cart operations using session storage
"""
import logging
from flask import session

logger = logging.getLogger(__name__)


class CartManager:
    """Handles shopping cart operations using session storage"""

    @staticmethod
    def add_item(pizza_id, pizza_name, price):
        """
        Add pizza to cart or increment quantity if already present

        Args:
            pizza_id: Unique pizza identifier
            pizza_name: Name of the pizza
            price: Price in INR
        """
        try:
            if 'cart' not in session:
                session['cart'] = {}
            
            cart = session['cart']
            
            # Validate cart structure
            if not isinstance(cart, dict):
                logger.warning("Corrupted cart data detected, reinitializing cart")
                cart = {}
                session['cart'] = cart
            
            pizza_id_str = str(pizza_id)
            
            if pizza_id_str in cart:
                # Validate existing cart item structure
                if isinstance(cart[pizza_id_str], dict) and 'quantity' in cart[pizza_id_str]:
                    cart[pizza_id_str]['quantity'] += 1
                else:
                    logger.warning(f"Corrupted cart item data for pizza {pizza_id}, reinitializing")
                    cart[pizza_id_str] = {
                        'name': pizza_name,
                        'price': price,
                        'quantity': 1
                    }
            else:
                cart[pizza_id_str] = {
                    'name': pizza_name,
                    'price': price,
                    'quantity': 1
                }
            
            session['cart'] = cart
            session.modified = True
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            # Reinitialize cart on error
            session['cart'] = {}
            session.modified = True
            raise

    @staticmethod
    def get_cart():
        """
        Retrieve current cart contents

        Returns:
            Dict mapping pizza_id to {name, price, quantity}
        """
        try:
            if 'cart' not in session:
                session['cart'] = {}
            
            cart = session['cart']
            
            # Validate cart structure
            if not isinstance(cart, dict):
                logger.warning("Corrupted cart data detected, reinitializing cart")
                session['cart'] = {}
                return {}
            
            # Validate each cart item
            valid_cart = {}
            for pizza_id, item in cart.items():
                if isinstance(item, dict) and 'name' in item and 'price' in item and 'quantity' in item:
                    valid_cart[pizza_id] = item
                else:
                    logger.warning(f"Corrupted cart item for pizza {pizza_id}, skipping")
            
            # Update session if we had to clean up corrupted items
            if len(valid_cart) != len(cart):
                session['cart'] = valid_cart
                session.modified = True
            
            return valid_cart
        except Exception as e:
            logger.error(f"Error retrieving cart: {str(e)}")
            session['cart'] = {}
            session.modified = True
            return {}

    @staticmethod
    def get_cart_total():
        """
        Calculate total price of all items in cart

        Returns:
            Total price in INR
        """
        try:
            cart = CartManager.get_cart()
            total = 0.0
            for item in cart.values():
                if isinstance(item, dict) and 'price' in item and 'quantity' in item:
                    total += item['price'] * item['quantity']
            return total
        except Exception as e:
            logger.error(f"Error calculating cart total: {str(e)}")
            return 0.0

    @staticmethod
    def is_empty():
        """Check if cart contains any items"""
        cart = CartManager.get_cart()
        return len(cart) == 0

    @staticmethod
    def remove_item(pizza_id):
        """
        Remove pizza from cart completely

        Args:
            pizza_id: Unique pizza identifier
        """
        try:
            if 'cart' not in session:
                session['cart'] = {}
                return
            
            cart = session['cart']
            
            # Validate cart structure
            if not isinstance(cart, dict):
                logger.warning("Corrupted cart data detected, reinitializing cart")
                session['cart'] = {}
                return
            
            pizza_id_str = str(pizza_id)
            
            if pizza_id_str in cart:
                del cart[pizza_id_str]
                session['cart'] = cart
                session.modified = True
        except Exception as e:
            logger.error(f"Error removing item from cart: {str(e)}")
            # Don't reinitialize cart on remove error, just log it

    @staticmethod
    def clear_cart():
        """Remove all items from cart"""
        session['cart'] = {}
        session.modified = True
