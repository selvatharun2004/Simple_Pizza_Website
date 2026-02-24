"""
Database connection and initialization module
"""
import sqlite3
import logging

logger = logging.getLogger(__name__)


def get_db_connection(database='pizza_shop.db'):
    """
    Create and return a database connection
    
    Args:
        database: Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection with Row factory
        
    Raises:
        Exception: If connection fails
    """
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")


def init_db(database='pizza_shop.db'):
    """
    Initialize database with schema and sample data
    
    Args:
        database: Path to the database file
        
    Raises:
        Exception: If initialization fails
    """
    conn = None
    try:
        conn = get_db_connection(database)
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
        if conn:
            conn.close()
        raise
