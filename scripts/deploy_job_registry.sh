#!/bin/bash

# GalaxyRend Job Registry Deployment Script
# Usage: ./deploy_job_registry.sh [network] [account]
# Example: ./deploy_job_registry.sh sepolia stark1

set -e

# Default values
NETWORK=${1:-"dev_net"}
ACCOUNT=${2:-"account-1"}
DECLARE=${3:-false}
BUILD_CONTRACT=${4:-false}
# RELEASE=${4:-false}
TOKEN_ADDRESS=${5:-"0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"} # Sepolia STRK

# echo "[INIT] Waiting for StarkNet Devnet..."
# until curl -s $URL/is_alive > /dev/null; do
#     sleep 2
# done

CLASS_HASH=""

echo "Foundry version: $(sncast --version)"

echo "🚀 Deploying Job Registry Contract..."
echo "Network: $NETWORK"
echo "Account: $ACCOUNT"

# Change to contract directory
cd "$(dirname "$0")/../contracts/job_registry_v2"

if [ "$BUILD_CONTRACT" = true ]; then
    # Build the contract first
    echo "📦 Building contract..."
    if [ "$NETWORK" = "mainnet" ]; then
        scarb build --release
    else
        scarb build
    fi
fi

# Check if the compiled contract exists
if [ ! -f "target/dev/galaxyrend_job_registry_v2_JobRegistryV2.contract_class.json" ]; then
    echo "❌ Contract compilation failed - contract class file not found"
    exit 1
fi

echo "✅ Contract built successfully"


echo "🔍 Validating RPC connection..."
if [ "$NETWORK" = "dev_net" ]; then
    RPC_URL="http://localhost:5050"
    # Test devnet connection
    if ! curl -s -f "$RPC_URL/is_alive" > /dev/null; then
        echo "❌ Starknet devnet is not running. Please start it with:"
        echo "starknet-devnet --host 0.0.0.0 --port 5050"
        exit 1
    fi
elif [ "$NETWORK" = "sepolia" ]; then
    RPC_URL="https://api.cartridge.gg/x/starknet/sepolia"
    CLASS_HASH="0x282f8cb7a7f399a536b67f85715848fa9138be08d174faa0ea8af473d36fccb"
elif [ "$NETWORK" = "mainnet" ]; then
    RPC_URL="https://api.cartridge.gg/x/starknet/mainnet"
    CLASS_HASH=""
fi

# Test RPC connection
if ! curl -s -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"starknet_blockNumber","params":[],"id":1}' \
    "$RPC_URL" > /dev/null; then
    echo "❌ Cannot connect to RPC endpoint: $RPC_URL"
    exit 1
fi

echo "✅ RPC connection validated"



if [ "$DECLARE" = true ]; then
    # Deploy the contract
echo "🔧 Declaring contract..."
DECLARE_OUTPUT=$(sncast --profile $ACCOUNT declare --contract-name JobRegistryV2 2>&1)

# Check if contract is already declared
    if echo "$DECLARE_OUTPUT" | grep -q "already declared"; then
        echo "ℹ️  Contract is already declared, extracting class hash from error message..."
        # Extract class hash from "already declared" error message
        CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -o "0x[a-fA-F0-9]\{64\}" | head -1)
        if [ -n "$CLASS_HASH" ]; then
            echo "✅ Found existing class hash: $CLASS_HASH"
        else
            echo "❌ Could not extract class hash from already declared error:"
            echo "$DECLARE_OUTPUT"

            # Check deploment file
            DEPLOYMENT_FILE="deployments/job_registry_v2_${NETWORK}.json"
            if [ -f "$DEPLOYMENT_FILE" ]; then
                echo "⚠️  Deployment file already exists for network '$NETWORK': $DEPLOYMENT_FILE"
                CLASS_HASH=$(grep -o '"class_hash": "[^"]*"' "$DEPLOYMENT_FILE" | cut -d'"' -f4)
                echo "Using existing class hash: $CLASS_HASH"
            else
                exit 1
            fi
        fi
    elif echo "$DECLARE_OUTPUT" | grep -q "error"; then
        echo "❌ Contract declaration failed:"
        echo "$DECLARE_OUTPUT"
        exit 1
    else
        # Extract class hash from successful declare output (new format in sncast 0.52.0)
        # Look for "Class Hash: 0x..." pattern
        CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep "Class Hash:" | grep -o "0x[a-fA-F0-9]*" | head -1)
        
        if [ -z "$CLASS_HASH" ]; then
            # Try old format: "class_hash: 0x..."
            CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -o "class_hash: 0x[a-fA-F0-9]*" | cut -d' ' -f2)
        fi
        
        if [ -z "$CLASS_HASH" ]; then
            # Try extracting any 64-character hex string (class hash format)
            CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -o "0x[a-fA-F0-9]\{63,64\}" | head -1)
        fi
        
        if [ -z "$CLASS_HASH" ]; then
            echo "❌ Could not extract class hash from declare output:"
            echo "$DECLARE_OUTPUT"
            exit 1
        fi
        
        echo "✅ Contract declared successfully"
        echo "Class Hash: $CLASS_HASH"
    fi
