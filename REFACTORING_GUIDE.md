# Pizza Shop Application - Refactored Structure

## Overview

The application has been refactored from a monolithic `app.py` file into a modular structure for better maintainability, testability, and scalability.

## New File Structure

```
pizza-shop-website/
├── app.py                      # Original monolithic file (kept for reference)
├── app_new.py                  # New modular application entry point
├── config.py                   # Configuration settings
├── database.py                 # Database connection and initialization
├── requirements.txt            # Python dependencies
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── menu_service.py        # Menu operations
│   ├── cart_manager.py        # Cart operations
│   └── order_processor.py     # Order processing
│
├── routes/                     # Route handlers (controllers)
│   ├── __init__.py
│   ├── main_routes.py         # Homepage routes
│   ├── cart_routes.py         # Cart routes
│   ├── order_routes.py        # Checkout and order routes
│   └── error_handlers.py      # Error page handlers
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── cart.html
│   ├── checkout.html
│   ├── confirmation.html
│   ├── 404.html
│   └── 500.html
│
├── static/                     # Static assets
│   └── css/
│       └── style.css
│
└── tests/                      # Test files
    ├── test_menu_service.py
    ├── test_cart_manager.py
    ├── test_order_processor.py
    ├── test_cart_page.py
    ├── test_checkout_route.py
    ├── test_e2e_user_flow.py
    └── ...
```

## Module Descriptions

### Core Application Files

#### `app_new.py`

- Main application entry point using the application factory pattern
- Creates and configures the Flask application
- Registers blueprints and error handlers
- Initializes the database

#### `config.py`

- Configuration classes for different environments (Development, Production, Testing)
- Centralizes all configuration settings
- Environment-specific settings

#### `database.py`

- Database connection management
- Database initialization and schema creation
- Sample data population

### Services Layer (`services/`)

Business logic separated from route handlers:

#### `menu_service.py`

- `MenuService.get_all_pizzas()` - Retrieve all pizzas
- `MenuService.get_pizza_by_id(pizza_id)` - Get specific pizza

#### `cart_manager.py`

- `CartManager.add_item()` - Add item to cart
- `CartManager.get_cart()` - Retrieve cart contents
- `CartManager.get_cart_total()` - Calculate total
- `CartManager.remove_item()` - Remove item
- `CartManager.clear_cart()` - Empty cart
- `CartManager.is_empty()` - Check if cart is empty

#### `order_processor.py`

- `OrderProcessor.create_order()` - Save order to database
- `OrderProcessor.get_order_by_id()` - Retrieve order details

### Routes Layer (`routes/`)

HTTP request handlers organized by feature:

#### `main_routes.py`

- `GET /` - Homepage with menu display

#### `cart_routes.py`

- `POST /add_to_cart/<pizza_id>` - Add item to cart
- `GET /cart` - Display cart
- `POST /remove_from_cart/<pizza_id>` - Remove item

#### `order_routes.py`

- `GET /checkout` - Display checkout form
- `POST /checkout` - Process order
- `GET /confirmation/<order_id>` - Order confirmation

#### `error_handlers.py`

- 404 error handler
- 500 error handler

## Benefits of Refactored Structure

### 1. Separation of Concerns

- Business logic (services) separated from HTTP handling (routes)
- Database operations isolated in dedicated module
- Configuration centralized

### 2. Improved Testability

- Each module can be tested independently
- Easier to mock dependencies
- Clear boundaries between components

### 3. Better Maintainability

- Smaller, focused files are easier to understand
- Changes to one feature don't affect others
- Clear file organization

### 4. Scalability

- Easy to add new features (new blueprints/services)
- Can split into microservices if needed
- Application factory pattern supports multiple instances

### 5. Reusability

- Services can be imported and used in different contexts
- Business logic can be reused across different routes
- Configuration can be easily switched

## Migration Guide

### Running the Refactored Application

**Option 1: Use the new modular version**

```bash
python app_new.py
```

**Option 2: Keep using the original (for backward compatibility)**

```bash
python app.py
```

### Updating Tests

Tests need to be updated to import from the new modules:

**Old imports:**

```python
from app import app, MenuService, CartManager, OrderProcessor
```

**New imports:**

```python
from app_new import app
from services import MenuService, CartManager, OrderProcessor
```

### Environment Configuration

Set the configuration environment:

```python
# Development (default)
app = create_app('development')

# Production
app = create_app('production')

# Testing
app = create_app('testing')
```

## Key Differences from Original

### Blueprint Registration

Routes are now organized into blueprints:

- `main_bp` - Main routes
- `cart_bp` - Cart routes
- `order_bp` - Order routes

### URL Generation

When using `url_for()`, include the blueprint name:

**Old:**

```python
redirect(url_for('cart'))
```

**New:**

```python
redirect(url_for('cart.cart'))
```

### Database Connection

Database path is now configurable via config:

```python
database_path = app.config.get('DATABASE', 'pizza_shop.db')
```

## Best Practices

1. **Keep services stateless** - Services should not maintain state between requests
2. **Use blueprints for feature grouping** - Related routes should be in the same blueprint
3. **Centralize configuration** - All settings should be in `config.py`
4. **Log appropriately** - Use the logging module for debugging and monitoring
5. **Handle errors gracefully** - Always catch and log exceptions

## Future Enhancements

Possible improvements to the structure:

1. **Add models layer** - Create ORM models using SQLAlchemy
2. **Add validators** - Separate validation logic into dedicated modules
3. **Add middleware** - Request/response processing middleware
4. **Add API versioning** - Support multiple API versions
5. **Add caching** - Implement Redis or similar for session/data caching
6. **Add authentication** - User login and authentication system
7. **Add admin panel** - Management interface for pizzas and orders

## Backward Compatibility

The original `app.py` file is preserved for backward compatibility. Both versions can coexist:

- `app.py` - Original monolithic version
- `app_new.py` - New modular version

Choose the version that best fits your needs. For new development, use `app_new.py`.
