# Worker Testing Guide

Complete testing strategy for the API-based worker.

## Test Environment Setup

### Prerequisites

```bash
# 1. Backend running
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 2. IPFS daemon running
ipfs daemon

# 3. Frontend running (optional, for visual testing)
cd frontend
npm run dev
```

### Test Data Preparation

Create a simple test `.blend` file:

```python
# save as create_test_blend.py
import bpy

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a simple cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))

# Add a camera
bpy.ops.object.camera_add(location=(7, -7, 5))
bpy.context.scene.camera = bpy.context.object

# Add a light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))

# Save
bpy.ops.wm.save_as_mainfile(filepath='test_scene.blend')
print("Created test_scene.blend")
```

Run it:

```bash
blender --background --python create_test_blend.py
```

Upload to IPFS:

```bash
ipfs add test_scene.blend
# Note the CID: QmXyz...
```

## Unit Tests

### Test 1: Worker Authentication

**Purpose**: Verify worker can authenticate with backend

**Test Code**:

```python
import asyncio
from src.main_api import WorkerAuthenticator

async def test_auth():
    auth = WorkerAuthenticator(
        backend_url="http://localhost:8000/api/v1",
        worker_address="0x1234567890abcdef1234567890abcdef12345678",
        private_key=""
    )

    success = await auth.authenticate()
    assert success, "Authentication should succeed"
    assert auth.token is not None, "Token should be set"
    print(f"✅ Authentication successful: {auth.token[:20]}...")

asyncio.run(test_auth())
```

**Expected Output**:

```
[Worker] Requesting auth challenge for 0x1234...
[Worker] Submitting signed challenge
[Worker] Successfully authenticated. Token: eyJhbGciOiJIUzI1NiIs...
✅ Authentication successful: eyJhbGciOiJIUzI1NiIs...
```

### Test 2: IPFS Client

**Purpose**: Verify IPFS download/upload works

**Test Code**:

```python
import tempfile
import os
from src.main_api import IPFSClient

def test_ipfs():
    ipfs = IPFSClient("/ip4/127.0.0.1/tcp/5001")

    # Test upload
    test_file = "test.txt"
    with open(test_file, 'w') as f:
        f.write("Hello, GalaxyRend!")

    result = ipfs.add(test_file)
    cid = result["Hash"]
    print(f"✅ Uploaded file, CID: {cid}")

    # Test download
    with tempfile.TemporaryDirectory() as temp_dir:
        ipfs.get(cid, temp_dir)
        downloaded = os.path.join(temp_dir, cid)
        assert os.path.exists(downloaded), "File should be downloaded"
        print(f"✅ Downloaded file to: {downloaded}")

    os.remove(test_file)

test_ipfs()
```

**Expected Output**:

```
[Worker] Connected to IPFS using ipfshttpclient
✅ Uploaded file, CID: QmXyz...
[Worker] Downloading CID: QmXyz... via IPFS API
✅ Downloaded file to: /tmp/tmpxyz/QmXyz...
```

### Test 3: Blend File Validation

**Purpose**: Verify Blender can open files

**Test Code**:

```python
import asyncio
from src.main_api import validate_blend_file

async def test_validation():
    # Test valid file
    valid = await validate_blend_file("test_scene.blend")
    assert valid, "Valid blend file should pass"
    print("✅ Valid blend file validated")

    # Test invalid file
    with open("invalid.blend", 'w') as f:
        f.write("not a blend file")

    invalid = await validate_blend_file("invalid.blend")
    assert not invalid, "Invalid blend file should fail"
    print("✅ Invalid blend file rejected")

    os.remove("invalid.blend")

asyncio.run(test_validation())
```

**Expected Output**:

```
[Worker] Validating blend file: test_scene.blend
[Worker] Blend file validation successful
✅ Valid blend file validated
[Worker] Validating blend file: invalid.blend
[Worker] Blend file validation failed
✅ Invalid blend file rejected
```

### Test 4: Rendering

**Purpose**: Verify Blender can render

**Test Code**:

```python
import asyncio
import tempfile
from src.main_api import render_blend_file

async def test_render():
    with tempfile.TemporaryDirectory() as temp_dir:
        result = await render_blend_file("test_scene.blend", temp_dir)

        assert result is not None, "Render should succeed"
        assert os.path.exists(result), "Rendered file should exist"
        print(f"✅ Render successful: {result}")

asyncio.run(test_render())
```

**Expected Output**:

```
[Worker] Rendering blend file to: /tmp/tmpxyz/render.png
[Worker] Executing: blender -b test_scene.blend -E BLENDER_EEVEE ...
[Worker] Render successful: /tmp/tmpxyz/render0001.png
✅ Render successful: /tmp/tmpxyz/render0001.png
```

