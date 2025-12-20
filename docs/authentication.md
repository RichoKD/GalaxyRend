# GalaxyRend Authentication System

## Overview

The GalaxyRend authentication system provides secure, decentralized authentication using StarkNet wallet signatures and JWT tokens. This implementation supports worker registration, verification, and role-based access control.

## Architecture

### Components

1. **StarkNet Authenticator** (`app/auth/starknet_auth.py`)
   - Generates authentication challenges
   - Verifies wallet signatures
   - Manages challenge lifecycle

2. **JWT Handler** (`app/auth/jwt_handler.py`)
   - Creates and verifies JWT tokens
   - Manages token expiration
   - Supports access and refresh tokens

3. **Authentication Dependencies** (`app/auth/dependencies.py`)
   - FastAPI dependencies for route protection
   - Role-based access control
   - Current user extraction

4. **Authentication Routes** (`app/auth/routes.py`)
   - API endpoints for authentication flow
   - Challenge generation and verification
   - Token management

5. **Authentication Schemas** (`app/schemas/auth.py`)
   - Pydantic models for request/response validation
   - Type safety for authentication data

## Authentication Flow

### 1. Challenge Generation
```http
POST /api/v1/auth/challenge
Content-Type: application/json

{
  "address": "0x1234567890abcdef..."
}
```

**Response:**
```json
{
  "message": "GalaxyRend Authentication\\nAddress: 0x1234...\\nTimestamp: 1693834567\\nNonce: abc123...",
  "timestamp": "1693834567",
  "nonce": "abc123def456",
  "expires_at": "1693834867"
}
```

### 2. Wallet Signature
The frontend prompts the user to sign the challenge message using their StarkNet wallet (ArgentX, Braavos, etc.).

### 3. Authentication
```http
POST /api/v1/auth/authenticate
Content-Type: application/json

{
  "address": "0x1234567890abcdef...",
  "message": "GalaxyRend Authentication\\n...",
  "signature": ["0x1a2b3c...", "0x4d5e6f..."],
  "timestamp": 1693834567
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "worker": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "address": "0x1234567890abcdef...",
    "verified": true,
    "reputation": 750,
    "is_admin": false,
    ...
  }
}
```

### 4. Authenticated Requests
Include the access token in the Authorization header:
```http
GET /api/v1/workers/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. Token Refresh
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/challenge` - Generate authentication challenge
- `POST /api/v1/auth/authenticate` - Authenticate with signed challenge
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/verify-token` - Verify token validity
- `POST /api/v1/auth/logout` - Logout (invalidate tokens)
- `GET /api/v1/auth/me` - Get current user information

### Protected Endpoints
- `PUT /api/v1/workers/{address}` - Update worker (own profile or admin)
- `POST /api/v1/workers/{address}/verify` - Verify worker (admin only)

## Security Features

### JWT Token Security
- **Algorithm**: HS256
- **Access Token Expiry**: 60 minutes (configurable)
- **Refresh Token Expiry**: 7 days (configurable)
- **Secret Key**: Configurable via environment variables

### Challenge Security
- **Expiry**: 5 minutes
- **Nonce**: Random 16-byte hex string
- **Timestamp**: Unix timestamp for replay protection
- **Message Format**: Human-readable with structured data

### Role-Based Access Control
- **Worker**: Basic authenticated user
- **Verified Worker**: Worker verified by admin
- **Admin**: Worker with administrative privileges

## Configuration

### Environment Variables
```env
# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# General Security
SECRET_KEY=your-general-secret-key-here
```

### Dependencies
Required packages in `requirements.txt`:
```
python-jose[cryptography]==3.3.0
fastapi==0.104.1
starknet-py==0.21.0
```

## Usage Examples

### Frontend Integration (JavaScript)
```javascript
// 1. Generate challenge
const challengeResponse = await fetch('/api/v1/auth/challenge', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ address: walletAddress })
});
const challenge = await challengeResponse.json();

// 2. Sign challenge with wallet
const signature = await wallet.signMessage(challenge.message);

// 3. Authenticate
const authResponse = await fetch('/api/v1/auth/authenticate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    address: walletAddress,
    message: challenge.message,
    signature: signature,
    timestamp: parseInt(challenge.timestamp)
  })
});
const authData = await authResponse.json();

// 4. Store tokens
localStorage.setItem('access_token', authData.access_token);
localStorage.setItem('refresh_token', authData.refresh_token);

// 5. Use in subsequent requests
const response = await fetch('/api/v1/workers/me', {
  headers: {
    'Authorization': `Bearer ${authData.access_token}`
  }
});
```

### FastAPI Route Protection
```python
from app.auth.dependencies import require_authenticated_worker, require_admin_worker

@router.get("/protected")
async def protected_endpoint(
    current_worker: Worker = Depends(require_authenticated_worker)
):
    return {"message": f"Hello, {current_worker.address}!"}

@router.post("/admin-only")
async def admin_endpoint(
    admin_worker: Worker = Depends(require_admin_worker)
):
    return {"message": "Admin access granted"}
```

## Production Considerations

### 1. Redis Integration
For production, replace in-memory challenge storage with Redis:
```python
import redis

class StarkNetAuthenticator:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.redis_url)
        
    def generate_challenge(self, address: str):
        challenge = {...}
        self.redis_client.setex(f"challenge:{address}", 300, json.dumps(challenge))
        return challenge
```

### 2. Token Blacklisting
Implement token blacklisting for logout:
```python
@router.post("/logout")
async def logout(token: str = Depends(get_current_token)):
    redis_client.setex(f"blacklist:{token}", 3600, "1")
    return {"message": "Logged out"}
```

### 3. Rate Limiting
Add rate limiting to authentication endpoints:
```python
from slowapi import Limiter

@router.post("/challenge")
@limiter.limit("5/minute")
async def get_auth_challenge(request: Request, ...):
    ...
```

### 4. Signature Verification
Implement proper StarkNet signature verification:
```python
async def verify_starknet_signature(address, message_hash, signature):
    # Get account contract
    account = await starknet_client.get_contract(address)
    
    # Verify signature
    result = await account.functions["is_valid_signature"].call(
        hash=message_hash,
        signature=signature
    )
    
    return result.is_valid == 1
```

## Testing

Run the authentication test:
```bash
cd backend
python test_auth.py
```

## Troubleshooting

### Common Issues

1. **"Invalid signature"**
   - Check wallet connection
   - Verify challenge hasn't expired
   - Ensure proper message format

2. **"Worker not registered"**
   - Worker must be registered before authentication
   - Use worker registration endpoint first

3. **"Token expired"**
   - Use refresh token to get new access token
   - Check system clock synchronization

4. **"Admin privileges required"**
   - User must have `is_admin = True` in database
   - Only admins can verify workers

### Logs
Authentication events are logged with the following format:
```
INFO: Generated authentication challenge for address: 0x1234...
INFO: Successfully verified signature for address: 0x1234...
INFO: Created access token for worker: 0x1234...
WARNING: Challenge expired for address: 0x1234...
ERROR: Signature verification failed for address: 0x1234...
```
