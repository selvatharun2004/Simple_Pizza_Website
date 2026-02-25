import pytest
import json
from app import app, init_db, MenuService, CartManager
import os
import tempfile


@pytest.fixture
def client():
    """Create a test client with a temporary database"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    
    # Override the DATABASE constant in app module
    import app as app_module
    original_db = app_module.DATABASE
    app_module.DATABASE = db_path
    
    # Initialize database
    init_db()
    
    # Create test client
    with app.test_client() as client:
        with app.app_context():
            yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    app_module.DATABASE = original_db


def test_add_to_cart_valid_pizza(client):
    """Test adding a valid pizza to cart"""
    # Get a valid pizza ID from the database
    pizzas = MenuService.get_all_pizzas()
    assert len(pizzas) > 0, "Database should have pizzas"
    
    pizza = pizzas[0]
    pizza_id = pizza['id']
    
    # Add pizza to cart
    response = client.post(f'/add_to_cart/{pizza_id}')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'message' in data
    assert pizza['name'] in data['message']


def test_add_to_cart_invalid_pizza(client):
    """Test adding an invalid pizza ID to cart"""
    # Use a pizza ID that doesn't exist
    invalid_pizza_id = 99999
    
    # Try to add invalid pizza to cart
    response = client.post(f'/add_to_cart/{invalid_pizza_id}')
    
    # Check response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
    assert 'Invalid pizza ID' in data['error']


def test_add_to_cart_increments_quantity(client):
    """Test that adding the same pizza twice increments quantity"""
    # Get a valid pizza
    pizzas = MenuService.get_all_pizzas()
    pizza = pizzas[0]
    pizza_id = pizza['id']
    
    # Add pizza to cart twice
    with client.session_transaction() as sess:
        sess['cart'] = {}
    
    client.post(f'/add_to_cart/{pizza_id}')
    client.post(f'/add_to_cart/{pizza_id}')
    
    # Check cart contents
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        pizza_id_str = str(pizza_id)
        assert pizza_id_str in cart
        assert cart[pizza_id_str]['quantity'] == 2


def test_add_to_cart_creates_entry(client):
    """Test that adding a pizza creates an entry in the cart"""
    # Get a valid pizza
    pizzas = MenuService.get_all_pizzas()
    pizza = pizzas[0]
    pizza_id = pizza['id']
    
    # Ensure cart is empty
    with client.session_transaction() as sess:
        sess['cart'] = {}
    
    # Add pizza to cart
    client.post(f'/add_to_cart/{pizza_id}')
    
    # Check cart contains the pizza
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        pizza_id_str = str(pizza_id)
        assert pizza_id_str in cart
        assert cart[pizza_id_str]['name'] == pizza['name']
        assert cart[pizza_id_str]['price'] == pizza['price']
        assert cart[pizza_id_str]['quantity'] == 1
