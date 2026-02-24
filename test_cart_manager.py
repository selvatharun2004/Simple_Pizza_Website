import pytest
from app import app, CartManager, init_db
from flask import session


@pytest.fixture
def client():
    """Create a test client with a test database"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_add_item_to_empty_cart(client):
    """Test adding a pizza to an empty cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        CartManager.add_item(1, 'Margherita', 299.0)
        cart = session['cart']
        
        assert '1' in cart
        assert cart['1']['name'] == 'Margherita'
        assert cart['1']['price'] == 299.0
        assert cart['1']['quantity'] == 1


def test_add_item_increments_quantity(client):
    """Test adding the same pizza twice increments quantity"""
    with app.test_request_context():
        session['cart'] = {}
        
        CartManager.add_item(1, 'Margherita', 299.0)
        CartManager.add_item(1, 'Margherita', 299.0)
        
        cart = session['cart']
        assert cart['1']['quantity'] == 2


def test_add_multiple_different_items(client):
    """Test adding different pizzas to cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        CartManager.add_item(1, 'Margherita', 299.0)
        CartManager.add_item(2, 'Pepperoni', 399.0)
        
        cart = session['cart']
        assert len(cart) == 2
        assert '1' in cart
        assert '2' in cart


def test_get_cart_empty(client):
    """Test getting an empty cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        cart = CartManager.get_cart()
        assert cart == {}


def test_get_cart_with_items(client):
    """Test getting cart with items"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2}
        }
        
        cart = CartManager.get_cart()
        assert '1' in cart
        assert cart['1']['quantity'] == 2


def test_get_cart_total_empty(client):
    """Test calculating total for empty cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        total = CartManager.get_cart_total()
        assert total == 0.0


def test_get_cart_total_single_item(client):
    """Test calculating total for single item"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
        
        total = CartManager.get_cart_total()
        assert total == 299.0


def test_get_cart_total_multiple_quantities(client):
    """Test calculating total for item with multiple quantities"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 3}
        }
        
        total = CartManager.get_cart_total()
        assert total == 897.0


def test_get_cart_total_multiple_items(client):
    """Test calculating total for multiple different items"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
        
        total = CartManager.get_cart_total()
        assert total == 997.0  # (299 * 2) + (399 * 1)


def test_is_empty_true(client):
    """Test is_empty returns True for empty cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        assert CartManager.is_empty() is True


def test_is_empty_false(client):
    """Test is_empty returns False for cart with items"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
        
        assert CartManager.is_empty() is False


def test_cart_initializes_if_not_exists(client):
    """Test that cart is initialized if it doesn't exist in session"""
    with app.test_request_context():
        # Don't initialize cart in session
        cart = CartManager.get_cart()
        assert cart == {}
        assert isinstance(cart, dict)


# Property-Based Tests using Hypothesis

from hypothesis import given, strategies as st, settings, HealthCheck


# Feature: pizza-shop-website, Property 2: Add to Cart Creates Entry
# **Validates: Requirements 2.1**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    pizza_id=st.integers(min_value=1, max_value=1000),
    pizza_name=st.text(min_size=1, max_size=50),
    price=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    existing_cart=st.dictionaries(
        keys=st.integers(min_value=1, max_value=1000).map(str),
        values=st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'price': st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        max_size=10
    )
)
def test_property_add_to_cart_creates_entry(client, pizza_id, pizza_name, price, existing_cart):
    """
    Property 2: Add to Cart Creates Entry
    
    For any pizza and any cart state, adding that pizza to the cart 
    should result in the cart containing an entry for that pizza.
    """
    with app.test_request_context():
        # Set up the existing cart state
        session['cart'] = existing_cart
        
        # Record if pizza already existed and its original quantity
        pizza_id_str = str(pizza_id)
        pizza_existed = pizza_id_str in existing_cart
        original_quantity = existing_cart.get(pizza_id_str, {}).get('quantity', 0)
        
        # Add the pizza to the cart
        CartManager.add_item(pizza_id, pizza_name, price)
        
        # Get the updated cart
        cart = session['cart']
        
        # Property: The cart must contain an entry for the added pizza
        assert pizza_id_str in cart, f"Pizza {pizza_id} should be in cart after adding"
        
        # If pizza already existed, it should have incremented quantity
        # and kept original name/price. If new, it should have the provided details.
        if pizza_existed:
            # Quantity should have incremented
            assert cart[pizza_id_str]['quantity'] == original_quantity + 1
            # Name and price should remain unchanged from original
            assert cart[pizza_id_str]['name'] == existing_cart[pizza_id_str]['name']
            assert cart[pizza_id_str]['price'] == existing_cart[pizza_id_str]['price']
        else:
            # New entry should have the provided details
            assert cart[pizza_id_str]['name'] == pizza_name
            assert cart[pizza_id_str]['price'] == price
            assert cart[pizza_id_str]['quantity'] == 1


