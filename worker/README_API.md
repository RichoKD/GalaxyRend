# GalaxyRend Worker - API-Based Architecture

This worker connects to the FluxFrame backend API to receive and process rendering jobs. It replaces the direct blockchain polling approach with a more efficient API-based workflow.

## Architecture Overview

### Old Approach (main.py)

- Polls blockchain directly for jobs
- Checks job eligibility and worker registration on-chain
- Submits results via blockchain transactions

### New Approach (main_api.py) ✨

- Authenticates with backend API using wallet signature
- Polls `/api/v1/jobs/available` for pending jobs
- Claims jobs via `POST /api/v1/jobs/{id}/assign`
- Submits results via `POST /api/v1/jobs/{id}/complete`
- Backend handles blockchain interactions

## Benefits of API-Based Approach

1. **Reduced Blockchain Load**: Backend batches transactions
2. **Better Error Handling**: API provides detailed error messages
3. **Centralized State**: Backend tracks job states consistently
4. **Authentication**: Secure worker authentication with JWT tokens
5. **Monitoring**: Backend can track worker performance and health

## How it Works

### 1. Authentication

```
Worker → POST /api/v1/auth/challenge {address}
Backend → {challenge}
Worker → Signs challenge with private key
Worker → POST /api/v1/auth/worker-auth {address, signature, challenge}
Backend → {access_token, worker}
```

### 2. Job Discovery

```
Worker → GET /api/v1/jobs/available?status=pending
Backend → [{id, asset_cid, reward, creator, ...}]
Worker → Filters out already completed jobs
```

### 3. Job Claiming

```
Worker → POST /api/v1/jobs/{id}/assign {worker_address}
Backend → Updates job status to "in_progress"
Backend → Returns success confirmation
```

### 4. Job Processing

1. **Download**: Downloads .blend file from IPFS using asset_cid
2. **Validate**: Checks if Blender can open the file
3. **Render**: Uses Blender EEVEE engine to render frame 1
4. **Upload**: Uploads result PNG to IPFS
5. **Complete**: Returns result_cid

### 5. Result Submission

```
Worker → POST /api/v1/jobs/{id}/complete {result_cid}
Backend → Updates job status to "completed"
Backend → Stores result_cid
Backend → Triggers blockchain transaction (optional)
Backend → Emits event for frontend notification
```

## Environment Variables

Create a `.env` file in the `worker/` directory:

```bash
# Backend API Configuration
BACKEND_API_URL=http://localhost:8000/api/v1

# Worker Identity
WORKER_ADDRESS=0x1234567890abcdef1234567890abcdef12345678
WORKER_PRIVATE_KEY=your_starknet_private_key

# IPFS Configuration
IPFS_API=/ip4/127.0.0.1/tcp/5001
IPFS_GATEWAY=http://127.0.0.1:8080/ipfs

# Blender Configuration
BLENDER_PATH=blender  # or full path like /usr/bin/blender

# Polling Configuration
POLL_INTERVAL=10  # seconds between job polls
```

## Requirements

### System Dependencies

- **Blender** - For rendering 3D scenes
- **Python 3.11+** - Runtime environment
- **IPFS node** - For downloading/uploading files

### Python Dependencies

Install via pip:

```bash
pip install -r requirements.txt
```

Key packages:

- `requests` - HTTP client for API communication
- `python-dotenv` - Environment variable management
- `ipfshttpclient` - IPFS operations (optional, has HTTP fallback)

## Running the Worker

### 1. Setup Environment

Copy the example env file and configure it:

```bash
cd worker
cp .env.example .env
# Edit .env with your actual values
```

### 2. Run the Worker

Using the new API-based worker:

```bash
python src/main_api.py
```

Using the old blockchain-based worker (deprecated):

```bash
python src/main.py
```

### 3. Expected Output

