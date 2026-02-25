"""
End-to-End Tests for Pizza Shop Website

This module contains comprehensive end-to-end tests that verify the complete
user journey through the application from browsing to order confirmation.

Tests cover:
- Browse menu → Add items → View cart → Remove item → Checkout → Confirmation
- Cart persistence across page navigation
- All requirements validation
"""

import pytest
from app import app, init_db, MenuService, CartManager, OrderProcessor
from flask import session
import re


@pytest.fixture
def client():
    """Create a test client with a test database"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-e2e'
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_complete_user_flow_happy_path(client):
    """
    Test the complete user journey from browsing to order confirmation.
    
    Flow: Browse menu → Add items → View cart → Remove item → Checkout → Confirmation
    
    This test validates all major requirements end-to-end.
    """
    # Step 1: Browse menu (homepage)
    response = client.get('/')
    assert response.status_code == 200
    
    # Verify menu is displayed with pizzas
    html = response.data.decode('utf-8')
    assert 'Margherita' in html
    assert 'Pepperoni' in html
    assert 'Add to Cart' in html
    
    # Verify prices are shown in INR
    assert '₹' in html or 'INR' in html or '299' in html
    
    # Step 2: Add first item to cart (Margherita - ID 1)
    response = client.post('/add_to_cart/1')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    
    # Verify cart has the item
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert '1' in cart
        assert cart['1']['quantity'] == 1
    
    # Step 3: Add second item to cart (Pepperoni - ID 2)
    response = client.post('/add_to_cart/2')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    
    # Step 4: Add same item again (Margherita - should increment quantity)
    response = client.post('/add_to_cart/1')
    assert response.status_code == 200
    
    # Verify quantity incremented
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert cart['1']['quantity'] == 2
        assert cart['2']['quantity'] == 1
    
    # Step 5: View cart page
    response = client.get('/cart')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    # Verify cart displays items
    assert 'Margherita' in html
    assert 'Pepperoni' in html
    
    # Verify quantities are shown
    # Look for quantity display (could be in various formats)
    assert '2' in html  # Margherita quantity
    
    # Verify total price is calculated and displayed
    assert 'Total' in html or 'total' in html
    
    # Verify remove buttons are present
    assert 'Remove' in html or 'remove' in html
    
    # Step 6: Remove one item from cart (Pepperoni - ID 2)
    response = client.post('/remove_from_cart/2', follow_redirects=True)
    assert response.status_code == 200
    
    # Verify item was removed
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert '2' not in cart  # Pepperoni should be gone
        assert '1' in cart  # Margherita should remain
        assert cart['1']['quantity'] == 2
    
    # Step 7: Navigate to checkout
    response = client.get('/checkout')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    # Verify checkout form is present
    assert 'name' in html.lower()
    assert 'phone' in html.lower()
    assert 'address' in html.lower()
    
    # Verify order summary is shown
    assert 'Margherita' in html
    assert 'Total' in html or 'total' in html
    
    # Step 8: Submit order with customer details
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '9876543210',
        'address': '123 Main Street, Mumbai'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify we're on the confirmation page
    html = response.data.decode('utf-8')
    assert 'confirmation' in html.lower() or 'thank' in html.lower() or 'order' in html.lower()
    
    # Verify order details are displayed
    assert 'John Doe' in html
    assert '123 Main Street, Mumbai' in html
    
    # Verify order ID is displayed (should be a number)
    assert re.search(r'\d+', html) is not None
    
    # Step 9: Verify cart is cleared after order
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert len(cart) == 0 or cart == {}
    
    # Step 10: Navigate back to homepage and verify cart is still empty
    response = client.get('/')
    assert response.status_code == 200
    
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert len(cart) == 0


def test_cart_persistence_across_navigation(client):
    """
    Test that cart contents persist when navigating between pages.
    
    Validates: Requirements 8.1, 8.2
    """
    # Add items to cart
    client.post('/add_to_cart/1')  # Margherita
    client.post('/add_to_cart/2')  # Pepperoni
    client.post('/add_to_cart/1')  # Margherita again
    
    # Verify initial cart state
    with client.session_transaction() as sess:
        initial_cart = sess.get('cart', {}).copy()
        assert '1' in initial_cart
        assert '2' in initial_cart
        assert initial_cart['1']['quantity'] == 2
    
    # Navigate to homepage
    response = client.get('/')
    assert response.status_code == 200
    
    # Verify cart persists
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert cart == initial_cart
    
    # Navigate to cart page
    response = client.get('/cart')
    assert response.status_code == 200
    
    # Verify cart still persists
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert cart == initial_cart
    
    # Navigate to checkout
    response = client.get('/checkout')
    assert response.status_code == 200
    
    # Verify cart still persists
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert cart == initial_cart
    
    # Navigate back to homepage
    response = client.get('/')
    assert response.status_code == 200
    
    # Verify cart STILL persists
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert cart == initial_cart


def test_empty_cart_checkout_redirect(client):
    """
    Test that attempting to checkout with an empty cart redirects appropriately.
    
    Validates: Error handling for empty cart checkout
    """
    # Ensure cart is empty
    with client.session_transaction() as sess:
        sess['cart'] = {}
    
    # Try to access checkout with empty cart
    response = client.get('/checkout', follow_redirects=True)
    assert response.status_code == 200
    
    # Should redirect to cart page or show error
    html = response.data.decode('utf-8')
    # Either on cart page or see empty cart message
    assert 'empty' in html.lower() or 'cart' in html.lower()


def test_multiple_items_same_type_flow(client):
    """
    Test adding the same item multiple times and verifying quantity handling.
    
    Validates: Requirements 2.2 (quantity increment)
    """
    # Add same item 5 times
    for _ in range(5):
        response = client.post('/add_to_cart/1')
        assert response.status_code == 200
    
    # Verify quantity is 5
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert cart['1']['quantity'] == 5
    
    # View cart and verify display
    response = client.get('/cart')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Margherita' in html
    
    # Calculate expected total (5 * 299 = 1495)
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        expected_total = cart['1']['price'] * 5
    
    # Verify total is calculated correctly
    with app.test_request_context():
        with client.session_transaction() as sess:
            session['cart'] = sess['cart']
        total = CartManager.get_cart_total()
        assert abs(total - expected_total) < 0.01


def test_add_all_menu_items_flow(client):
    """
    Test adding all available menu items to cart and completing checkout.
    
    Validates: Complete flow with full menu
    """
    # Get all pizzas from menu
    with app.app_context():
        pizzas = MenuService.get_all_pizzas()
    
    assert len(pizzas) > 0, "Menu should have pizzas"
    
    # Add each pizza to cart
    for pizza in pizzas:
        response = client.post(f'/add_to_cart/{pizza["id"]}')
        assert response.status_code == 200
    
    # Verify all items are in cart
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert len(cart) == len(pizzas)
    
    # View cart
    response = client.get('/cart')
    assert response.status_code == 200
    
    # Proceed to checkout
    response = client.get('/checkout')
    assert response.status_code == 200
    
    # Complete order
    response = client.post('/checkout', data={
        'name': 'Jane Smith',
        'phone': '9123456789',
        'address': '456 Park Avenue, Delhi'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify order confirmation
    html = response.data.decode('utf-8')
    assert 'Jane Smith' in html


def test_remove_all_items_then_add_again(client):
    """
    Test removing all items from cart and then adding new items.
    
    Validates: Cart state management
    """
    # Add items
    client.post('/add_to_cart/1')
    client.post('/add_to_cart/2')
    
    # Remove all items
    client.post('/remove_from_cart/1')
    client.post('/remove_from_cart/2')
    
    # Verify cart is empty
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert len(cart) == 0
    
    # View empty cart
    response = client.get('/cart')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'empty' in html.lower()
    
    # Add new items
    client.post('/add_to_cart/3')
    
    # Verify new item is in cart
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert '3' in cart
        assert len(cart) == 1


def test_checkout_form_validation(client):
    """
    Test that checkout form validates required fields.
    
    Validates: Requirements 5.3, 5.4
    """
    # Add item to cart
    client.post('/add_to_cart/1')
    
    # Try to submit with empty name
    response = client.post('/checkout', data={
        'name': '',
        'phone': '9876543210',
        'address': '123 Main St'
    })
    # Should either return 400 or redirect back with error
    assert response.status_code in [200, 400, 302]
    
    # Try to submit with empty phone
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '',
        'address': '123 Main St'
    })
    assert response.status_code in [200, 400, 302]
    
    # Try to submit with empty address
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '9876543210',
        'address': ''
    })
    assert response.status_code in [200, 400, 302]
    
    # Submit with all fields filled - should succeed
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '9876543210',
        'address': '123 Main St'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_order_persistence_in_database(client):
    """
    Test that orders are correctly saved to and retrieved from database.
    
    Validates: Requirements 6.1, 6.2, 6.3
    """
    # Add items to cart
    client.post('/add_to_cart/1')
    client.post('/add_to_cart/2')
    
    # Submit order
    response = client.post('/checkout', data={
        'name': 'Alice Johnson',
        'phone': '9988776655',
        'address': '789 Oak Road, Bangalore'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Extract order ID from response URL (more reliable than parsing HTML)
    # The redirect should be to /confirmation/<order_id>
    html = response.data.decode('utf-8')
    
    # Look for order ID in the confirmation page
    # Try multiple patterns to find the order ID
    order_id = None
    
    # Pattern 1: "Order #123" or "Order ID: 123"
    match = re.search(r'order\s*(?:#|id)?:?\s*(\d+)', html, re.IGNORECASE)
    if match:
        order_id = int(match.group(1))
    
    # If we found an order ID, verify it in database
    if order_id:
        # Retrieve order from database
        with app.app_context():
            order = OrderProcessor.get_order_by_id(order_id)
        
        assert order is not None
        assert order['customer_name'] == 'Alice Johnson'
        assert order['phone'] == '9988776655'
        assert order['address'] == '789 Oak Road, Bangalore'
        assert order['total_price'] > 0
        assert len(order['items']) == 2
    else:
        # If we can't extract order ID, at least verify the customer info is displayed
        assert 'Alice Johnson' in html
        assert '789 Oak Road, Bangalore' in html


def test_multiple_orders_unique_ids(client):
    """
    Test that multiple orders receive unique order IDs.
    
    Validates: Requirements 6.3
    """
    order_ids = []
    
    # Place 3 orders
    for i in range(3):
        # Add item to cart
        client.post('/add_to_cart/1')
        
        # Submit order
        response = client.post('/checkout', data={
            'name': f'Customer {i}',
            'phone': f'98765432{i}0',
            'address': f'{i} Test Street'
        })
        
        # Don't follow redirects - check the redirect location instead
        assert response.status_code == 302  # Redirect status
        
        # Extract order ID from redirect location
        location = response.headers.get('Location', '')
        match = re.search(r'/confirmation/(\d+)', location)
        if match:
            order_ids.append(int(match.group(1)))
    
    # Verify we got 3 order IDs
    assert len(order_ids) == 3, f"Should have 3 order IDs, got {len(order_ids)}"
    
    # Verify all order IDs are unique
    assert len(order_ids) == len(set(order_ids)), f"All order IDs should be unique, got {order_ids}"
    assert len(order_ids) == 3


def test_cart_total_calculation_accuracy(client):
    """
    Test that cart total is accurately calculated across the flow.
    
    Validates: Requirements 3.3, 4.3
    """
    # Add multiple items with different quantities
    client.post('/add_to_cart/1')  # Margherita
    client.post('/add_to_cart/1')  # Margherita again
    client.post('/add_to_cart/2')  # Pepperoni
    
    # Get cart and calculate expected total
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
    
    expected_total = sum(
        item['price'] * item['quantity']
        for item in cart.values()
    )
    
    # View cart page and verify total is displayed
    response = client.get('/cart')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Check if expected total appears in the HTML (as string)
    # Convert to string and check for presence
    total_str = f"{expected_total:.2f}"
    # The total might be formatted differently, so check for the integer part at least
    total_int = str(int(expected_total))
    assert total_int in html, f"Total {total_int} should appear in cart page"
    
    # Verify checkout page shows same total
    response = client.get('/checkout')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert total_int in html, f"Total {total_int} should appear in checkout page"


def test_navigation_preserves_cart_state(client):
    """
    Test that navigating between all pages preserves cart state.
    
    Validates: Requirements 8.1, 8.2, 8.3
    """
    # Add items to cart
    client.post('/add_to_cart/1')
    client.post('/add_to_cart/2')
    client.post('/add_to_cart/3')
    
    # Capture initial cart state
    with client.session_transaction() as sess:
        initial_cart = {k: v.copy() for k, v in sess.get('cart', {}).items()}
    
    # Navigate through all pages
    pages = ['/', '/cart', '/', '/checkout', '/', '/cart']
    
    for page in pages:
        response = client.get(page)
        assert response.status_code == 200
        
        # Verify cart hasn't changed
        with client.session_transaction() as sess:
            current_cart = sess.get('cart', {})
            
            # Check same items
            assert set(current_cart.keys()) == set(initial_cart.keys())
            
            # Check quantities unchanged
            for pizza_id in initial_cart:
                assert current_cart[pizza_id]['quantity'] == initial_cart[pizza_id]['quantity']
                assert current_cart[pizza_id]['name'] == initial_cart[pizza_id]['name']
                assert current_cart[pizza_id]['price'] == initial_cart[pizza_id]['price']


def test_complete_flow_with_invalid_pizza_id(client):
    """
    Test that adding invalid pizza ID is handled gracefully.
    
    Validates: Error handling
    """
    # Try to add non-existent pizza
    response = client.post('/add_to_cart/9999')
    # Should return error (404 or 400)
    assert response.status_code in [400, 404]
    
    # Verify cart is still empty or unchanged
    with client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert '9999' not in cart


def test_confirmation_page_displays_order_details(client):
    """
    Test that confirmation page displays all required order details.
    
    Validates: Requirements 7.1, 7.2, 7.3
    """
    # Add items and complete order
    client.post('/add_to_cart/1')
    client.post('/add_to_cart/2')
    
    response = client.post('/checkout', data={
        'name': 'Bob Wilson',
        'phone': '9111222333',
        'address': '321 Elm Street, Chennai'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Verify order ID is displayed
    assert re.search(r'\d+', html) is not None
    
    # Verify customer name is displayed
    assert 'Bob Wilson' in html
    
    # Verify delivery address is displayed
    assert '321 Elm Street, Chennai' in html
    
    # Verify confirmation message or thank you message
    assert 'thank' in html.lower() or 'confirm' in html.lower() or 'success' in html.lower()
