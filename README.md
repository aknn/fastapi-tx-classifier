
# FastAPI Transaction Classifier

A FastAPI-based microservice for classifying financial transaction text with machine learning capabilities. This project includes structured JSON logging, Redis integration, and MLflow experiment tracking.

## Features

- FastAPI-based REST API with async support
- Transaction classification with configurable rules and ML models
- Redis integration for caching and data persistence
- MLflow integration for experiment tracking and model registry
- Structured JSON logging
- Pre-commit hooks for code quality (Black, Ruff, mypy)
- Comprehensive test suite with pytest

## Project Structure

```
fastapi-template/
├── fastapi_tx_classifier/          # Main application package
│   ├── main.py                     # FastAPI application setup
│   ├── config.py                   # Application configuration
│   ├── models.py                   # Pydantic models
│   ├── classification_logic.py     # Core classification logic
│   ├── model_registry.py           # MLflow model management
│   ├── redis_client.py             # Redis client setup
│   ├── exceptions.py               # Custom exceptions
│   └── routers/                    # API route modules
│       ├── classification.py       # Classification endpoints
│       ├── transactions.py         # Transaction endpoints
│       ├── messages.py             # Message endpoints
│       └── system.py               # System/health endpoints
├── tests/                          # Test suite
├── scripts/                        # Utility scripts
├── data/                           # Data files
├── mlruns/                         # MLflow experiment tracking
├── requirements.txt                # Production dependencies
├── dev-requirements.txt            # Development dependencies
└── main.py                         # Application entry point
```

## Quick Start

### Prerequisites

- Python 3.11+
- Redis server (for caching and data storage)

### Option 1: Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd fastapi-template
   make init                    # Setup venv, install deps, setup pre-commit
   ```

2. **Start Redis (in separate terminal):**
   ```bash
   redis-server
   ```

3. **Run the application:**
   ```bash
   make dev                     # or: python main.py
   ```

### Option 2: Docker Compose (For environments with Docker)

1. **Clone and start:**
   ```bash
   git clone <repository-url>
   cd fastapi-template
   make docker-up              # or: docker compose up -d
   ```

2. **View logs:**
   ```bash
   make docker-logs            # or: docker compose logs -f
   ```

> **Note:** Docker Compose provides Redis and the API in containers. If Docker is not available, use Option 1 with a local Redis installation.

### Access the Application

- **API Documentation:** http://localhost:8000/docs
- **Alternative docs:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

## API Endpoints

The application provides several REST endpoints:

### System Endpoints
- `GET /health` - Health check endpoint
- `GET /ready` - Readiness probe (checks Redis connectivity)
- `GET /metrics` - Prometheus metrics endpoint

### Core Application
- `GET /` - Home endpoint
- `GET /about` - About page

### Classification
- `POST /classify-transaction` - Classify a financial transaction

### Messages
- `GET /messages/` - List all messages
- `POST /messages/` - Add a new message

### Transactions
- `GET /transactions/` - List transactions
- `POST /transactions/` - Add a new transaction

### Testing Endpoints
- `GET /api/valid-endpoint` - Test endpoint for API validation
- `POST /api/endpoint` - Generic test endpoint

For complete API documentation with request/response schemas, visit the interactive docs at `/docs` when the application is running.

## Development

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality

### Running Tests

```bash
# Run all tests
make test                    # or: pytest

# Run tests with coverage
make test-cov               # or: pytest --cov=fastapi_tx_classifier

# Run specific test file
pytest tests/test_transactions.py

# Use the API tester script
python scripts/api_tester.py --run-all --base-url http://localhost:8000
```

### Code Quality

```bash
# Format code
make format                 # or: black . && ruff check --fix .

# Run linting
make lint                   # or: ruff check . && mypy fastapi_tx_classifier/

# Clean cache files
make clean
```

## Configuration

The application can be configured through environment variables or a `.env` file:

- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379/0`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `APP_HOST`: Application host (default: `0.0.0.0`)
- `APP_PORT`: Application port (default: `5000`, but main.py overrides to `8000`)
- `MLFLOW_TRACKING_URI`: MLflow tracking URI (default: `file:./mlruns`)
- `MLFLOW_EXPERIMENT_NAME`: MLflow experiment name (default: `classification_experiments`)

## Docker Support

For a quick setup with Docker, you can use the provided docker-compose configuration:

```bash
# Start the application and Redis with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## MLflow Integration

The project includes MLflow for experiment tracking and model registry:

- Experiments are tracked locally in the `mlruns/` directory
- Models can be registered and versioned through the MLflow UI
- Start MLflow UI: `mlflow ui` (then visit http://localhost:5000)
- The application automatically logs classification experiments

## Available Commands

This project includes a Makefile with common development tasks:

```bash
make help          # Show all available commands
make init          # Setup development environment
make dev           # Run development server
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting (ruff + mypy)
make format        # Format code (black + ruff --fix)
make clean         # Clean cache files
make docker-up     # Start with Docker Compose
make docker-down   # Stop Docker Compose services
make docker-logs   # View Docker Compose logs
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup, code formatting, testing, and contribution guidelines.

## Project Status

✅ **Working Features:**
- FastAPI REST API with async support
- Transaction classification with configurable rules
- Redis integration for caching
- MLflow experiment tracking
- Comprehensive test suite (21 tests passing)
- Pre-commit hooks with Black, Ruff, and mypy
- Docker support with docker-compose
- Makefile for common development tasks

🚧 **In Development:**
- Advanced ML models and SHAP explanations
- OpenTelemetry observability integration
- Production deployment configurations (Kubernetes, Helm)
- Performance optimizations and benchmarking

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup, code formatting, testing, and contribution guidelines.

---

*This README was updated to accurately reflect the current state of the project as of June 2025.*
