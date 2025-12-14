#!/bin/bash

# The Graph Subgraph Setup Script for GalaxyRend

set -e

echo "📊 Setting up The Graph subgraph for GalaxyRend..."

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUBGRAPH_DIR="$SCRIPT_DIR"

cd "$SUBGRAPH_DIR"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not found. Please install Node.js 16+ and try again."
    exit 1
fi

# Check Node.js version
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 16 ]; then
    echo "❌ Node.js 16+ is required. Found version: $(node --version)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if contract ABI exists
CONTRACT_ABI_PATH="../contracts/job_registry/target/dev/galaxyrend_job_registry.contract_class.json"
if [ ! -f "$CONTRACT_ABI_PATH" ]; then
    echo "❌ Contract ABI not found at $CONTRACT_ABI_PATH"
    echo "Please compile your contract first by running:"
    echo "  cd ../contracts/job_registry && scarb build"
    exit 1
fi

# Create abis directory and copy ABI
echo "📋 Copying contract ABI..."
mkdir -p abis
cp "$CONTRACT_ABI_PATH" abis/JobRegistry.json

# Read contract address from deployment file
DEPLOYMENT_FILE="../contracts/job_registry/deployments/job_registry_sepolia.json"
if [ -f "$DEPLOYMENT_FILE" ]; then
    CONTRACT_ADDRESS=$(grep -o '"address": *"[^"]*"' "$DEPLOYMENT_FILE" | head -1 | cut -d'"' -f4)
    START_BLOCK=$(grep -o '"block_number": *[0-9]*' "$DEPLOYMENT_FILE" | head -1 | cut -d':' -f2 | tr -d ' ')
    
    if [ -n "$CONTRACT_ADDRESS" ] && [ -n "$START_BLOCK" ]; then
        echo "✅ Found contract deployment:"
        echo "   Address: $CONTRACT_ADDRESS"
        echo "   Start Block: $START_BLOCK"
        
        # Replace placeholders in subgraph.yaml
        sed -i "s/{{CONTRACT_ADDRESS}}/$CONTRACT_ADDRESS/g" subgraph.yaml
        sed -i "s/{{START_BLOCK}}/$START_BLOCK/g" subgraph.yaml
    else
        echo "⚠️  Could not parse contract address or start block from deployment file"
        echo "Please manually update subgraph.yaml with your contract details"
    fi
else
    echo "⚠️  Deployment file not found at $DEPLOYMENT_FILE"
    echo "Please deploy your contract first or manually update subgraph.yaml"
fi

echo ""
echo "✅ Subgraph setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Update subgraph.yaml if needed:"
echo "   - Contract address"
echo "   - Start block number"
echo "   - Network (starknet-sepolia or starknet-mainnet)"
echo ""
echo "2. Generate code and build:"
echo "   npm run codegen"
echo "   npm run build"
echo ""
echo "3. Deploy to The Graph:"
echo "   # For local development:"
echo "   npm run create-local"
echo "   npm run deploy-local"
echo ""
echo "   # For hosted service:"
echo "   npm run deploy"
echo ""
echo "4. Query your subgraph:"
echo "   GraphQL endpoint will be available after deployment"
echo ""

# Check if The Graph CLI is installed globally
if ! command -v graph &> /dev/null; then
    echo "💡 Tip: Install The Graph CLI globally for easier development:"
    echo "   npm install -g @graphprotocol/graph-cli"
fi

echo "🎉 The Graph subgraph is ready for GalaxyRend!"
