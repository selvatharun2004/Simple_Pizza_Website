import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from app import app, init_db, CartManager
import os


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Use a test database
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_checkout_route_with_items_in_cart(client):
    """Test that checkout page displays when cart has items"""
    # Add items to cart using session
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
    
    # Access checkout page
    response = client.get('/checkout')
    
    # Should render checkout page successfully
    assert response.status_code == 200
    assert b'Checkout' in response.data
    assert b'Delivery Information' in response.data
    assert b'Order Summary' in response.data
    
    # Should display cart items
    assert b'Margherita' in response.data
    assert b'Pepperoni' in response.data
    
    # Should display total
    assert b'Total:' in response.data


def test_checkout_route_redirects_when_cart_empty(client):
    """Test that checkout redirects to cart page when cart is empty"""
    # Ensure cart is empty
    with client.session_transaction() as sess:
        sess['cart'] = {}
    
    # Try to access checkout page
    response = client.get('/checkout', follow_redirects=False)
    
    # Should redirect to cart page
    assert response.status_code == 302
    assert '/cart' in response.location


def test_checkout_route_redirects_when_no_cart_session(client):
    """Test that checkout redirects when there's no cart in session"""
    # Access checkout page without setting up cart
    response = client.get('/checkout', follow_redirects=False)
    
    # Should redirect to cart page
    assert response.status_code == 302
    assert '/cart' in response.location


def test_checkout_displays_correct_total(client):
    """Test that checkout page displays correct cart total"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '3': {'name': 'Vegetarian', 'price': 349.0, 'quantity': 1}
        }
    
    # Access checkout page
    response = client.get('/checkout')
    
    # Calculate expected total: (299 * 2) + (349 * 1) = 947.0
    assert response.status_code == 200
    assert b'947.00' in response.data


def test_checkout_form_fields_present(client):
    """Test that checkout page contains all required form fields"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Access checkout page
    response = client.get('/checkout')
    
    assert response.status_code == 200
    # Check for form fields
    assert b'name="name"' in response.data
    assert b'name="phone"' in response.data
    assert b'name="address"' in response.data
    assert b'Place Order' in response.data


# Feature: pizza-shop-website, Property 9: Checkout Displays Cart Total
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
def test_property_checkout_displays_cart_total(client, cart_items):
    """
    **Validates: Requirements 5.2**
    
    Property 9: Checkout Displays Cart Total
    
    For any cart state when viewing the checkout page, the displayed 
    order summary total should match the cart total.
    """
    # Set up the cart with the generated items
    with client.session_transaction() as sess:
        sess['cart'] = cart_items
    
    # Calculate the expected total
    expected_total = sum(item['price'] * item['quantity'] for item in cart_items.values())
    
    # Request the checkout page
    response = client.get('/checkout')
    html_content = response.data.decode('utf-8')
    
    # Verify response is successful
    assert response.status_code == 200, "Checkout page should be accessible with items in cart"
    
    # Property: The displayed total should match the calculated cart total
    # Format the expected total as it would appear in the HTML (2 decimal places)
    expected_total_str = f"{expected_total:.2f}"
    
    assert expected_total_str in html_content, \
        f"Checkout page should display total '{expected_total_str}' matching the cart total"
    
    # Additionally verify that "Total:" label is present in the order summary
    assert "Total:" in html_content or "Total" in html_content, \
        "Checkout page should have a 'Total' label in the order summary"


# Feature: pizza-shop-website, Property 8: Checkout Form Validation
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=st.text(max_size=100),
    phone=st.text(max_size=50),
    address=st.text(max_size=200)
)
def test_property_checkout_form_validation(client, name, phone, address):
    """
    **Validates: Requirements 5.3, 5.4**
    
    Property 8: Checkout Form Validation
    
    For any combination of customer name, phone, and address inputs, 
    order submission should succeed if and only if all three fields are non-empty.
    """
    # Set up cart with at least one item
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Test Pizza', 'price': 299.0, 'quantity': 1}
        }
    
    # Submit checkout form with generated inputs
    response = client.post('/checkout', data={
        'name': name,
        'phone': phone,
        'address': address
    }, follow_redirects=False)
    
    # Determine if all fields are non-empty (after stripping whitespace)
    all_fields_valid = (
        name.strip() != '' and 
        phone.strip() != '' and 
        address.strip() != ''
    )
    
    # Property: Order submission should succeed if and only if all fields are non-empty
    if all_fields_valid:
        # Should redirect to confirmation page (success)
        assert response.status_code == 302, \
            f"Expected redirect (302) for valid inputs, got {response.status_code}"
        assert '/confirmation/' in response.location, \
            f"Expected redirect to confirmation page, got {response.location}"
        
        # Cart should be cleared after successful order
        with client.session_transaction() as sess:
            assert sess.get('cart', {}) == {}, \
                "Cart should be cleared after successful order submission"
    else:
        # Should return 400 error (validation failure)
        assert response.status_code == 400, \
            f"Expected 400 error for invalid inputs (name='{name}', phone='{phone}', address='{address}'), got {response.status_code}"
        assert b'All fields are required' in response.data, \
            "Error message should indicate all fields are required"
        
        # Cart should NOT be cleared on validation failure
        with client.session_transaction() as sess:
            assert '1' in sess.get('cart', {}), \
                "Cart should be preserved when validation fails"


