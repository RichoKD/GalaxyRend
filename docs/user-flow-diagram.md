# GalaxyRend User Flow Diagram

## Overview
GalaxyRend is a decentralized Blender rendering platform that connects job creators with workers through smart contracts on Starknet. This document outlines the complete user flows for different user types.

## System Architecture Flow

```
┌─────────────────┐    
| Backend(Fastapi)|    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │  Smart Contract │    │     Worker      │
│   (Next.js)     │◄──►│   (Starknet)    │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      IPFS       │    │   STRK Token    │    │     Blender     │
│   (Storage)     │    │   (Payment)     │    │   (Rendering)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## User Types and Primary Flows

### 1. Job Creator Flow

**Goal**: Submit a Blender rendering job and receive completed results

#### Phase 1: Setup and Authentication
```
1. Access Frontend (localhost:3000)
   ↓
2. Connect Starknet Wallet (ArgentX/Braavos)
   ↓
3. Verify Network Connection (Testnet/Mainnet)
   ↓
4. Check STRK Token Balance
```

#### Phase 2: Job Creation
```
5. Navigate to Job Creation Form
   ↓
6. Upload .blend File
   │ ├── File validation (.blend format)
   │ ├── Upload to IPFS
   │ └── Receive IPFS hash (CID)
   ↓
7. Configure Job Parameters
   │ ├── Set Reward Amount (STRK tokens)
   │ ├── Set Deadline (timestamp)
   │ ├── Add Description (optional)
   │ └── Set Minimum Worker Reputation (optional)
   ↓
8. Submit Transaction
   │ ├── Split IPFS CID into two felt252 parts
   │ ├── Call create_job() on smart contract
   │ ├── Escrow STRK tokens
   │ └── Wait for transaction confirmation
   ↓
9. Receive Job ID and Track Status
```

#### Phase 3: Job Monitoring
```
10. Monitor Job Dashboard
    ├── View job status: "open" → "assigned" → "completed"
    ├── Track worker assignment
    └── Receive notifications
    ↓
11. Review Completed Results
    ├── Download rendered files from IPFS
    ├── Rate worker quality (0-100 score)
    └── Release payment to worker
```

### 2. Worker Flow

**Goal**: Find and complete rendering jobs to earn STRK tokens

#### Phase 1: Worker Registration
```
1. Setup Worker Environment
   │ ├── Install Python dependencies
   │ ├── Configure Blender installation
   │ └── Setup IPFS node
   ↓
2. Register on Platform
   │ ├── Generate worker keypair
   │ ├── Upload worker info to IPFS
   │ ├── Call register_worker() on contract
   │ └── Wait for admin verification
   ↓
3. Verification Process (Admin Required)
   ├── Admin reviews worker credentials
   ├── Admin calls verify_worker()
   └── Worker status: verified = true
```

#### Phase 2: Job Discovery and Assignment
```
4. Poll for Available Jobs
   │ ├── Query contract for open jobs
   │ ├── Check eligibility requirements
   │ │   ├── Minimum reputation check
   │ │   ├── Worker verification status
   │ │   └── Capability requirements
   │ └── Filter suitable jobs
   ↓
5. Claim Job (Auto-assignment)
   │ ├── Call is_worker_eligible()
   │ ├── Auto-assign if eligible
   │ └── Update job status to "assigned"
```

#### Phase 3: Job Execution
```
6. Download Job Assets
   │ ├── Retrieve IPFS CID from contract
   │ ├── Download .blend file from IPFS
   │ └── Validate file integrity
   ↓
7. Execute Rendering
   │ ├── Load .blend file in Blender
   │ ├── Execute rendering process
   │ ├── Monitor progress and logs
   │ └── Generate output images/videos
   ↓
8. Upload Results
   │ ├── Upload rendered files to IPFS
   │ ├── Receive result IPFS CID
   │ └── Call submit_result() on contract
   ↓
9. Job Finalization
   ├── Contract validates submission
   ├── Quality scoring by job creator
   ├── Payment release to worker
   └── Reputation update
```

### 3. Administrator Flow

**Goal**: Manage platform integrity and worker verification

#### Admin Functions
```
1. Worker Verification
   │ ├── Review worker registration details
   │ ├── Validate credentials and capabilities
   │ └── Call verify_worker() to approve/reject
   ↓
2. Platform Monitoring
   │ ├── Monitor job completion rates
   │ ├── Track worker performance metrics
   │ └── Identify and address disputes
   ↓
3. Emergency Controls
   ├── Pause/unpause contract operations
   ├── Slash worker reputation for misconduct
   └── Resolve disputed jobs