# Feature: pizza-shop-website, Property 3: Repeated Addition Increments Quantity
# **Validates: Requirements 2.2**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    pizza_id=st.integers(min_value=1, max_value=1000),
    pizza_name=st.text(min_size=1, max_size=50),
    price=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    initial_quantity=st.integers(min_value=1, max_value=50),
    other_items=st.dictionaries(
        keys=st.integers(min_value=1, max_value=1000).filter(lambda x: x != 1).map(str),
        values=st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'price': st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        max_size=10
    )
)
def test_property_repeated_addition_increments_quantity(client, pizza_id, pizza_name, price, initial_quantity, other_items):
    """
    Property 3: Repeated Addition Increments Quantity
    
    For any pizza already in the cart, adding it again should increment 
    its quantity by 1 while keeping all other cart items unchanged.
    """
    with app.test_request_context():
        # Set up cart with the target pizza already present
        pizza_id_str = str(pizza_id)
        initial_cart = {
            pizza_id_str: {
                'name': pizza_name,
                'price': price,
                'quantity': initial_quantity
            }
        }
        
        # Add other items to the cart (ensuring they don't conflict with our target pizza)
        for item_id, item_data in other_items.items():
            if item_id != pizza_id_str:
                initial_cart[item_id] = item_data
        
        session['cart'] = initial_cart
        
        # Take a snapshot of other items before adding
        other_items_snapshot = {k: v.copy() for k, v in initial_cart.items() if k != pizza_id_str}
        
        # Add the same pizza again
        CartManager.add_item(pizza_id, pizza_name, price)
        
        # Get the updated cart
        cart = session['cart']
        
        # Property 1: The target pizza's quantity should be incremented by exactly 1
        assert cart[pizza_id_str]['quantity'] == initial_quantity + 1, \
            f"Expected quantity {initial_quantity + 1}, got {cart[pizza_id_str]['quantity']}"
        
        # Property 2: The target pizza's name and price should remain unchanged
        assert cart[pizza_id_str]['name'] == pizza_name
        assert cart[pizza_id_str]['price'] == price
        
        # Property 3: All other cart items should remain completely unchanged
        for item_id, original_data in other_items_snapshot.items():
            assert item_id in cart, f"Item {item_id} should still be in cart"
            assert cart[item_id]['name'] == original_data['name'], \
                f"Item {item_id} name should be unchanged"
            assert cart[item_id]['price'] == original_data['price'], \
                f"Item {item_id} price should be unchanged"
            assert cart[item_id]['quantity'] == original_data['quantity'], \
                f"Item {item_id} quantity should be unchanged"
        
        # Property 4: No new items should be added (cart size should remain the same)
        assert len(cart) == len(initial_cart), \
            f"Cart size should remain {len(initial_cart)}, got {len(cart)}"


# Feature: pizza-shop-website, Property 5: Cart Total Invariant
# **Validates: Requirements 3.3, 4.3**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    cart_items=st.dictionaries(
        keys=st.integers(min_value=1, max_value=1000).map(str),
        values=st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'price': st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        min_size=0,
        max_size=20
    )
)
def test_property_cart_total_invariant(client, cart_items):
    """
    Property 5: Cart Total Invariant
    
    For any cart state, the displayed total price should equal the sum 
    of (price × quantity) for all items in the cart.
    """
    with app.test_request_context():
        # Set up the cart with the generated items
        session['cart'] = cart_items
        
        # Calculate the expected total manually
        expected_total = sum(
            item['price'] * item['quantity'] 
            for item in cart_items.values()
        )
        
        # Get the total from CartManager
        actual_total = CartManager.get_cart_total()
        
        # Property: The cart total must equal the sum of (price × quantity) for all items
        assert abs(actual_total - expected_total) < 0.01, \
            f"Cart total mismatch: expected {expected_total}, got {actual_total}"


# Feature: pizza-shop-website, Property 7: Remove Eliminates Item
# **Validates: Requirements 4.2**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    target_pizza_id=st.integers(min_value=1, max_value=1000),
    target_pizza_data=st.fixed_dictionaries({
        'name': st.text(min_size=1, max_size=50),
        'price': st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
        'quantity': st.integers(min_value=1, max_value=100)
    }),
    other_items=st.dictionaries(
        keys=st.integers(min_value=1, max_value=1000).map(str),
        values=st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'price': st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        max_size=10
    )
)
def test_property_remove_eliminates_item(client, target_pizza_id, target_pizza_data, other_items):
    """
    Property 7: Remove Eliminates Item
    
    For any pizza in the cart, removing it should result in the cart 
    no longer containing that pizza.
    """
    with app.test_request_context():
        # Set up cart with the target pizza and other items
        target_pizza_id_str = str(target_pizza_id)
        initial_cart = {target_pizza_id_str: target_pizza_data}
        
        # Add other items to the cart (ensuring they don't conflict with target pizza)
        for item_id, item_data in other_items.items():
            if item_id != target_pizza_id_str:
                initial_cart[item_id] = item_data
        
        session['cart'] = initial_cart
        
        # Take a snapshot of other items before removal
        other_items_snapshot = {k: v.copy() for k, v in initial_cart.items() if k != target_pizza_id_str}
        
        # Remove the target pizza
        CartManager.remove_item(target_pizza_id)
        
        # Get the updated cart
        cart = session['cart']
        
        # Property 1: The target pizza should no longer be in the cart
        assert target_pizza_id_str not in cart, \
            f"Pizza {target_pizza_id} should not be in cart after removal"
        
        # Property 2: All other items should remain unchanged
        for item_id, original_data in other_items_snapshot.items():
            assert item_id in cart, f"Item {item_id} should still be in cart"
            assert cart[item_id]['name'] == original_data['name'], \
                f"Item {item_id} name should be unchanged"
            assert cart[item_id]['price'] == original_data['price'], \
                f"Item {item_id} price should be unchanged"
            assert cart[item_id]['quantity'] == original_data['quantity'], \
                f"Item {item_id} quantity should be unchanged"
        
        # Property 3: Cart size should equal the number of other items (initial cart minus the removed item)
        expected_size = len(other_items_snapshot)
        assert len(cart) == expected_size, \
            f"Cart size should be {expected_size}, got {len(cart)}"


