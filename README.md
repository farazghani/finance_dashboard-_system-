# Finance Data Processing and Access Control Backend

### Overview

This project is a backend system for managing financial records and providing summary insights for a dashboard. It demonstrates backend design principles such as data modeling, API design, role-based access control, and aggregation logic.

The system allows users with different roles to interact with financial data securely and efficiently.

### features

## User features
user can 
```
sign in 
sign out
login
logout

```

User can have three roles: 


 viewer-> can only view dashboard data
 analyst -> can view records and access insights
 admin -> can create , update and manage records and users

## records features:
 should have following feature
 ```
 creating records
 viewing records
 updating records 
 deleting records
 filtering records based on criteria as date, category or type

```

## Access control logic
```
| Action        | Viewer | Analyst | Admin |
| ------------- | ------ | ------- | ----- |
| Create Record | ❌      | ❌       | ✅     |
| View Records  | ✅      | ✅       | ✅     |
| Update Record | ❌      | ❌       | ✅     |
| Delete Record | ❌      | ❌       | ✅     |
| View Summary  | ✅      | ✅       | ✅     |
| Manage Users  | ❌      | ❌       | ✅     |
```

## dashboard features:
should view following analytics:
total income , total expense for a user,
category wise expense
date wise expense , income


### TECH STACK
# 1. Core Framework: FastAPI
# 2. Data Validation: Pydantic v2
# 3. Database: SQLite (Raw SQL)
# 4. Security & Identity: PyJWT & Passlib

### SYSTEM ARCHITECTURE (mental model)







### PROJECT STRUCTURE

```
finance_backend/
├── src/
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── security.py (dependency injection for auth)
│   ├── models/ (Pydantic)
│   │   ├── user.py
│   │   ├── transaction.py
│   │   └── dashboard.py 
|   ├── schemas
          ├── userSchema.py
          └──recordSchema.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── finance_service.py
│   │   └── dashboard_service.py
│   ├── routes/
│   │   ├── users.py
│   │   ├── records.py
│   │   └── dashboard.py
│   ├── db/
│   │   ├── database.py
│   │   └── migrations.sql
│   └── main.py
├── tests/
│   ├── test_access_control.py
│   ├── test_finance_service.py
│   └── test_dashboard.py
├── README.md (with permission matrix)
└── requirements.txt
|
└──tests/

```

### Data Modeling Architecture

## physical data model

# USER

```
USER(
id
name 
email
password(encrpyted)
role
createdAt
)
```

# RECORDS
```
RECORD(
id
userid
amount > 0
type (debit , credit)
category ('salary' 'expense' 'food' 'Rent')
date
notes
createdAt
)
```
# AUDIT LOGS
```
audit_log(
id
user_id
action
target_id
details
created_at
)
```
## Logical Data Model (Pydantic Schemas)

# user schema hierarchy

UserBase: Contains common fields like email, name, and role.

UserCreate: Extends UserBase to include a password field (Write-only).

UserResponse: Extends UserBase to include id and created_at. Crucial: It excludes the password hash to ensure security.

# Transaction Schema Hierarchy

RecordBase: Defines the shape of a financial entry (amount, category, type, date).

RecordCreate: Used for incoming POST requests. Includes validation logic (e.g., date must not be in the future).

RecordResponse: Adds the system-generated id and the owner's user_id

# Analytics & Dashboard Schemas

These are "Virtual Models" that do not map 1:1 to a single table but represent the output of complex SQL aggregations.

CategorySummary: Represents a grouped total (e.g., "Food: $500").

DashboardSummary: The master contract for the frontend, containing totals, net balance, and a list of recent activity.

## RBAC logic implementation

mvp approach would be checking role.user == "Admin" on each protected endpoint was thinking to implement a middleware  

but my approach here is to implement a Stateless RBAC architecture instead of querying the database for permissions on every request, the user's role is securely encoded into their JWT (JSON Web Token).


# implementation layer


# A. identity layer
when user authenticates , the user_services fetches their role from the  database

the role is then added to the JWT payload

```
{
  "sub": "user_123",
  "role": "analyst",
  "exp": 1712150000
}

```

# B. Gateway Layer

use a custom  Rolechecker dependency to gate specific routes 


## Security Considerations
Immutability: Once a JWT is issued, the role cannot be changed by the client because any tampering would invalidate the cryptographic signature.


Granularity: The RoleChecker allows for multiple roles to access the same resource (e.g., ["admin", "analyst"]), providing flexibility without code duplication.


Fail-Safe: By default, all routes are protected. Access must be explicitly granted by attaching the dependency to the route.

## Error Handling & Messaging Strategy
The application implements a Centralized Exception Mapping pattern. This ensures that every error—whether it's a database constraint violation, a failed login, or a permission issue—returns a consistent, machine-readable JSON response.

1. Global Exception Handler
Instead of using try-except blocks inside every route, the system uses a Global Exception Handler in main.py. This middleware intercepts custom Python exceptions and converts them into standardized HTTP responses.

```
{
  "status_code": 403,
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "message": "You do not have the required 'admin' role to delete this record.",
  "timestamp": "2026-04-03T02:20:00Z"
}

```
2. Categorized Error
following error categories are handled explicitly:Category

```
## ⚠️ Error Handling

| Category         | HTTP Status              | Scenario                                                                  |
| ---------------- | ------------------------ | ------------------------------------------------------------------------- |
| Validation Error | 422 Unprocessable Entity | Pydantic catches invalid data formats (e.g., negative amounts, bad email) |
| Authentication   | 401 Unauthorized         | Invalid or expired authentication token (e.g., JWT)                       |
| Authorization    | 403 Forbidden            | User is authenticated but lacks required role/permission                  |
| Resource Missing | 404 Not Found            | Requested resource (e.g., transaction ID) does not exist                  |
| Conflict         | 409 Conflict             | Duplicate resource (e.g., email already registered)                       |


```

### API

The API follows RESTful principles, using standard HTTP methods and status codes. All requests and responses are encoded in application/json.

 Interactive Documentation
Once the server is running, you can access the interactive OpenAPI (Swagger) documentation at:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

1. Authentication (/auth)
Endpoints for identity management and session establishment.

2. Financial Records (/records)
Core CRUD operations for managing income and expenses. Requirement #2

3. Dashboard & Analytics (/dashboard)
Aggregated data for high-level financial oversight. Requirement #3

4. Administrative Tools (/admin)
User and system management. Requirement #4

🛠 Request & Response Examples
Example: Create a Record (POST /records)
Request Body:

Successful Response (201 Created):

Example: Unauthorized Access (403 Forbidden)
If a Viewer attempts to DELETE a record, the system returns: