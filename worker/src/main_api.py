"""
GalaxyRend Worker - API-Based Version
Polls backend API for jobs instead of direct blockchain access
"""

import os
import sys
import asyncio
import subprocess
import tempfile
import json
import shutil
import tarfile
import zipfile
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if ipfshttpclient is available
IPFS_CLIENT_AVAILABLE = False
try:
    import ipfshttpclient
    IPFS_CLIENT_AVAILABLE = True
    print("[Worker] ipfshttpclient imported successfully")
except ImportError as e:
    print(f"[Worker] Warning: Could not import ipfshttpclient: {e}")
    print("[Worker] Will use HTTP API fallback for IPFS operations")

# Configuration from environment
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")
WORKER_ADDRESS = os.getenv("WORKER_ADDRESS", "0x1234567890abcdef1234567890abcdef12345678")
WORKER_PRIVATE_KEY = os.getenv("WORKER_PRIVATE_KEY", "")  # For signing authentication challenges
IPFS_API = os.getenv("IPFS_API", "/ip4/127.0.0.1/tcp/5001")
IPFS_GATEWAY = os.getenv("IPFS_GATEWAY", "http://127.0.0.1:8080/ipfs")
BLENDER_PATH = os.getenv("BLENDER_PATH", "blender")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))  # seconds
USE_PERSISTENT_TEMP = os.getenv("USE_PERSISTENT_TEMP", "true").lower() in ("true", "1", "yes")  # Use ./temp or system temp

# Ensure temp directory exists
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Track completed jobs to avoid reprocessing
COMPLETED_JOBS_FILE = TEMP_DIR / "completed_jobs.json"


class WorkerAuthenticator:
    """Handles worker authentication with the backend API"""
    
    def __init__(self, backend_url: str, worker_address: str, private_key: str = ""):
        self.backend_url = backend_url
        self.worker_address = worker_address
        self.private_key = private_key
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    async def authenticate(self) -> bool:
        """Authenticate with the backend and get a JWT token"""
        try:
            # Step 1: Get authentication challenge
            print(f"[Worker] Requesting auth challenge for {self.worker_address}")
            challenge_response = requests.post(
                f"{self.backend_url}/auth/challenge",
                json={"address": self.worker_address}
            )
            challenge_response.raise_for_status()
            challenge_data = challenge_response.json()
            
            # Extract challenge fields
            message = challenge_data["message"]
            timestamp = challenge_data["timestamp"]
            nonce = challenge_data["nonce"]
            
            print(f"[Worker] Received challenge: {message[:50]}...")
            
            # Step 2: Sign the challenge
            # For demo purposes, we'll use a simple signature
            # In production, this should use StarkNet wallet signing
            signature = self._sign_challenge(message)
            
            # Step 3: Submit signature and get token (use worker-auth endpoint)
            print(f"[Worker] Submitting signed challenge to /worker-auth")
            auth_response = requests.post(
                f"{self.backend_url}/auth/worker-auth",
                json={
                    "address": self.worker_address,
                    "message": message,
                    "signature": signature,
                    "timestamp": int(timestamp) if isinstance(timestamp, str) else timestamp
                }
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            
            self.token = auth_data["access_token"]
            print(f"[Worker] Successfully authenticated. Token: {self.token[:20]}...")
            
            return True
            
        except Exception as e:
            print(f"[Worker] Authentication failed: {e}")
            return False
    
    def _sign_challenge(self, challenge: str) -> List[str]:
        """Sign the authentication challenge"""
        # TODO: Implement proper StarkNet signature
        # For now, return a mock signature as a list of strings
        # In production, this would be [r, s] components from the signature
        return ["0x123456789", "0x987654321"]
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication token"""
        if not self.token:
            return {}
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid token, re-authenticate if needed"""
        if not self.token:
            return await self.authenticate()
        return True


class IPFSClient:
    """Wrapper for IPFS operations with fallback to HTTP API"""
    
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint
        self.client = None
        
        # Try to use ipfshttpclient first
        if IPFS_CLIENT_AVAILABLE:
            try:
                self.client = ipfshttpclient.connect(api_endpoint)
                print("[Worker] Connected to IPFS using ipfshttpclient")
            except Exception as e:
                print(f"[Worker] ipfshttpclient connection failed: {e}")
                print("[Worker] Falling back to HTTP API")
        
        # Parse API endpoint for HTTP fallback
        if api_endpoint.startswith('/'):
            # Convert multiaddr format to HTTP URL
            parts = api_endpoint.split('/')
            if len(parts) >= 6 and parts[1] == 'ip4':
                self.http_url = f"http://{parts[2]}:{parts[4]}"
            else:
                self.http_url = "http://127.0.0.1:5001"
        else:
            self.http_url = api_endpoint
    
    def get(self, cid: str, target: str) -> Dict[str, str]:
        """Download file from IPFS"""
        if self.client:
            try:
                return self.client.get(cid, target=target)
            except Exception as e:
                print(f"[Worker] ipfshttpclient.get failed: {e}, trying fallback methods")
        
        # Try gateway first (returns raw file, not tar-wrapped)
        try:
            print(f"[Worker] Downloading CID: {cid} via IPFS Gateway")
            gateway_url = f"{IPFS_GATEWAY}/{cid}"
            response = requests.get(gateway_url, stream=True, timeout=60)
            response.raise_for_status()
            
            file_path = os.path.join(target, cid)
            total_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            print(f"[Worker] Downloaded via gateway to: {file_path} ({total_size} bytes)")
            return {"Hash": cid}
            
        except Exception as gateway_error:
            print(f"[Worker] IPFS Gateway download failed: {gateway_error}")
            
            # Fallback to API endpoint (may return tar-wrapped)
            try:
                print(f"[Worker] Trying IPFS API endpoint as fallback")
                response = requests.post(
                    f"{self.http_url}/api/v0/get",
                    params={"arg": cid},
                    stream=True,
                    timeout=60
                )
                response.raise_for_status()
                
                file_path = os.path.join(target, cid)
                total_size = 0
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                
                print(f"[Worker] Downloaded via API to: {file_path} ({total_size} bytes)")
                return {"Hash": cid}
                
            except Exception as api_error:
                print(f"[Worker] IPFS API download also failed: {api_error}")
                raise Exception(f"All download methods failed. Gateway: {gateway_error}, API: {api_error}")
    
    def add(self, file_path: str) -> Dict[str, str]:
        """Upload file to IPFS"""
        if self.client:
            return self.client.add(file_path)
        else:
            # HTTP API fallback
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.http_url}/api/v0/add", files=files)
                response.raise_for_status()
                result = response.json()
                return {"Hash": result["Hash"]}


