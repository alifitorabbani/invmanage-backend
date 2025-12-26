# Web Architecture - Inventory Management System (InvManage)

## System Overview

InvManage is a modern web-based inventory management system built with Django REST Framework backend and vanilla JavaScript frontend, designed for scalability, performance, and maintainability.

## Complete System Architecture

```mermaid
graph TB
    %% External Users
    subgraph "End Users"
        UA[Admin User<br/>Full System Access]
        UR[Regular User<br/>Limited Access]
        UG[Guest User<br/>Read-Only Access]
    end

    %% Client Layer
    subgraph "Client Layer"
        subgraph "Web Browser"
            HTML[HTML5<br/>Semantic Structure]
            CSS[CSS3<br/>Responsive Design]
            JS[Vanilla JavaScript<br/>ES6+ Features]
            AJAX[AJAX/Fetch API<br/>REST Client]
        end
    end

    %% Network Layer
    subgraph "Network Layer"
        HTTPS[HTTPS/TLS 1.3<br/>Secure Communication]
        CORS[CORS Headers<br/>Cross-Origin Support]
        WS[WebSocket<br/>Real-time Updates<br/>Optional]
    end

    %% API Gateway / Load Balancer
    subgraph "API Gateway"
        NGINX[Nginx/Apache<br/>Reverse Proxy<br/>Static Files<br/>Load Balancer]
        GUNICORN[Gunicorn<br/>WSGI Server<br/>Process Manager]
    end

    %% Application Layer
    subgraph "Application Layer (Django)"
        subgraph "Django REST Framework"
            URLS[URL Configuration<br/>Route Mapping]
            VIEWS[ViewSets<br/>Business Logic<br/>CRUD Operations]
            SERIALIZERS[Serializers<br/>Data Validation<br/>DTO Pattern]
            PERMS[Permissions<br/>Authentication<br/>Authorization]
        end

        subgraph "Django Core"
            MODELS[Models<br/>ORM<br/>Business Entities]
            FORMS[Forms<br/>Validation<br/>User Input]
            ADMIN[Django Admin<br/>Management Interface]
            AUTH[Django Auth<br/>User Management]
        end

        subgraph "Middleware"
            AUTH_MW[Authentication MW<br/>Session Management]
            CORS_MW[CORS Middleware<br/>Cross-Origin Headers]
            CSRF_MW[CSRF Protection<br/>Security Tokens]
            CACHE_MW[Cache Middleware<br/>Performance]
        end
    end

    %% Business Logic Layer
    subgraph "Business Logic Layer"
        subgraph "Core Services"
            INV_SVC[Inventory Service<br/>Stock Management<br/>Item CRUD]
            LOAN_SVC[Loan Service<br/>Borrow/Return Logic<br/>Due Date Tracking]
            TXN_SVC[Transaction Service<br/>Audit Logging<br/>History Tracking]
            REPORT_SVC[Report Service<br/>Analytics<br/>Chart Generation]
        end

        subgraph "Utility Services"
            CACHE_SVC[Cache Service<br/>Redis/Database Cache<br/>Performance]
            EMAIL_SVC[Email Service<br/>SMTP<br/>Notifications]
            LOG_SVC[Logging Service<br/>Error Tracking<br/>Audit Logs]
            VALIDATION_SVC[Validation Service<br/>Business Rules<br/>Data Integrity]
        end
    end

    %% Data Access Layer
    subgraph "Data Access Layer"
        subgraph "Django ORM"
            QUERY[QuerySets<br/>Database Queries<br/>Optimization]
            MIGRATIONS[Migration System<br/>Schema Management<br/>Version Control]
        end

        subgraph "Database Layer"
            POSTGRES[(PostgreSQL<br/>Primary Database<br/>ACID Compliant)]
            CACHE_DB[(Cache Database<br/>Performance<br/>Session Storage)]
        end
    end

    %% Infrastructure Layer
    subgraph "Infrastructure Layer"
        subgraph "Server Environment"
            OS[Ubuntu/Debian<br/>Linux Server]
            PYTHON[Python 3.12<br/>Runtime Environment]
            PIP[Package Management<br/>Dependencies]
        end

        subgraph "External Services"
            SMTP[SMTP Server<br/>Email Delivery]
            REDIS[(Redis Cache<br/>Optional<br/>High Performance)]
            MONITOR[Monitoring<br/>Logs & Metrics]
        end
    end

    %% Data Flow
    UA --> HTTPS
    UR --> HTTPS
    UG --> HTTPS

    HTTPS --> NGINX
    NGINX --> GUNICORN

    GUNICORN --> URLS
    URLS --> VIEWS
    VIEWS --> SERIALIZERS
    VIEWS --> PERMS

    VIEWS --> INV_SVC
    VIEWS --> LOAN_SVC
    VIEWS --> TXN_SVC
    VIEWS --> REPORT_SVC

    INV_SVC --> CACHE_SVC
    LOAN_SVC --> CACHE_SVC
    TXN_SVC --> CACHE_SVC
    REPORT_SVC --> CACHE_SVC

    INV_SVC --> VALIDATION_SVC
    LOAN_SVC --> VALIDATION_SVC
    TXN_SVC --> VALIDATION_SVC

    INV_SVC --> QUERY
    LOAN_SVC --> QUERY
    TXN_SVC --> QUERY
    REPORT_SVC --> QUERY

    QUERY --> POSTGRES
    CACHE_SVC --> CACHE_DB
    CACHE_SVC --> REDIS

    EMAIL_SVC --> SMTP
    LOG_SVC --> MONITOR

    %% Styling
    classDef client fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef network fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef gateway fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef app fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef business fill:#fff8e1,stroke:#fbc02d,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef infra fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef external fill:#efebe9,stroke:#5d4037,stroke-width:2px

    class HTML,CSS,JS,AJAX client
    class HTTPS,CORS,WS network
    class NGINX,GUNICORN gateway
    class URLS,VIEWS,SERIALIZERS,PERMS,MODELS,FORMS,ADMIN,AUTH,AUTH_MW,CORS_MW,CSRF_MW,CACHE_MW app
    class INV_SVC,LOAN_SVC,TXN_SVC,REPORT_SVC,CACHE_SVC,EMAIL_SVC,LOG_SVC,VALIDATION_SVC business
    class QUERY,MIGRATIONS,POSTGRES,CACHE_DB data
    class OS,PYTHON,PIP,SMTP,REDIS,MONITOR infra
    class UA,UR,UG external
```

