# Algorithm Learning Platform - Backend API

A comprehensive FastAPI-based backend for an algorithm learning platform that provides interactive coding exercises, AI-powered tutoring, and progress tracking for students learning algorithms and data structures.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Course System**: Structured algorithm courses with chapters and learning points
- **Interactive Coding**: Code execution environment with multiple language support
- **AI Tutor**: Intelligent hints and guidance powered by Pydantic AI
- **Progress Tracking**: Chapter completion and learning analytics
- **Rate Limiting**: API protection with request throttling
- **Admin Panel**: Course and user administration capabilities

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLModel](https://sqlmodel.tiangolo.com/)
- **Authentication**: JWT tokens with HTTP-only cookies
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) for database schema management
- **AI Integration**: [Pydantic AI](https://ai.pydantic.dev/) for intelligent tutoring
- **Code Execution**: [Piston API](https://piston.readthedocs.io/) integration
- **Monitoring**: [Logfire](https://logfire.pydantic.dev/) for observability
- **Package Management**: [uv](https://docs.astral.sh/uv/) for fast Python package management

## 📋 Prerequisites

- **Python**: 3.13 or higher
- **PostgreSQL**: 12 or higher
- **uv**: Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/philippspitzley/algorithm-sensei.git
cd backend
```

### 2. Install Dependencies

```bash
# Install uv if you haven't already: 
curl -LsSf https://astral.sh/uv/install.sh | sh


# Install project dependencies
uv sync
```

### 3. Environment Configuration

Create a `.env` file in the project root (backend folder):

```bash
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=algorithm_learning_db

# Application Settings
PROJECT_NAME="Algorithm Learning Platform API"
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days
ENVIRONMENT=local

# Frontend Configuration
FRONTEND_HOST=http://localhost:5173
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# AI Configuration (Optional)
OPENAI_API_KEY=your-gemini-api-key
LOGFIRE_TOKEN=your-logfire-token

# Piston API (Code Execution)
# You can self host Piston API with docker or use the public API
PISTON_API_URL=https://emkc.org/api/v2/piston

```

### 4. Database Setup

```bash
# Start PostgreSQL service (macOS with Homebrew)
brew services start postgresql

# Create database
createdb algorithm_learning_db

# Run database migrations
uv run alembic upgrade head
```

### 5. Initialize Sample Data (Optional)

```bash
# Create initial admin user and sample courses
uv run python -c "from app.initial_data import init; init()"
```

### 6. Run the Development Server

```bash
# Start the FastAPI development server
uv run fastapi dev app/main.py
```

The API will be available at:

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ⚙️ Configuration

Key environment variables and their purposes:

| Variable                      | Description           | Default               |
| ----------------------------- | --------------------- | --------------------- |
| `POSTGRES_SERVER`             | Database host         | localhost             |
| `POSTGRES_PORT`               | Database port         | 5432                  |
| `PROJECT_NAME`                | API title             | ""                    |
| `SECRET_KEY`                  | JWT signing key       | Auto-generated        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity        | 11520 (8 days)        |
| `ENVIRONMENT`                 | Deployment env        | local                 |
| `FRONTEND_HOST`               | Frontend URL for CORS | http://localhost:5173 |

## 🗄️ Database Management

### Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Downgrade to previous revision
uv run alembic downgrade -1
```

### Database Reset

```bash
# Drop and recreate database
dropdb algorithm_learning_db
createdb algorithm_learning_db
uv run alembic upgrade head
```

## 📚 API Documentation

### Available Endpoints

The API provides the following main endpoint groups:

#### Authentication

- `POST /api/v1/login/access-token` - User login
- `POST /api/v1/users/signup` - User registration

#### Users

- `GET /api/v1/users/me` - Get current user profile
- `GET /api/v1/users/me/courses` - Get enrolled courses
- `POST /api/v1/users/me/courses/{course_id}/enroll` - Enroll in course

#### Courses & Chapters

- `GET /api/v1/courses` - List all courses
- `GET /api/v1/courses/{course_id}` - Get course details
- `GET /api/v1/chapters` - List chapters
- `GET /api/v1/chapters/{chapter_id}` - Get chapter details

#### AI Tutor

- `POST /api/v1/ai/generate` - Get AI-powered hints
- `GET /api/v1/ai/health` - AI service health check

#### Code Execution

- `POST /api/v1/piston/execute` - Execute code snippets

#### Statistics

- `GET /api/v1/stats` - Get platform statistics

### Authentication

The API uses JWT tokens with HTTP-only cookies for authentication. After login, the token is automatically included in requests.

Example login request:

```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

## 🏗️ Development

### Project Structure

```
backend/
├── app/
│   ├── api/                 # API routes and dependencies
│   │   ├── routes/         # Individual route modules
│   │   ├── deps.py         # Dependency injection
│   │   └── exceptions.py   # Custom exception handlers
│   ├── core/               # Core functionality
│   │   ├── config.py       # Application settings
│   │   ├── db.py          # Database connection
│   │   └── security.py    # Authentication utilities
│   ├── models/             # Pydantic/SQLModel models
│   ├── services/           # Business logic services
│   ├── alembic/           # Database migrations
│   └── main.py            # FastAPI application entry point
├── pyproject.toml         # Project dependencies
└── alembic.ini           # Migration configuration
```

### Code Quality

The project includes pre-commit hooks and linting:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run linting manually
uv run ruff check .
uv run ruff format .
```

### Testing

```bash
# Run tests (when implemented)
uv run pytest
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **HTTP-Only Cookies**: Prevents XSS attacks
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Controlled cross-origin access
- **Password Hashing**: Bcrypt for secure password storage
- **Input Validation**: Pydantic models for data validation

## 📈 Monitoring & Observability

The application includes integrated monitoring with Logfire. By default it is only used for the AI tutor, but can be extended to other parts of the application.

```python
# Monitoring is configured in app/main.py
logfire.configure(token=settings.LOGFIRE_TOKEN)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Note**: This backend is based on the [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) and has been customized for algorithm learning platform requirements.
