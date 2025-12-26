# Use Case Diagram - Inventory Management System (InvManage)

## System Overview
InvManage is a comprehensive inventory management system designed for organizations to efficiently manage their inventory items, track loans/borrowings, monitor transactions, and generate detailed reports.

## Actors

### Primary Actors
- **Admin**: System administrator with full access to all features
- **User**: Regular system user (employees, staff) with limited access
- **Guest**: Anonymous user with read-only access to public information

### Secondary Actors
- **Database System**: PostgreSQL database for data persistence
- **Email System**: For password reset and notifications
- **Cache System**: Redis/Database cache for performance optimization

## Use Case Diagram

```mermaid
graph TD
    %% Define actors
    A[Admin]:::actor
    U[User]:::actor
    G[Guest]:::actor

    %% Define use cases
    subgraph "Authentication & Authorization"
        UC1[Login]:::usecase
        UC2[Register]:::usecase
        UC3[Reset Password]:::usecase
        UC4[Logout]:::usecase
        UC5[Change Password]:::usecase
        UC6[Update Profile]:::usecase
    end

    subgraph "Inventory Management"
        UC7[View Items]:::usecase
        UC8[Add Item]:::usecase
        UC9[Edit Item]:::usecase
        UC10[Delete Item]:::usecase
        UC11[Search Items]:::usecase
        UC12[Filter Items]:::usecase
        UC13[Update Stock]:::usecase
        UC14[View Low Stock Alerts]:::usecase
    end

    subgraph "Loan Management"
        UC15[View Loans]:::usecase
        UC16[Create Loan]:::usecase
        UC17[Return Item]:::usecase
        UC18[View Overdue Loans]:::usecase
        UC19[Extend Loan]:::usecase
    end

    subgraph "Transaction Management"
        UC20[View Transactions]:::usecase
        UC21[Record Transaction]:::usecase
        UC22[View Transaction History]:::usecase
    end

    subgraph "Reporting & Analytics"
        UC23[View Dashboard]:::usecase
        UC24[Generate Reports]:::usecase
        UC25[View Statistics]:::usecase
        UC26[Export Data]:::usecase
        UC27[View Charts]:::usecase
    end

    subgraph "User Management"
        UC28[Manage Users]:::usecase
        UC29[View User Activity]:::usecase
        UC30[Manage Roles]:::usecase
    end

    subgraph "Feedback System"
        UC31[Submit Feedback]:::usecase
        UC32[View Feedback]:::usecase
        UC33[Manage Feedback]:::usecase
    end

    %% Define relationships
    A --> UC1
    A --> UC2
    A --> UC5
    A --> UC6
    A --> UC8
    A --> UC9
    A --> UC10
    A --> UC13
    A --> UC16
    A --> UC19
    A --> UC21
    A --> UC24
    A --> UC26
    A --> UC28
    A --> UC30
    A --> UC32
    A --> UC33

    U --> UC1
    U --> UC3
    U --> UC4
    U --> UC5
    U --> UC6
    U --> UC7
    U --> UC11
    U --> UC12
    U --> UC14
    U --> UC15
    U --> UC16
    U --> UC17
    U --> UC18
    U --> UC20
    U --> UC22
    U --> UC23
    U --> UC25
    U --> UC27
    U --> UC29
    U --> UC31

    G --> UC7
    G --> UC11
    G --> UC23
    G --> UC25

    %% Include/extend relationships
    UC8 ..> UC13 : includes
    UC9 ..> UC13 : includes
    UC16 ..> UC21 : includes
    UC17 ..> UC21 : includes
    UC24 ..> UC26 : includes
    UC24 ..> UC27 : includes

    %% System boundary
    subgraph "InvManage System"
        UC1
        UC2
        UC3
        UC4
        UC5
        UC6
        UC7
        UC8
        UC9
        UC10
        UC11
        UC12
        UC13
        UC14
        UC15
        UC16
        UC17
        UC18
        UC19
        UC20
        UC21
        UC22
        UC23
        UC24
        UC25
        UC26
        UC27
        UC28
        UC29
        UC30
        UC31
        UC32
        UC33
    end

    %% Styles
    classDef actor fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef usecase fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

## Detailed Use Case Descriptions

### Authentication Use Cases

#### UC1: Login
- **Actor**: Admin, User
- **Description**: User authenticates to access the system
- **Preconditions**: User has valid account
- **Postconditions**: User is authenticated and redirected to appropriate dashboard
- **Alternative Flows**:
  - Invalid credentials: Show error message
  - Account locked: Contact administrator

#### UC2: Register
- **Actor**: Admin
- **Description**: Create new user accounts
- **Preconditions**: Admin is logged in
- **Postconditions**: New user account created
- **Alternative Flows**:
  - Duplicate email/username: Show validation error
  - Invalid admin code: Registration denied

### Inventory Management Use Cases

#### UC8: Add Item
- **Actor**: Admin
- **Description**: Add new inventory item to the system
- **Preconditions**: Admin is logged in
- **Postconditions**: Item added to database, stock initialized
- **Validation**:
  - Unique item name
  - Valid stock and price values
  - Minimum stock threshold set

#### UC13: Update Stock
- **Actor**: Admin
- **Description**: Modify item stock levels with transaction logging
- **Preconditions**: Item exists, admin access
- **Postconditions**: Stock updated, transaction recorded
- **Business Rules**:
  - Stock cannot be negative
  - All changes logged in transaction history
  - Cache invalidated for reports

### Loan Management Use Cases

#### UC16: Create Loan
- **Actor**: Admin, User
- **Description**: Borrow items from inventory
- **Preconditions**: Sufficient stock available
- **Postconditions**: Loan created, stock reduced
- **Business Rules**:
  - Check stock availability
  - Record loan details
  - Update inventory stock
  - Log transaction

#### UC17: Return Item
- **Actor**: Admin, User
- **Description**: Return borrowed items
- **Preconditions**: Active loan exists
- **Postconditions**: Loan closed, stock restored
- **Business Rules**:
  - Validate return quantity
  - Update loan status
  - Restore inventory stock
  - Log return transaction

### Reporting Use Cases

#### UC23: View Dashboard
- **Actor**: Admin, User, Guest
- **Description**: Access main dashboard with key metrics
- **Preconditions**: Appropriate access level
- **Postconditions**: Dashboard displayed with current data
- **Data Displayed**:
  - Total items, loans, transactions
  - Low stock alerts
  - Recent activity
  - System statistics

#### UC24: Generate Reports
- **Actor**: Admin
- **Description**: Create detailed reports with charts and analytics
- **Preconditions**: Admin access
- **Postconditions**: Report generated and displayed
- **Report Types**:
  - Inventory status reports
  - Transaction history
  - Loan analytics
  - User activity reports

## Security Considerations

### Access Control
- **Role-based permissions**: Admin vs User vs Guest
- **Authentication required**: For all write operations
- **Session management**: Secure session handling
- **Password policies**: Strong password requirements

### Data Protection
- **Input validation**: All user inputs validated
- **SQL injection prevention**: Parameterized queries
- **XSS protection**: Input sanitization
- **CSRF protection**: Token-based protection

## Performance Requirements

### Response Times
- **Dashboard loading**: < 2 seconds
- **Search operations**: < 1 second
- **CRUD operations**: < 500ms
- **Report generation**: < 5 seconds

### Scalability
- **Concurrent users**: Support 100+ simultaneous users
- **Database optimization**: Indexed queries
- **Caching strategy**: Multi-level caching implementation
- **API rate limiting**: Prevent abuse