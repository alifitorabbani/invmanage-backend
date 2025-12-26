# API Documentation - Inventory Management System (InvManage)

## Overview

The InvManage API provides a comprehensive REST interface for inventory management operations. Built with Django REST Framework, it offers CRUD operations, advanced reporting, and real-time analytics.

**Base URL:** `http://localhost:8001/api`
**Authentication:** Session-based with role permissions
**Format:** JSON
**Version:** v1

## Authentication

### Admin Login
```http
POST /api/admin/login/
Content-Type: application/json

{
  "nama": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "nama": "admin",
    "email": "admin@invmanage.com",
    "role": "admin",
    "is_admin": true
  },
  "redirect_to": "admin_dashboard"
}
```

### User Login
```http
POST /api/login/
Content-Type: application/json

{
  "nama": "john_doe",
  "password": "password123"
}
```

### Registration
```http
POST /api/register/
Content-Type: application/json

{
  "nama": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "user"
}
```

## Core API Endpoints

### 1. Inventory Management (Barang)

#### List Items
```http
GET /api/barang/
Query Parameters:
- search: string (search in name/stock)
- status: "low_stock" | "out_of_stock" | "available"
```

**Response:**
```json
[
  {
    "id": 1,
    "nama": "Laptop Dell",
    "stok": 15,
    "harga": 8500000,
    "minimum": 5,
    "is_low_stock": false,
    "is_out_of_stock": false,
    "stock_status": "available"
  }
]
```

#### Create Item
```http
POST /api/barang/
Content-Type: application/json

{
  "nama": "New Laptop",
  "stok": 10,
  "harga": 7500000,
  "minimum": 3
}
```

#### Update Item
```http
PUT /api/barang/{id}/
Content-Type: application/json

{
  "nama": "Updated Laptop",
  "stok": 12,
  "harga": 8000000,
  "minimum": 4
}
```

#### Delete Item
```http
DELETE /api/barang/{id}/
```

**Safety Checks:**
- Cannot delete items currently on loan
- Cannot delete items with transaction history
- Returns detailed error messages

#### Update Stock
```http
POST /api/barang/{id}/update_stok/
Content-Type: application/json

{
  "jumlah": 5,
  "tipe": "masuk",  // "masuk" or "keluar"
  "catatan": "Restock from supplier",
  "user_id": 1
}
```

### 2. User Management

#### List Users
```http
GET /api/users/
```

#### Create User
```http
POST /api/users/
Content-Type: application/json

{
  "nama": "Jane Smith",
  "email": "jane@example.com",
  "password": "password123",
  "role": "user",
  "departemen": "IT"
}
```

#### Update User
```http
PUT /api/users/{id}/
```

#### Change Password
```http
POST /api/users/{id}/change_password/
Content-Type: application/json

{
  "old_password": "oldpass",
  "new_password": "newpass"
}
```

### 3. Loan Management (Peminjaman)

#### List Loans
```http
GET /api/peminjaman/
Query Parameters:
- user: int (filter by user ID)
- status: "dipinjam" | "dikembalikan"
- overdue: "true" (show only overdue loans)
```

#### Create Loan
```http
POST /api/peminjaman/
Content-Type: application/json

{
  "barang": 1,
  "user": 2,
  "jumlah": 2,
  "catatan": "For project work"
}
```

**Business Logic:**
- Validates stock availability
- Reduces item stock
- Creates transaction record
- Auto-calculates due dates

#### Return Item
```http
POST /api/peminjaman/{id}/kembalikan/
```

**Business Logic:**
- Restores item stock
- Updates loan status
- Sets return date
- Creates return transaction

### 4. Transaction History

#### List Transactions
```http
GET /api/transaksi/
Query Parameters:
- barang: int (filter by item)
- user: int (filter by user)
- tipe: "masuk" | "keluar"
```

**Response:**
```json
[
  {
    "id": 1,
    "barang": 1,
    "barang_nama": "Laptop Dell",
    "user": 2,
    "user_nama": "John Doe",
    "jumlah": 2,
    "tipe": "keluar",
    "catatan": "Loan to John Doe",
    "tanggal": "2025-12-26T08:00:00Z"
  }
]
```

### 5. Feedback System

#### List Feedback
```http
GET /api/feedback/
```

#### Submit Feedback
```http
POST /api/feedback/
Content-Type: application/json

{
  "user": 1,
  "pesan": "Great system, very helpful!"
}
```

## Reporting API Endpoints

### Dashboard Overview
```http
GET /api/reports/dashboard/
```

