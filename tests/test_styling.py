"""
Test CSS styling and responsive design improvements
"""
import pytest
from app import app, init_db
import os


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_static_css_file_exists():
    """Test that the custom CSS file exists"""
    css_path = os.path.join('static', 'css', 'style.css')
    assert os.path.exists(css_path), "Custom CSS file should exist"


def test_base_template_includes_custom_css(client):
    """Test that base template includes link to custom CSS"""
    response = client.get('/')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Check that custom CSS is linked
    assert 'css/style.css' in html, "Base template should include custom CSS link"
    assert 'url_for' in html or '/static/css/style.css' in html, "CSS should be properly linked"


def test_homepage_has_pizza_card_class(client):
    """Test that homepage pizza cards have the custom pizza-card class"""
    response = client.get('/')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Check for pizza-card class
    assert 'pizza-card' in html, "Pizza cards should have pizza-card class for custom styling"


def test_homepage_has_feedback_message_container(client):
    """Test that homepage has feedback message container for visual feedback"""
    response = client.get('/')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Check for feedback message container
    assert 'feedback-message' in html, "Homepage should have feedback message container"
    assert 'feedback-text' in html, "Homepage should have feedback text element"


def test_checkout_has_order_summary_card_class(client):
    """Test that checkout page has order-summary-card class for sticky positioning"""
    # Add item to cart first
    client.post('/add_to_cart/1')
    
    response = client.get('/checkout')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Check for order-summary-card class
    assert 'order-summary-card' in html, "Checkout should have order-summary-card class"


def test_buttons_have_consistent_styling_classes(client):
    """Test that buttons across pages have consistent Bootstrap classes"""
    # Test homepage
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'btn btn-danger' in html, "Homepage should have danger buttons"
    
    # Test cart page
    client.post('/add_to_cart/1')
    response = client.get('/cart')
    html = response.data.decode('utf-8')
    assert 'btn btn-danger' in html, "Cart should have danger buttons"
    assert 'btn btn-outline-danger' in html or 'btn-sm btn-outline-danger' in html, "Cart should have outline buttons"
    assert 'btn btn-outline-secondary' in html, "Cart should have secondary buttons"


def test_forms_have_proper_styling_classes(client):
    """Test that forms have proper Bootstrap form classes"""
    # Add item to cart
    client.post('/add_to_cart/1')
    
    # Test checkout form
    response = client.get('/checkout')
    html = response.data.decode('utf-8')
    
    assert 'form-control' in html, "Forms should use form-control class"
    assert 'form-label' in html, "Forms should use form-label class"
    assert 'required' in html, "Forms should have required attributes"


def test_responsive_grid_layout(client):
    """Test that homepage uses responsive grid layout"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Check for responsive grid classes
    assert 'row-cols-1' in html, "Should have single column on mobile"
    assert 'row-cols-md-2' in html, "Should have 2 columns on medium screens"
    assert 'row-cols-lg-3' in html, "Should have 3 columns on large screens"


def test_cards_have_shadow_classes(client):
    """Test that cards have shadow classes for depth"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert 'shadow-sm' in html, "Cards should have shadow classes"


def test_navigation_has_proper_structure(client):
    """Test that navigation has proper Bootstrap navbar structure"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert 'navbar' in html, "Should have navbar"
    assert 'navbar-brand' in html, "Should have navbar brand"
    assert 'nav-link' in html, "Should have nav links"
    assert 'navbar-toggler' in html, "Should have mobile menu toggle"


def test_confirmation_page_has_success_icon(client):
    """Test that confirmation page has success icon"""
    # Create an order
    client.post('/add_to_cart/1')
    response = client.post('/checkout', data={
        'name': 'Test User',
        'phone': '1234567890',
        'address': 'Test Address'
    }, follow_redirects=True)
    
    html = response.data.decode('utf-8')
    
    # Check for success icon (SVG)
    assert 'svg' in html or 'success-icon' in html, "Confirmation should have success icon"


def test_mobile_responsive_meta_tag(client):
    """Test that pages have mobile responsive viewport meta tag"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert 'viewport' in html, "Should have viewport meta tag"
    assert 'width=device-width' in html, "Viewport should set device width"


def test_add_to_cart_button_has_loading_state_js(client):
    """Test that add to cart JavaScript includes loading state functionality"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Check for loading state JavaScript
    assert 'loading' in html, "JavaScript should include loading state"
    assert 'disabled' in html, "JavaScript should disable button during loading"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
