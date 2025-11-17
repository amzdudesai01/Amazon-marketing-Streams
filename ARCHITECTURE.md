# Architecture Overview

## System Architecture

```
┌─────────────────────────┐
│ Amazon Marketing Stream │
│   (SP, SB, SD datasets) │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│      AWS SQS Queue      │
│  (Message Buffer)       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   FastAPI Application   │
│  ┌───────────────────┐ │
│  │  SQS Worker       │ │
│  │  (Polls messages) │ │
│  └─────────┬─────────┘ │
│            │           │
│            ▼           │
│  ┌───────────────────┐ │
│  │ Message Processor│ │
│  │ (Parses & stores)│ │
│  └─────────┬─────────┘ │
│            │           │
│            ▼           │
│  ┌───────────────────┐ │
│  │  Alert Service   │ │
│  │ (Checks metrics) │ │
│  └─────────┬─────────┘ │
└────────────┼───────────┘
             │
             ▼
┌─────────────────────────┐
│   PostgreSQL Database   │
│  ┌───────────────────┐ │
│  │ Stream Messages   │ │
│  │ Performance Data  │ │
│  │ Aggregates        │ │
│  │ Alerts            │ │
│  └───────────────────┘ │
└────────────┬───────────┘
             │
             ▼
┌─────────────────────────┐
│   Slack Webhook         │
│   (Alert Notifications) │
└─────────────────────────┘
```

## Component Overview

### 1. Clients (`app/clients/`)

**SQSClient** (`sqs_client.py`)
- Receives messages from AWS SQS
- Falls back to `MockSQSClient` when AWS credentials are not configured
- Handles message deletion after processing

**SlackClient** (`slack_client.py`)
- Sends alerts to Slack via webhook
- Formats messages with rich blocks
- Logs to console if webhook not configured

**MockSQSClient** (`mock_sqs.py`)
- In-memory queue for local development
- Allows testing without AWS access
- Automatically used when AWS credentials are missing

### 2. Services (`app/services/`)

**MessageProcessor** (`message_processor.py`)
- Parses Amazon Marketing Stream messages
- Extracts performance metrics
- Stores data in database
- Calculates derived metrics (CTR, ACOS, ROAS, etc.)

**AlertService** (`alert_service.py`)
- Monitors performance metrics against thresholds
- Detects:
  - CTR drops (>20% decrease)
  - Spend spikes (>50% increase)
  - High ACOS (>30%)
  - Low ROAS (<2.0)
- Creates alert records
- Sends notifications to Slack

**AggregationService** (`aggregation_service.py`)
- Aggregates performance data by hour and day
- Calculates averages for metrics
- Prevents duplicate aggregates
- Optimizes query performance

### 3. Workers (`app/workers/`)

**SQSWorker** (`sqs_worker.py`)
- Polls SQS queue at configured intervals
- Processes messages in batches
- Handles errors gracefully
- Can be enabled/disabled via config

**AggregationWorker** (`aggregation_worker.py`)
- Runs hourly and daily aggregations
- Scheduled via APScheduler
- Processes all campaigns

**Scheduler** (`scheduler.py`)
- Manages background tasks
- Starts/stops with FastAPI lifecycle
- Configures job intervals

### 4. Models (`app/models/`)

**StreamMessage**
- Raw messages from Amazon Marketing Stream
- Tracks processing status
- Stores JSON payload

**PerformanceData**
- Processed performance metrics
- Campaign, ad group, keyword level
- Calculated metrics (CTR, ACOS, ROAS)
- Time period tracking

**PerformanceAggregate**
- Hourly and daily summaries
- Aggregated totals and averages
- Optimized for reporting queries

**Alert**
- Alert records with metadata
- Tracks sent status
- Supports acknowledgment

### 5. API Routes (`app/api/routes/`)

**Health** (`health.py`)
- Basic health check
- Database connectivity check
- Configuration status

**Metrics** (`metrics.py`)
- Campaign performance queries
- Aggregate data retrieval
- Alert history

## Data Flow

1. **Ingestion**
   - Amazon Marketing Stream sends messages to SQS
   - SQS Worker polls queue every 5 seconds (configurable)
   - Messages are received in batches (up to 10)

2. **Processing**
   - MessageProcessor parses message body
   - Extracts campaign, metrics, and time period
   - Calculates derived metrics
   - Stores in PerformanceData table

3. **Alerting**
   - AlertService checks new performance data
   - Compares against thresholds and previous periods
   - Creates Alert records
   - Sends to Slack if configured

4. **Aggregation**
   - AggregationWorker runs hourly and daily
   - Processes all campaigns
   - Creates PerformanceAggregate records
   - Optimizes for reporting

## Configuration

All configuration is managed via environment variables (see `env.example`):

- **Database**: PostgreSQL connection string
- **AWS**: Credentials and SQS queue URL
- **Amazon Ads**: API credentials (for Phase 2)
- **Slack**: Webhook URL for alerts
- **Worker**: Poll intervals and batch sizes
- **Alerts**: Threshold values

## Mock Mode

When AWS credentials are not configured:
- `SQSClient` automatically uses `MockSQSClient`
- Messages can be added via `add_sample_message()`
- All functionality works identically
- Perfect for local development and testing

## Error Handling

- Database errors: Rollback transactions, log errors
- SQS errors: Log but don't delete message (allows retry)
- Slack errors: Log but continue processing
- Message parsing errors: Log and skip message

## Scalability Considerations

- Database indexes on common query fields
- Batch processing for SQS messages
- Connection pooling for database
- Background workers don't block API requests
- Aggregates reduce query load

## Security

- Environment variables for sensitive data
- No credentials in code
- Database connection pooling with limits
- Input validation via Pydantic schemas

## Future Enhancements (Phase 2)

- Bid optimization service
- Budget adjustment automation
- ML-based performance prediction
- Campaign management API integration
- Advanced alerting rules