## Integration Tests

### Test 5: API Job Polling

**Purpose**: Verify worker can poll for jobs

**Test Code**:

```python
import asyncio
from src.main_api import WorkerAuthenticator, poll_available_jobs

async def test_polling():
    auth = WorkerAuthenticator(
        backend_url="http://localhost:8000/api/v1",
        worker_address="0x1234567890abcdef1234567890abcdef12345678"
    )

    await auth.authenticate()
    jobs = await poll_available_jobs(auth)

    print(f"✅ Found {len(jobs)} available jobs")
    for job in jobs:
        print(f"   - Job {job['id']}: {job.get('asset_cid', 'N/A')}")

asyncio.run(test_polling())
```

**Expected Output**:

```
[Worker] Requesting auth challenge...
[Worker] Successfully authenticated...
[Worker] Found 0 available jobs
✅ Found 0 available jobs
```

### Test 6: Job Claiming

**Purpose**: Verify worker can claim a job

**Setup**: Create a job in the frontend first

**Test Code**:

```python
import asyncio
from src.main_api import WorkerAuthenticator, poll_available_jobs, claim_job

async def test_claim():
    auth = WorkerAuthenticator(
        backend_url="http://localhost:8000/api/v1",
        worker_address="0x1234567890abcdef1234567890abcdef12345678"
    )

    await auth.authenticate()
    jobs = await poll_available_jobs(auth)

    if not jobs:
        print("⚠️  No jobs available to claim")
        return

    job_id = jobs[0]["id"]
    success = await claim_job(auth, job_id)

    assert success, "Job claim should succeed"
    print(f"✅ Successfully claimed job {job_id}")

asyncio.run(test_claim())
```

**Expected Output**:

```
[Worker] Successfully authenticated...
[Worker] Found 1 available jobs
[Worker] Successfully claimed job 1
✅ Successfully claimed job 1
```

### Test 7: Full Job Processing

**Purpose**: Test complete job workflow

**Setup**:

1. Create a job in frontend with `test_scene.blend` CID
2. Run test

**Test Code**:

```python
import asyncio
from src.main_api import (
    WorkerAuthenticator,
    IPFSClient,
    poll_available_jobs,
    claim_job,
    process_render_job,
    submit_job_completion
)

async def test_full_workflow():
    # Setup
    auth = WorkerAuthenticator(
        backend_url="http://localhost:8000/api/v1",
        worker_address="0x1234567890abcdef1234567890abcdef12345678"
    )
    ipfs = IPFSClient("/ip4/127.0.0.1/tcp/5001")

    # Authenticate
    await auth.authenticate()
    print("✅ Authenticated")

    # Poll for jobs
    jobs = await poll_available_jobs(auth)
    if not jobs:
        print("⚠️  No jobs available")
        return

    job = jobs[0]
    job_id = job["id"]
    asset_cid = job.get("asset_cid", "")
    print(f"✅ Found job {job_id}")

    # Claim job
    claimed = await claim_job(auth, job_id)
    assert claimed
    print(f"✅ Claimed job {job_id}")

    # Process job
    result_cid = await process_render_job(ipfs, job_id, asset_cid)
    assert result_cid
    print(f"✅ Processed job, result: {result_cid}")

    # Submit result
    submitted = await submit_job_completion(auth, job_id, result_cid)
    assert submitted
    print(f"✅ Submitted result for job {job_id}")

    print(f"\n🎉 Full workflow completed successfully!")

asyncio.run(test_full_workflow())
```

**Expected Output**:

```
[Worker] Successfully authenticated...
✅ Authenticated
[Worker] Found 1 available jobs
✅ Found job 1
[Worker] Successfully claimed job 1
✅ Claimed job 1
[Worker] Downloading asset CID: QmXyz...
[Worker] Rendering blend file...
[Worker] Upload successful. CID: QmAbc...
✅ Processed job, result: QmAbc...
[Worker] Successfully submitted result for job 1
✅ Submitted result for job 1

🎉 Full workflow completed successfully!
```

## End-to-End Tests

### Test 8: Complete System Test

**Steps**:

1. **Start all services**:

```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: IPFS
ipfs daemon

# Terminal 3: Frontend
cd frontend && npm run dev

# Terminal 4: Worker
cd worker && python3 src/main_api.py
```

2. **Create a job**:

   - Go to `http://localhost:3000/dashboard/creators`
   - Click "Create Job"
   - Upload `test_scene.blend` to IPFS
   - Set reward, deadline, reputation
   - Submit

3. **Observe worker**:

   - Watch worker terminal for job pickup
   - Should see: Found job → Claimed → Downloaded → Rendered → Uploaded → Submitted

