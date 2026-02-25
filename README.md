# 🍕 Pizza Shop Website

A full-featured pizza ordering website built with Flask, featuring a shopping cart, checkout system, and manager dashboard.

## Features

- **Pizza Menu**: Browse available pizzas with images and prices
- **Shopping Cart**: Add/remove items with real-time updates
- **Checkout System**: Complete order form with validation
- **Order Confirmation**: View order details after purchase
- **Manager Dashboard**: View all orders with pagination and detailed order information
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Error Handling**: Custom 404 and 500 error pages

## Project Structure

```
pizza-shop/
├── app.py                  # Main application file
├── database.py             # Database connection and initialization
├── requirements.txt        # Python dependencies
├── pizza_shop.db          # SQLite database (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── images/
│       └── pizzas/        # Pizza images
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Homepage/menu
│   ├── cart.html          # Shopping cart
│   ├── checkout.html      # Checkout form
│   ├── confirmation.html  # Order confirmation
│   ├── 404.html           # Not found page
│   ├── 500.html           # Server error page
│   └── manager/
│       ├── orders.html    # Orders list
│       └── order_detail.html  # Order details
└── tests/                 # Test files
    ├── test_add_to_cart.py
    ├── test_cart_manager.py
    ├── test_checkout_route.py
    ├── test_e2e_user_flow.py
    ├── test_error_conditions.py
    ├── test_error_pages.py
    ├── test_manager_routes.py
    ├── test_menu_service.py
    ├── test_order_processor.py
    └── test_styling.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**

   ```bash
   cd pizza-shop
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**

   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to: `http://127.0.0.1:5000`

## Usage

### Customer Flow

1. **Browse Menu**: View all available pizzas on the homepage
2. **Add to Cart**: Click "Add to Cart" on any pizza
3. **View Cart**: Click "Cart" in the navigation to review items
4. **Checkout**: Click "Proceed to Checkout" and fill in your details
5. **Confirmation**: View your order confirmation with order ID

### Manager Dashboard

1. Navigate to `/manager/orders` or click "Manager" in the navigation
2. View all orders with pagination (20 orders per page)
3. Click on any order to see detailed information
4. Print order receipts using the print button

## Database Schema

### Tables

**pizzas**

- `id`: Primary key
- `name`: Pizza name
- `price`: Price in INR
- `image_url`: Image filename

**orders**

- `id`: Primary key
- `customer_name`: Customer's name
- `phone`: Contact number
- `address`: Delivery address
- `total_price`: Total order amount
- `order_date`: Timestamp

**order_items**

- `id`: Primary key
- `order_id`: Foreign key to orders
- `pizza_id`: Foreign key to pizzas
- `pizza_name`: Pizza name (denormalized)
- `price`: Price at time of order
- `quantity`: Number of items

## Testing

Run all tests:

```bash
pytest tests/
```

Run specific test file:

```bash
pytest tests/test_cart_manager.py
```

Run with coverage:

```bash
pytest --cov=. tests/
```

### Test Coverage

- Unit tests for all service classes (MenuService, CartManager, OrderProcessor)
- Integration tests for all routes
- End-to-end user flow tests
- Error handling tests
- Edge case tests

## Technologies Used

- **Backend**: Flask 3.0.0
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 5.3.2
- **Testing**: pytest, pytest-flask

## Configuration

### Secret Key

The application uses a secret key for session management. In production, set the `SECRET_KEY` environment variable:

```bash
export SECRET_KEY="your-secure-secret-key"
```

### Database

The SQLite database is automatically created on first run with sample pizza data:

- Margherita (₹299)
- Pepperoni (₹399)
- Vegetarian (₹349)
- BBQ Chicken (₹449)
- Hawaiian (₹379)
- Four Cheese (₹429)

## Adding Pizza Images

Pizza images should be placed in `static/images/pizzas/` with the following filenames:

- `margherita.jpg`
- `pepperoni.jpg`
- `vegetarian.png`
- `bbq-chicken.jpg`
- `hawaiian.jpg`
- `four-cheese.jpeg`
- `default-pizza.jpg` (fallback)

**Image Requirements**:

- Format: JPG, JPEG, or PNG
- Recommended size: 800x800 pixels
- File size: Under 500KB for optimal loading

## Features in Detail

### Shopping Cart

- Session-based storage (no login required)
- Add/remove items
- Automatic quantity tracking
- Real-time total calculation
- Persistent across page navigation

### Checkout System

- Form validation (all fields required)
- Order processing with database storage
- Automatic cart clearing after successful order
- Error handling for failed transactions

### Manager Dashboard

- Paginated order list (20 per page)
- Order details view
- Print-friendly order receipts
- Responsive table design

### Responsive Design

- Mobile-first approach
- Bootstrap grid system
- Touch-friendly buttons
- Optimized images

## API Endpoints

### Public Routes

- `GET /` - Homepage with pizza menu
- `POST /add_to_cart/<pizza_id>` - Add pizza to cart (AJAX)
- `GET /cart` - View shopping cart
- `POST /remove_from_cart/<pizza_id>` - Remove item from cart
- `GET /checkout` - Checkout form
- `POST /checkout` - Process order
- `GET /confirmation/<order_id>` - Order confirmation

### Manager Routes

- `GET /manager/orders` - List all orders (paginated)
- `GET /manager/orders/<order_id>` - View order details

## Troubleshooting

### Database Issues

If you encounter database errors, delete `pizza_shop.db` and restart the application to recreate it.

### Port Already in Use

If port 5000 is already in use, modify the last line in `app.py`:

```python
app.run(debug=True, port=5001)
```

### Images Not Displaying

1. Verify images exist in `static/images/pizzas/`
2. Check file names match database entries
3. Ensure proper file permissions
4. Clear browser cache

## Development

### Debug Mode

The application runs in debug mode by default. To disable:

```python
app.run(debug=False)
```

### Logging

Logs are output to console with INFO level. To change:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- Session cookies are used for cart management
- CSRF protection should be added for production
- Input validation on all forms
- SQL injection prevention via parameterized queries
- XSS prevention via template escaping

## Future Enhancements

- User authentication system
- Order tracking for customers
- Payment gateway integration
- Email notifications
- Pizza customization options
- Delivery time estimation
- Order status updates
- Admin panel for pizza management

## License

This project is for educational purposes.

## Support

For issues or questions, please check the code comments or review the test files for usage examples.

---

**Enjoy your pizza shop! 🍕**