fi

# Deploy the contract with constructor arguments
echo "🚀 Deploying contract... $ACCOUNT : $CLASS_HASH"

# Get the account address for the owner parameter
ACCOUNT_LIST_OUTPUT=$(sncast account list 2>/dev/null)
ACCOUNT_ADDRESS=$(echo "$ACCOUNT_LIST_OUTPUT" | grep -A 5 "^- $ACCOUNT:" | grep "address:" | grep -o "0x[a-fA-F0-9]*")

if [ -z "$ACCOUNT_ADDRESS" ]; then
    echo "❌ Could not get account address for $ACCOUNT"
    echo "Available accounts:"
    echo "$ACCOUNT_LIST_OUTPUT"
    exit 1
fi

echo "📋 Constructor Parameters:"
echo "  Owner Address: $ACCOUNT_ADDRESS"
echo "  Token Address: $TOKEN_ADDRESS"

# Deploy with constructor arguments: owner, reward_token_address
DEPLOY_OUTPUT=$(sncast --profile $ACCOUNT deploy --class-hash $CLASS_HASH --constructor-calldata $ACCOUNT_ADDRESS $TOKEN_ADDRESS) #2>&1)
echo "$DEPLOY_OUTPUT"
if echo "$DEPLOY_OUTPUT" | grep -q "error"; then
    echo "❌ Contract deployment failed:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

# Extract contract address from deploy output
CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -o "contract_address: 0x[a-fA-F0-9]*" | cut -d' ' -f2)

if [ -z "$CONTRACT_ADDRESS" ]; then
    # Try alternative extraction method
    CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -o "0x[a-fA-F0-9]\{64\}" | head -1)
fi

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Could not extract contract address from deploy output:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

echo "✅ Contract deployed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "====================="
echo "Network: $NETWORK"
echo "Account: $ACCOUNT"
echo "Class Hash: $CLASS_HASH"
echo "Contract Address: $CONTRACT_ADDRESS"
echo ""

# Save deployment info to a file
DEPLOYMENT_FILE="deployments/job_registry_v2_${NETWORK}.json"
mkdir -p deployments

cat > "$DEPLOYMENT_FILE" << EOF
{
  "network": "$NETWORK",
  "account": "$ACCOUNT",
  "contract_name": "JobRegistryV2",
  "class_hash": "$CLASS_HASH",
  "contract_address": "$CONTRACT_ADDRESS",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "abi_path": "target/dev/galaxyrend_job_registry_JobRegistryV2.contract_class.json"
}
EOF

echo "💾 Deployment info saved to: $DEPLOYMENT_FILE"

# Update worker .env file with deployment info
WORKER_ENV_FILE="../../worker/src/.env"
echo ""
echo "📝 Updating worker.env file..."

# Determine RPC URL based on network
if [ "$NETWORK" = "sepolia" ]; then
    RPC_URL="https://api.cartridge.gg/x/starknet/sepolia"
elif [ "$NETWORK" = "mainnet" ]; then
    RPC_URL="https://api.cartridge.gg/x/starknet/mainnet"
else
    RPC_URL="http://localhost:5050"  # devnet default
fi


# Create worker/src directory if it doesn't exist
# mkdir -p worker/src

cat > "$WORKER_ENV_FILE" << EOF
# GalaxyRend Worker Environment Variables
# Auto-generated by deployment script on $(date -u +%Y-%m-%dT%H:%M:%SZ)

# Starknet Configuration
STARKNET_RPC=$RPC_URL
JOB_REGISTRY_ADDRESS=$CONTRACT_ADDRESS

# IPFS Configuration  
IPFS_API=http://127.0.0.1:5001
IPFS_GATEWAY=http://127.0.0.1:8080/ipfs

# Blender Configuration
BLENDER_PATH=blender

# Worker Configuration
WORKER_POLL_INTERVAL=10
MAX_JOB_ID=100
EOF

echo "✅ Worker .env file updated: $WORKER_ENV_FILE"

# Update frontend .env.local file with deployment info
FRONTEND_ENV_FILE="../../frontend/.env.local"
echo ""
echo "📝 Updating frontend .env.local file..."

cat > "$FRONTEND_ENV_FILE" << EOF

NEXT_PUBLIC_STARKNET_RPC=$RPC_URL
NEXT_PUBLIC_JOB_REGISTRY_ADDRESS=$CONTRACT_ADDRESS
NEXT_PUBLIC_IPFS_GATEWAY=http://localhost:8080/ipfs/
NEXT_PUBLIC_IPFS_API=http://localhost:5001
EOF

echo "✅ Frontend .env.local file updated: $FRONTEND_ENV_FILE"
echo ""

# Run the setup script to initialize the contract
echo "🔧 Running contract setup..."
# cd "$(dirname "$0")/../contracts/job_registry"
# cd "$(dirname "$0")"
echo "Current directory: $(pwd)"
cd "../../scripts"
echo "Current directory: $(pwd)"

./setup_contract.sh $NETWORK $CONTRACT_ADDRESS $TOKEN_ADDRESS $ACCOUNT

echo ""
echo "🎉 Deployment and setup completed successfully!"