```
[Worker] Starting GalaxyRend Worker (API-based)
[Worker] Backend API: http://localhost:8000/api/v1
[Worker] Worker Address: 0x1234...
[Worker] Blender found: Blender 4.0.0
[Worker] Requesting auth challenge for 0x1234...
[Worker] Successfully authenticated. Token: eyJhbGciOiJIUzI1NiIs...
[Worker] Starting job polling loop (interval: 10s)

[Worker] [14:32:15] Polling for jobs...
[Worker] Found 1 available jobs
[Worker] Found job 42 - Asset CID: QmXyz...
[Worker] Successfully claimed job 42
[Worker] Downloading asset CID: QmXyz...
[Worker] Found blend file: /tmp/tmpxyz/scene.blend
[Worker] Validating blend file: /tmp/tmpxyz/scene.blend
[Worker] Blend file validation successful
[Worker] Rendering blend file to: /tmp/tmpxyz/render.png
[Worker] Render successful: /tmp/tmpxyz/render0001.png
[Worker] Uploading render result to IPFS: /tmp/tmpxyz/render0001.png
[Worker] Upload successful. CID: QmAbc...
[Worker] Successfully submitted result for job 42
[Worker] ✓ Successfully completed job 42
```

## API Endpoints Used

| Endpoint              | Method | Purpose                                          |
| --------------------- | ------ | ------------------------------------------------ |
| `/auth/challenge`     | POST   | Get authentication challenge                     |
| `/auth/worker-auth`   | POST   | Submit signature and get JWT token (for workers) |
| `/jobs/available`     | GET    | Get list of pending jobs                         |
| `/jobs/{id}/assign`   | POST   | Claim a job for this worker                      |
| `/jobs/{id}/complete` | POST   | Submit completed job result                      |

## Error Handling

The worker handles several error scenarios:

### Authentication Failures

- Retries authentication on token expiry
- Logs detailed error messages
- Exits if authentication repeatedly fails

### Job Processing Errors

- **Download Failed**: Skips job, logs error, continues polling
- **Validation Failed**: Skips job (invalid .blend file)
- **Render Failed**: Logs error, skips job
- **Upload Failed**: Retries upload, then skips job
- **Submission Failed**: Retries submission, then moves to next job

### Network Errors

- Retries API calls with exponential backoff
- Falls back to IPFS gateway if API fails
- Continues polling even after network errors

## Completed Jobs Tracking

The worker maintains a local JSON file to track completed jobs:

**Location**: `worker/src/temp/completed_jobs.json`

**Format**:

```json
{
  "completed_jobs": [1, 2, 5, 8, 13]
}
```

This prevents re-processing jobs after worker restart.

## Development vs Production

### Development Mode

- Uses local backend at `http://localhost:8000`
- Uses local IPFS node at `127.0.0.1:5001`
- Mock signatures for testing
- Verbose logging

### Production Mode

- Backend API URL from environment
- Remote IPFS nodes or Pinata/Infura
- Real StarkNet wallet signatures
- Structured logging with log levels

## Monitoring

Monitor worker health by checking:

1. **Logs**: Look for successful job completions
2. **Temp Directory**: Check for stuck rendering processes
3. **API Status**: Ensure backend is reachable
4. **IPFS Status**: Verify IPFS node connectivity
5. **Blender**: Test Blender execution manually

## Troubleshooting

### "Authentication failed"

- Check `WORKER_ADDRESS` matches a registered worker
- Verify `BACKEND_API_URL` is correct
- Ensure backend is running and accessible

### "No available jobs"

- No jobs are pending in the system
- Worker may not meet job requirements (reputation)
- Jobs may be claimed by other workers

### "Blender not found"

- Install Blender or update `BLENDER_PATH`
- Test: `blender --version`

### "IPFS download failed"

- Check IPFS node is running: `ipfs id`
- Verify `IPFS_API` configuration
- Try accessing IPFS gateway in browser

### "Render timeout"

- Complex scenes may exceed 300s limit
- Increase timeout in `render_blend_file()`
- Consider using faster render engine

## Upgrading from Old Worker

If you're currently using the blockchain-based worker (`main.py`):

1. **Backup** your current `.env` file
2. **Update** environment variables (see above)
3. **Test** new worker with `python src/main_api.py`
4. **Monitor** for issues during first few jobs
5. **Switch** to new worker once validated

Both workers can run simultaneously for gradual migration.

## Contributing

When working on the worker:

1. **Test locally** with a single job first
2. **Check logs** for errors
3. **Validate** IPFS uploads manually
4. **Monitor** resource usage during rendering
5. **Document** any new environment variables

## License

Same as main GalaxyRend project.
