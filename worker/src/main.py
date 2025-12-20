import os
import time
import asyncio
import subprocess
import tempfile
import shutil
import requests
import json
import hashlib
import tarfile
import zipfile

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print(os.getenv("STARKNET_RPC"))
# Try to import starknet_py components with better error handling
try:
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.contract import Contract
    STARKNET_AVAILABLE = True
except ImportError as e:
    print(f"[Worker] Failed to import starknet_py: {e}")
    print("[Worker] Please reinstall starknet_py: pip install --force-reinstall starknet_py")
    STARKNET_AVAILABLE = False
except Exception as e:
    print(f"[Worker] Error initializing starknet_py: {e}")
    print("[Worker] This might be due to missing core_structures.json file")
    print("[Worker] Try: pip uninstall starknet_py && pip install starknet_py==0.21.0")
    STARKNET_AVAILABLE = False

# Try to import ipfshttpclient, fallback to requests if version incompatible
try:
    import ipfshttpclient
    IPFS_CLIENT_AVAILABLE = True
except ImportError:
    IPFS_CLIENT_AVAILABLE = False
    print("[Worker] ipfshttpclient not available, using requests fallback")

STARKNET_RPC = os.getenv("STARKNET_RPC", "http://localhost:5050")
# IPFS_API = os.getenv("IPFS_API", "/dns/ipfs-node/tcp/5001/http")
JOB_REGISTRY_ADDRESS = int(os.getenv("JOB_REGISTRY_ADDRESS", "0"), 16)
IPFS_API = os.getenv("IPFS_API", "http://127.0.0.1:5001")
IPFS_GATEWAY = os.getenv("IPFS_GATEWAY", "http://127.0.0.1:8080/ipfs")

# STARKNET_RPC = "https://api.cartridge.gg/x/starknet/sepolia"
# IPFS_API = "http://127.0.0.1:5001"
# IPFS_GATEWAY = "http://127.0.0.1:8080/ipfs"
# JOB_REGISTRY_ADDRESS = int("0x0000f133b188900619b3df297bb72e46cc82b246a030acd14c132c12a32beafa", 16)
BLENDER_PATH = os.getenv("BLENDER_PATH", "blender")  # Path to Blender executable

# Load the contract ABI with proper type definitions
CONTRACT_ABI = [
    {
        "type": "function",
        "name": "get_job_creator",
        "inputs": [{"name": "job_id", "type": "felt"}],
        "outputs": [{"name": "creator", "type": "felt"}],
        "state_mutability": "view",
    },
    {
        "type": "function", 
        "name": "get_job_worker",
        "inputs": [{"name": "job_id", "type": "felt"}],
        "outputs": [{"name": "worker", "type": "felt"}],
        "state_mutability": "view",
    },
    {
        "type": "function",
        "name": "get_job_reward", 
        "inputs": [{"name": "job_id", "type": "felt"}],
        "outputs": [{"name": "reward_low", "type": "felt"}, {"name": "reward_high", "type": "felt"}],
        "state_mutability": "view",
    },
    {
            "type": "function",
            "name": "get_job_asset_cid",
            "inputs": [{"name": "job_id", "type": "felt"}],
            "outputs": [{"name": "part1", "type": "felt"}, {"name": "part2", "type": "felt"}],
            "state_mutability": "view",
        },
    {
        "type": "function",
        "name": "submit_result",
        "inputs": [
            {"name": "job_id", "type": "felt"},
            {"name": "result_cid", "type": "felt"}
        ],
        "outputs": [],
        "state_mutability": "external",
    },
    {
        "type": "function",
        "name": "get_job_result",
        "inputs": [{"name": "job_id", "type": "felt"}],
        "outputs": [{"name": "result_cid", "type": "felt"}],
        "state_mutability": "view",
    },
    # Worker Authorization and Reputation System
    {
        "type": "function",
        "name": "register_worker",
        "inputs": [{"name": "worker_info_cid", "type": "felt"}],
        "outputs": [],
        "state_mutability": "external",
    },
    {
        "type": "function",
        "name": "get_worker_status",
        "inputs": [{"name": "worker", "type": "felt"}],
        "outputs": [
            {"name": "verified", "type": "bool"},
            {"name": "reputation", "type": "u16"},
            {"name": "jobs_completed", "type": "u32"},
            {"name": "jobs_failed", "type": "u32"}
        ],
        "state_mutability": "view",
    },
    {
        "type": "function",
        "name": "is_worker_eligible",
        "inputs": [
            {"name": "worker", "type": "felt"},
            {"name": "job_id", "type": "felt"}
        ],
        "outputs": [{"name": "eligible", "type": "bool"}],
        "state_mutability": "view",
    },
    {
        "type": "function",
        "name": "get_minimum_reputation_for_job",
        "inputs": [{"name": "job_id", "type": "felt"}],
        "outputs": [{"name": "min_reputation", "type": "u16"}],
        "state_mutability": "view",
    },
]

