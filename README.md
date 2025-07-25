# Car Service Management API

A comprehensive RESTful API for managing car service appointments, built with FastAPI and SQLite.

## Features

- **User Management**: Customer registration and authentication
- **Mechanic Management**: Separate mechanic accounts with authentication
- **Car Management**: Vehicle registration and tracking
- **Service Management**: Service catalog and pricing
- **Appointment Scheduling**: Booking and managing service appointments
- **Document Management**: File uploads and storage
- **Role-based Access Control**: Customer, Mechanic, and Admin roles
- **Email Notifications**: Automated email sending for appointments
- **Background Tasks**: Celery integration for async operations
- **Redis Caching**: Role-based access control caching
- **JWT Authentication**: Secure token-based authentication

## Project Structure

```
car-service/
├── alembic/                 # Database migrations
├── app/
│   ├── config.py           # Application configuration
│   ├── main.py             # FastAPI application entry point
│   ├── dependencies/       # Dependency injection
│   │   ├── database.py     # Database session management
│   │   └── cache.py        # Redis client
│   ├── middlewares/        # Custom middlewares
│   ├── models/             # SQLAlchemy models
│   │   ├── base.py         # Base model
│   │   ├── user.py         # User model
│   │   ├── mechanic.py     # Mechanic model
│   │   ├── car.py          # Car model
│   │   ├── service.py      # Service model
│   │   ├── appointment.py  # Appointment model
│   │   └── document.py     # Document model
│   ├── routers/            # API route handlers
│   │   ├── auth_router.py  # Authentication routes
│   │   ├── users_router.py # User management
│   │   ├── cars_router.py  # Car management
│   │   ├── services_router.py # Service management
│   │   ├── appointments_router.py # Appointment management
│   │   ├── mechanics_router.py # Mechanic management
│   │   ├── documents_router.py # Document management
│   │   └── admin_router.py # Admin panel
│   ├── schemas/            # Pydantic schemas
│   │   ├── base_schema.py  # Base schema
│   │   ├── user_schema.py  # User schemas
│   │   ├── car_schema.py   # Car schemas
│   │   ├── service_schema.py # Service schemas
│   │   ├── appointment_schema.py # Appointment schemas
│   │   ├── mechanic_schema.py # Mechanic schemas
│   │   └── document_schema.py # Document schemas
│   ├── services/           # Business logic
│   │   ├── email_service.py # Email sending
│   │   ├── init_admin.py   # Admin initialization
│   │   └── celery.py       # Background tasks
│   └── utils/              # Utility functions
│       ├── auth.py         # Authentication utilities
│       ├── password.py     # Password hashing
│       └── tokens.py       # JWT token management
├── documents/              # File storage
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── alembic.ini            # Alembic configuration
└── README.md              # This file
```

## Quick Start (SQLite - No Server Required)

### Database Configuration

The application supports multiple database types through environment variables:

**SQLite (Default - No server required):**
```env
DATABASE_URL=sqlite+aiosqlite:///./car_service.db
DB_ECHO=True
```

**MySQL (Requires MySQL server):**
```env
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/car_service_db
DB_ECHO=False
```

**PostgreSQL (Requires PostgreSQL server):**
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/car_service_db
DB_ECHO=False
```

### 1. Clone the Repository
```bash
git clone <repository-url>
cd car-service
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Copy the example environment file and configure it:
```bash
cp env.example .env
```

Edit the `.env` file with your settings. See `env.example` for all available options:

**Required Settings:**
```env
# Database Settings
DATABASE_URL=sqlite+aiosqlite:///./car_service.db
DB_ECHO=True

# JWT Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=30

# Redis Settings (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

**Optional Settings:**
```env
# Email settings (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Frontend settings
FRONTEND_URL=http://localhost:3000
FRONTEND_SIGNUP_URL=http://localhost:3000/signup

# CORS settings
ALLOWED_ORIGINS=*
CORS_ALLOW_ALL=True
```

### 5. Initialize Database
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration to create tables
alembic upgrade head
```

### 6. Create Initial Admin Users
```bash
# This will be done automatically when the server starts
# Or run manually:
python -m app.services.init_admin
```

### 7. Run the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Using Swagger UI

1. **Open Swagger UI**: Navigate to http://localhost:8000/docs
2. **Login**: Click the "Authorize" button (🔒) in the top right
3. **Enter credentials**: Use the `/auth/sign-in-swagger` endpoint with:
   - `username`: your email
   - `password`: your password
4. **Test endpoints**: All protected endpoints will now work with your authentication

### Authentication Flow

1. **Register**: Use `/auth/register` to create a customer account
2. **Login**: Use `/auth/login` (JSON) or `/auth/sign-in-swagger` (form)
3. **Get tokens**: Receive access and refresh tokens
4. **Use API**: Include `Authorization: Bearer <access_token>` header
5. **Refresh**: Use `/auth/refresh-token` when access token expires

### Testing the API

#### Using curl
```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "password123"}'

# Use the access token
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Using Python requests
```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "name": "John Doe",
    "email": "john@example.com", 
    "password": "password123"
})

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "john@example.com",
    "password": "password123"
})

token = response.json()["tokens"]["access_token"]

