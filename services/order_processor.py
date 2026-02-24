"""
Order Processor - Handles order processing and database operations
"""
import logging
from database import get_db_connection

logger = logging.getLogger(__name__)


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
            List of order dictionaries with basic info (id, customer_name, total_price, order_date)
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Build query with optional limit and offset
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

            # Convert to list of dictionaries
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
