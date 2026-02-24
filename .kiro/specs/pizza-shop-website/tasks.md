# Implementation Plan: Pizza Shop Website

## Overview

This plan implements a full-stack pizza shop website using Python Flask, HTML/CSS/Bootstrap, and SQLite. The implementation follows an incremental approach, building core functionality first, then adding features layer by layer, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and database
  - Create Flask application structure with app.py
  - Set up SQLite database with schema (pizzas, orders, order_items tables)
  - Populate pizzas table with sample menu items
  - Configure Flask session management with secret key
  - Create requirements.txt with Flask dependency
  - _Requirements: 6.1, 6.2, 8.3_

- [x] 2. Implement Menu Service
  - [x] 2.1 Create MenuService class with database operations
    - Implement get_all_pizzas() method to query pizzas table
    - Implement get_pizza_by_id() method for single pizza lookup
    - _Requirements: 1.1_
  - [x] 2.2 Write property test for Menu Service
    - **Property 1: Complete Menu Display**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 3. Implement Cart Manager
  - [x] 3.1 Create CartManager class with session-based operations
    - Implement add_item() to add or increment pizza in session cart
    - Implement get_cart() to retrieve current cart contents
    - Implement get_cart_total() to calculate total price
    - Implement is_empty() to check cart state
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 8.1, 8.2, 8.3_
  - [x] 3.2 Write property tests for cart operations
    - **Property 2: Add to Cart Creates Entry**
    - **Validates: Requirements 2.1**
  - [x] 3.3 Write property test for quantity increment
    - **Property 3: Repeated Addition Increments Quantity**
    - **Validates: Requirements 2.2**
  - [x] 3.4 Write property test for cart total calculation
    - **Property 5: Cart Total Invariant**
    - **Validates: Requirements 3.3, 4.3**
  - [x] 3.5 Implement remove_item() and clear_cart() methods
    - Add remove_item() to delete pizza from cart
    - Add clear_cart() to empty entire cart
    - _Requirements: 4.1, 4.2, 7.4_
  - [x] 3.6 Write property test for item removal
    - **Property 7: Remove Eliminates Item**
    - **Validates: Requirements 4.2**
  - [x] 3.7 Write property test for cart persistence
    - **Property 14: Cart Persistence Across Navigation**
    - **Validates: Requirements 8.1, 8.2**

- [x] 4. Implement Order Processor
  - [x] 4.1 Create OrderProcessor class with database operations
    - Implement create_order() to save order and order_items to database
    - Implement get_order_by_id() to retrieve order details
    - Add error handling for database failures
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [x] 4.2 Write property test for order persistence
    - **Property 10: Order Persistence Round Trip**
    - **Validates: Requirements 6.1, 6.2**
  - [x] 4.3 Write property test for order ID uniqueness
    - **Property 11: Order ID Uniqueness**
    - **Validates: Requirements 6.3**

- [x] 5. Checkpoint - Ensure core backend logic works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Create base template and homepage
  - [x] 6.1 Create base.html template with Bootstrap
    - Add Bootstrap 5 CDN links
    - Create navigation structure
    - Add common page structure and styling
    - _Requirements: 1.1_
  - [x] 6.2 Create index.html template for menu display
    - Display all pizzas in a responsive grid layout
    - Show pizza name and price in INR for each item
    - Add "Add to Cart" button for each pizza
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [x] 6.3 Implement homepage route (GET /)
    - Query MenuService.get_all_pizzas()
    - Render index.html with pizza data
    - _Requirements: 1.1_

- [x] 7. Implement add to cart functionality
  - [x] 7.1 Create add to cart route (POST /add_to_cart/<int:pizza_id>)
    - Validate pizza_id exists in database
    - Call CartManager.add_item() with pizza details
    - Return JSON response with success status
    - Add error handling for invalid pizza IDs
    - _Requirements: 2.1, 2.2_
  - [x] 7.2 Add JavaScript for add to cart interaction
    - Handle button click events
    - Send AJAX POST request to add_to_cart route
    - Display visual feedback message on success
    - _Requirements: 2.3_