def combine_cid_parts(part1, part2):
    """Combine two felt252 parts back into a full IPFS CID"""
    try:
        # Convert each part to string
        str_part1 = felt252_to_string(part1)
        str_part2 = felt252_to_string(part2)
        
        # Combine parts
        full_cid = str_part1 + str_part2
        return full_cid.strip()
    except Exception as e:
        print(f"[Worker] Error combining CID parts: {e}")
        return f"{part1}_{part2}"

def felt252_to_string(felt_value):
    """Convert felt252 to string (simplified IPFS CID conversion)"""
    try:
        # Convert felt to bytes and decode (this is simplified - in production use proper encoding)
        if felt_value == 0:
            return ""
        byte_data = felt_value.to_bytes(32, 'big').lstrip(b'\x00')
        return byte_data.decode('utf-8', errors='ignore')
    except:
        return str(felt_value)

def string_to_felt252(text):
    """Convert string to felt252 (simplified conversion)"""
    try:
        # Take first 31 bytes to fit in felt252
        byte_data = text.encode('utf-8')[:31]
        return int.from_bytes(byte_data, 'big')
    except:
        return 0

def uint256_to_int(reward_response):
    """Convert Uint256 response to integer"""
    try:
        # If it's a tuple/list with two elements (low, high)
        if isinstance(reward_response, (tuple, list)) and len(reward_response) == 2:
            return reward_response[0] + (reward_response[1] << 128)
        # If it's a dict with low/high keys
        elif isinstance(reward_response, dict) and 'low' in reward_response and 'high' in reward_response:
            return reward_response['low'] + (reward_response['high'] << 128)
        # If it's already an integer
        elif isinstance(reward_response, int):
            return reward_response
        else:
            return 0
    except:
        return 0

async def download_blend_file(ipfs, cid, temp_dir):
    """Download .blend file from IPFS"""
    try:
        blend_path = os.path.join(temp_dir, f"{cid}.blend")
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        print(f"[Worker] Downloading .blend file from IPFS CID: {cid}")
        
        # Download file from IPFS
        ipfs.get(cid, target=temp_dir)
        
        # Check different possible locations for the downloaded file
        # 1. IPFS creates a directory with the CID name (ipfshttpclient behavior)
        cid_dir = os.path.join(temp_dir, cid)
        if os.path.exists(cid_dir) and os.path.isdir(cid_dir):
            for file in os.listdir(cid_dir):
                if file.endswith('.blend'):
                    src_path = os.path.join(cid_dir, file)
                    shutil.move(src_path, blend_path)
                    print(f"[Worker] Downloaded .blend file to: {blend_path}")
                    await validate_blend_file(blend_path)
                    return blend_path
        
        # 2. File downloaded directly with CID as filename (HTTP API fallback)
        downloaded_path = os.path.join(temp_dir, cid)
        if os.path.exists(downloaded_path) and os.path.isfile(downloaded_path):
            # Check file content before processing
            file_type = await validate_downloaded_file(downloaded_path, cid)
            
            if file_type == "blender":
                # It's already a Blender file, just rename
                shutil.move(downloaded_path, blend_path)
                print(f"[Worker] Downloaded .blend file to: {blend_path}")
                await validate_blend_file(blend_path)
                return blend_path
            
            elif file_type in ["tar", "zip"]:
                # It's an archive, extract it
                blend_file = await extract_and_find_blend_file(downloaded_path, extract_dir)
                if blend_file:
                    # Copy the found blend file to the expected location
                    shutil.copy2(blend_file, blend_path)
                    print(f"[Worker] Extracted and copied .blend file to: {blend_path}")
                    await validate_blend_file(blend_path)
                    return blend_path
                else:
                    print(f"[Worker] No .blend file found in extracted archive")
                    return None
            
            else:
                print(f"[Worker] Unknown file format, attempting direct use as .blend file")
                shutil.move(downloaded_path, blend_path)
                print(f"[Worker] Downloaded .blend file to: {blend_path}")
                # Try validation anyway
                if await validate_blend_file(blend_path):
                    return blend_path
                else:
                    return None
        
        # 3. Look for any .blend files in the temp directory
        for file in os.listdir(temp_dir):
            if file.endswith('.blend'):
                src_path = os.path.join(temp_dir, file)
                if src_path != blend_path:  # Don't move to itself
                    shutil.move(src_path, blend_path)
                    print(f"[Worker] Downloaded .blend file to: {blend_path}")
                    await validate_blend_file(blend_path)
                    return blend_path
            
        print(f"[Worker] Error: Could not find .blend file for CID {cid}")
        print(f"[Worker] Files in temp directory: {os.listdir(temp_dir)}")
        if os.path.exists(extract_dir):
            print(f"[Worker] Files in extract directory: {os.listdir(extract_dir)}")
        return None
        
    except Exception as e:
        print(f"[Worker] Error downloading .blend file: {e}")
        import traceback
        traceback.print_exc()
        return None

