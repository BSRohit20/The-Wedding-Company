# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Health Check

#### GET /health

Check if the API is running and database is connected.

**Authentication Required**: No

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### 2. Create Organization

#### POST /org/create

Create a new organization with an admin user and dedicated collection.

**Authentication Required**: No

**Request Body:**
```json
{
  "organization_name": "techcorp",
  "email": "admin@techcorp.com",
  "password": "SecurePass123"
}
```

**Field Validations:**
- `organization_name`: 3-50 characters, alphanumeric with underscores/hyphens
- `email`: Valid email format
- `password`: Minimum 8 characters

**Success Response (201 Created):**
```json
{
  "organization_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "organization_name": "techcorp",
  "collection_name": "org_techcorp",
  "admin_email": "admin@techcorp.com",
  "created_at": "2025-12-12T10:00:00.000000"
}
```

**Error Responses:**

400 Bad Request - Organization exists:
```json
{
  "detail": "Organization 'techcorp' already exists"
}
```

400 Bad Request - Email exists:
```json
{
  "detail": "Admin with email 'admin@techcorp.com' already exists"
}
```

422 Unprocessable Entity - Validation error:
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "techcorp",
    "email": "admin@techcorp.com",
    "password": "SecurePass123"
  }'
```

---

### 3. Admin Login

#### POST /admin/login

Authenticate admin user and receive JWT access token.

**Authentication Required**: No

**Request Body:**
```json
{
  "email": "admin@techcorp.com",
  "password": "SecurePass123"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG1pbl9pZCI6ImExYjJjM2Q0LWU1ZjYtNzg5MC1hYmNkLWVmMTIzNDU2Nzg5MCIsImVtYWlsIjoiYWRtaW5AdGVjaGNvcnAuY29tIiwib3JnYW5pemF0aW9uX2lkIjoieDFZMnozYTQtYjVjNi03ODkwLXd4eXotYWIxMjM0NTY3ODkwIiwib3JnYW5pemF0aW9uX25hbWUiOiJ0ZWNoY29ycCIsImV4cCI6MTcwMjMzOTIwMH0.signature",
  "token_type": "bearer",
  "organization_name": "techcorp",
  "admin_email": "admin@techcorp.com"
}
```

**Token Expiration**: 30 minutes (default)

**Error Responses:**

401 Unauthorized - Invalid credentials:
```json
{
  "detail": "Invalid email or password"
}
```

403 Forbidden - Inactive account:
```json
{
  "detail": "Admin account is inactive"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@techcorp.com",
    "password": "SecurePass123"
  }'
```

**JWT Token Payload:**
```json
{
  "admin_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "admin@techcorp.com",
  "organization_id": "x1y2z3a4-b5c6-7890-wxyz-ab1234567890",
  "organization_name": "techcorp",
  "exp": 1702339200
}
```

---

### 4. Get Organization

#### GET /org/get

Retrieve organization details by name.

**Authentication Required**: No

**Query Parameters:**
- `organization_name` (required): Name of the organization

**Request:**
```http
GET /org/get?organization_name=techcorp HTTP/1.1
Host: localhost:8000
```

**Success Response (200 OK):**
```json
{
  "organization_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "organization_name": "techcorp",
  "collection_name": "org_techcorp",
  "admin_email": "admin@techcorp.com",
  "created_at": "2025-12-12T10:00:00.000000",
  "updated_at": null
}
```

**Error Response:**

404 Not Found:
```json
{
  "detail": "Organization 'techcorp' not found"
}
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/org/get?organization_name=techcorp"
```

---

### 5. Update Organization

#### PUT /org/update

Update organization name and migrate all data to a new collection.

**Authentication Required**: Yes (JWT Token)

**Request Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "organization_name": "techcorp",
  "new_organization_name": "techcorp_global"
}
```

**Success Response (200 OK):**
```json
{
  "organization_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "organization_name": "techcorp_global",
  "collection_name": "org_techcorp_global",
  "admin_email": "admin@techcorp.com",
  "created_at": "2025-12-12T10:00:00.000000",
  "updated_at": "2025-12-12T11:30:00.000000"
}
```

**Process:**
1. Validates current organization exists
2. Checks user is admin of this organization
3. Validates new name doesn't exist
4. Creates new collection
5. Migrates all data
6. Updates organization record
7. Deletes old collection

**Error Responses:**

401 Unauthorized - No token:
```json
{
  "detail": "Not authenticated"
}
```

401 Unauthorized - Invalid token:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden - Not organization admin:
```json
{
  "detail": "You don't have permission to update this organization"
}
```

404 Not Found:
```json
{
  "detail": "Organization 'techcorp' not found"
}
```

400 Bad Request - Name exists:
```json
{
  "detail": "Organization 'techcorp_global' already exists"
}
```

