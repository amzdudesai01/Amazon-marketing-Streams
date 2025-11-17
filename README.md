# Amazon Marketing Stream Automation System

Real-time campaign monitoring and performance optimization system for Amazon Ads using Amazon Marketing Stream, AWS SQS, and FastAPI.

## 🎯 Project Overview

This system automates real-time campaign monitoring by:
- Collecting live performance data from Amazon Marketing Stream (SP, SB, SD datasets)
- Storing data in a structured PostgreSQL database
- Sending automated alerts via Slack based on performance metrics
- (Phase 2) Automating bid and budget optimization

## 🏗️ Architecture

```
Amazon Marketing Stream → AWS SQS → FastAPI Worker → PostgreSQL → Alert System (Slack)
```

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL database (or Neon)
- Amazon Developer Account with Ads API access
- AWS Account (for SQS)
- Slack Webhook URL (for alerts)

## 🚀 Setup

### 1. Clone and Install Dependencies

```bash
# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 4. Run the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with poetry
poetry run uvicorn app.main:app --reload
```

## 📁 Project Structure

```
.
├── app/
│   ├── api/              # API routes
│   ├── core/             # Core configuration
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── clients/          # External API clients
│   ├── workers/          # Background workers
│   └── utils/            # Utilities
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── sample_data/          # Sample data for testing
└── alembic/              # Database migrations
```

## 🔧 Configuration

Key environment variables (see `.env.example`):
- `DATABASE_URL`: PostgreSQL connection string
- `AWS_*`: AWS credentials and SQS queue URL
- `AMAZON_ADVERTISING_API_*`: Amazon Ads API credentials
- `SLACK_WEBHOOK_URL`: Slack webhook for alerts

## 📊 Features

### Phase 1 (Current)
- ✅ Real-time data ingestion from Amazon Marketing Stream
- ✅ SQS message processing
- ✅ Database storage and aggregation
- ✅ Performance metric calculations (CTR, ACOS, ROAS)
- ✅ Automated Slack alerts

### Phase 2 (Planned)
- 🔄 Automated bid optimization
- 🔄 Budget adjustment automation
- 🔄 ML-driven optimization rules

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## 📝 Development

Before AWS access is available, the system uses mock clients for local development. Once AWS credentials are configured, the real clients will be used automatically.

## 📄 License

Proprietary - Internal use only

