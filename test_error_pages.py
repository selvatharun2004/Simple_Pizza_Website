"""
Unit tests for custom error pages
"""
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_404_error_page(client):
    """Test that 404 error page is displayed for non-existent routes"""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page Not Found' in response.data
    assert b'Back to Homepage' in response.data


def test_404_error_page_uses_template(client):
    """Test that 404 error page uses the custom template"""
    response = client.get('/this-does-not-exist')
    assert response.status_code == 404
    # Check for template-specific content
    assert b'Pizza Shop' in response.data
    assert b"doesn't exist" in response.data


def test_500_error_handler_registered(client):
    """Test that 500 error handler is registered"""
    # We can't easily trigger a 500 error in tests without modifying the app
    # But we can verify the error handler exists
    from app import app as flask_app
    assert 500 in flask_app.error_handler_spec[None]


def test_404_includes_navigation(client):
    """Test that 404 page includes navigation back to homepage"""
    response = client.get('/invalid-route')
    assert response.status_code == 404
    # Check for link to homepage
    assert b'href="/"' in response.data
