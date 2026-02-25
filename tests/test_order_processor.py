"""Unit tests for OrderProcessor class"""
import pytest
import sqlite3
from app import app, OrderProcessor, init_db, get_db_connection


@pytest.fixture
def client():
    """Create a test client with a test database"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_create_order_success(client):
    """Test creating an order successfully"""
    with app.test_request_context():
        # Prepare test data
        customer_name = "John Doe"
        phone = "1234567890"
        address = "123 Main St"
        cart_items = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
        total = 997.0
        
        # Create order
        order_id = OrderProcessor.create_order(customer_name, phone, address, cart_items, total)
        
        # Verify order_id is returned
        assert isinstance(order_id, int)
        assert order_id > 0
        
        # Verify order was saved to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order_row = cursor.fetchone()
        
        assert order_row is not None
        assert order_row['customer_name'] == customer_name
        assert order_row['phone'] == phone
        assert order_row['address'] == address
        assert order_row['total_price'] == total
        
        # Verify order items were saved
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
        items_rows = cursor.fetchall()
        
        assert len(items_rows) == 2
        
        # Check first item
        item1 = [row for row in items_rows if row['pizza_id'] == 1][0]
        assert item1['pizza_name'] == 'Margherita'
        assert item1['price'] == 299.0
        assert item1['quantity'] == 2
        
        # Check second item
        item2 = [row for row in items_rows if row['pizza_id'] == 2][0]
        assert item2['pizza_name'] == 'Pepperoni'
        assert item2['price'] == 399.0
        assert item2['quantity'] == 1
        
        conn.close()


def test_create_order_empty_cart(client):
    """Test creating an order with empty cart"""
    with app.test_request_context():
        customer_name = "Jane Doe"
        phone = "9876543210"
        address = "456 Oak Ave"
        cart_items = {}
        total = 0.0
        
        # Create order with empty cart
        order_id = OrderProcessor.create_order(customer_name, phone, address, cart_items, total)
        
        # Verify order was created
        assert isinstance(order_id, int)
        assert order_id > 0
        
        # Verify no order items were saved
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
        items_rows = cursor.fetchall()
        
        assert len(items_rows) == 0
        conn.close()


def test_get_order_by_id_existing(client):
    """Test retrieving an existing order"""
    with app.test_request_context():
        # First create an order
        customer_name = "Alice Smith"
        phone = "5551234567"
        address = "789 Elm St"
        cart_items = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1},
            '3': {'name': 'Vegetarian', 'price': 349.0, 'quantity': 2}
        }
        total = 997.0
        
        order_id = OrderProcessor.create_order(customer_name, phone, address, cart_items, total)
        
        # Retrieve the order
        order = OrderProcessor.get_order_by_id(order_id)
        
        # Verify order details
        assert order is not None
        assert order['id'] == order_id
        assert order['customer_name'] == customer_name
        assert order['phone'] == phone
        assert order['address'] == address
        assert order['total_price'] == total
        assert 'order_date' in order
        
        # Verify order items
        assert 'items' in order
        assert len(order['items']) == 2
        
        # Check items
        item1 = [item for item in order['items'] if item['pizza_id'] == 1][0]
        assert item1['pizza_name'] == 'Margherita'
        assert item1['price'] == 299.0
        assert item1['quantity'] == 1
        
        item2 = [item for item in order['items'] if item['pizza_id'] == 3][0]
        assert item2['pizza_name'] == 'Vegetarian'
        assert item2['price'] == 349.0
        assert item2['quantity'] == 2


def test_get_order_by_id_nonexistent(client):
    """Test retrieving a non-existent order"""
    with app.test_request_context():
        # Try to get an order that doesn't exist
        order = OrderProcessor.get_order_by_id(99999)
        
        # Should return None
        assert order is None


def test_create_order_generates_unique_ids(client):
    """Test that multiple orders get unique IDs"""
    with app.test_request_context():
        # Create first order
        order_id1 = OrderProcessor.create_order(
            "Customer 1", "1111111111", "Address 1",
            {'1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}},
            299.0
        )
        
        # Create second order
        order_id2 = OrderProcessor.create_order(
            "Customer 2", "2222222222", "Address 2",
            {'2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}},
            399.0
        )
        
        # Verify IDs are different
        assert order_id1 != order_id2
        assert isinstance(order_id1, int)
        assert isinstance(order_id2, int)


def test_create_order_with_multiple_quantities(client):
    """Test creating an order with items having multiple quantities"""
    with app.test_request_context():
        cart_items = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 5},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 3}
        }
        total = (299.0 * 5) + (399.0 * 3)
        
        order_id = OrderProcessor.create_order(
            "Bob Johnson", "5559876543", "321 Pine Rd",
            cart_items, total
        )
        
        # Retrieve and verify
        order = OrderProcessor.get_order_by_id(order_id)
        
        assert order is not None
        assert len(order['items']) == 2
        
        item1 = [item for item in order['items'] if item['pizza_id'] == 1][0]
        assert item1['quantity'] == 5
        
        item2 = [item for item in order['items'] if item['pizza_id'] == 2][0]
        assert item2['quantity'] == 3



def test_create_order_database_error_handling(client):
    """Test that database errors are properly handled"""
    with app.test_request_context():
        # Try to create an order with invalid data that would cause a database error
        # We'll use a mock to simulate a database failure
        import unittest.mock as mock
        
        with mock.patch('app.get_db_connection') as mock_conn:
            # Simulate a database error
            mock_conn.side_effect = Exception("Database connection failed")
            
            # Attempt to create order should raise an exception
            with pytest.raises(Exception) as exc_info:
                OrderProcessor.create_order(
                    "Test User", "1234567890", "Test Address",
                    {'1': {'name': 'Pizza', 'price': 299.0, 'quantity': 1}},
                    299.0
                )
            
            # Verify the error message contains our database error
            assert "Failed to save order to database" in str(exc_info.value)


def test_get_order_by_id_database_error_handling(client):
    """Test that database errors during retrieval are properly handled"""
    with app.test_request_context():
        import unittest.mock as mock
        
        with mock.patch('app.get_db_connection') as mock_conn:
            # Simulate a database error
            mock_conn.side_effect = Exception("Database connection failed")
            
            # Attempt to get order should return None gracefully instead of raising
            result = OrderProcessor.get_order_by_id(1)
            
            # Verify it returns None on error
            assert result is None


# Property-Based Tests using Hypothesis

from hypothesis import given, strategies as st, settings, HealthCheck


# Feature: pizza-shop-website, Property 10: Order Persistence Round Trip
# **Validates: Requirements 6.1, 6.2**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    customer_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    phone=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Nd', 'Pd'))),
    address=st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    cart_items=st.dictionaries(
        keys=st.integers(min_value=1, max_value=1000).map(str),
        values=st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
            'price': st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        min_size=1,
        max_size=20
    )
)
def test_property_order_persistence_round_trip(client, customer_name, phone, address, cart_items):
    """
    Property 10: Order Persistence Round Trip
    
    For any valid order (with customer name, phone, address, cart items, and total), 
    saving the order and then retrieving it by ID should return an order containing 
    all the original information.
    """
    with app.test_request_context():
        # Calculate the total from cart items
        total = sum(item['price'] * item['quantity'] for item in cart_items.values())
        
        # Save the order to the database
        order_id = OrderProcessor.create_order(customer_name, phone, address, cart_items, total)
        
        # Property 1: Order ID should be returned and be a positive integer
        assert isinstance(order_id, int), "Order ID should be an integer"
        assert order_id > 0, "Order ID should be positive"
        
        # Retrieve the order by ID
        retrieved_order = OrderProcessor.get_order_by_id(order_id)
        
        # Property 2: Retrieved order should not be None
        assert retrieved_order is not None, f"Order {order_id} should be retrievable"
        
        # Property 3: Customer name should match
        assert retrieved_order['customer_name'] == customer_name, \
            f"Customer name mismatch: expected '{customer_name}', got '{retrieved_order['customer_name']}'"
        
        # Property 4: Phone should match
        assert retrieved_order['phone'] == phone, \
            f"Phone mismatch: expected '{phone}', got '{retrieved_order['phone']}'"
        
        # Property 5: Address should match
        assert retrieved_order['address'] == address, \
            f"Address mismatch: expected '{address}', got '{retrieved_order['address']}'"
        
        # Property 6: Total price should match (with floating point tolerance)
        assert abs(retrieved_order['total_price'] - total) < 0.01, \
            f"Total price mismatch: expected {total}, got {retrieved_order['total_price']}"
        
        # Property 7: Order should have an order_date field
        assert 'order_date' in retrieved_order, "Order should have an order_date field"
        
        # Property 8: Order should have items
        assert 'items' in retrieved_order, "Order should have an items field"
        assert isinstance(retrieved_order['items'], list), "Order items should be a list"
        
        # Property 9: Number of items should match
        assert len(retrieved_order['items']) == len(cart_items), \
            f"Number of items mismatch: expected {len(cart_items)}, got {len(retrieved_order['items'])}"
        
        # Property 10: All cart items should be present in the retrieved order with correct details
        for pizza_id_str, original_item in cart_items.items():
            pizza_id = int(pizza_id_str)
            
            # Find the corresponding item in the retrieved order
            matching_items = [item for item in retrieved_order['items'] if item['pizza_id'] == pizza_id]
            assert len(matching_items) == 1, \
                f"Pizza {pizza_id} should appear exactly once in retrieved order items"
            
            retrieved_item = matching_items[0]
            
            # Verify pizza name matches
            assert retrieved_item['pizza_name'] == original_item['name'], \
                f"Pizza {pizza_id} name mismatch: expected '{original_item['name']}', got '{retrieved_item['pizza_name']}'"
            
            # Verify price matches (with floating point tolerance)
            assert abs(retrieved_item['price'] - original_item['price']) < 0.01, \
                f"Pizza {pizza_id} price mismatch: expected {original_item['price']}, got {retrieved_item['price']}"
            
            # Verify quantity matches
            assert retrieved_item['quantity'] == original_item['quantity'], \
                f"Pizza {pizza_id} quantity mismatch: expected {original_item['quantity']}, got {retrieved_item['quantity']}"


# Feature: pizza-shop-website, Property 11: Order ID Uniqueness
# **Validates: Requirements 6.3**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    num_orders=st.integers(min_value=2, max_value=20),
    customer_names=st.lists(
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        min_size=2,
        max_size=20
    ),
    phones=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Nd', 'Pd'))),
        min_size=2,
        max_size=20
    ),
    addresses=st.lists(
        st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        min_size=2,
        max_size=20
    )
)
def test_property_order_id_uniqueness(client, num_orders, customer_names, phones, addresses):
    """
    Property 11: Order ID Uniqueness
    
    For any two distinct orders saved to the database, they should have different order IDs.
    """
    with app.test_request_context():
        # Ensure we have enough data for the number of orders
        num_orders = min(num_orders, len(customer_names), len(phones), len(addresses))
        
        # Create multiple orders and collect their IDs
        order_ids = []
        
        for i in range(num_orders):
            # Create a simple cart with one item
            cart_items = {
                '1': {
                    'name': 'Test Pizza',
                    'price': 299.0,
                    'quantity': 1
                }
            }
            total = 299.0
            
            # Create the order
            order_id = OrderProcessor.create_order(
                customer_names[i],
                phones[i],
                addresses[i],
                cart_items,
                total
            )
            
            # Property 1: Order ID should be a positive integer
            assert isinstance(order_id, int), f"Order ID should be an integer, got {type(order_id)}"
            assert order_id > 0, f"Order ID should be positive, got {order_id}"
            
            # Collect the order ID
            order_ids.append(order_id)
        
        # Property 2: All order IDs should be unique
        assert len(order_ids) == len(set(order_ids)), \
            f"Order IDs should be unique. Got {len(order_ids)} orders but only {len(set(order_ids))} unique IDs. IDs: {order_ids}"
        
        # Property 3: For any two distinct orders, their IDs should be different
        for i in range(len(order_ids)):
            for j in range(i + 1, len(order_ids)):
                assert order_ids[i] != order_ids[j], \
                    f"Order {i} and Order {j} have the same ID: {order_ids[i]}"