async def download_blend_file(ipfs: IPFSClient, asset_cid: str, temp_dir: str) -> Optional[str]:
    """Download and extract .blend file from IPFS"""
    try:
        # Validate CID format
        if not asset_cid or len(asset_cid) < 10:
            print(f"[Worker] Error: Invalid IPFS CID format: '{asset_cid}'")
            print(f"[Worker] CID should be a valid IPFS hash (e.g., 'QmXyz...', 'bafybeiabc...')")
            return None
        
        # Check if it looks like a test/placeholder CID
        if asset_cid.startswith("Qm") and not any(c in "0123456789" for c in asset_cid[2:20]):
            print(f"[Worker] Warning: CID '{asset_cid}' appears to be a placeholder/test value")
            print(f"[Worker] Real IPFS CIDs contain alphanumeric characters")
            print(f"[Worker] Please upload the file to IPFS and use the returned CID")
            return None
        
        print(f"[Worker] Downloading asset CID: {asset_cid}")
        ipfs.get(asset_cid, temp_dir)
        
        # The file is now in temp_dir with name = asset_cid
        downloaded_file = os.path.join(temp_dir, asset_cid)
        
        if not os.path.exists(downloaded_file):
            print(f"[Worker] Error: Downloaded file not found at {downloaded_file}")
            return None
        
        # Get file size to verify download
        file_size = os.path.getsize(downloaded_file)
        print(f"[Worker] Downloaded file size: {file_size} bytes")
        
        # Try to extract if it's an archive
        extracted = False
        
        # Check if it's a tar archive
        try:
            if tarfile.is_tarfile(downloaded_file):
                print(f"[Worker] Detected tar archive, extracting...")
                try:
                    with tarfile.open(downloaded_file, 'r:*') as tar:
                        # List contents before extracting
                        members = tar.getmembers()
                        print(f"[Worker] Tar archive contains {len(members)} file(s)")
                        
                        # Extract all files
                        tar.extractall(temp_dir)
                        extracted = True
                        print(f"[Worker] Successfully extracted tar archive")
                except tarfile.ReadError as e:
                    print(f"[Worker] Tar extraction failed: {e}")
                    print(f"[Worker] File may be corrupted or not a complete tar archive")
                    # Try to treat as raw file instead
                    extracted = False
        except Exception as e:
            print(f"[Worker] Error checking tar file: {e}")
        
        # Check if it's a zip archive
        if not extracted:
            try:
                if zipfile.is_zipfile(downloaded_file):
                    print(f"[Worker] Detected zip archive, extracting...")
                    with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    extracted = True
                    print(f"[Worker] Successfully extracted zip archive")
            except Exception as e:
                print(f"[Worker] Zip extraction failed: {e}")
        
        # If not an archive or extraction failed, treat as raw file
        if not extracted:
            print(f"[Worker] Treating as raw .blend file (not an archive)")
            if not downloaded_file.endswith('.blend'):
                blend_path = downloaded_file + '.blend'
                shutil.move(downloaded_file, blend_path)
                downloaded_file = blend_path
                print(f"[Worker] Renamed to: {blend_path}")
        
        # Find the .blend file
        blend_files = list(Path(temp_dir).rglob("*.blend"))
        if not blend_files:
            print(f"[Worker] No .blend file found in downloaded content")
            print(f"[Worker] Files in temp dir: {list(Path(temp_dir).iterdir())}")
            return None
        
        blend_path = str(blend_files[0])
        print(f"[Worker] Found blend file: {blend_path}")
        return blend_path
        
    except Exception as e:
        error_msg = str(e)
        print(f"[Worker] Error downloading blend file: {error_msg}")
        
        # Provide helpful troubleshooting tips
        if "Invalid" in error_msg or "Bad Request" in error_msg:
            print(f"[Worker] Troubleshooting tips:")
            print(f"[Worker]   1. Verify the CID is a valid IPFS hash")
            print(f"[Worker]   2. Upload the .blend file to IPFS: ipfs add file.blend")
            print(f"[Worker]   3. Use the returned CID in the job creation")
            print(f"[Worker]   4. Test download: ipfs get <CID>")
        elif "500" in error_msg or "Internal Server Error" in error_msg:
            print(f"[Worker] IPFS node may be having issues. Check: ipfs id")
        elif "Connection" in error_msg or "timeout" in error_msg:
            print(f"[Worker] Cannot reach IPFS node. Is the daemon running?")
        
        import traceback
        traceback.print_exc()
        return None


