#!/bin/bash

# Post-deployment setup script for GalaxyRend Job Registry with Worker Authorization
# Usage: ./setup_contract.sh [network] [contract_address] [token_address] [account]

set -e

# Default values
NETWORK=${1:-"sepolia"}
CONTRACT_ADDRESS=${2:-""}
TOKEN_ADDRESS=${3:-"0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"}  # Sepolia STRK
ACCOUNT=${4:-"stark1"}

if [ -z "$CONTRACT_ADDRESS" ]; then
    # Try to read from deployment file
    DEPLOYMENT_FILE="../contracts/job_registry_v2/deployments/job_registry_v2_${NETWORK}.json"
    if [ -f "$DEPLOYMENT_FILE" ]; then
        CONTRACT_ADDRESS=$(grep -o '"contract_address": "[^"]*"' "$DEPLOYMENT_FILE" | cut -d'"' -f4)
        echo "📖 Read contract address from deployment file: $CONTRACT_ADDRESS"
    else
        echo "❌ No contract address provided and no deployment file found"
        echo "Usage: ./setup_contract.sh [network] [contract_address] [token_address] [account]"
        exit 1
    fi
fi

echo "🔧 Setting up Job Registry Contract with Worker Authorization..."
echo "Network: $NETWORK"
echo "Contract: $CONTRACT_ADDRESS"
echo "Token: $TOKEN_ADDRESS"
echo "Account: $ACCOUNT"
echo ""

cd "$(dirname "$0")/../contracts/job_registry_v2"

# Step 1: Test basic contract functions
echo "1️⃣ Testing contract connectivity..."
JOB_COUNTER=$(sncast --profile $ACCOUNT call --contract-address $CONTRACT_ADDRESS --function get_job_counter 2>&1)

if echo "$JOB_COUNTER" | grep -q "error"; then
    echo "❌ Failed to read job counter:"
    echo "$JOB_COUNTER"
    exit 1
else
    echo "✅ Contract is accessible - Current job counter: $JOB_COUNTER"
fi

echo ""

# Step 2: Set up token approval for testing
echo "2️⃣ Setting up token approval for testing..."
echo "Approving 1000 STRK tokens for the contract to spend..."

APPROVE_OUTPUT=$(sncast --profile $ACCOUNT invoke --contract-address $TOKEN_ADDRESS --function approve --calldata $CONTRACT_ADDRESS 1000000000000000000000 0 2>&1)

if echo "$APPROVE_OUTPUT" | grep -q "error"; then
    echo "❌ Token approval failed:"
    echo "$APPROVE_OUTPUT"
    
    # Check if it's a known recoverable error
    if echo "$APPROVE_OUTPUT" | grep -q "already approved\|insufficient allowance"; then
        echo "ℹ️  Token approval might already be set"
    else
        echo "⚠️  Continuing without approval - you may need to approve manually for job creation"
    fi
else
    echo "✅ Token approval successful"
fi

echo ""

# # Step 3: Register and verify a test worker
# echo "3️⃣ Setting up test worker registration..."

# # Get account address for worker registration
# ACCOUNT_LIST_OUTPUT=$(sncast account list 2>/dev/null)
# TEST_WORKER_ADDRESS=$(echo "$ACCOUNT_LIST_OUTPUT" | grep -A 5 "^- $ACCOUNT:" | grep "address:" | grep -o "0x[a-fA-F0-9]*")

# if [ -z "$TEST_WORKER_ADDRESS" ]; then
#     echo "❌ Could not get worker address for $ACCOUNT"
#     echo "Skipping worker setup..."
# else
#     echo "Test worker address: $TEST_WORKER_ADDRESS"
    
#     # Check if worker is already registered
#     WORKER_STATUS=$(sncast --profile $ACCOUNT call --contract-address $CONTRACT_ADDRESS --function get_worker_status --calldata $TEST_WORKER_ADDRESS 2>&1)
    
#     if echo "$WORKER_STATUS" | grep -q "error"; then
#         echo "❌ Failed to check worker status:"
#         echo "$WORKER_STATUS"
#     else
#         echo "✅ Worker status checked: $WORKER_STATUS"
        
#         # Register worker if not already registered
#         echo "Registering test worker with sample info..."
#         REGISTER_OUTPUT=$(sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function register_worker --calldata 0x516d576f726b6572496e666f313233 2>&1)
        
#         if echo "$REGISTER_OUTPUT" | grep -q "error"; then
#             if echo "$REGISTER_OUTPUT" | grep -q "already registered"; then
#                 echo "ℹ️  Worker already registered"
#             else
#                 echo "❌ Worker registration failed:"
#                 echo "$REGISTER_OUTPUT"
#             fi
#         else
#             echo "✅ Worker registered successfully"
#         fi
        
#         # Verify the worker (only owner can do this)
#         echo "Verifying test worker..."
#         VERIFY_OUTPUT=$(sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function verify_worker --calldata $TEST_WORKER_ADDRESS 1 2>&1)
        
#         if echo "$VERIFY_OUTPUT" | grep -q "error"; then
#             if echo "$VERIFY_OUTPUT" | grep -q "Only owner"; then
#                 echo "ℹ️  Only contract owner can verify workers"
#                 echo "ℹ️  Use the owner account to verify workers"
#             else
#                 echo "❌ Worker verification failed:"
#                 echo "$VERIFY_OUTPUT"
#             fi
#         else
#             echo "✅ Worker verified successfully"
#         fi
#     fi
# fi

