# Requirements Document

## Introduction

This document specifies the requirements for a full-stack pizza shop website that enables customers to browse available pizzas, manage a shopping cart, and place orders online. The system will use Python Flask for the backend, HTML/CSS/Bootstrap for the frontend, and SQLite for persistent order storage.

## Glossary

- **Pizza_Shop_System**: The complete web application including frontend, backend, and database
- **Menu_Display**: The component responsible for showing available pizzas on the homepage
- **Cart_Manager**: The component that handles shopping cart operations
- **Order_Processor**: The component that processes checkout and saves orders to the database
- **Customer**: A user browsing the website and placing orders
- **Pizza_Item**: A menu item with name, price in INR, and add-to-cart functionality
- **Order**: A collection of pizza items with customer details and delivery information
- **Cart**: A temporary collection of pizza items selected by the customer

## Requirements

### Requirement 1: Display Pizza Menu

**User Story:** As a customer, I want to see all available pizzas on the homepage, so that I can choose what to order.

#### Acceptance Criteria

1. THE Menu_Display SHALL render all available pizzas on the homepage
2. FOR EACH Pizza_Item, THE Menu_Display SHALL display the pizza name
3. FOR EACH Pizza_Item, THE Menu_Display SHALL display the price in INR
4. FOR EACH Pizza_Item, THE Menu_Display SHALL provide an "Add to Cart" button

### Requirement 2: Add Items to Cart

**User Story:** As a customer, I want to add pizzas to my cart, so that I can order multiple items.

#### Acceptance Criteria

1. WHEN a customer clicks the "Add to Cart" button, THE Cart_Manager SHALL add the selected Pizza_Item to the Cart
2. WHEN a Pizza_Item is added to the Cart, THE Cart_Manager SHALL increment the quantity if the item already exists in the Cart
3. WHEN a Pizza_Item is added to the Cart, THE Pizza_Shop_System SHALL provide visual feedback confirming the addition

### Requirement 3: View Cart Contents

**User Story:** As a customer, I want to view my cart, so that I can see what I'm about to order.

#### Acceptance Criteria

1. THE Cart_Manager SHALL display all Pizza_Items currently in the Cart
2. FOR EACH Pizza_Item in the Cart, THE Cart_Manager SHALL display the pizza name, price, and quantity
3. THE Cart_Manager SHALL calculate and display the total price of all items in the Cart
4. WHEN the Cart is empty, THE Cart_Manager SHALL display a message indicating the Cart contains no items

### Requirement 4: Remove Items from Cart

**User Story:** As a customer, I want to remove items from my cart, so that I can change my order before checkout.

#### Acceptance Criteria

1. FOR EACH Pizza_Item in the Cart, THE Cart_Manager SHALL provide a remove button
2. WHEN a customer clicks the remove button, THE Cart_Manager SHALL remove the corresponding Pizza_Item from the Cart
3. WHEN a Pizza_Item is removed, THE Cart_Manager SHALL recalculate and update the total price

### Requirement 5: Collect Customer Information at Checkout

**User Story:** As a customer, I want to provide my delivery details at checkout, so that my order can be delivered to me.

#### Acceptance Criteria

1. THE Order_Processor SHALL provide a checkout page with input fields for customer name, phone number, and delivery address
2. WHEN the checkout page is displayed, THE Order_Processor SHALL show the order summary with total price
3. THE Order_Processor SHALL require all three fields (name, phone, address) to be filled before submission
4. WHEN any required field is empty, THE Order_Processor SHALL prevent order submission and display a validation message

### Requirement 6: Save Order to Database

**User Story:** As a business owner, I want orders saved to a database, so that I can track and fulfill customer orders.

#### Acceptance Criteria

1. WHEN a customer submits a valid order, THE Order_Processor SHALL save the order details to the SQLite database
2. THE Order_Processor SHALL store the customer name, phone number, delivery address, ordered items, and total price
3. THE Order_Processor SHALL generate a unique order identifier for each saved order
4. IF the database save operation fails, THEN THE Order_Processor SHALL display an error message to the customer

### Requirement 7: Display Order Confirmation

**User Story:** As a customer, I want to see a confirmation after placing my order, so that I know my order was successful.

#### Acceptance Criteria

1. WHEN an order is successfully saved to the database, THE Order_Processor SHALL display an order confirmation page
2. THE Order_Processor SHALL display the unique order identifier on the confirmation page
3. THE Order_Processor SHALL display the customer name and delivery address on the confirmation page
4. WHEN the confirmation page is displayed, THE Cart_Manager SHALL clear all items from the Cart

### Requirement 8: Maintain Cart State

**User Story:** As a customer, I want my cart to persist while I browse, so that I don't lose my selections.

#### Acceptance Criteria

1. WHILE a customer navigates between pages, THE Cart_Manager SHALL maintain the Cart contents
2. WHEN a customer returns to the homepage from the cart page, THE Cart_Manager SHALL preserve all previously added items
3. THE Cart_Manager SHALL maintain cart state using session storage or server-side sessions
