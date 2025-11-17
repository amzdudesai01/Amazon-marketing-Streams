# Setup Guide

This guide will help you set up the Amazon Marketing Stream Automation System before you have AWS access.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or Neon account)
- (Optional) Slack webhook URL for alerts

## Step 1: Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using poetry (if you have it)
poetry install
```

## Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and configure at minimum:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - Other settings can remain as defaults for now

## Step 3: Set Up Database

1. Create your PostgreSQL database:
   ```sql
   CREATE DATABASE amazon_marketing_streams;
   ```

2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/amazon_marketing_streams
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

## Step 4: Test the System (Without AWS)

The system uses mock clients when AWS credentials are not configured, so you can test locally:

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Test the health endpoints:
   ```bash
   curl http://localhost:8000/api/v1/health
   curl http://localhost:8000/api/v1/health/config
   ```

3. Test with sample data:
   ```bash
   python scripts/seed_sample_data.py
   ```

4. Test mock SQS:
   ```bash
   python scripts/test_mock_sqs.py
   ```

5. Test Slack client (will log to console if webhook not configured):
   ```bash
   python scripts/test_slack_client.py
   ```

## Step 5: When You Get AWS Access

Once you have AWS credentials:

1. Update `.env` with:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   SQS_QUEUE_URL=your_sqs_queue_url
   ```

2. The system will automatically switch from mock clients to real AWS clients.

3. Configure Amazon Marketing Stream to send messages to your SQS queue.

## Step 6: Configure Slack Alerts (Optional)

1. Create a Slack webhook:
   - Go to your Slack workspace settings
   - Create an incoming webhook
   - Copy the webhook URL

2. Update `.env`:
   ```
   SLACK_WEBHOOK_URL=your_slack_webhook_url
   ```

## Development Workflow

### Running the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Accessing the API

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- Metrics: http://localhost:8000/api/v1/metrics/aggregates

### Background Workers

The system automatically starts background workers when the server starts:
- SQS message poller (runs every 5 seconds by default)
- Hourly aggregation (runs every hour)
- Daily aggregation (runs once per day)

You can disable workers by setting `WORKER_ENABLED=false` in `.env`.

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Database Connection Issues

- Verify your `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check firewall settings if connecting to remote database

### Mock Clients Not Working

- The system automatically uses mock clients when AWS credentials are missing
- Check logs for messages prefixed with `[MOCK]`

### Migration Issues

- If migrations fail, you may need to drop and recreate the database
- Always backup your data before running migrations in production

## Next Steps

Once AWS is configured:

1. Set up Amazon Marketing Stream subscriptions
2. Configure SQS queue to receive stream messages
3. Monitor the `/api/v1/health/config` endpoint to verify all services are connected
4. Check Slack for alerts (or console logs if Slack is not configured)

