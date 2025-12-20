# Worker Authorization and Reputation System

## Overview

The GalaxyRend Worker Authorization and Reputation System provides a comprehensive framework for verifying worker nodes and tracking their performance through a reputation-based scoring mechanism. This system ensures quality control and incentivizes good performance while providing protection against malicious actors.

## Features

### 1. Worker Registration
- Workers must register with the system by providing worker information (stored on IPFS)
- Registration includes capabilities, hardware specs, and contact information
- Initial reputation score of 500/1000 is assigned upon registration

### 2. Worker Verification
- Only contract owners can verify workers
- Verification is required before workers can accept jobs
- Verified workers receive a reputation boost (minimum 600)
- Unverified workers have their reputation reduced

### 3. Reputation System
- Reputation scores range from 1 to 1000
- Reputation affects job eligibility
- Different job creators can set minimum reputation requirements
- Reputation changes based on job performance

### 4. Job Eligibility Checks
- Workers must be registered and verified
- Workers must meet minimum reputation requirements for specific jobs
- Workers with high failure rates (>30%) are ineligible
- Real-time eligibility checking before job assignment

## Smart Contract Functions

### Registration Functions
```cairo
fn register_worker(ref self: ContractState, worker_info_cid: felt252)
fn verify_worker(ref self: ContractState, worker: ContractAddress, verification_status: bool)
```

### Reputation Management
```cairo
fn update_worker_reputation(ref self: ContractState, worker: ContractAddress, job_id: felt252, quality_score: u8)
fn slash_worker_reputation(ref self: ContractState, worker: ContractAddress, slash_amount: u16)
```

### Job Creation with Requirements
```cairo
fn create_job_with_requirements(ref self: ContractState, asset_cid_part1: felt252, asset_cid_part2: felt252, reward_amount: u256, deadline_timestamp: u64, min_reputation: u16) -> felt252
```

### Query Functions
```cairo
fn get_worker_status(self: @ContractState, worker: ContractAddress) -> (bool, u16, u32, u32)
fn is_worker_eligible(self: @ContractState, worker: ContractAddress, job_id: felt252) -> bool
fn get_minimum_reputation_for_job(self: @ContractState, job_id: felt252) -> u16
```

## Reputation Scoring

### Quality Score Mapping
- **90-100 points**: Excellent work (+20 reputation)
- **75-89 points**: Good work (+10 reputation)
- **60-74 points**: Acceptable work (+5 reputation)
- **40-59 points**: Poor work (no change)
- **0-39 points**: Very poor work (-15 reputation)

### Performance Tracking
- **Jobs Completed**: Successfully completed jobs
- **Jobs Failed**: Failed or poor quality jobs
- **Failure Rate**: Calculated as (failed / total) * 100
- **Eligibility Threshold**: Workers with >30% failure rate become ineligible

## Storage Structure

```cairo
// Worker Authorization Storage
worker_verified: Map<ContractAddress, bool>                // Verification status
worker_reputation: Map<ContractAddress, u16>               // Reputation score (0-1000)
worker_jobs_completed: Map<ContractAddress, u32>           // Successful jobs count
worker_jobs_failed: Map<ContractAddress, u32>              // Failed jobs count
worker_info_cid: Map<ContractAddress, felt252>             // IPFS CID for worker info
worker_registration_time: Map<ContractAddress, u64>        // Registration timestamp
job_minimum_reputation: Map<felt252, u16>                  // Per-job reputation requirements
job_quality_scores: Map<felt252, u8>                       // Quality ratings for completed jobs
```

## Events

### Worker Registration Events
```cairo
WorkerRegistered {
    worker: ContractAddress,
    info_cid: felt252,
    registration_time: u64,
}

WorkerVerified {
    worker: ContractAddress,
    verified: bool,
    verifier: ContractAddress,
}
```

### Reputation Events
```cairo
ReputationUpdated {
    worker: ContractAddress,
    job_id: felt252,
    old_reputation: u16,
    new_reputation: u16,
    quality_score: u8,
}

ReputationSlashed {
    worker: ContractAddress,
    old_reputation: u16,
    new_reputation: u16,
    slash_amount: u16,
    reason: felt252,
}
```

## Python Worker Integration

### Authorization Checks
The Python worker now includes:
- Worker registration status checking
- Verification status validation
- Job eligibility verification before accepting jobs
- Reputation and performance tracking

### Key Functions
```python
async def check_worker_registration(contract, worker_address)
async def register_worker_if_needed(contract, worker_address)
async def check_job_eligibility(contract, worker_address, job_id)
async def check_for_jobs(contract, worker_address, max_job_id=5)
```

## Security Features

1. **Access Control**: Only contract owners can verify workers and slash reputation
2. **Reentrancy Protection**: All state-changing functions use reentrancy guards
3. **Pausability**: System can be paused in emergencies
4. **Input Validation**: All inputs are validated for safety
5. **Reputation Bounds**: Reputation scores are bounded between 1-1000

## Usage Flow

1. **Worker Registration**:
   ```python
   # Worker uploads info to IPFS and registers
   await contract.functions["register_worker"].invoke(worker_info_cid)
   ```

2. **Admin Verification**:
   ```cairo
   self.verify_worker(worker_address, true);
   ```

3. **Job Creation with Requirements**:
   ```cairo
   let job_id = self.create_job_with_requirements(
       asset_cid_part1, asset_cid_part2, 
       reward_amount, deadline, 
       600_u16  // Minimum reputation required
   );
   ```

4. **Worker Job Application**:
   ```python
   # Check eligibility before applying
   eligible = await contract.functions["is_worker_eligible"].call(worker_address, job_id)
   if eligible:
       await contract.functions["submit_result"].invoke(job_id, result_cid_part1, result_cid_part2)
   ```

5. **Performance Rating**:
   ```cairo
   self.update_worker_reputation(worker_address, job_id, 85_u8);  // 85% quality score
   ```

## Benefits

- **Quality Assurance**: Only verified, reputable workers can take jobs
- **Performance Incentives**: Good work is rewarded with higher reputation
- **Risk Mitigation**: Poor performers are naturally filtered out
- **Transparency**: All reputation changes are recorded on-chain
- **Flexibility**: Job creators can set their own quality requirements

This system creates a self-regulating marketplace where quality workers are rewarded and poor performers are discouraged, leading to better overall service quality.
