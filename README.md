# Algorithm Sensei Backend 🥷

<div align="center">
  
  <h2>FastAPI backend for a code learning platform</h2>
  
  [![Python](https://img.shields.io/badge/Python-3.13-4886B9.svg)](https://python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-029485.svg)](https://fastapi.tiangolo.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg)](https://postgresql.org/)
  [![SQLModel](https://img.shields.io/badge/SQLModel-0.0.24-7E56C2.svg)](https://sqlmodel.tiangolo.com/)
  [![Pydantic-AI](https://img.shields.io/badge/PydanticAI-0.2.17-E92063.svg)](https://sqlmodel.tiangolo.com/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🚀 Getting Started](#-getting-started)
- [🏗️ Project Structure](#️-project-structure)
- [🛠️ Technology Stack](#️-technology-stack)
- [⚙️ Configuration](#️-configuration)
- [🗄️ Database Management](#️-database-management)
- [🔒 Security Features](#-security-features)
- [📝 License](#-license)

## 🌟 Overview

Algorithm Sensei Backend is a comprehensive FastAPI-based API that powers an algorithm learning platform. This backend provides the foundation for interactive coding exercises, AI-powered tutoring, and structured learning paths. It works together with the [Algorithm Samurai Frontend](https://github.com/philippspitzley/algorithm-samurai.git) to deliver a complete learning experience with real-time code execution, intelligent hints, and secure user management.

## ✨ Key Features

- **RESTful API**: Clean, well-documented endpoints with automatic OpenAPI generation
- **User Management**: Complete authentication system with JWT tokens and HTTP-only cookies
- **Course System**: Structured algorithm courses with chapter-based organization
- **Code Execution**: Secure multi-language code execution via Piston API integration
- **Progress Tracking**: Comprehensive analytics and learning journey monitoring

<br>

- **Rate Limiting**: API protection with configurable request throttling
- **Monitoring**: Integrated observability with Logfire
- **Admin Panel**: Course and user administration capabilities
- **Database Migrations**: Version-controlled schema management with Alembic

### 🤖 AI Integration

- **Intelligent Tutoring**: Context-aware hints and explanations powered by Pydantic AI
- **Error Analysis**: Detailed feedback on code execution and compilation issues
- **Personalized Learning**: Adaptive difficulty and content recommendations

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.13 or higher
- **PostgreSQL**: 12 or higher
- **uv**: Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Frontend**: This backend works with the [Algorithm Samurai Frontend](https://github.com/philippspitzley/algorithm-samurai.git)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/philippspitzley/algorithm-sensei.git
   cd backend
   ```

2. **Install dependencies**

   ```bash
   # Install uv if you haven't already:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies
   uv sync
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root (backend folder):

   ```bash
   # Copy the sample environment file
   cp .env.sample .env
   ```

   Then edit the `.env` file and fill in your actual values:

   - **Database credentials**: Update `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
   - **Secret key**: Generate a secure secret key for JWT tokens
   - **AI configuration**: Add your Gemini API key and Logfire token (optional)
   - **Piston API**: Keep the default public API URL or update for self-hosted setup

4. **Set up Piston API (Code Execution)**

   #### Option A: Use Public Piston API

   No additional setup required. The public API is already configured in the `.env` file.

   #### Option B: Self-Host Piston API with Docker Compose

   Follow the instructions from the [Piston API documentation](https://github.com/engineer-man/piston?tab=readme-ov-file#getting-started)

   ```bash
   # Update your .env file
   PISTON_API_URL=http://localhost:2000/api/v2/piston
   ```

> [!IMPORTANT]
> Do not forget to [install](https://github.com/engineer-man/piston?tab=readme-ov-file#cli) the javascript runtime for the Piston API to support JavaScript code execution.

<br>

> [!TIP]
> To raise the limits for output and execution time, you can use the following docker configuration before composing up:
>
> 1. Create docker-compose.yaml for Piston API:
>  ```yaml
>   cat > docker-compose.yaml << 'EOF'
>   version: '3.2'
>
>   services:
>       api:
>           image: ghcr.io/engineer-man/piston
>           container_name: piston_api
>           environment:
>               - PISTON_OUTPUT_MAX_SIZE=50000000
>               - PISTON_RUN_OUTPUT_MAX_SIZE=50000000
>               - PISTON_COMPILE_OUTPUT_MAX_SIZE=50000000
>               - PISTON_CPU_TIME_LIMIT=15000
>               - PISTON_WALL_TIME_LIMIT=20000
>           restart: always
>           privileged: true
>           ports:
>               - 2000:2000
>           volumes:
>               - ./data/piston/packages:/piston/packages
>           tmpfs:
>               - /tmp:exec
>   EOF
>   ```
>
> 2. Start Piston API
>   ```bash
>   docker compose up -d
>   ```

5. **Set up database**

   ```bash
   # Start PostgreSQL service (macOS with Homebrew)
   brew services start postgresql

   # Create database
   createdb algorithm_learning_db

   # Run database migrations
   uv run alembic upgrade head
   ```

6. **Start the development server**

   ```bash
   # Start the FastAPI development server
   uv run fastapi dev app/main.py
   ```

7. **Open your browser**
   - **API Base URL**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

> [!NOTE]
> Make sure the [Algorithm Samurai Frontend](https://github.com/philippspitzley/algorithm-samurai.git) is set up to connect to this backend.

### Development Scripts

| Command                     | Description               |
| --------------------------- | ------------------------- |
| `uv run fastapi dev`        | Start development server  |
| `uv run alembic upgrade`    | Apply database migrations |
| `uv run ruff check`         | Run linting               |
| `uv run ruff format`        | Format code               |
| `uv run pre-commit install` | Install git hooks         |

## 🏗️ Project Structure

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

## 🛠️ Technology Stack

### Backend Framework

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[SQLModel](https://sqlmodel.tiangolo.com/)** - SQL databases with Python type annotations
- **[Pydantic](https://pydantic.dev/)** - Data validation and settings management
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database schema migration tool

### Database & Authentication

- **[PostgreSQL](https://www.postgresql.org/)** - Robust relational database
- **[JWT Tokens](https://jwt.io/)** - Secure authentication with HTTP-only cookies
- **[Bcrypt](https://pypi.org/project/bcrypt/)** - Password hashing for security

### AI & Code Execution

- **[Pydantic AI](https://ai.pydantic.dev/)** - Intelligent tutoring and hint generation
- **[Piston API](https://github.com/engineer-man/piston)** - Secure multi-language code execution
- **[Gemini AI](https://ai.google.dev/)** - Advanced AI capabilities

### Monitoring & Development

- **[Logfire](https://logfire.pydantic.dev/docs/)** - Observability and performance monitoring
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package management
- **[Ruff](https://docs.astral.sh/ruff/)** - Code linting and formatting
- **[Pre-commit](https://pre-commit.com/)** - Git hooks for quality assurance

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

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **HTTP-Only Cookies**: Prevents XSS attacks
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Controlled cross-origin access
- **Password Hashing**: Bcrypt for secure password storage
- **Input Validation**: Pydantic models for data validation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Built with ❤️</p>
</div>
