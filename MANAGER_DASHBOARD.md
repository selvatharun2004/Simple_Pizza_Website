# Manager Dashboard Feature

## Overview

The Manager Dashboard is a new feature that allows pizza shop managers to view and manage all customer orders from a centralized interface.

## Features

### 1. Orders List Page (`/manager/orders`)

**Features:**

- View all orders in a paginated table
- Display key order information:
  - Order ID
  - Customer name
  - Phone number
  - Delivery address
  - Total amount
  - Order date
- Summary cards showing:
  - Total number of orders
  - Current page number
  - Orders per page
- Pagination controls for easy navigation
- Responsive design for mobile and desktop

**Access:** Navigate to `/manager/orders` or click "Manager" in the navigation bar

### 2. Order Detail Page (`/manager/orders/<order_id>`)

**Features:**

- Detailed view of a specific order
- Order information section:
  - Order ID
  - Order date
  - Total amount
- Customer information section:
  - Customer name (with icon)
  - Phone number (clickable to call)
  - Delivery address (with icon)
- Order items table:
  - Pizza name
  - Quantity
  - Unit price
  - Subtotal
  - Grand total
- Print functionality for order receipts
- Back navigation to orders list

**Access:** Click "View Details" button on any order in the orders list

## Technical Implementation

### New Files Created

#### Routes

- `routes/manager_routes.py` - Manager route handlers
  - `GET /manager/orders` - Orders list with pagination
  - `GET /manager/orders/<order_id>` - Order detail view

#### Templates

- `templates/manager/orders.html` - Orders list page
- `templates/manager/order_detail.html` - Order detail page

#### Services

Added methods to `OrderProcessor` class:

- `get_all_orders(limit, offset)` - Retrieve orders with pagination
- `get_order_count()` - Get total count of orders

### Database Queries

**Get all orders (paginated):**

```sql
SELECT id, customer_name, phone, address, total_price, order_date
FROM orders
ORDER BY order_date DESC
LIMIT ? OFFSET ?
```

**Get order count:**

```sql
SELECT COUNT(*) as count FROM orders
```

## Usage

### For Managers

1. **View All Orders:**
   - Click "Manager" in the navigation bar
   - Or navigate to `/manager/orders`
   - Browse through orders using pagination

2. **View Order Details:**
   - Click "View Details" button on any order
   - Review customer information and order items
   - Print order for kitchen or delivery

3. **Navigate:**
   - Use pagination controls to browse through orders
   - Use "Back to All Orders" button to return to list
   - Use "Back to Homepage" to return to main site

### Pagination

- Default: 20 orders per page
- Customize with URL parameters:
  - `?page=2` - View page 2
  - `?per_page=50` - Show 50 orders per page
  - `?page=3&per_page=10` - Page 3 with 10 orders per page

## UI Components

### Bootstrap Icons Used

- `bi-clipboard-data` - Manager dashboard icon
- `bi-list-ul` - Orders list icon
- `bi-eye` - View details icon
- `bi-receipt` - Order receipt icon
- `bi-person-fill` - Customer name icon
- `bi-telephone-fill` - Phone icon
- `bi-geo-alt-fill` - Address icon
- `bi-cart` - Order items icon
- `bi-printer` - Print icon
- `bi-arrow-left` - Back navigation icon
- `bi-chevron-left/right` - Pagination arrows

### Color Scheme

- Primary: Danger red (`#dc3545`) - Consistent with pizza shop branding
- Cards: White with shadow
- Headers: Red background with white text
- Tables: Hover effects for better UX

## Testing

Run the manager routes tests:

```bash
pytest test_manager_routes.py -v
```

**Test Coverage:**

- Empty orders page
- Orders page with data
- Pagination functionality
- Order detail page
- Invalid order ID handling
- Order count display
- Order dates display
- Order items display
- Navigation link presence

## Security Considerations

**Current Implementation:**

- No authentication required (suitable for internal use)
- All orders are visible to anyone accessing the manager routes

**Future Enhancements:**

- Add authentication/login system
- Role-based access control (manager vs. staff)
- Session management
- Password protection

## Future Enhancements

### Potential Features

1. **Order Status Management**
   - Mark orders as "Pending", "Preparing", "Out for Delivery", "Completed"
   - Status filtering and sorting

2. **Search and Filters**
   - Search by customer name, phone, or order ID
   - Filter by date range
   - Filter by order amount

3. **Analytics Dashboard**
   - Total revenue
   - Most popular pizzas
   - Orders per day/week/month
   - Average order value

4. **Export Functionality**
   - Export orders to CSV/Excel
   - Generate reports
   - Print batch receipts

5. **Order Management**
   - Edit order details
   - Cancel orders
   - Refund processing

6. **Real-time Updates**
   - WebSocket integration for live order updates
   - Notification system for new orders

7. **Kitchen Display**
   - Separate view optimized for kitchen staff
   - Focus on order items and preparation

## Integration with Existing Code

### Original App (`app.py`)

- Added `get_all_orders()` and `get_order_count()` methods to `OrderProcessor` class
- Added two new routes: `/manager/orders` and `/manager/orders/<order_id>`
- Updated navigation in `templates/base.html`

### Refactored App (`app_new.py`)

- Created `routes/manager_routes.py` with `manager_bp` blueprint
- Updated `services/order_processor.py` with new methods
- Registered `manager_bp` in application factory
- Updated navigation in `templates/base.html`

Both implementations work identically and maintain backward compatibility.

## Troubleshooting

### Orders Not Showing

- Verify database has orders: Check `pizza_shop.db`
- Check console for errors
- Verify route is registered correctly

### Pagination Not Working

- Check URL parameters are being passed correctly
- Verify `get_all_orders()` method is using limit/offset
- Check total_pages calculation

### Styling Issues

- Ensure Bootstrap 5 CSS is loaded
- Verify Bootstrap Icons CDN is included
- Check custom CSS in `static/css/style.css`

## API Endpoints

### GET /manager/orders

**Query Parameters:**

- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 20) - Orders per page

**Response:** HTML page with orders list

### GET /manager/orders/<order_id>

**Path Parameters:**

- `order_id` (required) - Order ID to display

**Response:** HTML page with order details or 404 if not found

## Accessibility

- Semantic HTML structure
- ARIA labels for navigation
- Keyboard navigation support
- Screen reader friendly
- Print-friendly layout
- Responsive design for all devices

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Pagination prevents loading all orders at once
- Efficient database queries with LIMIT/OFFSET
- Minimal JavaScript (only for print functionality)
- Cached static assets (Bootstrap, icons)

## Conclusion

The Manager Dashboard provides a simple, effective way for pizza shop managers to view and manage orders. It integrates seamlessly with the existing application and follows the same design patterns and styling conventions.
