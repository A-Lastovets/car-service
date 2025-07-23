# Car Service API

A comprehensive car service management system built with FastAPI, featuring user management, appointment scheduling, car maintenance tracking, and document management.

## Features

- **User Management**: Customer registration, authentication, and role-based access control
- **Car Management**: Add, edit, and track customer vehicles
- **Service Management**: Define and manage car services
- **Appointment Scheduling**: Book and manage service appointments
- **Mechanic Management**: Assign mechanics to appointments
- **Document Management**: Upload and store service documents
- **Email Notifications**: Automated email confirmations
- **Admin Panel**: Comprehensive admin interface for system management

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **Email**: Celery with Redis
- **Documentation**: Swagger/OpenAPI
- **Validation**: Pydantic

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Redis (for Celery)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd car-service
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL Database**

   **Step 1: Install MySQL Server**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install mysql-server
   
   # Windows
   # Download and install MySQL from https://dev.mysql.com/downloads/mysql/
   
   # macOS
   brew install mysql
   ```

   **Step 2: Start MySQL Service**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start mysql
   sudo systemctl enable mysql
   
   # Windows
   # MySQL service should start automatically
   
   # macOS
   brew services start mysql
   ```

   **Step 3: Secure MySQL Installation**
   ```bash
   sudo mysql_secure_installation
   ```

   **Step 4: Create Database and User**
   ```bash
   mysql -u root -p
   ```
   
   ```sql
   -- Create database
   CREATE DATABASE car_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- Create user
   CREATE USER 'car_service_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON car_service_db.* TO 'car_service_user'@'localhost';
   FLUSH PRIVILEGES;
   
   -- Exit MySQL
   EXIT;
   ```

4. **Configure Environment Variables**
   
   Copy the example environment file:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your settings:
   ```env
   # Database Configuration
   DATABASE_URL=mysql+aiomysql://car_service_user:your_secure_password@localhost:3306/car_service_db
   
   # Authentication Settings
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   RESET_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # Frontend Settings
   FRONTEND_URL=http://localhost:3000,http://127.0.0.1:3000
   FRONTEND_URL_FOR_LINKS=http://localhost:3000
   
   # Redis Settings (for Celery)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   
   # Email Settings
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   EMAIL_FROM=your-email@gmail.com
   ```

5. **Initialize Database**
   ```bash
   # Run the application to create tables and initial admin
   python -m uvicorn app.main:app --reload
   ```

6. **Start the Application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## Authentication System

### User Types and Authentication

The system supports two separate authentication flows:

#### 1. Clients and Administrators (users table)
- **Registration**: `POST /auth/register` - Only for customers
- **Login**: `POST /auth/login` - Email + password
- **Roles**: `customer`, `admin`

#### 2. Mechanics (mechanics table)
- **Login**: `POST /mechanics/login` - Login + password
- **Roles**: `mechanic`, `admin`
- **Creation**: Only by administrators via `POST /mechanics/`

### Creating the first administrator

When you start the application for the first time with a clean database, the system automatically creates initial admin users:

- **Admin User**: `admin@car-service.com` / `admin123!`
- **Admin Mechanic**: `admin_mechanic` / `admin123!`

⚠️ **Important**: Change these passwords after first login!

## API Endpoints

### Authentication
- `POST /auth/register` - Register new customer
- `POST /auth/login` - Login for customers/admins
- `POST /mechanics/login` - Login for mechanics

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `PATCH /users/me/password` - Change password

### Cars
- `GET /cars/` - Get user's cars
- `POST /cars/` - Add new car
- `GET /cars/{car_id}` - Get specific car
- `PUT /cars/{car_id}` - Update car
- `DELETE /cars/{car_id}` - Delete car

### Services
- `GET /services/` - Get all services
- `POST /services/` - Create service (admin only)
- `GET /services/{service_id}` - Get specific service
- `PUT /services/{service_id}` - Update service (admin only)
- `DELETE /services/{service_id}` - Delete service (admin only)

### Appointments
- `GET /appointments/` - Get user's appointments
- `POST /appointments/` - Create appointment
- `GET /appointments/history` - Get appointment history
- `GET /appointments/{appointment_id}` - Get specific appointment
- `PUT /appointments/{appointment_id}` - Update appointment
- `DELETE /appointments/{appointment_id}` - Delete appointment
- `PATCH /appointments/{appointment_id}/status` - Update appointment status

### Mechanics
- `GET /mechanics/` - Get all mechanics
- `POST /mechanics/` - Create mechanic (admin only)
- `GET /mechanics/{mechanic_id}` - Get specific mechanic
- `PUT /mechanics/{mechanic_id}` - Update mechanic (admin only)
- `DELETE /mechanics/{mechanic_id}` - Delete mechanic (admin only)

### Documents
- `GET /documents/` - Get user's documents
- `POST /documents/upload` - Upload document
- `GET /documents/{document_id}` - Get specific document
- `DELETE /documents/{document_id}` - Delete document

### Admin
- `GET /admin/users` - Get all users (admin only)
- `GET /admin/mechanics` - Get all mechanics (admin only)
- `GET /admin/documents` - Get all documents (admin only)
- `GET /admin/appointments` - Get all appointments (admin only)
- `PATCH /admin/users/{user_id}/change_role` - Change user role (admin only)

## Database Structure

### Tables

1. **users** - Customer and admin accounts
   - id, name, email, password, role

2. **mechanics** - Mechanic accounts
   - id, name, birth_date, login, password, role, position

3. **cars** - Customer vehicles
   - id, user_id, brand, model, year, license_plate, vin

4. **services** - Available services
   - id, name, description, price, duration

5. **appointments** - Service appointments
   - id, user_id, car_id, service_id, mechanic_id, appointment_date, status

6. **documents** - Service documents
   - id, user_id, filename, file_path, upload_date

## Working with documents

Documents are stored locally in the `documents/` directory. The system supports:
- File upload with validation
- Secure file storage
- File metadata tracking in database

## Appointment management

### Statuses
- **Заплановано** - Scheduled
- **В роботі** - In Progress
- **Завершено** - Completed
- **Скасовано** - Cancelled

### Features
- Automatic email confirmations
- Mechanic assignment
- Status tracking
- History management

## Testing

### Manual Testing
1. Start the application
2. Open `http://localhost:8000/docs`
3. Test endpoints using Swagger UI

### API Testing
```bash
# Test registration
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'

# Test login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## Tips

### Development
- Use `--reload` flag for development
- Check logs for debugging
- Use Swagger UI for API testing

### Production
- Change default admin passwords
- Use strong SECRET_KEY
- Configure proper email settings
- Set up SSL/TLS
- Use environment variables for sensitive data

### Database
- Regular backups
- Monitor performance
- Use proper indexes
- Configure connection pooling

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify DATABASE_URL in .env
   - Ensure database and user exist

2. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Permission Errors**
   - Ensure documents/ directory is writable
   - Check file permissions

4. **Email Not Working**
   - Verify SMTP settings in .env
   - Check firewall settings
   - Use app passwords for Gmail

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.