```

## Detailed Technical Flow

### Smart Contract Interactions

#### Job Creation Flow
```
Frontend → IPFS Upload → Smart Contract
┌─────────────────────────────────────────┐
│ 1. uploadToIPFS(blendFile)              │
│    └── Returns: IPFS_CID                │
├─────────────────────────────────────────┤
│ 2. Split CID into felt252 parts         │
│    ├── part1 = CID[0:31]                │
│    └── part2 = CID[31:]                 │
├─────────────────────────────────────────┤
│ 3. create_job(part1, part2, reward,     │
│              deadline, min_reputation)  │
│    ├── Escrow STRK tokens               │
│    ├── Generate job_id                  │
│    └── Emit JobCreated event            │
└─────────────────────────────────────────┘
```

#### Worker Assignment Flow
```
Worker → Smart Contract → Backend API
┌─────────────────────────────────────────┐
│ 1. is_worker_eligible(worker, job_id)   │
│    ├── Check verification status        │
│    ├── Check reputation >= minimum      │
│    └── Returns: bool                    │
├─────────────────────────────────────────┤
│ 2. Auto-assignment (if eligible)        │
│    ├── Update job.worker = worker_addr  │
│    ├── Update job.status = "assigned"   │
│    └── Emit JobAssigned event           │
├─────────────────────────────────────────┤
│ 3. Backend API sync                     │
│    ├── POST /api/v1/jobs/{id}/assign    │
│    └── Update local database            │
└─────────────────────────────────────────┘
```

#### Result Submission Flow
```
Worker → IPFS → Smart Contract → Frontend
┌─────────────────────────────────────────┐
│ 1. Render .blend file                   │
│    └── Generate output files            │
├─────────────────────────────────────────┤
│ 2. Upload results to IPFS               │
│    └── Returns: result_CID              │
├─────────────────────────────────────────┤
│ 3. submit_result(job_id, result_CID)    │
│    ├── Update job with result CID       │
│    ├── Mark job as completed            │
│    └── Emit JobCompleted event          │
├─────────────────────────────────────────┤
│ 4. Notify frontend                      │
│    ├── POST /api/job-completed          │
│    └── Update UI with results           │
└─────────────────────────────────────────┘
```

## State Transitions

### Job States
```
[open] → [assigned] → [completed] → [finalized]
   ↓         ↓           ↓             ↓
[cancelled] [failed] [disputed] [payment_released]
```

### Worker States
```
[registered] → [verified] → [active] → [working]
     ↓            ↓          ↓           ↓
[pending]    [rejected] [suspended] [completed_job]
                                        ↓
                                [reputation_updated]
```

## Error Handling and Edge Cases

### Job Creator Scenarios
- **Insufficient STRK balance**: Show error before transaction
- **Invalid .blend file**: Validate file format before upload
- **IPFS upload failure**: Retry mechanism with user notification
- **Transaction failure**: Clear error messages with retry option
- **Job deadline expired**: Automatic refund mechanism

### Worker Scenarios
- **Network connectivity issues**: Graceful degradation and retry logic
- **Blender rendering failures**: Error reporting and job reassignment
- **IPFS download/upload failures**: Multiple IPFS gateway fallbacks
- **Reputation too low**: Clear eligibility requirements display

### System-Wide Scenarios
- **Smart contract paused**: User-friendly maintenance mode
- **High network congestion**: Gas estimation and retry logic
- **IPFS gateway failures**: Multiple gateway configuration

## Integration Points

### External Services
- **IPFS Network**: Decentralized file storage
- **Starknet RPC**: Blockchain interaction
- **Blender Engine**: 3D rendering execution
- **Web3 Wallets**: User authentication and signing

### Internal Components
- **Frontend (Next.js)**: User interface and wallet integration
- **Backend API (FastAPI)**: Job tracking and worker management
- **Smart Contracts (Cairo)**: Core business logic and payments
- **Worker Nodes (Python)**: Distributed rendering execution

## Performance Considerations

### Scalability Metrics
- **Job throughput**: Target 100+ concurrent jobs
- **Worker capacity**: Support 50+ active workers
- **File size limits**: .blend files up to 100MB
- **Rendering timeouts**: Configurable per job complexity

### Optimization Strategies
- **IPFS clustering**: Multiple nodes for redundancy
- **Contract batching**: Group multiple operations
- **Frontend caching**: Reduce API calls with smart caching
- **Worker load balancing**: Distribute jobs efficiently

This user flow provides a comprehensive guide for all stakeholders interacting with the GalaxyRend platform, ensuring clear understanding of processes, technical requirements, and system behavior.