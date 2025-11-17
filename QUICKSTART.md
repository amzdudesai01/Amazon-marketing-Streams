# Quick Start Guide

Get up and running in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up Environment

```bash
# Copy example env file
cp env.example .env

# Edit .env and set at minimum:
# DATABASE_URL=postgresql://user:password@localhost:5432/amazon_marketing_streams
```

## 3. Create Database & Run Migrations

```bash
# Create database (PostgreSQL)
createdb amazon_marketing_streams

# Run migrations
alembic upgrade head
```

## 4. Start the Server

```bash
# Option 1: Direct uvicorn
uvicorn app.main:app --reload

# Option 2: Using script
python scripts/run_dev.py
```

## 5. Test It Out

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Seed sample data
python scripts/seed_sample_data.py

# View API docs
# Open http://localhost:8000/docs in your browser
```

## That's It! 🎉

The system is now running with:
- ✅ Mock SQS client (no AWS needed)
- ✅ Database storage
- ✅ Background workers
- ✅ Alert system (logs to console if Slack not configured)

## Next Steps

1. **Test the mock system**: Run `python scripts/test_mock_sqs.py`
2. **Add more sample data**: Edit `sample_data/sample_stream_message.json`
3. **Configure Slack**: Add webhook URL to `.env` for real alerts
4. **When AWS is ready**: Add credentials to `.env` and the system will automatically switch to real clients

## Troubleshooting

- **Database errors**: Check your `DATABASE_URL` in `.env`
- **Import errors**: Make sure you're in the project root directory
- **Port already in use**: Change port in `scripts/run_dev.py` or use `--port 8001`

For more details, see [SETUP.md](SETUP.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

