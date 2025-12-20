# Quick Start Guide - API Worker

Get the new API-based worker running in 5 minutes.

## Prerequisites

- ✅ Backend running on `http://localhost:8000`
- ✅ IPFS node running on `127.0.0.1:5001`
- ✅ Blender installed
- ✅ Python 3.11+

## Setup Steps

### 1. Navigate to Worker Directory
```bash
cd /home/rico/cairo/GalaxyRend/worker
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set your worker address:

```bash
WORKER_ADDRESS=0xYourWorkerAddressHere
```

### 3. Run the Worker

```bash
python3 src/main_api.py
```

## Expected Output

```
[Worker] Starting GalaxyRend Worker (API-based)
[Worker] Backend API: http://localhost:8000/api/v1
[Worker] Worker Address: 0x1234...
[Worker] ipfshttpclient imported successfully
[Worker] Connected to IPFS using ipfshttpclient
[Worker] Blender found: Blender 4.0.0
[Worker] Requesting auth challenge for 0x1234...
[Worker] Successfully authenticated. Token: eyJhbGc...
[Worker] Starting job polling loop (interval: 10s)

[Worker] [14:30:00] Polling for jobs...
[Worker] No available jobs
```

## Test the Full Flow

### 1. Create a Job (Frontend)

1. Go to `http://localhost:3000/dashboard/creators`
2. Click "Create Job"
3. Fill in details and upload a `.blend` file to IPFS
4. Submit the job

### 2. Watch Worker Pick Up Job

The worker should log:

```
[Worker] Found 1 available jobs
[Worker] Found job 1 - Asset CID: QmXyz...
[Worker] Successfully claimed job 1
[Worker] Downloading asset CID: QmXyz...
[Worker] Rendering blend file...
[Worker] Upload successful. CID: QmAbc...
[Worker] ✓ Successfully completed job 1
```

### 3. Check Result (Frontend)

1. Go to job details page
2. See job status: "completed"
3. View rendered image from IPFS

## Troubleshooting

### "Failed to authenticate"

**Fix**: Check that backend is running

```bash
curl http://localhost:8000/health
```

### "Blender not found"

**Fix**: Install Blender or set path in `.env`

```bash
# Ubuntu/Debian
sudo apt install blender

# Or set full path
BLENDER_PATH=/usr/bin/blender
```

### "IPFS download failed"

**Fix**: Start IPFS daemon

```bash
ipfs daemon
```

### "No available jobs"

This is normal if no jobs are pending. Create one in the frontend.

## Using the Helper Script

For easier testing:

```bash
# Make script executable
chmod +x worker.sh

# Run it
./worker.sh
```

This gives you a menu to:

1. Run new worker
2. Run old worker
3. Check dependencies
4. View logs
5. Clean temp files

## Configuration Options

### Adjust Polling Frequency

In `.env`:

```bash
POLL_INTERVAL=5  # Poll every 5 seconds (faster)
```

### Use Remote Backend

```bash
BACKEND_API_URL=https://api.galaxyrend.io/api/v1
```

### Use Remote IPFS

```bash
IPFS_API=/dns/ipfs.infura.io/tcp/5001/https
IPFS_GATEWAY=https://ipfs.io/ipfs
```

## Development Tips

### View Completed Jobs

```bash
cat src/temp/completed_jobs.json
```

### Clear Completed Jobs Cache

```bash
rm src/temp/completed_jobs.json
```

### Monitor in Real-Time

```bash
python3 src/main_api.py | tee worker.log
```

### Test Authentication Only

```python
# In Python shell
from src.main_api import WorkerAuthenticator
import asyncio

auth = WorkerAuthenticator(
    "http://localhost:8000/api/v1",
    "0x1234567890abcdef1234567890abcdef12345678"
)
asyncio.run(auth.authenticate())
```

## Next Steps

1. ✅ Worker is running and polling
2. 📝 Create jobs in frontend
3. 👀 Watch worker process them
4. 🎨 View rendered results
5. 📊 Monitor performance

## Support

If you encounter issues:

1. Check all services are running (backend, IPFS, Blender)
2. Review worker logs for error messages
3. Verify environment configuration
4. Test components individually

## Performance Tips

- **Faster Rendering**: Use EEVEE instead of Cycles
- **Faster Polling**: Reduce `POLL_INTERVAL` to 5 seconds
- **Multiple Workers**: Run multiple instances with different addresses
- **Better IPFS**: Use pinning service like Pinata or Infura

---

**Ready to go?** Just run: `python3 src/main_api.py`