def test_checkout_post_with_valid_data(client):
    """Test that checkout POST creates order and redirects to confirmation"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
    
    # Submit checkout form with valid data
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Main St, City'
    }, follow_redirects=False)
    
    # Should redirect to confirmation page
    assert response.status_code == 302
    assert '/confirmation/' in response.location
    
    # Cart should be cleared
    with client.session_transaction() as sess:
        assert sess.get('cart', {}) == {}


def test_checkout_post_with_empty_name(client):
    """Test that checkout POST validates empty name field"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Submit with empty name
    response = client.post('/checkout', data={
        'name': '',
        'phone': '1234567890',
        'address': '123 Main St'
    })
    
    # Should return 400 error
    assert response.status_code == 400
    assert b'All fields are required' in response.data
    
    # Cart should not be cleared
    with client.session_transaction() as sess:
        assert '1' in sess.get('cart', {})


def test_checkout_post_with_empty_phone(client):
    """Test that checkout POST validates empty phone field"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Submit with empty phone
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '',
        'address': '123 Main St'
    })
    
    # Should return 400 error
    assert response.status_code == 400
    assert b'All fields are required' in response.data


def test_checkout_post_with_empty_address(client):
    """Test that checkout POST validates empty address field"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Submit with empty address
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '1234567890',
        'address': ''
    })
    
    # Should return 400 error
    assert response.status_code == 400
    assert b'All fields are required' in response.data