async def extract_and_find_blend_file(file_path, extract_dir):
    """Extract archive and find .blend file inside"""
    try:
        print(f"[Worker] Attempting to extract archive: {file_path}")
        
        # Check if it's a TAR file
        if tarfile.is_tarfile(file_path):
            print(f"[Worker] File is a TAR archive")
            with tarfile.open(file_path, 'r:*') as tar:
                # List contents before extracting
                members = tar.getnames()
                print(f"[Worker] TAR archive contents: {members}")
                tar.extractall(path=extract_dir)
                print(f"[Worker] Extracted TAR archive to: {extract_dir}")
        
        # Check if it's a ZIP file
        elif zipfile.is_zipfile(file_path):
            print(f"[Worker] File is a ZIP archive")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # List contents before extracting
                members = zip_ref.namelist()
                print(f"[Worker] ZIP archive contents: {members}")
                zip_ref.extractall(extract_dir)
                print(f"[Worker] Extracted ZIP archive to: {extract_dir}")
        
        else:
            print(f"[Worker] File is not a recognized archive format")
            return None
        
        # List all files in the extracted directory for debugging
        print(f"[Worker] Files in extract directory after extraction:")
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path_full = os.path.join(root, file)
                file_size = os.path.getsize(file_path_full)
                print(f"[Worker]   {file_path_full} ({file_size} bytes)")
        
        # Search for .blend files in the extracted directory
        blend_files = []
        all_files = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path_full = os.path.join(root, file)
                all_files.append(file_path_full)
                
                if file.endswith('.blend'):
                    blend_files.append(file_path_full)
                    print(f"[Worker] Found .blend file: {file_path_full}")
                # Also check for files that might be blend files without extension
                elif file.lower() in ['copper', 'scene', 'default'] or 'blend' in file.lower():
                    print(f"[Worker] Found potential blend file: {file_path_full}")
                    # Check if it's actually a blend file by header
                    try:
                        with open(file_path_full, 'rb') as f:
                            header = f.read(16)
                            if header.startswith(b'BLENDER'):
                                print(f"[Worker] Confirmed {file_path_full} is a blend file")
                                blend_files.append(file_path_full)
                    except:
                        pass
        
        if blend_files:
            # Return the first .blend file found
            selected_blend = blend_files[0]
            print(f"[Worker] Using .blend file: {selected_blend}")
            return selected_blend
        else:
            print(f"[Worker] No .blend files found in extracted archive")
            print(f"[Worker] All extracted files: {all_files}")
            
            # If no .blend files found, try to use the largest file as it might be the blend file
            if all_files:
                largest_file = max(all_files, key=lambda f: os.path.getsize(f))
                largest_size = os.path.getsize(largest_file)
                print(f"[Worker] Trying largest file as potential blend file: {largest_file} ({largest_size} bytes)")
                
                # Check if it might be a blend file
                try:
                    with open(largest_file, 'rb') as f:
                        header = f.read(16)
                        print(f"[Worker] Largest file header: {header}")
                        if header.startswith(b'BLENDER'):
                            print(f"[Worker] Largest file is actually a blend file!")
                            return largest_file
                except:
                    pass
                    
            return None
            
    except Exception as e:
        print(f"[Worker] Error extracting archive: {e}")
        import traceback
        traceback.print_exc()
        return None

async def validate_downloaded_file(file_path, cid):
    """Validate the downloaded file content and format"""
    try:
        file_size = os.path.getsize(file_path)
        print(f"[Worker] Downloaded file size: {file_size} bytes")
        
        # Check file header (first 16 bytes)
        with open(file_path, 'rb') as f:
            header = f.read(16)
            print(f"[Worker] File header (hex): {header.hex()}")
            print(f"[Worker] File header (ascii): {header.decode('ascii', errors='ignore')}")
            
        # Check if it's a valid Blender file (should start with "BLENDER")
        if header.startswith(b'BLENDER'):
            print(f"[Worker] File appears to be a valid Blender file")
            return "blender"
        # Check if it's a TAR archive (common IPFS format)
        elif tarfile.is_tarfile(file_path):
            print(f"[Worker] File appears to be a TAR archive")
            return "tar"
        # Check if it's a ZIP archive
        elif zipfile.is_zipfile(file_path):
            print(f"[Worker] File appears to be a ZIP archive")
            return "zip"
        # Check for other common archive signatures
        elif header.startswith(b'PK'):
            print(f"[Worker] File appears to be a ZIP archive (PK signature)")
            return "zip"
        else:
            print(f"[Worker] WARNING: File format not recognized!")
            print(f"[Worker] Header: {header}")
            return "unknown"
            
    except Exception as e:
        print(f"[Worker] Error validating downloaded file: {e}")
        return "error"