## Detailed Component Architecture

### 1. Client Layer Architecture

#### Frontend Structure
```
frontend/
├── index.html          # Landing page
├── dashboard.html      # Main dashboard
├── admin-login.html    # Admin authentication
├── app.js             # Main application logic
├── script.js          # Additional functionality
├── style.css          # Styling
└── assets/            # Static assets
```

#### JavaScript Architecture
```javascript
// Modular JavaScript Structure
const InvManage = {
    // API Client
    api: {
        baseURL: 'http://localhost:8001/api',
        login: async (credentials) => { /* ... */ },
        getItems: async () => { /* ... */ },
        // ... other API methods
    },

    // UI Components
    ui: {
        dashboard: {
            init: () => { /* ... */ },
            renderCharts: () => { /* ... */ },
            updateStats: () => { /* ... */ }
        },
        inventory: {
            loadItems: () => { /* ... */ },
            addItem: () => { /* ... */ },
            editItem: () => { /* ... */ }
        }
    },

    // Business Logic
    business: {
        validateItem: (item) => { /* ... */ },
        calculateStats: (data) => { /* ... */ }
    },

    // Utilities
    utils: {
        formatDate: (date) => { /* ... */ },
        showNotification: (message) => { /* ... */ }
    }
};
```

### 2. Application Layer Architecture

#### Django Project Structure
```
invmanage-backend/
├── invmanage/              # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── api/                   # Main application
│   ├── models.py         # Database models
│   ├── views.py          # API endpoints
│   ├── serializers.py    # Data serialization
│   ├── urls.py           # API routing
│   ├── admin.py          # Django admin
│   ├── apps.py           # App configuration
│   ├── tests.py          # Unit tests
│   └── migrations/       # Database migrations
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── manage.py             # Django management
└── db.sqlite3            # Development database
```

#### API Endpoint Architecture
```python
# URL Configuration Structure
urlpatterns = [
    # Authentication
    path('api/admin/login/', admin_login_view),
    path('api/login/', login_view),
    path('api/register/', register_view),

    # CRUD Endpoints
    path('api/', include(router.urls)),  # ViewSet routes

    # Reporting
    path('api/reports/dashboard/', reports_dashboard),
    path('api/reports/item-stock-levels/', item_stock_levels),
    # ... other report endpoints
]

# Router Configuration
router = DefaultRouter()
router.register(r'barang', BarangViewSet)
router.register(r'users', UsersViewSet)
router.register(r'peminjaman', PeminjamanViewSet)
router.register(r'transaksi', RiwayatTransaksiViewSet)
router.register(r'feedback', FeedbackViewSet)
```

### 3. Data Layer Architecture

