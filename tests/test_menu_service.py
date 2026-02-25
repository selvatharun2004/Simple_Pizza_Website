"""Unit tests for MenuService class"""
import pytest
import sqlite3
import os
from hypothesis import given, settings, strategies as st, HealthCheck
from app import MenuService, get_db_connection, init_db, DATABASE, app


@pytest.fixture
def test_db():
    """Create a test database"""
    # Use the existing database for testing
    init_db()
    yield
    # Cleanup is not needed as we're using the same database


def test_get_all_pizzas(test_db):
    """Test that get_all_pizzas returns all pizzas from database"""
    pizzas = MenuService.get_all_pizzas()
    
    # Should return a list
    assert isinstance(pizzas, list)
    
    # Should have at least the sample pizzas
    assert len(pizzas) >= 6
    
    # Each pizza should have id, name, and price
    for pizza in pizzas:
        assert 'id' in pizza
        assert 'name' in pizza
        assert 'price' in pizza
        assert isinstance(pizza['id'], int)
        assert isinstance(pizza['name'], str)
        assert isinstance(pizza['price'], float)


def test_get_pizza_by_id_existing(test_db):
    """Test that get_pizza_by_id returns correct pizza for valid ID"""
    # First get all pizzas to find a valid ID
    pizzas = MenuService.get_all_pizzas()
    assert len(pizzas) > 0
    
    # Get the first pizza by ID
    first_pizza_id = pizzas[0]['id']
    pizza = MenuService.get_pizza_by_id(first_pizza_id)
    
    # Should return a dictionary
    assert isinstance(pizza, dict)
    
    # Should have correct structure
    assert 'id' in pizza
    assert 'name' in pizza
    assert 'price' in pizza
    
    # Should match the pizza from get_all_pizzas
    assert pizza['id'] == pizzas[0]['id']
    assert pizza['name'] == pizzas[0]['name']
    assert pizza['price'] == pizzas[0]['price']


def test_get_pizza_by_id_nonexistent(test_db):
    """Test that get_pizza_by_id returns None for invalid ID"""
    # Use a very large ID that shouldn't exist
    pizza = MenuService.get_pizza_by_id(99999)
    
    # Should return None
    assert pizza is None


def test_get_all_pizzas_returns_sample_data(test_db):
    """Test that sample pizzas are present in the database"""
    pizzas = MenuService.get_all_pizzas()
    pizza_names = [p['name'] for p in pizzas]
    
    # Check that some expected pizzas are present
    expected_pizzas = ['Margherita', 'Pepperoni', 'Vegetarian']
    for expected in expected_pizzas:
        assert expected in pizza_names, f"{expected} should be in the menu"


# Feature: pizza-shop-website, Property 1: Complete Menu Display
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    pizza_name=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    pizza_price=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
def test_property_complete_menu_display(test_db, pizza_name, pizza_price):
    """
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
    
    Property 1: Complete Menu Display
    For any pizza in the database, the rendered menu page should contain 
    the pizza's name, price in INR, and an "Add to Cart" button.
    """
    from markupsafe import escape
    
    # Insert a test pizza into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pizzas (name, price) VALUES (?, ?)', (pizza_name, pizza_price))
    conn.commit()
    pizza_id = cursor.lastrowid
    conn.close()
    
    try:
        # Create a test client and render the homepage
        with app.test_client() as client:
            response = client.get('/')
            html_content = response.data.decode('utf-8')
            
            # Verify the pizza name appears in the rendered HTML (accounting for Jinja2/MarkupSafe escaping)
            escaped_name = str(escape(pizza_name))
            assert escaped_name in html_content, f"Pizza name '{pizza_name}' (escaped as '{escaped_name}') should appear in menu"
            
            # Verify the price appears in the rendered HTML (formatted as INR)
            # Price could be formatted in various ways, so check for the numeric value
            price_str = f"{pizza_price:.2f}"
            assert price_str in html_content or str(int(pizza_price)) in html_content, \
                f"Pizza price '{pizza_price}' should appear in menu"
            
            # Verify an "Add to Cart" button exists for this pizza
            # The button should reference the pizza_id
            assert f'add_to_cart/{pizza_id}' in html_content or f'add-to-cart/{pizza_id}' in html_content or \
                   f'pizza_id={pizza_id}' in html_content or f'data-pizza-id="{pizza_id}"' in html_content, \
                f"Add to Cart button for pizza {pizza_id} should exist in menu"
    finally:
        # Cleanup: remove the test pizza
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pizzas WHERE id = ?', (pizza_id,))
        conn.commit()
        conn.close()