4. **Verify result**:
   - Go to job details page
   - Status should be "completed"
   - Result image should be viewable from IPFS
   - Timeline should show worker assignment and completion

**Success Criteria**:

- ✅ Job created in frontend
- ✅ Worker picked up job within 10 seconds
- ✅ Worker completed rendering
- ✅ Result uploaded to IPFS
- ✅ Job marked completed in frontend
- ✅ Result image is viewable

## Performance Tests

### Test 9: Multiple Jobs

**Purpose**: Test worker handles multiple jobs sequentially

**Setup**: Create 5 jobs in frontend

**Test**: Run worker and measure processing time

**Expected**: Worker should process jobs one by one without errors

### Test 10: Concurrent Workers

**Purpose**: Test multiple workers don't conflict

**Setup**:

1. Configure two workers with different addresses
2. Create 10 jobs

**Test**: Run both workers simultaneously

**Expected**:

- Each worker claims different jobs
- No jobs are processed twice
- All jobs complete successfully

## Error Scenario Tests

### Test 11: Network Interruption

**Scenario**: IPFS goes down during job processing

**Test**:

1. Worker claims job
2. Stop IPFS daemon
3. Observe error handling

**Expected**:

- Worker logs IPFS error
- Worker skips job
- Worker continues polling after IPFS restarts

### Test 12: Backend Unavailable

**Scenario**: Backend crashes during polling

**Test**:

1. Worker is running
2. Stop backend
3. Observe error handling

**Expected**:

- Worker logs API error
- Worker retries authentication
- Worker resumes when backend restarts

### Test 13: Invalid Blend File

**Scenario**: Job has corrupted .blend file

**Test**:

1. Create job with non-blend file CID
2. Worker claims job

**Expected**:

- Worker downloads file
- Validation fails
- Worker logs error and skips job
- Worker continues polling

### Test 14: Render Timeout

**Scenario**: Complex scene takes too long

**Test**:

1. Create job with very complex scene
2. Worker starts rendering

**Expected**:

- Render hits 300s timeout
- Worker logs timeout error
- Worker skips job
- Worker continues polling

## Regression Tests

After any changes to worker code, run this checklist:

- [ ] Worker authenticates successfully
- [ ] Worker polls for jobs every 10s
- [ ] Worker can download from IPFS
- [ ] Worker validates blend files
- [ ] Worker renders correctly
- [ ] Worker uploads results to IPFS
- [ ] Worker submits results to backend
- [ ] Worker handles errors gracefully
- [ ] Worker doesn't process same job twice
- [ ] Worker logs are clear and helpful

## Test Automation

Create a test suite:

```bash
# tests/test_worker.py
import pytest
import asyncio
from src.main_api import *

@pytest.mark.asyncio
async def test_authentication():
    auth = WorkerAuthenticator(
        "http://localhost:8000/api/v1",
        "0x1234567890abcdef1234567890abcdef12345678"
    )
    success = await auth.authenticate()
    assert success

@pytest.mark.asyncio
async def test_ipfs_upload():
    ipfs = IPFSClient("/ip4/127.0.0.1/tcp/5001")
    # Create temp file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test data")
        f.flush()
        result = ipfs.add(f.name)
        assert "Hash" in result

# Add more tests...
```

Run tests:

```bash
pip install pytest pytest-asyncio
pytest tests/test_worker.py -v
```

## Manual Testing Checklist

Before deploying worker:

- [ ] Environment variables are set correctly
- [ ] Blender is installed and accessible
- [ ] IPFS node is running
- [ ] Backend is running and healthy
- [ ] Worker can authenticate
- [ ] Worker can poll jobs
- [ ] Worker can claim jobs
- [ ] Worker can download files
- [ ] Worker can render scenes
- [ ] Worker can upload results
- [ ] Worker can submit completions
- [ ] Worker handles errors without crashing
- [ ] Worker logs are informative
- [ ] Completed jobs are tracked correctly
- [ ] Worker can run continuously for 1+ hour

## Monitoring in Production

After deployment, monitor:

1. **Worker Logs**: Check for errors
2. **Job Completion Rate**: Should be >95%
3. **Average Processing Time**: Track trends
4. **IPFS Success Rate**: Monitor download/upload failures
5. **Authentication Failures**: Should be rare
6. **Memory Usage**: Check for leaks
7. **CPU Usage**: Should spike during rendering
8. **Disk Usage**: Temp files should be cleaned up

## Debugging Tools

```bash
# Watch worker logs in real-time
tail -f worker.log

# Check IPFS status
ipfs swarm peers

# Test backend health
curl http://localhost:8000/health

# View completed jobs
cat src/temp/completed_jobs.json

# Monitor process
htop  # or top
```

---

**Testing Status**: All tests should pass before production deployment ✅
