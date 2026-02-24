"""
Tests for cart page template rendering
"""
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from app import app, init_db, CartManager


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_cart_page_empty_cart_message(client):
    """Test that empty cart displays 'Cart is empty' message"""
    # Request cart page with empty cart
    response = client.get('/cart')
    
    assert response.status_code == 200
    assert b'Cart is empty' in response.data


def test_cart_page_displays_items_in_table(client):
    """Test that cart page displays items in a table with name, price, quantity"""
    # Add items to cart using the client session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
    
    # Request cart page
    response = client.get('/cart')
    
    assert response.status_code == 200
    # Check for table structure
    assert b'<table' in response.data
    assert b'Pizza Name' in response.data
    assert b'Price' in response.data
    assert b'Quantity' in response.data
    
    # Check for pizza items
    assert b'Margherita' in response.data
    assert b'299.00' in response.data
    assert b'Pepperoni' in response.data
    assert b'399.00' in response.data


def test_cart_page_shows_remove_buttons(client):
    """Test that each cart item has a remove button"""
    # Add items to cart using the client session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
    
    # Request cart page
    response = client.get('/cart')
    
    assert response.status_code == 200
    # Check for remove buttons
    assert b'Remove' in response.data
    assert b'/remove_from_cart/1' in response.data
    assert b'/remove_from_cart/2' in response.data


def test_cart_page_displays_total_price(client):
    """Test that cart page displays total price at bottom"""
    # Add items to cart using the client session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
    
    # Request cart page
    response = client.get('/cart')
    
    assert response.status_code == 200
    # Check for total
    assert b'Total' in response.data
    assert b'698.00' in response.data  # 299 + 399


def test_cart_page_shows_checkout_button(client):
    """Test that cart page shows 'Proceed to Checkout' button"""
    # Add item to cart using the client session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Request cart page
    response = client.get('/cart')
    
    assert response.status_code == 200
    # Check for checkout button
    assert b'Proceed to Checkout' in response.data
    assert b'/checkout' in response.data


def test_remove_from_cart_route(client):
    """Test that remove_from_cart route works correctly"""
    # Add items to cart using the client session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
    
    # Remove one item
    response = client.post('/remove_from_cart/1', follow_redirects=True)
    
    assert response.status_code == 200
    # Check that Margherita is removed but Pepperoni remains
    assert b'Margherita' not in response.data
    assert b'Pepperoni' in response.data


def test_cart_page_shows_subtotal_for_each_item(client):
    """Test that cart page shows subtotal (price * quantity) for each item"""
    # Add item with quantity > 1 using the client session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2}
        }
    
    # Request cart page
    response = client.get('/cart')
    
    assert response.status_code == 200
    # Check for subtotal column
    assert b'Subtotal' in response.data
    # Check for calculated subtotal (299 * 2 = 598)
    assert b'598.00' in response.data


# Feature: pizza-shop-website, Property 4: Cart Display Completeness
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
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
def test_property_cart_display_completeness(client, cart_items):
    """
    **Validates: Requirements 3.1, 3.2**
    
    Property 4: Cart Display Completeness
    
    For any item in the cart, the rendered cart page should display 
    the pizza name, price, and quantity for that item.
    """
    from markupsafe import escape
    
    # Set up the cart with the generated items
    with client.session_transaction() as sess:
        sess['cart'] = cart_items
    
    # Request the cart page
    response = client.get('/cart')
    html_content = response.data.decode('utf-8')
    
    # Verify response is successful
    assert response.status_code == 200, "Cart page should be accessible"
    
    # Property: For each item in the cart, verify name, price, and quantity are displayed
    for pizza_id, item in cart_items.items():
        pizza_name = item['name']
        pizza_price = item['price']
        pizza_quantity = item['quantity']
        
        # Verify pizza name appears in the rendered HTML (accounting for escaping)
        escaped_name = str(escape(pizza_name))
        assert escaped_name in html_content, \
            f"Pizza name '{pizza_name}' (escaped as '{escaped_name}') should appear in cart page"
        
        # Verify price appears in the rendered HTML (formatted as INR with 2 decimal places)
        price_str = f"{pizza_price:.2f}"
        assert price_str in html_content, \
            f"Pizza price '{price_str}' should appear in cart page for {pizza_name}"
        
        # Verify quantity appears in the rendered HTML
        quantity_str = str(pizza_quantity)
        assert quantity_str in html_content, \
            f"Pizza quantity '{quantity_str}' should appear in cart page for {pizza_name}"


# Feature: pizza-shop-website, Property 6: Remove Button Presence
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
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
def test_property_remove_button_presence(client, cart_items):
    """
    **Validates: Requirements 4.1**
    
    Property 6: Remove Button Presence
    
    For any item in the cart, the rendered cart page should include 
    a remove button for that item.
    """
    # Set up the cart with the generated items
    with client.session_transaction() as sess:
        sess['cart'] = cart_items
    
    # Request the cart page
    response = client.get('/cart')
    html_content = response.data.decode('utf-8')
    
    # Verify response is successful
    assert response.status_code == 200, "Cart page should be accessible"
    
    # Property: For each item in the cart, verify a remove button exists
    for pizza_id, item in cart_items.items():
        pizza_name = item['name']
        
        # Verify that a remove button/link exists for this pizza_id
        # The remove button should link to /remove_from_cart/<pizza_id>
        remove_url = f"/remove_from_cart/{pizza_id}"
        assert remove_url in html_content, \
            f"Remove button with URL '{remove_url}' should exist for pizza '{pizza_name}' (ID: {pizza_id})"