echo ""

# Step 4: Test creating a job with worker requirements
# echo "4️⃣ Testing job creation with worker requirements..."

# # Create a test job with minimum reputation requirement
# echo "Creating a test job with asset CID 'QmTestAsset123'..."
# # Convert CID to felt252 parts (simplified for demo)
# ASSET_CID_PART1="0x516d546573744173736574313233"  # "QmTestAsset123" encoded
# ASSET_CID_PART2="0x0"  # Empty second part
# REWARD_AMOUNT_LOW="1000000000000000000"  # 1 token (low part of u256)
# REWARD_AMOUNT_HIGH="0"  # High part of u256
# DEADLINE=$(($(date +%s) + 86400))  # 24 hours from now
# MIN_REPUTATION="400"  # Minimum reputation required

# CREATE_JOB_OUTPUT=$(sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function create_job_with_requirements --calldata $ASSET_CID_PART1 $ASSET_CID_PART2 $REWARD_AMOUNT_LOW $REWARD_AMOUNT_HIGH $DEADLINE $MIN_REPUTATION 2>&1)

# if echo "$CREATE_JOB_OUTPUT" | grep -q "error"; then
#     echo "❌ Job creation failed:"
#     echo "$CREATE_JOB_OUTPUT"
    
#     # Try creating a simple job without requirements
#     echo "Trying simple job creation..."
#     SIMPLE_JOB_OUTPUT=$(sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function create_job --calldata $ASSET_CID_PART1 $ASSET_CID_PART2 $REWARD_AMOUNT_LOW $REWARD_AMOUNT_HIGH $DEADLINE 2>&1)
    
#     if echo "$SIMPLE_JOB_OUTPUT" | grep -q "error"; then
#         echo "❌ Simple job creation also failed:"
#         echo "$SIMPLE_JOB_OUTPUT"
#     else
#         echo "✅ Simple job created successfully"
#     fi
# else
#     echo "✅ Job with requirements created successfully"
# fi

# echo ""

# Step 5: Test worker authorization functions
# echo "5️⃣ Testing worker authorization functions..."

# if [ -n "$TEST_WORKER_ADDRESS" ]; then
#     # Test worker eligibility for job 1
#     echo "Checking worker eligibility for job 1..."
#     ELIGIBILITY_OUTPUT=$(sncast --profile $ACCOUNT call --contract-address $CONTRACT_ADDRESS --function is_worker_eligible --calldata $TEST_WORKER_ADDRESS 1 2>&1)
    
#     if echo "$ELIGIBILITY_OUTPUT" | grep -q "error"; then
#         echo "❌ Failed to check worker eligibility:"
#         echo "$ELIGIBILITY_OUTPUT"
#     else
#         echo "✅ Worker eligibility check: $ELIGIBILITY_OUTPUT"
#     fi
    
#     # Check minimum reputation for job 1
#     echo "Checking minimum reputation requirement for job 1..."
#     MIN_REP_OUTPUT=$(sncast --profile $ACCOUNT call --contract-address $CONTRACT_ADDRESS --function get_minimum_reputation_for_job --calldata 1 2>&1)
    
#     if echo "$MIN_REP_OUTPUT" | grep -q "error"; then
#         echo "❌ Failed to check minimum reputation:"
#         echo "$MIN_REP_OUTPUT"
#     else
#         echo "✅ Minimum reputation for job 1: $MIN_REP_OUTPUT"
#     fi
# fi

echo ""
echo ""
echo "🎉 Contract setup completed!"
echo ""
echo "📋 Summary:"
echo "=========="
echo "Contract Address: $CONTRACT_ADDRESS"
echo "Token Address: $TOKEN_ADDRESS"
echo "Network: $NETWORK"
# echo "Test Worker: $TEST_WORKER_ADDRESS"
echo ""
echo "🔗 Next steps:"
echo "1. Create a job: sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function create_job --calldata <asset_cid_part1> <asset_cid_part2> <reward_low> <reward_high> <deadline>"
echo "2. Create job with requirements: sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function create_job_with_requirements --calldata <asset_cid_part1> <asset_cid_part2> <reward_low> <reward_high> <deadline> <min_reputation>"
echo "3. Register a worker: sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function register_worker --calldata <worker_info_cid>"
echo "4. Verify a worker (owner only): sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function verify_worker --calldata <worker_address> <true/false>"
echo "5. Check worker status: sncast --profile $ACCOUNT call --contract-address $CONTRACT_ADDRESS --function get_worker_status --calldata <worker_address>"
echo "6. Submit job result: sncast --profile $ACCOUNT invoke --contract-address $CONTRACT_ADDRESS --function submit_result --calldata <job_id> <result_cid_part1> <result_cid_part2>"
echo ""
echo "📚 Worker Authorization Features:"
echo "- Workers must register before taking jobs"
echo "- Only verified workers can accept jobs"
echo "- Reputation system (0-1000) affects job eligibility"
echo "- Job creators can set minimum reputation requirements"
echo "- Performance tracking and quality scoring"
