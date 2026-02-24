"""
Tests for add to cart JavaScript functionality
"""
import pytest
from app import app, init_db, MenuService
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


def test_index_page_contains_javascript(client):
    """Test that the index page contains the add to cart JavaScript"""
    response = client.get('/')
    assert response.status_code == 200
    
    # Check that the page contains the JavaScript code
    html = response.data.decode('utf-8')
    assert 'add-to-cart-form' in html
    assert 'data-pizza-id' in html
    assert 'fetch(url' in html
    assert 'showFeedback' in html


def test_index_page_contains_feedback_message_div(client):
    """Test that the index page contains the feedback message container"""
    response = client.get('/')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    assert 'id="feedback-message"' in html
    assert 'id="feedback-text"' in html


def test_forms_have_data_pizza_id_attribute(client):
    """Test that each form has the data-pizza-id attribute"""
    response = client.get('/')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Get all pizzas to verify each has a form with data-pizza-id
    pizzas = MenuService.get_all_pizzas()
    
    for pizza in pizzas:
        # Check that each pizza has a form with the correct data-pizza-id
        assert f'data-pizza-id="{pizza["id"]}"' in html


def test_ajax_endpoint_returns_json(client):
    """Test that the add_to_cart endpoint returns JSON response"""
    # Get a valid pizza
    pizzas = MenuService.get_all_pizzas()
    assert len(pizzas) > 0
    
    pizza = pizzas[0]
    
    # Make POST request to add_to_cart endpoint
    response = client.post(f'/add_to_cart/{pizza["id"]}')
    
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    # Check JSON response structure
    json_data = response.get_json()
    assert 'success' in json_data
    assert 'message' in json_data
    assert json_data['success'] is True


def test_ajax_endpoint_error_returns_json(client):
    """Test that the add_to_cart endpoint returns JSON error for invalid pizza"""
    # Use an invalid pizza ID
    invalid_pizza_id = 99999
    
    response = client.post(f'/add_to_cart/{invalid_pizza_id}')
    
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    
    # Check JSON error response structure
    json_data = response.get_json()
    assert 'success' in json_data
    assert 'error' in json_data
    assert json_data['success'] is False
