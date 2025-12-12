# Organization Management Service

A production-ready **full-stack** multi-tenant organization management service with a modern web UI, RESTful API built with FastAPI, and MongoDB backend. Features JWT authentication, dynamic collection creation, and a responsive frontend.

## 🌐 Live Application

**🎨 Frontend UI**: http://localhost:8000  
**📚 API Documentation**: http://localhost:8000/docs  
**🏥 Health Check**: http://localhost:8000/health

## 🏗️ Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  Authentication Layer (JWT + BCrypt)                        │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (Business Logic)                             │
├─────────────────────────────────────────────────────────────┤
│  Database Layer (MongoDB - Motor Async Driver)              │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │     Master Database             │
        │  ┌─────────────────────┐       │
        │  │  Organizations      │       │
        │  │  Collection         │       │
        │  └─────────────────────┘       │
        │  ┌─────────────────────┐       │
        │  │  Admins             │       │
        │  │  Collection         │       │
        │  └─────────────────────┘       │
        │  ┌─────────────────────┐       │
        │  │  org_company_a      │  ◄──── Dynamic collections
        │  └─────────────────────┘       │    per organization
        │  ┌─────────────────────┐       │
        │  │  org_company_b      │  ◄──── Isolated data
        │  └─────────────────────┘       │
        └─────────────────────────────────┘
```

### Multi-Tenant Strategy

This implementation uses a **Collection-per-Tenant** approach within a single database:

- **Master Collections**: Store global metadata (organizations, admins)
- **Dynamic Collections**: Each organization gets its own collection (`org_<organization_name>`)
- **Benefits**:
  - Data isolation at collection level
  - Easier to backup/restore individual organizations
  - Simple to implement and maintain
  - Good performance for moderate scale

## 📁 Project Structure

```
The Wedding Company/
├── app/
│   ├── __init__.py           # Application package
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration management
│   ├── database.py           # MongoDB connection & management
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── security.py           # Authentication & password hashing
│   ├── services.py           # Business logic layer
│   └── routes.py             # API endpoints
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🚀 Features

### Implemented Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/org/create` | POST | Create new organization with admin | No |
| `/org/get` | GET | Get organization details | No |
| `/org/update` | PUT | Update organization name & migrate data | Yes |
| `/org/delete` | DELETE | Delete organization & all data | Yes |
| `/admin/login` | POST | Admin authentication | No |
| `/health` | GET | Health check | No |

### Security Features

- ✅ Password hashing with BCrypt
- ✅ JWT token-based authentication
- ✅ Token expiration handling
- ✅ Role-based access control (admin-only operations)
- ✅ Input validation with Pydantic

### Database Features

- ✅ Master database for global metadata
- ✅ Dynamic collection creation per organization
- ✅ Automatic data migration on organization rename
- ✅ Cascade deletion of organization data
- ✅ Async database operations with Motor

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.9 or higher
- MongoDB 4.4 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "The Wedding Company"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and update values:
   # - MONGODB_URL: Your MongoDB connection string
   # - SECRET_KEY: Generate a secure secret key
   # - Other configuration as needed
   ```

5. **Start MongoDB**
   ```bash
   # If MongoDB is installed locally
   mongod
   
   # Or use Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

6. **Run the application**
   ```bash
   python -m app.main
   
   # Or use uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## 📖 API Usage Examples

### 1. Create Organization

```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "TechCorp",
    "email": "admin@techcorp.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "organization_id": "uuid-here",
  "organization_name": "techcorp",
  "collection_name": "org_techcorp",
  "admin_email": "admin@techcorp.com",
  "created_at": "2025-12-12T10:00:00"
}
```

### 2. Admin Login

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@techcorp.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "organization_name": "techcorp",
  "admin_email": "admin@techcorp.com"
}
```

### 3. Get Organization

```bash
curl -X GET "http://localhost:8000/org/get?organization_name=techcorp"
```

### 4. Update Organization

```bash
curl -X PUT "http://localhost:8000/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "organization_name": "techcorp",
    "new_organization_name": "techcorp_global"
  }'
```

### 5. Delete Organization