#### Database Schema Design
```sql
-- Core Tables
CREATE TABLE api_users (
    id BIGSERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(254) UNIQUE,
    password VARCHAR(128),
    role VARCHAR(10) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_barang (
    id BIGSERIAL PRIMARY KEY,
    nama VARCHAR(100) UNIQUE NOT NULL,
    stok INTEGER DEFAULT 0 CHECK (stok >= 0),
    harga INTEGER DEFAULT 0 CHECK (harga >= 0),
    minimum INTEGER DEFAULT 5 CHECK (minimum >= 0)
);

CREATE TABLE api_peminjaman (
    id BIGSERIAL PRIMARY KEY,
    barang_id BIGINT REFERENCES api_barang(id),
    user_id BIGINT REFERENCES api_users(id),
    jumlah INTEGER CHECK (jumlah > 0),
    status VARCHAR(15) DEFAULT 'dipinjam',
    tanggal_pinjam TIMESTAMP DEFAULT NOW(),
    tanggal_kembali TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_users_nama ON api_users(nama);
CREATE INDEX idx_users_role ON api_users(role);
CREATE INDEX idx_barang_nama ON api_barang(nama);
CREATE INDEX idx_peminjaman_status ON api_peminjaman(status);
CREATE INDEX idx_peminjaman_tanggal ON api_peminjaman(tanggal_pinjam);
```

#### Caching Architecture
```python
# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Cache Key Strategy
CACHE_KEYS = {
    'dashboard': 'reports_dashboard',
    'item_status': 'reports_item_status_overview',
    'stock_levels': 'reports_item_stock_levels',
    'user_stats': 'user_statistics',
    'item_details': lambda item_id: f'item_{item_id}'
}

# Cache TTL Strategy
CACHE_TIMEOUTS = {
    'dashboard': 180,      # 3 minutes
    'reports': 600,        # 10 minutes
    'statistics': 300,     # 5 minutes
    'user_data': 3600,     # 1 hour
}
```

### 4. Security Architecture

#### Authentication & Authorization
```python
# Permission Classes
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user
```

#### Security Middleware Stack
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 5. Deployment Architecture

#### Production Deployment
```yaml
# Docker Compose Configuration
version: '3.8'
services:
  web:
    build: .
    command: gunicorn invmanage.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/code
      - static_volume:/code/static
    expose:
      - 8000
    environment:
      - DJANGO_SETTINGS_MODULE=invmanage.settings.production

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/code/static
    ports:
      - "80:80"
      - "443:443"

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=invmanage
      - POSTGRES_USER=invmanage_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  static_volume:
```

#### Environment Configuration
```python
# settings/production.py
import os
from .base import *

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}
```

## Performance & Scalability

### Caching Strategy
- **Database Cache**: For development/simple deployments
- **Redis Cache**: For production/high-traffic scenarios
- **CDN**: For static assets in production
- **Browser Cache**: For frontend assets

### Database Optimization
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Read Replicas**: For read-heavy workloads
- **Indexing Strategy**: Composite indexes for complex queries
- **Query Optimization**: Select related/prefetch related

### Monitoring & Observability
```python
# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## API Documentation

### REST API Endpoints

#### Authentication Endpoints
```
POST   /api/admin/login/     - Admin login
POST   /api/login/          - User login
POST   /api/register/       - User registration
POST   /api/reset-password/ - Password reset
```

#### CRUD Endpoints
```
GET    /api/barang/         - List items
POST   /api/barang/         - Create item
GET    /api/barang/{id}/    - Get item details
PUT    /api/barang/{id}/    - Update item
DELETE /api/barang/{id}/    - Delete item
POST   /api/barang/{id}/update_stok/ - Update stock
```

#### Reporting Endpoints
```
GET    /api/reports/dashboard/              - Dashboard data
GET    /api/reports/item-stock-levels/      - Stock levels chart
GET    /api/reports/item-categories/        - Categories chart
GET    /api/reports/most-borrowed-items/    - Popular items chart
GET    /api/reports/item-transaction-trends/ - Transaction trends
GET    /api/reports/low-stock-alerts/       - Low stock alerts
```

## Data Flow Architecture

### Request Flow
1. **Client Request** → HTTPS → Nginx → Gunicorn
2. **URL Resolution** → ViewSet → Serializer → Model
3. **Business Logic** → Service Layer → Cache Check
4. **Database Query** → ORM → PostgreSQL
5. **Response** ← Serialization ← ViewSet ← Gunicorn

### Cache Flow
1. **Request** → Check Cache → Cache Hit? → Return Cached Data
2. **Cache Miss** → Database Query → Process Data → Store in Cache → Return Data

### Authentication Flow
1. **Login Request** → Validate Credentials → Generate Session
2. **API Request** → Check Session → Authorize → Process Request
3. **Logout** → Destroy Session → Clear Cache

This architecture provides a scalable, secure, and maintainable foundation for the inventory management system with clear separation of concerns and comprehensive documentation.