async def validate_blend_file(blend_path):
    """Validate the .blend file before rendering"""
    try:
        if not os.path.exists(blend_path):
            print(f"[Worker] ERROR: Blend file does not exist: {blend_path}")
            return False
            
        file_size = os.path.getsize(blend_path)
        print(f"[Worker] Blend file size: {file_size} bytes")
        
        if file_size == 0:
            print(f"[Worker] ERROR: Blend file is empty")
            return False
            
        # Check file header
        with open(blend_path, 'rb') as f:
            header = f.read(16)
            print(f"[Worker] Blend file header: {header.hex()}")
            
        # Blender files should start with "BLENDER"
        if header.startswith(b'BLENDER'):
            print(f"[Worker] Blend file validation passed")
            return True
        else:
            print(f"[Worker] ERROR: Invalid Blender file format!")
            print(f"[Worker] Expected 'BLENDER' header, got: {header}")
            return False
            
    except Exception as e:
        print(f"[Worker] Error validating blend file: {e}")
        return False

async def render_blend_file(blend_path, output_dir):
    """Render the .blend file using Blender"""
    try:
        # Use worker/src/temp directory
        temp_output_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_output_dir, exist_ok=True)
        output_path = os.path.join(temp_output_dir, "render.png")
        print(f"[Worker] Rendering {blend_path} to {output_path}")
        
        # Verify blend file exists and is readable
        if not os.path.exists(blend_path):
            print(f"[Worker] ERROR: Blend file does not exist: {blend_path}")
            return None
            
        file_size = os.path.getsize(blend_path)
        print(f"[Worker] Blend file size: {file_size} bytes")
        
        # Create a Python script to configure rendering settings
        python_script = f"""
import bpy

# Set render engine to EEVEE (faster and more compatible than Cycles)
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

# Disable denoising
if hasattr(bpy.context.scene.eevee, 'use_taa_reprojection'):
    bpy.context.scene.eevee.use_taa_reprojection = False

# Basic render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 50  # Render at 50% for speed

# Set output format
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = '{output_path}'

# Render the scene
bpy.ops.render.render(write_still=True)
"""
        
        # Write the Python script to a temporary file
        script_path = os.path.join(temp_output_dir, "render_script.py")
        with open(script_path, 'w') as f:
            f.write(python_script)
        
        # Blender command to render the file with custom Python script
        cmd = [
            BLENDER_PATH,
            "-b",  # Run in background
            blend_path,
            "--python", script_path,  # Execute our custom script
            "--python-exit-code", "1"  # Exit with error code on Python errors
        ]
        
        print(f"[Worker] Running Blender command: {' '.join(cmd)}")
        
        # Run Blender
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"[Worker] Blender return code: {result.returncode}")
        
        if result.stdout:
            print(f"[Worker] Blender stdout: {result.stdout}")
        if result.stderr:
            print(f"[Worker] Blender stderr: {result.stderr}")
        
        if result.returncode == 0 and os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            print(f"[Worker] Successfully rendered to: {output_path} (size: {output_size} bytes)")
            return output_path
        else:
            print(f"[Worker] Blender render failed:")
            print(f"[Worker] stdout: {result.stdout}")
            print(f"[Worker] stderr: {result.stderr}")
            
            # Check if output file was partially created
            if os.path.exists(output_path):
                partial_size = os.path.getsize(output_path)
                print(f"[Worker] Partial output file created: {partial_size} bytes")
            
            # Try a fallback method with even simpler settings
            print(f"[Worker] Trying fallback render method...")
            return await render_blend_file_fallback(blend_path, temp_output_dir)
            
    except subprocess.TimeoutExpired:
        print(f"[Worker] Blender render timed out after 5 minutes")
        return None
    except Exception as e:
        print(f"[Worker] Error during rendering: {e}")
        import traceback
        traceback.print_exc()
        return None