def test_remove_item_from_cart(client):
    """Test removing a pizza from cart"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1}
        }
        
        CartManager.remove_item(1)
        cart = session['cart']
        
        assert '1' not in cart
        assert '2' in cart
        assert len(cart) == 1


def test_remove_item_not_in_cart(client):
    """Test removing a pizza that doesn't exist in cart"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 1}
        }
        
        # Should not raise an error
        CartManager.remove_item(999)
        cart = session['cart']
        
        assert '1' in cart
        assert len(cart) == 1


def test_remove_item_from_empty_cart(client):
    """Test removing from an empty cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        # Should not raise an error
        CartManager.remove_item(1)
        cart = session['cart']
        
        assert cart == {}


def test_clear_cart(client):
    """Test clearing all items from cart"""
    with app.test_request_context():
        session['cart'] = {
            '1': {'name': 'Margherita', 'price': 299.0, 'quantity': 2},
            '2': {'name': 'Pepperoni', 'price': 399.0, 'quantity': 1},
            '3': {'name': 'Vegetarian', 'price': 349.0, 'quantity': 3}
        }
        
        CartManager.clear_cart()
        cart = session['cart']
        
        assert cart == {}
        assert len(cart) == 0


def test_clear_empty_cart(client):
    """Test clearing an already empty cart"""
    with app.test_request_context():
        session['cart'] = {}
        
        CartManager.clear_cart()
        cart = session['cart']
        
        assert cart == {}


# Feature: pizza-shop-website, Property 14: Cart Persistence Across Navigation
# **Validates: Requirements 8.1, 8.2**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    cart_items=st.dictionaries(
        keys=st.integers(min_value=1, max_value=1000).map(str),
        values=st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'price': st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        min_size=0,
        max_size=20
    )
)
def test_property_cart_persistence_across_navigation(client, cart_items):
    """
    Property 14: Cart Persistence Across Navigation
    
    For any cart state, navigating from the homepage to the cart page 
    and back to the homepage should preserve all cart items with their 
    quantities unchanged.
    """
    with client.session_transaction() as sess:
        # Set up the initial cart state
        sess['cart'] = cart_items
    
    # Take a snapshot of the original cart state
    original_cart = {k: v.copy() for k, v in cart_items.items()}
    
    # Navigate to the homepage (GET /)
    response_home = client.get('/')
    assert response_home.status_code == 200, "Homepage should be accessible"
    
    # Navigate to the cart page (GET /cart)
    response_cart = client.get('/cart')
    assert response_cart.status_code == 200, "Cart page should be accessible"
    
    # Navigate back to the homepage (GET /)
    response_home_again = client.get('/')
    assert response_home_again.status_code == 200, "Homepage should be accessible again"
    
    # Retrieve the cart state after navigation
    with client.session_transaction() as sess:
        final_cart = sess.get('cart', {})
    
    # Property 1: The cart should still exist and have the same number of items
    assert len(final_cart) == len(original_cart), \
        f"Cart size should remain {len(original_cart)}, got {len(final_cart)}"
    
    # Property 2: All original items should still be present with unchanged data
    for pizza_id, original_item in original_cart.items():
        assert pizza_id in final_cart, \
            f"Pizza {pizza_id} should still be in cart after navigation"
        
        final_item = final_cart[pizza_id]
        
        # Verify name is unchanged
        assert final_item['name'] == original_item['name'], \
            f"Pizza {pizza_id} name should be '{original_item['name']}', got '{final_item['name']}'"
        
        # Verify price is unchanged (with floating point tolerance)
        assert abs(final_item['price'] - original_item['price']) < 0.01, \
            f"Pizza {pizza_id} price should be {original_item['price']}, got {final_item['price']}"
        
        # Verify quantity is unchanged
        assert final_item['quantity'] == original_item['quantity'], \
            f"Pizza {pizza_id} quantity should be {original_item['quantity']}, got {final_item['quantity']}"
    
    # Property 3: No new items should have been added
    for pizza_id in final_cart.keys():
        assert pizza_id in original_cart, \
            f"Unexpected pizza {pizza_id} found in cart after navigation"
