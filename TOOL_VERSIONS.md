# GalaxyRend Tool Versions

This document lists all the tools and their versions used in the GalaxyRend project.

## Core Development Tools

### Cairo/Starknet Development
- **Scarb**: 2.11.4 (c0ef5ec6a 2025-04-09)
- **Cairo**: 2.11.4 (https://crates.io/crates/cairo-lang-compiler/2.11.4)
- **Sierra**: 1.7.0
- **snforge**: 0.43.1 (testing framework)
- **sncast**: 0.43.1 (contract interaction CLI)

### Runtime Environments
- **Node.js**: v22.15.1
- **npm**: 10.9.2
- **Python**: 3.12.3
- **Blender**: 4.0.2

## Frontend Dependencies

### Framework & Core
- **Next.js**: Latest (via package.json)
- **React**: Latest (via Next.js)
- **TypeScript**: Latest (via Next.js)

### Starknet Integration
- **@starknet-react/core**: ^4.0.4
- **@starknet-react/chains**: ^4.0.4
- **@tanstack/react-query**: ^5.85.3

### UI Components
- **@radix-ui/react-label**: ^2.1.7
- **@radix-ui/react-select**: ^2.2.6
- **@radix-ui/react-slot**: ^1.2.3
- **class-variance-authority**: ^0.7.1
- **clsx**: ^2.1.1
- **@hookform/resolvers**: ^5.2.1

## Worker Dependencies

### Core Python Packages
- **starknet_py**: >=0.21.0,<0.28.0
- **ipfshttpclient**: >=0.8.0a2
- **requests**: >=2.25.0
- **aiohttp**: >=3.8.0
- **Pillow**: >=10.0.0

## Infrastructure Tools

### IPFS
- **Docker**
- **IPFS Node**: Compatible with HTTP API v0
- **Gateway**: HTTP access on port 8080

### Blender Rendering
- **Blender**: 4.0.2 (headless mode)
- **EEVEE Engine**: Default render engine
- **PNG Output**: Image format

## Development Environment

### Operating System
- **Linux**: Compatible (tested on Ubuntu/Debian)
- **Shell**: bash

### Package Managers
- **Scarb**: Cairo package manager
- **npm**: JavaScript package manager  
- **pip**: Python package manager

## Network Configuration

### Starknet Networks
- **Sepolia Testnet**: https://api.cartridge.gg/x/starknet/sepolia
- **Mainnet**: https://api.cartridge.gg/x/starknet/mainnet
- **Local Devnet**: http://localhost:5050

### Contract Addresses
- **STRK Token (Sepolia)**: 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d
- **Job Registry (Sepolia)**: 0x03103f3d37047b8bd0680c22a9b8d9502d5d1e34ab12259659dea2f6354ad7e8

## Version Compatibility

### Critical Dependencies
- Cairo and Scarb versions must match for compilation
- snforge and sncast versions should match Scarb
- starknet_py version must be compatible with Cairo contract compilation
- Node.js version should support latest Next.js features

### Testing Compatibility
- All Cairo contracts tested with snforge 0.43.1
- Frontend tested with Node.js v22.15.1
- Worker tested with Python 3.12.3
- Blender rendering tested with version 4.0.2

## Installation Commands

### Cairo Development
```bash
# Install Scarb (includes Cairo)
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh

# Install Starknet Foundry (snforge, sncast)
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh
```

### Frontend
```bash
cd frontend
npm install
```

### Worker
```bash
cd worker
python3 -m venv venv
pip install -r requirements.txt
```
### IPFS
```bash
cd infra
docker compose up --build
```
### Blender
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install blender

# Or download from https://www.blender.org/download/
```

---

**Last Updated**: August 23, 2025  
**Project Version**: GalaxyRend v0.2.0