**Example cURL:**
```bash
curl -X PUT "http://localhost:8000/org/update" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "techcorp",
    "new_organization_name": "techcorp_global"
  }'
```

---

### 6. Delete Organization

#### DELETE /org/delete

Delete an organization and all associated data.

**Authentication Required**: Yes (JWT Token)

**Request Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "organization_name": "techcorp"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Organization 'techcorp' successfully deleted",
  "details": {
    "organization_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

**Process:**
1. Validates organization exists
2. Checks user is admin of this organization
3. Deletes organization collection
4. Deletes admin user
5. Deletes organization record

**Error Responses:**

401 Unauthorized - No token:
```json
{
  "detail": "Not authenticated"
}
```

403 Forbidden - Not organization admin:
```json
{
  "detail": "You don't have permission to delete this organization"
}
```

404 Not Found:
```json
{
  "detail": "Organization 'techcorp' not found"
}
```

**Example cURL:**
```bash
curl -X DELETE "http://localhost:8000/org/delete" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "techcorp"
  }'
```

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Request completed successfully |
| 201 | Created - Resource successfully created |
| 400 | Bad Request - Invalid input or business rule violation |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Authenticated but not authorized |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server-side error |

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Recommended: 100 requests per minute per IP
- Authentication endpoints: 10 requests per minute
- Protected endpoints: 60 requests per minute

---

## Pagination

Not implemented in current version. For large datasets, implement:
```
GET /org/list?page=1&limit=50
```

---

## Versioning

Current API version: v1.0.0

Future versions should be accessible via:
```
http://localhost:8000/v1/org/create
http://localhost:8000/v2/org/create
```

---

## Common Workflows

### Workflow 1: Create and Login

```bash
# Step 1: Create organization
curl -X POST http://localhost:8000/org/create \
  -H "Content-Type: application/json" \
  -d '{"organization_name": "mycompany", "email": "admin@mycompany.com", "password": "SecurePass123"}'

# Step 2: Login
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mycompany.com", "password": "SecurePass123"}'

# Save the access_token from response
```

### Workflow 2: Update Organization

```bash
# Step 1: Get token from login (see above)
TOKEN="your_jwt_token_here"

# Step 2: Update organization
curl -X PUT http://localhost:8000/org/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"organization_name": "mycompany", "new_organization_name": "mycompany_global"}'
```

### Workflow 3: Delete Organization

```bash
# Step 1: Get token from login
TOKEN="your_jwt_token_here"

# Step 2: Delete organization
curl -X DELETE http://localhost:8000/org/delete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"organization_name": "mycompany"}'
```

---

## Testing

### Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test endpoints directly
- Authenticate and test protected routes

### Postman Collection

Import `postman_collection.json` into Postman for complete API testing suite with:
- Pre-configured requests
- Environment variables
- Automatic token handling
- Test scripts

### Python Test Script

Run the included test script:
```bash
python test_api.py
```

---

## Security Best Practices

### For Clients

1. **Store tokens securely**: Never store in localStorage if XSS is a concern
2. **Use HTTPS**: Always use encrypted connections in production
3. **Token expiration**: Handle 401 errors and re-authenticate
4. **Don't log tokens**: Never log JWT tokens
5. **Validate responses**: Always validate API responses

### For Developers

1. **Change SECRET_KEY**: Use a strong, random secret key
2. **Enable HTTPS**: Use TLS/SSL certificates
3. **Rate limiting**: Implement rate limiting in production
4. **Input validation**: Already implemented with Pydantic
5. **Monitoring**: Add logging and monitoring
6. **Backups**: Regular database backups

---

## Database Schema

### Organizations Collection

```json
{
  "_id": ObjectId("..."),
  "organization_id": "uuid",
  "organization_name": "techcorp",
  "collection_name": "org_techcorp",
  "admin_id": "uuid",
  "created_at": ISODate("2025-12-12T10:00:00Z"),
  "updated_at": ISODate("2025-12-12T11:00:00Z")
}
```

### Admins Collection

```json
{
  "_id": ObjectId("..."),
  "admin_id": "uuid",
  "email": "admin@techcorp.com",
  "hashed_password": "$2b$12$...",
  "organization_id": "uuid",
  "created_at": ISODate("2025-12-12T10:00:00Z"),
  "is_active": true
}
```

### Dynamic Organization Collections

```json
{
  "_id": ObjectId("..."),
  "type": "metadata",
  "organization_id": "uuid",
  "created_at": ISODate("2025-12-12T10:00:00Z"),
  "description": "Data collection for techcorp"
}
```

---

## Support

For issues or questions:
1. Check this API documentation
2. Review [README.md](README.md) for setup issues
3. Check [QUICKSTART.md](QUICKSTART.md) for troubleshooting
4. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details

---

**API Version**: 1.0.0  
**Last Updated**: December 12, 2025  
**Base URL**: http://localhost:8000
