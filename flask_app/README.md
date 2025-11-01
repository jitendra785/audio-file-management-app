# Audio File Management App

A Flask web application for managing audio files with user authentication and role-based access control.

## Features

- **User Authentication**
  - Login and signup functionality
  - Password hashing with bcrypt
  - Session management with Flask-Login
  - Role-based access (ADMIN and USER)

- **Admin Panel**
  - Create, update, delete, and view users
  - Manage user roles
  - User table with search and filtering

- **Audio File Management**
  - Upload audio files (mp3, wav, ogg, m4a, flac)
  - Play audio directly in browser
  - Download audio files
  - Update/replace existing files
  - Delete files
  - File metadata stored in PostgreSQL
  - Actual files stored in MongoDB GridFS

## Technology Stack

- **Backend**: Flask 3.0
- **Databases**:
  - PostgreSQL (user data and file metadata)
  - MongoDB with GridFS (audio file storage)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with bcrypt
- **Validation**: Pydantic
- **Frontend**: Bootstrap 5 with Jinja2 templates
- **Containerization**: Docker and Docker Compose

## Project Structure

```
flask_app/
├── environments/
│   └── LOCAL.yml              # Environment configuration
│
├── src/
│   ├── basemodels/            # Pydantic request/response models
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── audio.py
│   │
│   ├── routers/               # Flask blueprints (routes)
│   │   ├── auth_routes.py
│   │   ├── admin_routes.py
│   │   └── audio_routes.py
│   │
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── audio_service.py
│   │
│   ├── dependencies/          # Config, DB connections, constants
│   │   ├── app_config.py
│   │   ├── database.py
│   │   └── constants.py
│   │
│   ├── dbentities/            # SQLAlchemy models
│   │   ├── user.py
│   │   └── audio_file.py
│   │
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── admin_users.html
│   │   └── audio_files.html
│   │
│   └── main.py                # Application entry point
│
├── tests/                     # Unit tests (to be implemented)
│
├── Dockerfile
├── docker-compose.yml
├── Pipfile
└── README.md
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.12 (if running without Docker)
- Pipenv (if running without Docker)

### Running with Docker (Recommended)

1. **Navigate to the project directory:**
   ```bash
   cd flask_app
   ```

2. **Build and start the containers:**
   ```bash
   APP_ENV=LOCAL docker compose up --build -d
   ```

3. **Access the application:**
   - Open your browser and navigate to: `http://localhost:5000/auth/login`

4. **Stop the containers:**
   ```bash
   docker compose down
   ```

### Running without Docker

1. **Navigate to the project directory:**
   ```bash
   cd flask_app
   ```

2. **Install dependencies using Pipenv:**
   ```bash
   pipenv install
   ```

3. **Activate the virtual environment:**
   ```bash
   pipenv shell
   ```

4. **Set up PostgreSQL and MongoDB:**
   - Install PostgreSQL and MongoDB locally
   - Update the database credentials in `environments/LOCAL.yml`

5. **Set environment variable:**
   ```bash
   export APP_ENV=LOCAL
   ```

6. **Run the application:**
   ```bash
   python src/main.py
   ```

7. **Access the application:**
   - Open your browser and navigate to: `http://localhost:5000`

## Default Configuration

The default configuration is located in `environments/LOCAL.yml`:

- **Flask App**: Runs on port 5000
- **PostgreSQL**:
  - Database: `audioapp`
  - Username: `audioapp_user`
  - Password: `audioapp_password`
- **MongoDB**:
  - Database: `audioapp`
  - Username: `audioapp_user`
  - Password: `audioapp_password`
- **File Upload**:
  - Max file size: 50 MB
  - Allowed extensions: mp3, wav, ogg, m4a, flac

## Usage

### First Time Setup

1. **Sign Up:**
   - Navigate to `http://localhost:5000`
   - Click "Sign Up"
   - Create your first user account (will be created as USER role)

2. **Create Admin User:**
   - Connect to PostgreSQL database
   - Manually update the first user's role to 'ADMIN'
   ```sql
   UPDATE users SET role = 'ADMIN' WHERE id = 1;
   ```
   - Or create an admin user through the database directly

### User Features

- **Login**: Access your account with username and password
- **Upload Audio**: Upload audio files up to 50 MB
- **Manage Files**: View, play, download, update, or delete your audio files
- **Play Audio**: Stream audio files directly in the browser

### Admin Features

- **User Management**: Create, edit, and delete users
- **Role Assignment**: Assign ADMIN or USER roles
- **View All Users**: See all registered users with their details

## API Endpoints

### Authentication Routes
- `GET /auth/login` - Login page
- `POST /auth/login` - Login handler
- `GET /auth/signup` - Signup page
- `POST /auth/signup` - Signup handler
- `GET /auth/logout` - Logout

### Admin Routes (ADMIN only)
- `GET /admin/users` - View all users
- `POST /admin/users/create` - Create new user
- `POST /admin/users/<id>/edit` - Edit user
- `POST /admin/users/<id>/delete` - Delete user
- `GET /admin/users/<id>/get` - Get user details (JSON)

### Audio Routes (Authenticated users)
- `GET /audio/files` - View user's audio files
- `POST /audio/upload` - Upload audio file
- `GET /audio/files/<id>/play` - Stream audio file
- `GET /audio/files/<id>/download` - Download audio file
- `POST /audio/files/<id>/update` - Update audio file
- `POST /audio/files/<id>/delete` - Delete audio file

## Development

### Running Tests
```bash
pipenv run pytest
```

### Code Formatting
```bash
pipenv run black src/
```

### Linting
```bash
pipenv run flake8 src/
```

## Environment Variables

- `APP_ENV`: Environment name (LOCAL, PROD, etc.) - defaults to LOCAL

## Security Notes

- Passwords are hashed using bcrypt
- Session management via Flask-Login
- Role-based access control for admin features
- File type validation for uploads
- File size limits enforced

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL and MongoDB containers are running
- Check database credentials in `environments/LOCAL.yml`
- Wait for health checks to pass before accessing the app

### File Upload Issues
- Verify file type is in allowed extensions
- Check file size doesn't exceed 50 MB limit
- Ensure MongoDB GridFS is properly initialized