async def render_blend_file_fallback(blend_path, output_dir):
    """Fallback render method with minimal settings"""
    try:
        # Use worker/src/temp directory
        temp_output_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_output_dir, exist_ok=True)
        output_path = os.path.join(temp_output_dir, "render.png")
        print(f"[Worker] Fallback rendering {blend_path} to {output_path}")
        
        # Very simple Blender command without custom scripts
        cmd = [
            BLENDER_PATH,
            "-b",  # Run in background
            blend_path,
            "-E", "BLENDER_EEVEE",  # Use EEVEE engine
            "-o", output_path,  # Output path
            "-f", "1",  # Render frame 1
        ]
        
        print(f"[Worker] Running fallback Blender command: {' '.join(cmd)}")
        
        # Run Blender
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"[Worker] Fallback Blender return code: {result.returncode}")
        
        if result.stdout:
            print(f"[Worker] Fallback Blender stdout: {result.stdout}")
        if result.stderr:
            print(f"[Worker] Fallback Blender stderr: {result.stderr}")
        
        if result.returncode == 0 and os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            print(f"[Worker] Fallback render successful: {output_path} (size: {output_size} bytes)")
            return output_path
        else:
            print(f"[Worker] Fallback render also failed")
            return None
            
    except Exception as e:
        print(f"[Worker] Error during fallback rendering: {e}")
        return None