**Response:**
```json
{
  "total_items": 699,
  "total_loans": 3326,
  "active_loans": 1470,
  "total_transactions": 5300,
  "low_stock_items": 51,
  "total_users": 382,
  "total_feedback": 2001
}
```

### Stock Levels Chart
```http
GET /api/reports/item-stock-levels/
```

**Response:**
```json
{
  "labels": ["Laptop Dell", "Mouse Logitech", "Keyboard HP"],
  "datasets": [{
    "label": "Stock Level",
    "data": [15, 25, 8],
    "backgroundColor": "rgba(54, 162, 235, 0.6)",
    "borderColor": "rgba(54, 162, 235, 1)"
  }]
}
```

### Item Categories Distribution
```http
GET /api/reports/item-categories/
```

### Most Borrowed Items
```http
GET /api/reports/most-borrowed-items/
```

**Response:**
```json
{
  "labels": ["Laptop Dell", "Projector Epson", "Mouse Logitech"],
  "datasets": [
    {
      "label": "Total Loans",
      "data": [45, 32, 28]
    },
    {
      "label": "Total Quantity",
      "data": [90, 64, 56]
    }
  ]
}
```

### Transaction Trends (30 days)
```http
GET /api/reports/item-transaction-trends/
```

### Low Stock Alerts
```http
GET /api/reports/low-stock-alerts/
```

## Error Handling

### Common Error Responses

#### Authentication Errors
```json
{
  "error": "Kredensial admin tidak valid"
}
```

#### Validation Errors
```json
{
  "nama": ["barang with this nama already exists."],
  "stok": ["Stock cannot be negative"]
}
```

#### Permission Errors
```json
{
  "error": "Authentication credentials were not provided."
}
```

#### Business Logic Errors
```json
{
  "error": "Stok tidak mencukupi"
}
```

## Rate Limiting

- **Anonymous users:** 100 requests/hour
- **Authenticated users:** 1000 requests/hour
- **Admin users:** 5000 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 3600
```

## Caching

All reporting endpoints implement caching:
- **Dashboard:** 3 minutes
- **Charts:** 5-10 minutes
- **Statistics:** 5 minutes
- **Trends:** 30 minutes

Cache is automatically invalidated on data changes.

## Data Models

### Users
```json
{
  "id": 1,
  "nama": "John Doe",
  "username": "john_doe",
  "email": "john@example.com",
  "phone": "+628123456789",
  "role": "user",
  "departemen": "IT",
  "foto": "base64_encoded_image",
  "is_admin": false,
  "is_user": true
}
```

### Barang (Items)
```json
{
  "id": 1,
  "nama": "Laptop Dell",
  "stok": 15,
  "harga": 8500000,
  "minimum": 5,
  "is_low_stock": false,
  "is_out_of_stock": false,
  "stock_status": "available"
}
```

### Peminjaman (Loans)
```json
{
  "id": 1,
  "barang": 1,
  "barang_nama": "Laptop Dell",
  "user": 2,
  "user_nama": "John Doe",
  "jumlah": 2,
  "status": "dipinjam",
  "catatan": "For project work",
  "tanggal_pinjam": "2025-12-26T08:00:00Z",
  "tanggal_kembali": null,
  "is_overdue": false,
  "days_borrowed": 1
}
```

## WebSocket Support (Future)

Real-time updates for:
- Stock level changes
- New loan requests
- System notifications
- Live dashboard updates

## Testing

### Sample Test Data
The system includes a management command to populate test data:

```bash
python manage.py populate_db
```

This creates:
- 1 Admin user (admin/admin123)
- 200 Regular users
- 500+ Inventory items
- 1500+ Loan records
- 3000+ Transaction records
- 1000 Feedback entries

## Deployment

### Development
```bash
python manage.py runserver 8001
```

### Production
```bash
gunicorn invmanage.wsgi:application --bind 0.0.0.0:8000
```

### Docker
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8001:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=invmanage.settings.production
```

## Monitoring

### Health Check
```http
GET /api/health/
```

### Metrics
- Response times
- Error rates
- Cache hit ratios
- Database connection pool status

## Version History

- **v1.0.0**: Initial release with core CRUD operations
- **v1.1.0**: Added reporting and analytics
- **v1.2.0**: Implemented caching and performance optimizations
- **v1.3.0**: Added advanced loan management features

## Support

For API support and questions:
- **Documentation:** `/api/docs/` (Django REST Framework browsable API)
- **Admin Interface:** `/admin/` (Django Admin)
- **Health Check:** `/api/health/`

## Security Notes

- All endpoints require proper authentication
- Admin endpoints have additional role checks
- Input validation on all requests
- SQL injection prevention via ORM
- XSS protection via input sanitization
- CSRF protection on state-changing operations