async def validate_blend_file(blend_path: str) -> bool:
    """Validate that the .blend file can be opened by Blender"""
    try:
        print(f"[Worker] Validating blend file: {blend_path}")
        
        # Try to open the file with Blender in background mode
        result = subprocess.run(
            [BLENDER_PATH, "-b", blend_path, "--python-expr", "import bpy; print('VALIDATION_SUCCESS')"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "VALIDATION_SUCCESS" in result.stdout:
            print(f"[Worker] Blend file validation successful")
            return True
        else:
            print(f"[Worker] Blend file validation failed")
            print(f"[Worker] stdout: {result.stdout}")
            print(f"[Worker] stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[Worker] Error validating blend file: {e}")
        return False


async def render_blend_file(blend_path: str, output_dir: str) -> Optional[str]:
    """Render a .blend file using Blender"""
    try:
        output_path = os.path.join(output_dir, "render.png")
        print(f"[Worker] Rendering blend file to: {output_path}")
        
        # Render using Blender's EEVEE engine for faster rendering
        render_cmd = [
            BLENDER_PATH,
            "-b", blend_path,
            "-E", "BLENDER_EEVEE",
            "-o", output_path,
            "-f", "1",  # Render frame 1
            "-F", "PNG"
        ]
        
        print(f"[Worker] Executing: {' '.join(render_cmd)}")
        result = subprocess.run(
            render_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Blender adds frame number to output in format: filename####.ext
        # So render.png becomes render.png0001.png
        actual_output_with_ext = output_path + "0001.png"  # render.png0001.png
        actual_output_no_ext = output_path.replace(".png", "0001.png")  # render0001.png
        
        # Check all possible output locations
        if os.path.exists(actual_output_with_ext):
            print(f"[Worker] Render successful: {actual_output_with_ext}")
            return actual_output_with_ext
        elif os.path.exists(actual_output_no_ext):
            print(f"[Worker] Render successful: {actual_output_no_ext}")
            return actual_output_no_ext
        elif os.path.exists(output_path):
            print(f"[Worker] Render successful: {output_path}")
            return output_path
        else:
            print(f"[Worker] Render failed - output file not found")
            print(f"[Worker] Checked locations:")
            print(f"[Worker]   - {actual_output_with_ext}")
            print(f"[Worker]   - {actual_output_no_ext}")
            print(f"[Worker]   - {output_path}")
            print(f"[Worker] stdout: {result.stdout[-500:]}")  # Last 500 chars
            print(f"[Worker] stderr: {result.stderr[-500:]}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"[Worker] Render timeout exceeded (300s)")
        return None
    except Exception as e:
        print(f"[Worker] Error rendering blend file: {e}")
        import traceback
        traceback.print_exc()
        return None


async def upload_render_result(ipfs: IPFSClient, render_path: str) -> Optional[str]:
    """Upload rendered image to IPFS"""
    try:
        print(f"[Worker] Uploading render result to IPFS: {render_path}")
        result = ipfs.add(render_path)
        cid = result["Hash"]
        print(f"[Worker] Upload successful. CID: {cid}")
        return cid
        
    except Exception as e:
        print(f"[Worker] Error uploading render result: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_completed_jobs() -> set:
    """Load the set of completed job IDs"""
    if COMPLETED_JOBS_FILE.exists():
        try:
            with open(COMPLETED_JOBS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get("completed_jobs", []))
        except Exception as e:
            print(f"[Worker] Error loading completed jobs: {e}")
    return set()

def save_completed_job(job_id: str):
    """Save a completed job ID to the local tracking file"""
    completed = load_completed_jobs()
    completed.add(job_id)
    
    try:
        with open(COMPLETED_JOBS_FILE, 'w') as f:
            json.dump({"completed_jobs": list(completed)}, f, indent=2)
    except Exception as e:
        print(f"[Worker] Error saving completed jobs: {e}")


def save_completed_job2(job_id: str):
    """Save a job ID to the completed jobs list"""

    completed = load_completed_jobs()
    completed.add(job_id)
    
    try:
        with open(COMPLETED_JOBS_FILE, 'w') as f:
            json.dump({"completed_jobs": list(completed)}, f, indent=2)
    except Exception as e:
        print(f"[Worker] Error saving completed jobs: {e}")


async def poll_available_jobs(auth: WorkerAuthenticator) -> List[Dict[str, Any]]:
    """Poll the backend API for available jobs"""
    try:
        await auth.ensure_authenticated()
        
        # Get available jobs from API
        response = requests.get(
            f"{auth.backend_url}/jobs/available",
            headers=auth.get_headers(),
            params={"status": "pending"}
        )
        response.raise_for_status()
        
        jobs = response.json()
        
        # Filter out completed jobs
        completed = load_completed_jobs()
        available_jobs = [job for job in jobs if job["id"] not in completed]
        
        if available_jobs:
            print(f"[Worker] Found {len(available_jobs)} available jobs")
        
        return available_jobs
        
    except Exception as e:
        print(f"[Worker] Error polling jobs: {e}")
        return []


async def claim_job(auth: WorkerAuthenticator, job_id: str) -> bool:
    """Claim a job by assigning it to this worker"""
    try:
        await auth.ensure_authenticated()
        
        response = requests.post(
            f"{auth.backend_url}/jobs/{job_id}/assign",
            headers=auth.get_headers(),
            json={"worker_address": auth.worker_address}
        )
        response.raise_for_status()
        
        print(f"[Worker] Successfully claimed job {job_id}")
        return True
        
    except Exception as e:
        print(f"[Worker] Error claiming job {job_id}: {e}")
        return False


async def submit_job_completion(auth: WorkerAuthenticator, job_id: str, result_cid: str) -> bool:
    """Submit completed job result to the backend using /jobs/{job_id}/complete endpoint"""
    try:
        await auth.ensure_authenticated()
        
        # Prepare payload according to JobCompletion schema
        # Split CID if it's too long (StarkNet contract limitation)
        result_cid_part1 = result_cid[:31] if len(result_cid) > 31 else result_cid
        result_cid_part2 = result_cid[31:] if len(result_cid) > 31 else None
        
        payload = {
            "result_cid_part1": result_cid_part1,
            "result_cid_part2": result_cid_part2,
            "quality_score": 100,  # Default quality score - could be enhanced with actual quality checks
            "worker_address": auth.worker_address
        }
        
        print(f"[Worker] Submitting job completion to /jobs/{job_id}/complete")
        print(f"[Worker] Result CID: {result_cid}")
        
        response = requests.post(
            f"{auth.backend_url}/jobs/{job_id}/complete",
            headers=auth.get_headers(),
            json=payload
        )
        response.raise_for_status()
        
        print(f"[Worker] Successfully submitted result for job {job_id}")
        save_completed_job(job_id)
        return True
        
    except Exception as e:
        print(f"[Worker] Error submitting job completion: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"[Worker] Response: {e.response.text}")
        return False


async def process_render_job(ipfs: IPFSClient, job_id: str, asset_cid: str) -> Optional[str]:
    """Process a complete rendering job: download .blend, render, upload result"""
    # Use persistent temp directory or create temporary one based on config
    if USE_PERSISTENT_TEMP:
        # Use persistent temp directory for debugging
        job_temp_dir = TEMP_DIR / f"job_{job_id}"
        job_temp_dir.mkdir(exist_ok=True)
        temp_dir = str(job_temp_dir)
        cleanup_temp = False
    else:
        # Use system temp directory (auto-cleanup)
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name
        cleanup_temp = True
    
    try:
        # Download .blend file from IPFS
        blend_path = await download_blend_file(ipfs, asset_cid, temp_dir)
        if not blend_path:
            print(f"[Worker] Failed to download blend file for job {job_id}")
            return None
        
        # Validate the blend file before attempting to render
        if not await validate_blend_file(blend_path):
            print(f"[Worker] Blend file validation failed for job {job_id}")
            return None
        
        # Render the .blend file
        render_path = await render_blend_file(blend_path, temp_dir)
        if not render_path:
            print(f"[Worker] Failed to render blend file for job {job_id}")
            return None
        
        # Upload rendered result to IPFS
        result_cid = await upload_render_result(ipfs, render_path)
        if not result_cid:
            print(f"[Worker] Failed to upload render result for job {job_id}")
            return None
        
        print(f"[Worker] Job {job_id} rendering complete. Result CID: {result_cid}")
        return result_cid
        
    except Exception as e:
        print(f"[Worker] Error processing render job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Cleanup temp directory if using system temp
        if cleanup_temp:
            try:
                temp_dir_obj.cleanup()
            except Exception as e:
                print(f"[Worker] Warning: Could not cleanup temp directory: {e}")


async def main():
    """Main worker loop"""
    print("[Worker] Starting GalaxyRend Worker (API-based)")
    print(f"[Worker] Backend API: {BACKEND_API_URL}")
    print(f"[Worker] Worker Address: {WORKER_ADDRESS}")
    print(f"[Worker] Blender path: {BLENDER_PATH}")
    print(f"[Worker] IPFS API: {IPFS_API}")
    print(f"[Worker] Temp directory: {'./temp (persistent)' if USE_PERSISTENT_TEMP else 'system temp (auto-cleanup)'}")
    
    # Check if Blender is available
    try:
        result = subprocess.run(
            [BLENDER_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
            print(f"[Worker] Blender found: {version_line}")
        else:
            print("[Worker] Warning: Blender not found or not working properly")
            return
    except Exception as e:
        print(f"[Worker] Error: Could not check Blender version: {e}")
        return
    
    # Initialize components
    auth = WorkerAuthenticator(BACKEND_API_URL, WORKER_ADDRESS, WORKER_PRIVATE_KEY)
    ipfs = IPFSClient(IPFS_API)
    
    # Authenticate with backend
    if not await auth.authenticate():
        print("[Worker] Failed to authenticate with backend. Exiting.")
        return
    
    print(f"[Worker] Starting job polling loop (interval: {POLL_INTERVAL}s)")
    
    # Main polling loop
    while True:
        try:
            # Poll for available jobs
            print(f"\n[Worker] [{datetime.now().strftime('%H:%M:%S')}] Polling for jobs...")
            jobs = await poll_available_jobs(auth)
            
            if jobs:
                # Process the first available job
                job = jobs[0]
                job_id = job["id"]
                # Try different field names for asset CID
                asset_cid = (
                    job.get("full_asset_cid") or 
                    job.get("asset_cid") or 
                    job.get("assetCid", "")
                )
                
                print(f"[Worker] Found job {job_id} - Asset CID: {asset_cid}")
                
                if not asset_cid:
                    print(f"[Worker] No asset CID found for job {job_id}, skipping")
                    continue
                
                # Claim the job
                if not await claim_job(auth, job_id):
                    print(f"[Worker] Failed to claim job {job_id}, trying next job")
                    continue
                
                # Process the rendering job
                result_cid = await process_render_job(ipfs, job_id, asset_cid)
                
                if result_cid:
                    # Submit the result
                    success = await submit_job_completion(auth, job_id, result_cid)
                    
                    if success:
                        print(f"[Worker] ✓ Successfully completed job {job_id}")
                    else:
                        print(f"[Worker] ✗ Failed to submit result for job {job_id}")
                else:
                    print(f"[Worker] ✗ Failed to process job {job_id}")
            else:
                print(f"[Worker] No available jobs")
            
            # Wait before next polling cycle
            await asyncio.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n[Worker] Shutting down...")
            break
        except Exception as e:
            print(f"[Worker] Error in main loop: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
