# InvManage Backend API

**Enterprise Inventory Management System - Backend API**

Django REST Framework API untuk sistem manajemen inventori enterprise dengan 10,000+ records sample data.

## 🚀 Quick Start

### Backend Server
```bash
python manage.py runserver 8001
```

## 📋 Access URLs

### Backend API
- **API Base**: `http://localhost:8001/api`
- **Admin Panel**: `http://localhost:8001/admin`
  - Username: `admin`
  - Password: `admin123`
- **API Documentation**: `http://localhost:8001/api` (Browsable API)

## 🗄️ Database

### Populate Large Dataset
```bash
python manage.py populate_db_large
```

### Current Data Statistics
- **Users**: 2003 records
- **Items (Barang)**: 930 records
- **Loans (Peminjaman)**: 1995 records
- **Transactions**: 3964 records
- **Feedback**: 2000 records
- **Total**: 10,892 records

## 🏗️ Architecture

### Backend (Django REST Framework)
- **Port**: 8001
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: RESTful endpoints with authentication
- **Caching**: Database-backed cache
- **Security**: CORS, CSRF, throttling

### Frontend (Vanilla JavaScript)
- **Port**: 3000
- **Architecture**: Modular JavaScript (9 modules)
- **Features**: Responsive, real-time data, search & filtering
- **Styling**: Modern CSS with animations

### File Structure
```
invmanage-backend/
├── api/                    # Django REST API app
│   ├── models.py          # Database models
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── urls.py            # API routing
│   └── management/        # Management commands
├── invmanage/             # Django project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── docs/                  # Documentation
├── manage.py              # Django management script
└── README.md              # This file
```

## 🔧 Development

### Prerequisites
- Python 3.8+
- Django 5.2+
- Django REST Framework
- SQLite (included) or PostgreSQL

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create cache table
python manage.py createcachetable

# Populate database
python manage.py populate_db_large
```

### Running Both Servers
```bash
# Terminal 1 - Backend
python manage.py runserver 8001

# Terminal 2 - Frontend
python run_frontend.py
```

## 📊 API Features

### ✅ RESTful Endpoints
- **Users API**: `GET /api/users/` - User management
- **Items API**: `GET /api/barang/` - Inventory management
- **Loans API**: `GET /api/peminjaman/` - Loan records (1995 entries)
- **Transactions API**: `GET /api/transaksi/` - Audit trail (3964 entries)
- **Feedback API**: `GET /api/feedback/` - User feedback (2000 entries)

### ✅ Advanced Features
- **Filtering & Search**: Query parameters support
- **Pagination**: Efficient data loading
- **Serialization**: Proper JSON responses
- **Validation**: Input validation and error handling
- **Relationships**: Foreign key relationships with nested data

### ✅ Admin Interface
- **Django Admin**: Full CRUD operations
- **Data Visualization**: Model relationships
- **Bulk Operations**: Mass data management
- **Export Capabilities**: Data export features

## 🔒 Security

- **CORS**: Configured for cross-origin requests
- **CSRF**: Protection enabled
- **Throttling**: Rate limiting (1000/hour user, 100/hour anon)
- **Authentication**: Ready for OAuth integration

## 📈 Performance

- **API Response**: < 500ms average
- **Database**: Optimized queries with select_related/prefetch_related
- **Caching**: Database-backed cache with TTL
- **Frontend**: Lazy loading and efficient DOM manipulation

## 🚀 Production Deployment

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
ALLOWED_HOSTS=your-domain.com
```

### Static Files
```bash
python manage.py collectstatic
```

### Gunicorn (WSGI)
```bash
gunicorn invmanage.wsgi:application --bind 0.0.0.0:8000
```

## 📚 API Documentation

### Endpoints
- `GET /api/users/` - User management
- `GET /api/barang/` - Inventory items
- `GET /api/peminjaman/` - Loan records
- `GET /api/transaksi/` - Transaction history
- `GET /api/feedback/` - User feedback
- `POST /api/admin/login/` - Admin authentication

### Response Format
```json
{
  "id": 1,
  "field": "value",
  "created_at": "2025-12-26T10:00:00Z"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `docs/` folder
- Review API documentation at `/api/`

---

**InvManage** - Modern Enterprise Inventory Solutions 🚀