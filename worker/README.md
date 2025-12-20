# GalaxyRend Blender Rendering Worker

This worker is a Python application that polls the GalaxyRend job registry smart contract for rendering jobs, downloads Blender (.blend) files from IPFS, renders them, and uploads the results back to IPFS.

## How it Works

### 1. Job Discovery
- The worker continuously polls the smart contract for available jobs
- It checks job IDs sequentially to find jobs that:
  - Have a creator (job exists)
  - Don't have a worker assigned yet (available for pickup)
  - Have an asset CID pointing to a .blend file

### 2. Job Processing
When a job is found:
1. **Download**: Downloads the .blend file from IPFS using the asset CID
2. **Render**: Uses Blender in headless mode to render the scene to a PNG image
3. **Upload**: Uploads the rendered result to IPFS
4. **Submit**: Submits the result CID back to the smart contract

### 3. Smart Contract Integration
The worker interacts with these contract functions:
- `get_job_creator(job_id)` - Check if job exists
- `get_job_worker(job_id)` - Check if job is available
- `get_job_reward(job_id)` - Get job reward amount
- `get_job_asset_cid(job_id)` - Get the IPFS CID of the .blend file
- `submit_result(job_id, result_cid)` - Submit rendered result

## Environment Variables

- `STARKNET_RPC`: StarkNet RPC endpoint (default: http://localhost:5050)
- `IPFS_API`: IPFS API endpoint (default: /dns/ipfs-node/tcp/5001/http)
- `JOB_REGISTRY_ADDRESS`: Contract address in hex format
- `BLENDER_PATH`: Path to Blender executable (default: blender)

## Requirements

### System Dependencies
- Blender (for rendering)
- Python 3.11+
- IPFS node access

### Python Dependencies
- `starknet_py>=0.27.0` - StarkNet Python SDK
- `ipfshttpclient` - IPFS HTTP client
- `Pillow>=10.0.0` - Image processing

## Running the Worker

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export JOB_REGISTRY_ADDRESS=0x1234...
export STARKNET_RPC=http://localhost:5050
export IPFS_API=/ip4/127.0.0.1/tcp/5001/http

# Run the worker
python src/main.py
```

### Docker
```bash
# Build the image
docker build -t galaxyrend-worker .

# Run with environment variables
docker run -e JOB_REGISTRY_ADDRESS=0x1234... \
           -e STARKNET_RPC=http://host.docker.internal:5050 \
           -e IPFS_API=/dns/ipfs-node/tcp/5001/http \
           galaxyrend-worker
```

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Job Creator   │───▶│ Smart Contract│───▶│   Worker    │
│                 │    │               │    │             │
│ 1. Upload .blend│    │ 2. Create Job │    │ 3. Poll Jobs│
│    to IPFS      │    │    with CID   │    │ 4. Download │
│ 2. Call create_ │    │               │    │ 5. Render   │
│    job()        │    │               │    │ 6. Upload   │
│                 │    │               │    │ 7. Submit   │
└─────────────────┘    └──────────────┘    └─────────────┘
```

## Blender Rendering

The worker uses Blender in background mode with these parameters:
- `-b`: Run in background (headless)
- `-o output.png`: Set output path
- `-f 1`: Render frame 1
- `--python-exit-code 1`: Exit with error code on Python errors

Timeout is set to 5 minutes per render to prevent hanging jobs.

## Error Handling

- Network errors: Retries with exponential backoff
- Blender errors: Logs output and skips job
- IPFS errors: Retries download/upload operations
- Contract errors: Logs and continues polling

## Security Considerations

- Downloads are isolated in temporary directories
- File size limits should be implemented for production
- Resource monitoring for CPU/memory usage
- Sandboxing for untrusted .blend files

## Monitoring

The worker logs:
- Job discovery and processing status
- Blender render output and errors
- IPFS upload/download status
- Contract interaction results
- Performance metrics (render time, file sizes)
