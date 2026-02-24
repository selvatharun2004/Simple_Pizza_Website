from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

DATABASE = 'pizza_shop.db'

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

def init_db():
    """Initialize database with schema and sample data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create pizzas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pizzas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                total_price REAL NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create order_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                pizza_id INTEGER NOT NULL,
                pizza_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (pizza_id) REFERENCES pizzas(id)
            )
        ''')
        
        # Check if pizzas table is empty and populate with sample data
        cursor.execute('SELECT COUNT(*) FROM pizzas')
        if cursor.fetchone()[0] == 0:
            sample_pizzas = [
                ('Margherita', 299.0),
                ('Pepperoni', 399.0),
                ('Vegetarian', 349.0),
                ('BBQ Chicken', 449.0),
                ('Hawaiian', 379.0),
                ('Four Cheese', 429.0)
            ]
            cursor.executemany('INSERT INTO pizzas (name, price) VALUES (?, ?)', sample_pizzas)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

# Initialize database on startup
init_db()


class MenuService:
    """Handles pizza menu operations"""

    @staticmethod
    def get_all_pizzas():
        """
        Retrieve all available pizzas from database

        Returns:
            List of dicts with keys: id, name, price
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, price FROM pizzas')
            rows = cursor.fetchall()
            conn.close()
            
            # Convert Row objects to dictionaries
            pizzas = [{'id': row['id'], 'name': row['name'], 'price': row['price']} for row in rows]
            return pizzas
        except Exception as e:
            logger.error(f"Error retrieving pizzas: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return []

    @staticmethod
    def get_pizza_by_id(pizza_id):
        """
        Retrieve a specific pizza by ID

        Args:
            pizza_id: Unique pizza identifier

        Returns:
            Dict with keys: id, name, price, or None if not found
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, price FROM pizzas WHERE id = ?', (pizza_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {'id': row['id'], 'name': row['name'], 'price': row['price']}
            return None
        except Exception as e:
            logger.error(f"Error retrieving pizza {pizza_id}: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return None


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


class OrderProcessor:
    """Handles order processing and database operations"""

    @staticmethod
    def create_order(customer_name, phone, address, cart_items, total):
        """
        Save order to database

        Args:
            customer_name: Customer's full name
            phone: Customer's phone number
            address: Delivery address
            cart_items: Dict of pizza items with quantities
            total: Total order price in INR

        Returns:
            Unique order ID

        Raises:
            Exception: If save operation fails
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert into orders table
            cursor.execute(
                'INSERT INTO orders (customer_name, phone, address, total_price) VALUES (?, ?, ?, ?)',
                (customer_name, phone, address, total)
            )
            order_id = cursor.lastrowid

            # Insert order items
            for pizza_id_str, item in cart_items.items():
                cursor.execute(
                    'INSERT INTO order_items (order_id, pizza_id, pizza_name, price, quantity) VALUES (?, ?, ?, ?, ?)',
                    (order_id, int(pizza_id_str), item['name'], item['price'], item['quantity'])
                )

            conn.commit()
            conn.close()
            
            logger.info(f"Order {order_id} created successfully for customer {customer_name}")
            return order_id
        except Exception as e:
            logger.error(f"Failed to save order to database: {str(e)}")
            if conn:
                conn.rollback()
                conn.close()
            raise Exception(f"Failed to save order to database: {str(e)}")

    @staticmethod
    def get_order_by_id(order_id):
        """
        Retrieve order details by ID

        Args:
            order_id: Unique order identifier

        Returns:
            Dict with order details or None if not found
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get order details
            cursor.execute(
                'SELECT id, customer_name, phone, address, total_price, order_date FROM orders WHERE id = ?',
                (order_id,)
            )
            order_row = cursor.fetchone()

            if not order_row:
                conn.close()
                return None

            # Get order items
            cursor.execute(
                'SELECT pizza_id, pizza_name, price, quantity FROM order_items WHERE order_id = ?',
                (order_id,)
            )
            items_rows = cursor.fetchall()

            conn.close()

            # Build order dictionary
            order = {
                'id': order_row['id'],
                'customer_name': order_row['customer_name'],
                'phone': order_row['phone'],
                'address': order_row['address'],
                'total_price': order_row['total_price'],
                'order_date': order_row['order_date'],
                'items': [
                    {
                        'pizza_id': row['pizza_id'],
                        'pizza_name': row['pizza_name'],
                        'price': row['price'],
                        'quantity': row['quantity']
                    }
                    for row in items_rows
                ]
            }

            return order
        except Exception as e:
            logger.error(f"Failed to retrieve order {order_id} from database: {str(e)}")
            if conn:
                conn.close()
            return None

    @staticmethod
    def get_all_orders(limit=None, offset=0):
        """
        Retrieve all orders from database with pagination support

        Args:
            limit: Maximum number of orders to retrieve (None for all)
            offset: Number of orders to skip (for pagination)

        Returns:
            List of order dictionaries with basic info
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = '''
                SELECT id, customer_name, phone, address, total_price, order_date
                FROM orders
                ORDER BY order_date DESC
            '''

            if limit:
                query += f' LIMIT {limit} OFFSET {offset}'

            cursor.execute(query)
            orders_rows = cursor.fetchall()
            conn.close()

            orders = [
                {
                    'id': row['id'],
                    'customer_name': row['customer_name'],
                    'phone': row['phone'],
                    'address': row['address'],
                    'total_price': row['total_price'],
                    'order_date': row['order_date']
                }
                for row in orders_rows
            ]

            return orders
        except Exception as e:
            logger.error(f"Failed to retrieve orders from database: {str(e)}")
            if conn:
                conn.close()
            return []

    @staticmethod
    def get_order_count():
        """
        Get total count of orders in database

        Returns:
            Integer count of total orders
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM orders')
            result = cursor.fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Failed to get order count: {str(e)}")
            if conn:
                conn.close()
            return 0





@app.route('/')
def index():
    """Display homepage with pizza menu"""
    try:
        pizzas = MenuService.get_all_pizzas()
        return render_template('index.html', pizzas=pizzas)
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        return render_template('500.html'), 500


@app.route('/add_to_cart/<int:pizza_id>', methods=['POST'])
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


@app.route('/cart')
def cart():
    """Display cart contents"""
    try:
        cart_items = CartManager.get_cart()
        total = CartManager.get_cart_total()
        return render_template('cart.html', cart=cart_items, total=total)
    except Exception as e:
        logger.error(f"Error loading cart page: {str(e)}")
        return render_template('500.html'), 500


@app.route('/remove_from_cart/<int:pizza_id>', methods=['POST'])
def remove_from_cart(pizza_id):
    """Remove pizza from cart"""
    try:
        # Validate pizza_id exists before removal
        pizza = MenuService.get_pizza_by_id(pizza_id)
        if pizza is None:
            logger.warning(f"Attempt to remove invalid pizza ID: {pizza_id}")
        
        CartManager.remove_item(pizza_id)
        logger.info(f"Pizza ID {pizza_id} removed from cart")
        return redirect(url_for('cart'))
    except Exception as e:
        logger.error(f"Error removing pizza {pizza_id} from cart: {str(e)}")
        return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
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
            return redirect(url_for('cart'))
        
        try:
            # Create order in database
            order_id = OrderProcessor.create_order(customer_name, phone, address, cart_items, total)
            
            # Clear cart after successful order
            CartManager.clear_cart()
            
            # Redirect to confirmation page with order_id
            return redirect(url_for('confirmation', order_id=order_id))
        
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
            return redirect(url_for('cart'))
        
        # Get cart data and total
        cart_items = CartManager.get_cart()
        total = CartManager.get_cart_total()
        
        # Render checkout page with cart summary
        return render_template('checkout.html', cart=cart_items, total=total)
    except Exception as e:
        logger.error(f"Error loading checkout page: {str(e)}")
        return render_template('500.html'), 500


@app.route('/confirmation/<int:order_id>')
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


# Error handlers
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


# Manager routes
@app.route('/manager/orders')
def manager_orders():
    """Display all orders for the manager"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get orders and total count
        all_orders = OrderProcessor.get_all_orders(limit=per_page, offset=offset)
        total_orders = OrderProcessor.get_order_count()
        
        # Calculate pagination info
        total_pages = (total_orders + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template(
            'manager/orders.html',
            orders=all_orders,
            page=page,
            per_page=per_page,
            total_orders=total_orders,
            total_pages=total_pages,
            has_prev=has_prev,
            has_next=has_next
        )
    except Exception as e:
        logger.error(f"Error loading manager orders page: {str(e)}")
        return render_template('500.html'), 500


@app.route('/manager/orders/<int:order_id>')
def manager_order_detail(order_id):
    """Display detailed view of a specific order"""
    try:
        order = OrderProcessor.get_order_by_id(order_id)
        
        if order is None:
            logger.warning(f"Manager accessed non-existent order ID: {order_id}")
            return render_template('404.html'), 404
        
        return render_template('manager/order_detail.html', order=order)
    except Exception as e:
        logger.error(f"Error loading order detail for order {order_id}: {str(e)}")
        return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
