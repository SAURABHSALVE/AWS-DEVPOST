# Multi-Lingual Content Creation Agent - Backend

Flask-based backend service for the Multi-Lingual Content Creation Agent.

## Project Structure

```
Backend/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── api/                 # API blueprints and routes
│   ├── models/              # SQLAlchemy data models
│   ├── services/            # Business logic services
│   └── health/              # Health check endpoints
├── config/                  # Configuration files
│   ├── base.py             # Base configuration
│   ├── development.py      # Development settings
│   ├── production.py       # Production settings
│   └── testing.py          # Testing settings
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` file with your configuration values.

5. Run the application:
```bash
python app.py
```

## Health Checks

- **Health Check**: `GET /health` - Basic service health status
- **Readiness Check**: `GET /ready` - Service readiness for deployment
- **API Status**: `GET /api/status` - API service status

## Configuration

The application uses environment-based configuration with three environments:
- `development` - Local development with debug enabled
- `production` - Production deployment with optimized settings
- `testing` - Test environment with in-memory database

Set `FLASK_ENV` environment variable to switch between configurations.