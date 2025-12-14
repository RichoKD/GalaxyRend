# GalaxyRend Backend

FastAPI backend service for the GalaxyRend decentralized computing platform.

## Features

- **Worker Management**: REST APIs for worker registration, verification, and reputation tracking
- **Job Management**: APIs for job creation, assignment, completion, and monitoring
- **Event Indexing**: Automatic indexing of blockchain events to maintain synchronized state
- **Real-time Updates**: WebSocket support for real-time job and worker status updates
- **Database Integration**: PostgreSQL with SQLAlchemy for robust data persistence
- **StarkNet Integration**: Native integration with StarkNet contracts using starknet-py
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Architecture

```
backend/
├── app/
│   ├── api/                 # REST API endpoints
│   │   ├── workers.py       # Worker management endpoints
│   │   ├── jobs.py          # Job management endpoints
│   │   └── events.py        # Event and contract data endpoints
│   ├── models/              # Database models (SQLAlchemy)
│   ├── schemas/             # Pydantic schemas for validation
│   ├── services/            # Business logic services
│   │   ├── starknet_client.py   # StarkNet contract interaction
│   │   └── event_indexer.py     # Blockchain event indexing
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup and session management
│   └── main.py              # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment configuration template
└── setup.sh                # Automated setup script
```

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)
- Access to StarkNet node (devnet or testnet)

### Installation

1. **Run the setup script:**
   ```bash
   cd backend
   ./setup.sh
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Update configuration in `.env`:**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/galaxyrend_db
   STARKNET_RPC_URL=http://localhost:5050
   CONTRACT_ADDRESS=0x...  # Your deployed contract address
   CONTRACT_ABI_PATH=../contracts/job_registry/target/dev/galaxyrend_job_registry.contract_class.json
   ```

4. **Start the backend:**
   ```bash
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env file

# Run the application
uvicorn app.main:app --reload
```

## API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Endpoints

### Workers
- `GET /api/v1/workers` - List workers with filtering
- `GET /api/v1/workers/{address}` - Get specific worker
- `POST /api/v1/workers/register` - Register new worker
- `GET /api/v1/workers/{address}/reputation-history` - Worker reputation history
- `GET /api/v1/workers/stats/overview` - Worker statistics

### Jobs
- `GET /api/v1/jobs` - List jobs with filtering
- `GET /api/v1/jobs/available` - Get available jobs
- `GET /api/v1/jobs/{id}` - Get specific job
- `POST /api/v1/jobs` - Create new job
- `POST /api/v1/jobs/{id}/assign` - Assign job to worker
- `POST /api/v1/jobs/{id}/complete` - Mark job as completed

### Events
- `GET /api/v1/events` - List contract events
- `GET /api/v1/events/unprocessed` - Get unprocessed events
- `GET /api/v1/events/summary/stats` - Event statistics

## Database Models

### Worker
- Registration and verification status
- Reputation score (0-1000)
- Job completion statistics
- Hardware capabilities
- Contact information

### Job
- On-chain job ID mapping
- Asset and result IPFS CIDs
- Reward amount and deadline
- Worker requirements
- Completion status and quality score

### Contract Events
- Raw blockchain event data
- Processing status
- Event type classification

## Event Indexing

The backend automatically indexes blockchain events to maintain synchronized state:

1. **Monitors contract events** from the StarkNet blockchain
2. **Processes events** to update database records
3. **Maintains consistency** between on-chain and off-chain data
4. **Provides real-time updates** through APIs

### Indexed Events
- `WorkerRegistered` - New worker registration
- `WorkerVerified` - Worker verification status change
- `JobCreated` - New job creation
- `JobAssigned` - Job assignment to worker
- `JobCompleted` - Job completion with results
- `ReputationUpdated` - Worker reputation changes

## Configuration

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/galaxyrend_db

# StarkNet
STARKNET_RPC_URL=http://localhost:5050
CONTRACT_ADDRESS=0x...
NETWORK=devnet

# Event Indexing
ENABLE_EVENT_INDEXING=true
START_BLOCK=0
INDEXER_POLL_INTERVAL=10

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
```

## Development

### Running in Development Mode

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

The application automatically creates database tables on startup. For production, consider using Alembic for migrations.

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Deployment

### Production Setup

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set up reverse proxy** (nginx recommended)

3. **Configure production database** with connection pooling

4. **Set up monitoring** and logging

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

The backend provides health check endpoints:

- `GET /health` - Detailed health status
- `GET /` - Basic status check

Monitor these endpoints for:
- Database connectivity
- Event indexer status
- StarkNet node connectivity

## Integration with GalaxyRend

The backend integrates with other GalaxyRend components:

1. **Smart Contracts**: Reads worker and job data from deployed contracts
2. **Worker Nodes**: Provides APIs for worker registration and job polling
3. **Frontend**: Serves data for the web interface
4. **Event System**: Maintains real-time synchronization with blockchain

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL is running
   - Verify connection string in `.env`
   - Ensure database exists

2. **StarkNet Connection Issues**
   - Verify RPC URL is accessible
   - Check contract address is correct
   - Ensure ABI file path is valid

3. **Event Indexing Problems**
   - Check StarkNet node connectivity
   - Verify contract events are being emitted
   - Review indexer logs for errors

### Logs

Logs are written to:
- Console output (development)
- `logs/` directory (production)

Set `LOG_LEVEL=DEBUG` in `.env` for detailed debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
