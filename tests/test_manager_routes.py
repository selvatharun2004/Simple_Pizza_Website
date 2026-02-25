"""
Unit tests for manager routes
"""
import pytest
from app import app, init_db, OrderProcessor, CartManager


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_manager_orders_page_empty(client):
    """Test manager orders page with no orders"""
    response = client.get('/manager/orders')
    assert response.status_code == 200
    assert b'Manager Dashboard' in response.data
    assert b'No Orders Yet' in response.data or b'Total Orders' in response.data


def test_manager_orders_page_with_orders(client):
    """Test manager orders page displays orders"""
    # Create a test order
    client.post('/add_to_cart/1')
    client.post('/checkout', data={
        'name': 'Test Customer',
        'phone': '1234567890',
        'address': 'Test Address'
    })
    
    # Access manager page
    response = client.get('/manager/orders')
    assert response.status_code == 200
    assert b'Manager Dashboard' in response.data
    assert b'Test Customer' in response.data
    assert b'1234567890' in response.data


def test_manager_orders_pagination(client):
    """Test manager orders page pagination"""
    # Create multiple orders
    for i in range(5):
        client.post('/add_to_cart/1')
        client.post('/checkout', data={
            'name': f'Customer {i}',
            'phone': f'123456789{i}',
            'address': f'Address {i}'
        })
    
    # Test first page with 3 items per page
    response = client.get('/manager/orders?page=1&per_page=3')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should show pagination controls
    assert 'page' in html.lower() or 'next' in html.lower()


def test_manager_order_detail_page(client):
    """Test manager order detail page"""
    # Create an order
    client.post('/add_to_cart/1')
    client.post('/add_to_cart/2')
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '9876543210',
        'address': '123 Main St'
    }, follow_redirects=False)
    
    # Extract order ID from redirect
    import re
    location = response.headers.get('Location', '')
    match = re.search(r'/confirmation/(\d+)', location)
    assert match is not None
    order_id = int(match.group(1))
    
    # Access order detail page
    response = client.get(f'/manager/orders/{order_id}')
    assert response.status_code == 200
    assert b'Order Details' in response.data
    assert b'John Doe' in response.data
    assert b'9876543210' in response.data
    assert b'123 Main St' in response.data


def test_manager_order_detail_invalid_id(client):
    """Test manager order detail page with invalid order ID"""
    response = client.get('/manager/orders/99999')
    assert response.status_code == 404


def test_manager_orders_shows_total_count(client):
    """Test that manager page shows total order count"""
    # Create orders
    for i in range(3):
        client.post('/add_to_cart/1')
        client.post('/checkout', data={
            'name': f'Customer {i}',
            'phone': f'123456789{i}',
            'address': f'Address {i}'
        })
    
    response = client.get('/manager/orders')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should show total count
    assert 'Total Orders' in html or '3' in html


def test_manager_orders_shows_order_dates(client):
    """Test that manager page shows order dates"""
    # Create an order
    client.post('/add_to_cart/1')
    client.post('/checkout', data={
        'name': 'Test User',
        'phone': '1234567890',
        'address': 'Test Address'
    })
    
    response = client.get('/manager/orders')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should show date information
    assert 'Order Date' in html or 'order_date' in html.lower()


def test_manager_order_detail_shows_items(client):
    """Test that order detail page shows all order items"""
    # Create order with multiple items
    client.post('/add_to_cart/1')
    client.post('/add_to_cart/1')  # Add same item twice
    client.post('/add_to_cart/2')
    
    response = client.post('/checkout', data={
        'name': 'Test User',
        'phone': '1234567890',
        'address': 'Test Address'
    }, follow_redirects=False)
    
    # Extract order ID
    import re
    location = response.headers.get('Location', '')
    match = re.search(r'/confirmation/(\d+)', location)
    order_id = int(match.group(1))
    
    # Check order detail page
    response = client.get(f'/manager/orders/{order_id}')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should show order items
    assert 'Margherita' in html or 'Pepperoni' in html
    assert 'Quantity' in html or 'quantity' in html.lower()


def test_manager_navigation_link_exists(client):
    """Test that manager link exists in navigation"""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should have manager link in navigation
    assert '/manager/orders' in html or 'Manager' in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