- [x] 8. Create cart page
  - [x] 8.1 Create cart.html template
    - Display all cart items in a table with name, price, quantity
    - Show remove button for each item
    - Display total price at bottom
    - Show "Cart is empty" message when cart has no items
    - Add "Proceed to Checkout" button
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1_
  - [x] 8.2 Implement cart route (GET /cart)
    - Call CartManager.get_cart() and get_cart_total()
    - Render cart.html with cart data
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 8.3 Write property test for cart display
    - **Property 4: Cart Display Completeness**
    - **Validates: Requirements 3.1, 3.2**
  - [x] 8.4 Write property test for remove button presence
    - **Property 6: Remove Button Presence**
    - **Validates: Requirements 4.1**

- [x] 9. Implement remove from cart functionality
  - [x] 9.1 Create remove from cart route (POST /remove_from_cart/<int:pizza_id>)
    - Call CartManager.remove_item()
    - Redirect back to cart page
    - _Requirements: 4.2, 4.3_

- [x] 10. Create checkout page
  - [x] 10.1 Create checkout.html template
    - Add form with input fields for name, phone, address
    - Mark all fields as required with HTML5 validation
    - Display order summary with cart items and total
    - Add submit button
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 10.2 Implement checkout GET route (GET /checkout)
    - Check if cart is empty, redirect to cart if true
    - Call CartManager.get_cart() and get_cart_total()
    - Render checkout.html with cart summary
    - _Requirements: 5.1, 5.2_
  - [x] 10.3 Write property test for checkout total display
    - **Property 9: Checkout Displays Cart Total**
    - **Validates: Requirements 5.2**
  - [x] 10.4 Implement checkout POST route (POST /checkout)
    - Validate all form fields are non-empty
    - Call OrderProcessor.create_order() with form data and cart
    - Call CartManager.clear_cart() after successful order
    - Redirect to confirmation page with order_id
    - Handle validation errors and database errors
    - _Requirements: 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 7.4_
  - [x] 10.5 Write property test for form validation
    - **Property 8: Checkout Form Validation**
    - **Validates: Requirements 5.3, 5.4**

- [x] 11. Create order confirmation page
  - [x] 11.1 Create confirmation.html template
    - Display order ID prominently
    - Show customer name and delivery address
    - Add thank you message and link back to homepage
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 11.2 Implement confirmation route (GET /confirmation/<int:order_id>)
    - Call OrderProcessor.get_order_by_id()
    - Render confirmation.html with order details
    - Handle case where order_id doesn't exist
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 11.3 Write property test for confirmation page completeness
    - **Property 12: Confirmation Page Completeness**
    - **Validates: Requirements 7.1, 7.2, 7.3**
  - [x] 11.4 Write property test for cart clearing
    - **Property 13: Cart Cleared After Order**
    - **Validates: Requirements 7.4**

- [x] 12. Add error handling and edge cases
  - [x] 12.1 Add custom error pages
    - Create 404 error page template
    - Create 500 error page template
    - Register error handlers in Flask app
  - [x] 12.2 Add input validation and error handling
    - Validate pizza_id exists before cart operations
    - Handle database connection errors gracefully
    - Handle corrupted session data
    - Add logging for errors
  - [x] 12.3 Write unit tests for error conditions
    - Test invalid pizza ID handling
    - Test empty form field validation
    - Test database error handling
    - Test empty cart checkout redirect
    - Test corrupted session data handling

- [x] 13. Final integration and polish
  - [x] 13.1 Add CSS styling and responsive design improvements
    - Style buttons and forms consistently
    - Ensure mobile responsiveness
    - Add visual feedback for user actions
  - [x] 13.2 Test complete user flow end-to-end
    - Browse menu → Add items → View cart → Remove item → Checkout → Confirmation
    - Verify cart persistence across page navigation
    - Verify all requirements are met

- [x] 14. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and error conditions
- The implementation builds incrementally: database → backend logic → frontend → integration
- Flask test client should be used for testing routes and templates
- Use in-memory SQLite database (`:memory:`) for testing