# Use API with token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/users/me", headers=headers)
print(response.json())
```

### Default Users

The application automatically creates:
- **Admin User**: `admin@example.com` / `admin123`
- **Sample Mechanic**: `mechanic@example.com` / `mechanic123`

**Important**: Change these default credentials in production!

## API Endpoints

### Authentication
- `POST /auth/register` - Customer registration
- `POST /auth/login` - User login (JSON)
- `POST /auth/sign-in-swagger` - User login (for Swagger UI)
- `POST /auth/refresh-token` - Refresh access token
- `POST /auth/logout` - Logout (blacklist token)
- `POST /auth/password-recovery` - Request password reset
- `POST /auth/password-reset` - Reset password with token

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile

### Cars
- `GET /cars/` - List user's cars
- `POST /cars/` - Register new car
- `PUT /cars/{car_id}` - Update car
- `DELETE /cars/{car_id}` - Delete car

### Services
- `GET /services/` - List available services
- `POST /services/` - Create service (Admin only)
- `PUT /services/{service_id}` - Update service (Admin only)
- `DELETE /services/{service_id}` - Delete service (Admin only)

### Appointments
- `GET /appointments/` - List user's appointments
- `POST /appointments/` - Create appointment
- `GET /appointments/history` - Get appointment history
- `PUT /appointments/{appointment_id}` - Update appointment
- `DELETE /appointments/{appointment_id}` - Cancel appointment
- `PATCH /appointments/{appointment_id}/status` - Update status
- `PATCH /appointments/{appointment_id}/assign_mechanic` - Assign mechanic (Admin only)

### Mechanics
- `GET /mechanics/` - List mechanics
- `POST /mechanics/` - Create mechanic account (Admin only)
- `POST /mechanics/login` - Mechanic login
- `PUT /mechanics/{mechanic_id}` - Update mechanic (Admin only)
- `DELETE /mechanics/{mechanic_id}` - Delete mechanic (Admin only)

### Documents
- `POST /documents/` - Upload document (Mechanic/Admin only)
- `PUT /documents/{document_id}` - Update document (Mechanic/Admin only)
- `DELETE /documents/{document_id}` - Delete document (Mechanic/Admin only)

### Admin Panel
- `GET /admin/users` - List all users (Admin only)
- `GET /admin/mechanics` - List all mechanics (Admin only)
- `GET /admin/documents` - List all documents (Admin only)
- `GET /admin/appointments` - List all appointments (Admin only)
- `PATCH /admin/users/{user_id}/change_role` - Change user role (Admin only)

## Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `phone`
- `role` (customer, mechanic, admin)
- `is_active`
- `last_login`
- `created_at`
- `updated_at`

### Mechanics Table
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `phone`
- `specialization`
- `is_active`
- `created_at`
- `updated_at`

### Cars Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `brand`
- `model`
- `year`
- `license_plate`
- `plate_number`
- `vin`
- `created_at`
- `updated_at`

### Services Table
- `id` (Primary Key)
- `name`
- `description`
- `price`
- `duration_minutes`
- `is_active`
- `created_at`
- `updated_at`

### Appointments Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `car_id` (Foreign Key)
- `mechanic_id` (Foreign Key)
- `service_id` (Foreign Key)
- `appointment_date`
- `status` (scheduled, in_progress, completed, cancelled)

### Documents Table
- `id` (Primary Key)
- `mechanic_id` (Foreign Key)
- `type`
- `file_path`

## Authentication & Authorization

### JWT Tokens
- Access tokens expire in 30 minutes (configurable)
- Refresh tokens for extending sessions
- Role-based access control with Redis caching

### Roles & Permissions
- **Customer**: Can manage their cars and appointments
- **Mechanic**: Can view assigned appointments and upload documents
- **Admin**: Full access to all endpoints and user management

### Security Features
- Password hashing with bcrypt
- JWT token blacklisting
- Role-based access control with caching
- CORS protection
- Input validation with Pydantic

## Background Tasks

The application uses Celery for background tasks:
- Email notifications for appointment confirmations
- Document processing
- Scheduled reminders

## File Storage

Documents are stored in the `documents/` directory with organized folder structure.

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

### Database Migration

Alembic is used for database migrations. Here's how to work with it:

```bash
# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1

# Check current migration status
alembic current

# View migration history
alembic history
```

**Important**: Always review auto-generated migrations before applying them!

### Redis Setup (Optional)

For role-based access control caching:

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Install Redis (macOS)
brew install redis

# Start Redis
redis-server

# Test Redis connection
redis-cli ping
```

## Production Deployment

### Security Considerations
1. Change default admin credentials
2. Use strong SECRET_KEY (generate with: `openssl rand -hex 32`)
3. Enable HTTPS
4. Configure proper CORS settings
5. Set up proper logging
6. Use environment variables for sensitive data
7. Configure Redis with authentication
8. Set up proper email SMTP settings

### Environment Variables for Production
```env
# Security
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
CORS_ALLOW_ALL=False
ALLOWED_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
DB_ECHO=False

# Redis
REDIS_HOST=your-redis-host
REDIS_PASSWORD=your-redis-password
REDIS_USE_SSL=True

# Email
SMTP_SERVER=your-smtp-server
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password
EMAIL_FROM=noreply@yourdomain.com
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **Database connection errors**: Check `DATABASE_URL` and ensure database is running
2. **Redis connection errors**: Check Redis settings and ensure Redis server is running
3. **Email sending fails**: Verify SMTP settings and credentials
4. **JWT token errors**: Check `SECRET_KEY` and token expiration settings
5. **CORS errors**: Configure `ALLOWED_ORIGINS`

### Logs
Check application logs for detailed error information:
```bash
# View logs
tail -f logs/app.log

# Check Redis logs
redis-cli monitor
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.