def test_checkout_post_with_whitespace_only_fields(client):
    """Test that checkout POST validates whitespace-only fields"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Submit with whitespace-only fields
    response = client.post('/checkout', data={
        'name': '   ',
        'phone': '  ',
        'address': '   '
    })
    
    # Should return 400 error
    assert response.status_code == 400
    assert b'All fields are required' in response.data


def test_checkout_post_with_missing_fields(client):
    """Test that checkout POST handles missing form fields"""
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
    
    # Submit with missing fields
    response = client.post('/checkout', data={
        'name': 'John Doe'
        # phone and address missing
    })
    
    # Should return 400 error
    assert response.status_code == 400
    assert b'All fields are required' in response.data


def test_checkout_post_creates_order_in_database(client):
    """Test that checkout POST saves order to database"""
    from app import get_db_connection
    
    # Add items to cart
    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '3': {'name': 'Vegetarian', 'price': 349.0, 'quantity': 1}
        }
    
    # Submit checkout form
    response = client.post('/checkout', data={
        'name': 'Jane Smith',
        'phone': '9876543210',
        'address': '456 Oak Ave, Town'
    }, follow_redirects=False)
    
    # Extract order_id from redirect location
    assert response.status_code == 302
    order_id = int(response.location.split('/')[-1])
    
    # Verify order exists in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    
    assert order is not None
    assert order['customer_name'] == 'Jane Smith'
    assert order['phone'] == '9876543210'
    assert order['address'] == '456 Oak Ave, Town'
    assert order['total_price'] == 947.0  # (299 * 2) + (349 * 1)
    
    # Verify order items
    cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
    items = cursor.fetchall()
    
    assert len(items) == 2
    conn.close()


def test_checkout_post_with_empty_cart_redirects(client):
    """Test that checkout POST redirects when cart is empty"""
    # Ensure cart is empty
    with client.session_transaction() as sess:
        sess['cart'] = {}
    
    # Try to submit checkout
    response = client.post('/checkout', data={
        'name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Main St'
    }, follow_redirects=False)
    
    # Should redirect to cart page
    assert response.status_code == 302
    assert '/cart' in response.location


def test_confirmation_page_displays_order_details(client):
    """Test that confirmation page displays order information"""
    from app import OrderProcessor
    
    # Create an order directly
    cart_items = {
        '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2}
    }
    order_id = OrderProcessor.create_order(
        'Test User',
        '1234567890',
        '789 Test St',
        cart_items,
        598.0
    )
    
    # Access confirmation page
    response = client.get(f'/confirmation/{order_id}')
    
    assert response.status_code == 200
    assert b'Order Confirmed!' in response.data
    assert b'Test User' in response.data
    assert b'1234567890' in response.data
    assert b'789 Test St' in response.data
    assert b'Margherita' in response.data
    assert str(order_id).encode() in response.data


def test_confirmation_page_with_invalid_order_id(client):
    """Test that confirmation page handles non-existent order ID"""
    # Try to access confirmation with invalid order_id
    response = client.get('/confirmation/99999')
    
    # Should return 404
    assert response.status_code == 404
    assert b'Order not found' in response.data


# Feature: pizza-shop-website, Property 12: Confirmation Page Completeness
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    customer_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    phone=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
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
def test_property_confirmation_page_completeness(client, customer_name, phone, address, cart_items):
    """
    **Validates: Requirements 7.1, 7.2, 7.3**
    
    Property 12: Confirmation Page Completeness
    
    For any successfully saved order, the confirmation page should display 
    the order ID, customer name, and delivery address.
    """
    from app import OrderProcessor
    from markupsafe import escape
    
    # Calculate total price
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    
    # Create order in database
    order_id = OrderProcessor.create_order(
        customer_name,
        phone,
        address,
        cart_items,
        total_price
    )
    
    # Request the confirmation page
    response = client.get(f'/confirmation/{order_id}')
    html_content = response.data.decode('utf-8')
    
    # Verify response is successful
    assert response.status_code == 200, \
        f"Confirmation page should be accessible for order {order_id}"
    
    # Property: Confirmation page must display order ID
    assert str(order_id) in html_content, \
        f"Confirmation page should display order ID '{order_id}'"
    
    # Property: Confirmation page must display customer name (Jinja2/MarkupSafe escaped)
    # Jinja2 uses MarkupSafe's escape function which is compatible with HTML escaping
    escaped_customer_name = str(escape(customer_name))
    assert escaped_customer_name in html_content, \
        f"Confirmation page should display customer name '{customer_name}' (escaped as '{escaped_customer_name}')"
    
    # Property: Confirmation page must display delivery address (Jinja2/MarkupSafe escaped)
    escaped_address = str(escape(address))
    assert escaped_address in html_content, \
        f"Confirmation page should display delivery address '{address}' (escaped as '{escaped_address}')'"


# Feature: pizza-shop-website, Property 13: Cart Cleared After Order
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    customer_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    phone=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
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
def test_property_cart_cleared_after_order(client, customer_name, phone, address, cart_items):
    """
    **Validates: Requirements 7.4**
    
    Property 13: Cart Cleared After Order
    
    For any cart state, after successfully placing an order and reaching 
    the confirmation page, the cart should be empty.
    """
    # Set up the cart with the generated items
    with client.session_transaction() as sess:
        sess['cart'] = cart_items
    
    # Calculate total price
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    
    # Submit the checkout form with valid customer information
    response = client.post('/checkout', data={
        'name': customer_name,
        'phone': phone,
        'address': address
    }, follow_redirects=False)
    
    # Verify the order was successfully created (redirect to confirmation)
    assert response.status_code == 302, \
        f"Expected redirect (302) after successful order submission, got {response.status_code}"
    assert '/confirmation/' in response.location, \
        f"Expected redirect to confirmation page, got {response.location}"
    
    # Property: Cart should be empty after successful order placement
    with client.session_transaction() as sess:
        cart_after_order = sess.get('cart', {})
        assert cart_after_order == {}, \
            f"Cart should be empty after order placement, but contains: {cart_after_order}"
    
    # Follow the redirect to the confirmation page
    confirmation_response = client.get(response.location)
    
    # Verify we successfully reached the confirmation page
    assert confirmation_response.status_code == 200, \
        f"Confirmation page should be accessible, got status {confirmation_response.status_code}"
    
    # Verify cart remains empty even after viewing confirmation page
    with client.session_transaction() as sess:
        cart_after_confirmation = sess.get('cart', {})
        assert cart_after_confirmation == {}, \
            f"Cart should remain empty after viewing confirmation page, but contains: {cart_after_confirmation}"