async def notify_frontend(job_id, result_cid):
    """Notify frontend about completed job"""
    try:
        # Method 1: Write to a results file that frontend can monitor
        results_file = os.path.join(os.path.dirname(__file__), "temp", "completed_jobs.json")
        
        # Load existing results
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
        else:
            results = []
        
        # Add new result
        result_entry = {
            "job_id": job_id,
            "result_cid": result_cid,
            "completed_at": time.time(),
            "ipfs_gateway_url": f"{IPFS_GATEWAY}/{result_cid}"
        }
        results.append(result_entry)
        
        # Keep only last 10 results
        results = results[-10:]
        
        # Write back to file
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[Worker] Notified frontend: Job {job_id} completed, result CID: {result_cid}")
        
        # Method 2: Try HTTP notification to frontend (optional)
        try:
            notification_data = {
                "job_id": job_id,
                "result_cid": result_cid,
                "status": "completed",
                "ipfs_url": f"{IPFS_GATEWAY}/{result_cid}"
            }
            
            # Try to notify frontend if it's running on port 3000
            response = requests.post(
                "http://localhost:3000/api/job-completed", 
                json=notification_data,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[Worker] Successfully notified frontend via HTTP")
        except:
            # Frontend might not be running or doesn't have this endpoint
            pass
            
    except Exception as e:
        print(f"[Worker] Error notifying frontend: {e}")

async def upload_render_result(ipfs, render_path):
    """Upload rendered image to IPFS"""
    try:
        print(f"[Worker] Uploading render result to IPFS: {render_path}")
        result = ipfs.add(render_path)
        cid = result['Hash']
        print(f"[Worker] Uploaded render result to IPFS CID: {cid}")
        return cid
    except Exception as e:
        print(f"[Worker] Error uploading render result: {e}")
        return None

async def check_worker_registration(contract, worker_address):
    """Check if worker is registered and verified"""
    try:
        print(f"[Worker] Checking registration status for worker: {hex(worker_address)}")
        
        # Get worker status
        status_response = await contract.functions["get_worker_status"].call(worker_address)
        
        # Handle response format
        if hasattr(status_response, 'verified'):
            verified = status_response.verified
            reputation = status_response.reputation
            jobs_completed = status_response.jobs_completed
            jobs_failed = status_response.jobs_failed
        else:
            # Fallback for tuple response
            verified = status_response[0] if len(status_response) > 0 else False
            reputation = status_response[1] if len(status_response) > 1 else 0
            jobs_completed = status_response[2] if len(status_response) > 2 else 0
            jobs_failed = status_response[3] if len(status_response) > 3 else 0
        
        print(f"[Worker] Status - Verified: {verified}, Reputation: {reputation}, Completed: {jobs_completed}, Failed: {jobs_failed}")
        
        return {
            "verified": verified,
            "reputation": reputation,
            "jobs_completed": jobs_completed,
            "jobs_failed": jobs_failed,
            "registered": reputation > 0  # If reputation > 0, worker is registered
        }
    except Exception as e:
        print(f"[Worker] Error checking worker registration: {e}")
        return {
            "verified": False,
            "reputation": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "registered": False
        }

async def register_worker_if_needed(contract, worker_address):
    """Register worker if not already registered"""
    try:
        status = await check_worker_registration(contract, worker_address)
        
        if not status["registered"]:
            print(f"[Worker] Worker not registered, attempting registration...")
            
            # Create worker info and upload to IPFS
            worker_info = {
                "worker_address": hex(worker_address),
                "registration_time": time.time(),
                "capabilities": ["blender_rendering", "3d_modeling"],
                "hardware_specs": {
                    "blender_version": "4.0+",
                    "gpu_available": True,  # Could be detected
                    "cpu_cores": 4,  # Could be detected
                },
                "contact_info": "worker@******.dev"
            }
            
            # Upload worker info to IPFS (for now, use a placeholder)
            worker_info_cid = string_to_felt252("QmWorkerInfo123")  # In production, upload to IPFS
            
            print(f"[Worker] Registering worker with info CID: {worker_info_cid}")
            
            # Note: This would require a wallet/account to sign transactions
            # For now, just log the intent
            print(f"[Worker] Would register worker with CID: {hex(worker_info_cid)}")
            print(f"[Worker] Registration requires transaction signing - implement wallet integration")
            
            return False  # Registration not completed in this demo
        else:
            print(f"[Worker] Worker already registered")
            return True
            
    except Exception as e:
        print(f"[Worker] Error during worker registration: {e}")
        return False

async def check_job_eligibility(contract, worker_address, job_id):
    """Check if worker is eligible for a specific job"""
    try:
        print(f"[Worker] Checking eligibility for job {job_id}")
        
        # Check worker eligibility
        eligibility_response = await contract.functions["is_worker_eligible"].call(worker_address, job_id)
        eligible = eligibility_response.eligible if hasattr(eligibility_response, 'eligible') else eligibility_response
        
        if not eligible:
            print(f"[Worker] Worker not eligible for job {job_id}")
            
            # Get minimum reputation requirement
            min_rep_response = await contract.functions["get_minimum_reputation_for_job"].call(job_id)
            min_reputation = min_rep_response.min_reputation if hasattr(min_rep_response, 'min_reputation') else min_rep_response
            
            # Get worker status for comparison
            status = await check_worker_registration(contract, worker_address)
            
            print(f"[Worker] Job requires minimum reputation: {min_reputation}")
            print(f"[Worker] Worker current reputation: {status['reputation']}")
            print(f"[Worker] Worker verified: {status['verified']}")
            
            return False
        else:
            print(f"[Worker] Worker eligible for job {job_id}")
            return True
            
    except Exception as e:
        print(f"[Worker] Error checking job eligibility: {e}")
        return False

async def check_for_jobs(contract, worker_address, max_job_id=5):
    """Check for available jobs by iterating through job IDs with authorization checks"""
    available_jobs = []

    # Read completed jobs to avoid reprocessing
    completed_jobs = set()
    try:
        results_file = os.path.join(os.path.dirname(__file__), "temp", "completed_jobs.json")
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
                completed_jobs = {result['job_id'] for result in results}
            print(f"[Worker] Loaded {len(completed_jobs)} completed jobs: {completed_jobs}")
    except Exception as e:
        print(f"[Worker] Error loading completed jobs: {e}")

    # Check worker registration and verification status
    worker_status = await check_worker_registration(contract, worker_address)
    
    if not worker_status["registered"]:
        print(f"[Worker] Worker not registered - attempting registration")
        registered = await register_worker_if_needed(contract, worker_address)
        if not registered:
            print(f"[Worker] Worker registration required but not completed")
            return []
    
    if not worker_status["verified"]:
        print(f"[Worker] Worker not verified - only verified workers can take jobs")
        print(f"[Worker] Current reputation: {worker_status['reputation']}")
        return []

    print(f"[Worker] Worker authorized - Reputation: {worker_status['reputation']}, Completed: {worker_status['jobs_completed']}, Failed: {worker_status['jobs_failed']}")

    for job_id in range(1, max_job_id + 1):
        # Skip already completed jobs
        if job_id in completed_jobs:
            print(f"[Worker] Skipping already completed job {job_id}")
            continue
            
        try:
            # Check if job exists by getting creator
            creator_response = await contract.functions["get_job_creator"].call(job_id)
            creator = creator_response.creator if hasattr(creator_response, 'creator') else creator_response
            print(f"[Worker] Checking job {job_id}, creator: {creator}")
            if creator != 0:  # Job exists
                
                # Check if worker is eligible for this specific job
                if not await check_job_eligibility(contract, worker_address, job_id):
                    print(f"[Worker] Worker not eligible for job {job_id} - skipping")
                    continue
                
                # Check if job has no worker assigned yet
                worker_response = await contract.functions["get_job_worker"].call(job_id)
                assigned_worker = worker_response.worker if hasattr(worker_response, 'worker') else worker_response
                
                if assigned_worker != 0:  # Job already has a worker
                    print(f"[Worker] Job {job_id} already has worker assigned: {hex(assigned_worker)}")
                    continue
                
                reward_response = await contract.functions["get_job_reward"].call(job_id)
                reward = uint256_to_int(reward_response)
                asset_cid_response = await contract.functions["get_job_asset_cid"].call(job_id)
                # Handle tuple response for two-part CID
                if hasattr(asset_cid_response, 'part1') and hasattr(asset_cid_response, 'part2'):
                    part1 = asset_cid_response.part1
                    part2 = asset_cid_response.part2
                else:
                    # Fallback for older response format
                    part1 = asset_cid_response[0] if len(asset_cid_response) > 0 else 0
                    part2 = asset_cid_response[1] if len(asset_cid_response) > 1 else 0
                
                asset_cid = combine_cid_parts(part1, part2)
                print(f"[Worker] Raw CID parts: {part1}, {part2}")
                print(f"[Worker] Combined asset_cid: {asset_cid}")
                
                if asset_cid == "QmCopper.blend":
                    print(f"[Worker] Skipping job {job_id} with asset CID: {asset_cid}")
                    continue

                # Get minimum reputation requirement for display
                min_rep_response = await contract.functions["get_minimum_reputation_for_job"].call(job_id)
                min_reputation = min_rep_response.min_reputation if hasattr(min_rep_response, 'min_reputation') else min_rep_response

                available_jobs.append({
                    "job_id": job_id,
                    "creator": hex(creator),
                    "reward": reward,
                    "asset_cid": asset_cid,
                    "min_reputation": min_reputation,
                })
                print(f"[Worker] Found available job {job_id} with reward {reward}, asset CID: {asset_cid}, min reputation: {min_reputation}")
                break  # Stop after finding the first available job

        except Exception as e:
            # Job might not exist, continue
            print(f"[Worker] Error checking job {job_id}: {e}")
            continue
            
    return available_jobs

async def submit_job_result(contract, job_id, result_cid):
    """Submit a result for a specific job"""
    # try:
        # Convert IPFS CID string to felt252
    cid_felt = string_to_felt252(result_cid)
    
    print(f"[Worker] Submitting result for job {job_id}, CID: {result_cid}, felt: {cid_felt}")

    return True  
        # Submit the result - try different methods for different starknet_py versions
        # try:
        #     # Method 1: Modern starknet_py (0.21.0+)
        #     call = await contract.functions["submit_result"].invoke_v1(job_id, cid_felt)
        #     await call.wait_for_acceptance()
        #     print(f"[Worker] Successfully submitted result for job {job_id} using invoke_v1")
        #     return True
        # except AttributeError:
        #     try:
        #         # Method 2: Older starknet_py with invoke
        #         call = await contract.functions["submit_result"].invoke(job_id, cid_felt)
        #         await call.wait_for_acceptance()
        #         print(f"[Worker] Successfully submitted result for job {job_id} using invoke")
        #         return True
        #     except AttributeError:
        #         try:
        #             # Method 3: Even older starknet_py with call
        #             call = contract.functions["submit_result"].prepare(job_id, cid_felt)
        #             result = await call.invoke()
        #             await result.wait_for_acceptance()
        #             print(f"[Worker] Successfully submitted result for job {job_id} using prepare/invoke")
        #             return True
        #         except Exception as e:
        #             print(f"[Worker] All submission methods failed: {e}")
        #             return False
                    
    # except Exception as e:
    #     print(f"[Worker] Error submitting result for job {job_id}: {e}")
    #     import traceback
    #     traceback.print_exc()
    #     return False

async def process_render_job(ipfs, job_id, asset_cid):
    """Process a complete rendering job: download .blend, render, upload result"""
    with tempfile.TemporaryDirectory() as temp_dir:
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

class IPFSClient:
    """Wrapper for IPFS operations with fallback to HTTP API"""
    
    def __init__(self, api_endpoint):
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
    
    def get(self, cid, target):
        """Download file from IPFS"""
        if self.client:
            try:
                return self.client.get(cid, target=target)
            except Exception as e:
                print(f"[Worker] ipfshttpclient.get failed: {e}, trying HTTP API fallback")
        
        # HTTP API fallback - try both POST (API) and GET (gateway) methods
        try:
            # Method 1: IPFS API (POST request)
            print(f"[Worker] Trying IPFS API download for CID: {cid}")
            response = requests.post(f"{self.http_url}/api/v0/get", params={"arg": cid}, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to target directory
            file_path = os.path.join(target, cid)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[Worker] Downloaded via IPFS API to: {file_path}")
            return {"Hash": cid}
            
        except Exception as e:
            print(f"[Worker] IPFS API download failed: {e}")
            
            # Method 2: IPFS Gateway (GET request)
            try:
                print(f"[Worker] Trying IPFS Gateway download for CID: {cid}")
                gateway_url = f"{IPFS_GATEWAY}/{cid}"
                response = requests.get(gateway_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Save to target directory
                file_path = os.path.join(target, cid)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"[Worker] Downloaded via IPFS Gateway to: {file_path}")
                return {"Hash": cid}
                
            except Exception as e2:
                print(f"[Worker] IPFS Gateway download also failed: {e2}")
                raise Exception(f"All download methods failed. API: {e}, Gateway: {e2}")
    
    def add(self, file_path):
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

async def main():
    print("[Worker] Starting Blender rendering worker...")
    print(f"[Worker] Blender path: {BLENDER_PATH}")
    
    # Check if required dependencies are available
    if not STARKNET_AVAILABLE:
        print("[Worker] ERROR: starknet_py is not properly installed")
        print("[Worker] Please run: pip install --force-reinstall starknet_py==0.21.0")
        return
    
    # Check if Blender is available
    try:
        result = subprocess.run([BLENDER_PATH, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
            print(f"[Worker] Blender found: {version_line}")
        else:
            print("[Worker] Warning: Blender not found or not working properly")
            print(f"[Worker] Error: {result.stderr}")
    except Exception as e:
        print(f"[Worker] Warning: Could not check Blender version: {e}")
    
    if JOB_REGISTRY_ADDRESS == 0:
        print("[Worker] No job registry address provided. Exiting.")
        return
    
    try:
        # Initialize clients with better error handling
        print("[Worker] Initializing StarkNet client...")
        client = FullNodeClient(node_url=STARKNET_RPC)
        
        print("[Worker] Initializing IPFS client...")
        ipfs = IPFSClient(IPFS_API)
        
        print("[Worker] Creating contract instance...")
        # Create contract instance with error handling
        contract = Contract(
            address=JOB_REGISTRY_ADDRESS,
            abi=CONTRACT_ABI,
            provider=client,
        )
        
        print(f"[Worker] Connected to job registry at {hex(JOB_REGISTRY_ADDRESS)}")
        print(f"[Worker] Connected to IPFS at {IPFS_API}")
        
        # For this demo, use a placeholder worker address
        # In production, this would be derived from the worker's wallet/account
        worker_address = int("0x1234567890abcdef1234567890abcdef12345678", 16)  # Placeholder
        print(f"[Worker] Worker address: {hex(worker_address)}")
        
        # Test contract connection
        try:
            print("[Worker] Testing contract connection...")
            test_job_response = await contract.functions["get_job_creator"].call(1)
            test_job = test_job_response.creator if hasattr(test_job_response, 'creator') else test_job_response
            print(f"[Worker] Contract connection successful, test job creator: {test_job}")
        except Exception as e:
            print(f"[Worker] Warning: Contract test failed: {e}")
        
        while True:
            try:
                # Check for available jobs
                print("[Worker] Polling for rendering jobs...")
                jobs = await check_for_jobs(contract, worker_address)
                
                if jobs:
                    # Process the first available job
                    job = jobs[0]
                    job_id = job["job_id"]
                    asset_cid = job["asset_cid"]
                    
                    print(f"[Worker] Taking render job {job_id} for asset CID: {asset_cid}")
                    
                    # Process the rendering job
                    result_cid = await process_render_job(ipfs, job_id, asset_cid)
                    
                    if result_cid:
                        # Submit the result
                        success = await submit_job_result(contract, job_id, result_cid)
                        
                        if success:
                            print(f"[Worker] Completed render job {job_id}")
                            # Notify frontend about completion
                            await notify_frontend(job_id, result_cid)
                        else:
                            print(f"[Worker] Failed to submit result for job {job_id}")
                    else:
                        print(f"[Worker] Failed to process render job {job_id}")

                    break
                else:
                    print("[Worker] No available rendering jobs found")
                
                # Wait before next polling cycle
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"[Worker] Error in main loop: {e}")
                await asyncio.sleep(5)
                
    except FileNotFoundError as e:
        if "core_structures.json" in str(e):
            print(f"[Worker] Missing starknet_py core file: {e}")
            print("[Worker] Please reinstall starknet_py:")
            print("[Worker]   pip uninstall starknet_py")
            print("[Worker]   pip install starknet_py==0.21.0")
        else:
            print(f"[Worker] File not found error: {e}")
    except Exception as e:
        print(f"[Worker] Initialization error: {e}")
        print(f"[Worker] Error type: {type(e).__name__}")
        import traceback
        print(f"[Worker] Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
    # print(f"[Worker] Error type: {type(e).__name__}")
    # import traceback
    # print(f"[Worker] Full traceback:")
    # traceback.print_exc()

# if __name__ == "__main__":
#     asyncio.run(main())