```bash
curl -X DELETE "http://localhost:8000/org/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "organization_name": "techcorp"
  }'
```

## 🎯 Design Choices & Rationale

### 1. **FastAPI Framework**
   - **Why**: Modern, fast, automatic API documentation, async support
   - **Benefits**: Type safety, excellent performance, built-in validation
   - **Trade-off**: Newer framework (less mature than Django)

### 2. **Collection-per-Tenant Architecture**
   - **Why**: Balance between isolation and simplicity
   - **Benefits**: 
     - Data isolation at collection level
     - Easier data migration and backup
     - Simpler than database-per-tenant
   - **Trade-offs**: 
     - Limited by MongoDB connection limits
     - Not suitable for 1000s of organizations
     - Better alternatives for very large scale

### 3. **MongoDB with Motor (Async)**
   - **Why**: Schema flexibility, good for dynamic collections
   - **Benefits**: Fast async operations, flexible schema
   - **Trade-offs**: No ACID transactions across collections (before v4.0)

### 4. **JWT Authentication**
   - **Why**: Stateless, scalable, industry standard
   - **Benefits**: No server-side session storage, works across services
   - **Trade-offs**: Token revocation requires additional mechanisms

### 5. **Class-Based Service Layer**
   - **Why**: Separation of concerns, testability, maintainability
   - **Benefits**: Clear structure, easy to mock for testing
   - **Trade-offs**: More boilerplate than functional approach

## 🔄 Scalability Analysis

### Current Architecture Strengths
✅ Horizontal scaling possible (stateless API)
✅ Async operations for better throughput
✅ Collection-level isolation
✅ Simple to understand and maintain

### Limitations & Solutions

| Limitation | Impact | Solution |
|------------|--------|----------|
| Single database | Connection limit | Shard across multiple databases |
| Collection per tenant | 1000s of collections | Switch to database-per-tenant or discriminator pattern |
| No caching | Repeated queries | Add Redis for frequently accessed data |
| No rate limiting | API abuse | Implement rate limiting middleware |
| Single point of failure | Downtime risk | MongoDB replica sets + load balancer |

### Recommended Improvements for Production

1. **Database Sharding**: Distribute organizations across multiple databases
2. **Caching Layer**: Redis for organization metadata and JWT blacklist
3. **Rate Limiting**: Protect endpoints from abuse
4. **Monitoring**: Prometheus + Grafana for metrics
5. **Logging**: Structured logging with ELK stack
6. **API Versioning**: Support backward compatibility
7. **Audit Logging**: Track all organization changes
8. **Background Jobs**: Celery for heavy operations (data migration)

## 🏆 Better Architecture (Enterprise Scale)

For 10,000+ organizations:

```
┌─────────────────────────────────────────┐
│  API Gateway (Kong/AWS API Gateway)     │
│  - Rate limiting                        │
│  - Authentication                       │
│  - Load balancing                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Application Cluster (K8s)              │
│  - Multiple FastAPI instances           │
│  - Auto-scaling                         │
│  - Health checks                        │
└─────────────────────────────────────────┘
              ↓
┌──────────────┬──────────────┬───────────┐
│ Redis Cache  │ Message Queue│ Monitoring│
│ (Sessions)   │ (RabbitMQ)   │ (Prom)    │
└──────────────┴──────────────┴───────────┘
              ↓
┌─────────────────────────────────────────┐
│  Database Layer                         │
│  ┌──────────┐  ┌──────────┐            │
│  │ Master   │  │ Org DB 1 │            │
│  │ (Global) │  │ (Shard)  │            │
│  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌──────────┐            │
│  │ Org DB 2 │  │ Org DB N │            │
│  │ (Shard)  │  │ (Shard)  │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

**Key Changes:**
- Database-per-tenant with sharding
- Distributed caching
- Message queue for async operations
- API gateway for centralized concerns
- Container orchestration

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (create test files as needed)
pytest tests/
```

## 📝 License

This project is created for assignment purposes.

## 👥 Author

Backend Intern Assignment Implementation

---

**Note**: This is a learning project demonstrating multi-tenant architecture patterns. For production use, implement additional security measures, monitoring, and scaling strategies outlined above.
