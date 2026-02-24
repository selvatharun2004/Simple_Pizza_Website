"""
Menu Service - Handles pizza menu operations
"""
import logging
from database import get_db_connection

logger = logging.getLogger(__name__)


class MenuService:
    """Handles pizza menu operations"""

    @staticmethod
    def get_all_pizzas():
        """
        Retrieve all available pizzas from database

        Returns:
            List of dicts with keys: id, name, price
        """
        conn = None
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
            if conn:
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
        conn = None
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
            if conn:
                conn.close()
            return None
