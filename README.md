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

Edit the `.env` file with your settings:
```env
# Database Settings
DATABASE_URL=sqlite+aiosqlite:///./car_service.db
DB_ECHO=True

# JWT Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Email settings (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Redis for Celery (if using background tasks)
REDIS_URL=redis://localhost:6379/0
```

### 5. Initialize Database
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration to create tables
alembic upgrade head
```

### 6. Run the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Initial Setup

The application automatically creates:
- **Admin User**: `admin@example.com` / `admin123`
- **Sample Mechanic**: `mechanic@example.com` / `mechanic123`

**Important**: Change these default credentials in production!

## API Endpoints

### Authentication
- `POST /auth/register` - Customer registration
- `POST /auth/login` - User login
- `POST /auth/mechanic/login` - Mechanic login
- `POST /auth/refresh` - Refresh access token

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `PATCH /users/{user_id}/role` - Change user role (Admin only)

### Cars
- `GET /cars/` - List user's cars
- `POST /cars/` - Register new car
- `GET /cars/{car_id}` - Get car details
- `PUT /cars/{car_id}` - Update car
- `DELETE /cars/{car_id}` - Delete car

### Services
- `GET /services/` - List available services
- `POST /services/` - Create service (Admin only)
- `GET /services/{service_id}` - Get service details
- `PUT /services/{service_id}` - Update service (Admin only)
- `DELETE /services/{service_id}` - Delete service (Admin only)

### Appointments
- `GET /appointments/` - List appointments
- `POST /appointments/` - Create appointment
- `GET /appointments/{appointment_id}` - Get appointment details
- `PUT /appointments/{appointment_id}` - Update appointment
- `DELETE /appointments/{appointment_id}` - Cancel appointment
- `PATCH /appointments/{appointment_id}/status` - Update status (Mechanic/Admin)

### Mechanics
- `GET /mechanics/` - List mechanics
- `POST /mechanics/` - Create mechanic account (Admin only)
- `GET /mechanics/{mechanic_id}` - Get mechanic details
- `PUT /mechanics/{mechanic_id}` - Update mechanic
- `DELETE /mechanics/{mechanic_id}` - Delete mechanic (Admin only)

### Documents
- `GET /documents/` - List documents
- `POST /documents/` - Upload document
- `GET /documents/{document_id}` - Download document
- `DELETE /documents/{document_id}` - Delete document

## Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `phone`
- `role` (customer, mechanic, admin)
- `is_active`
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
- `status` (pending, confirmed, in_progress, completed, cancelled)
- `notes`
- `created_at`
- `updated_at`

### Documents Table
- `id` (Primary Key)
- `appointment_id` (Foreign Key)
- `filename`
- `file_path`
- `file_size`
- `mime_type`
- `uploaded_at`

## Authentication & Authorization

### JWT Tokens
- Access tokens expire in 30 minutes (configurable)
- Refresh tokens for extending sessions
- Role-based access control

### Roles
- **Customer**: Can manage their cars and appointments
- **Mechanic**: Can view and update assigned appointments
- **Admin**: Full access to all endpoints and user management

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

## Production Deployment

### Security Considerations
1. Change default admin credentials
2. Use strong SECRET_KEY
3. Enable HTTPS
4. Configure proper CORS settings
5. Set up proper logging
6. Use environment variables for sensitive data

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.