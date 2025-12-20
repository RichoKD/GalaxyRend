# Authentication Implementation Guide

This document explains the authentication workflow implemented in the GalaxyRend frontend.

## Overview

The frontend uses a wallet-based authentication flow with the Starknet blockchain. Users connect their Starknet wallet (ArgentX or Braavos), sign a challenge message, and receive JWT tokens for authenticated API access.

## Architecture

### Components

1. **API Client** (`src/lib/api-client.ts`)

   - Handles all HTTP requests to the backend
   - Manages JWT token storage and refresh
   - Provides typed API methods for all endpoints

2. **Auth Context** (`src/contexts/AuthContext.tsx`)

   - Global authentication state management
   - User session handling
   - Role management (Creator, Node, Admin)

3. **Wallet Hook** (`src/hooks/useWallet.ts`)

   - Starknet wallet integration
   - Wallet connection and signature handling
   - Support for ArgentX and Braavos wallets

4. **Wallet Connect Button** (`src/components/WalletConnectButton.tsx`)
   - Reusable component for wallet connection
   - Shows wallet install prompts if needed
   - Handles connection errors gracefully

## Authentication Flow

```
1. User clicks "Connect Wallet"
   ↓
2. Frontend checks if Starknet wallet is installed
   ↓
3. Request wallet connection (user approves in wallet)
   ↓
4. Get authentication challenge from backend
   POST /api/v1/auth/challenge
   { address: "0x..." }
   ↓
5. Sign challenge with wallet
   User signs typed message in wallet UI
   ↓
6. Submit signature to backend
   POST /api/v1/auth/authenticate
   { address, message, signature, timestamp }
   ↓
7. Receive JWT tokens and user data
   { access_token, refresh_token, worker }
   ↓
8. Store tokens in localStorage
   ↓
9. Redirect to dashboard
```

## Usage Examples

### Using the Wallet Connect Button

```tsx
import { WalletConnectButton } from "@/components/WalletConnectButton";

export default function Page() {
  return (
    <WalletConnectButton
      redirectTo="/dashboard"
      size="lg"
      className="bg-blue-600"
    />
  );
}
```

### Using Auth Context

```tsx
"use client";

import { useAuth } from "@/contexts/AuthContext";

export default function ProfilePage() {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Please connect your wallet</div>;
  }

  return (
    <div>
      <p>Address: {user.address}</p>
      <p>Reputation: {user.reputation}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Making Authenticated API Calls

```tsx
import { jobsAPI } from "@/lib/api-client";

// Fetch user's jobs
const jobs = await jobsAPI.getJobs({
  creator_address: user.address,
  status: "open",
});

// Create a new job
const newJob = await jobsAPI.createJob({
  chain_job_id: 123,
  creator_address: user.address,
  asset_cid_part1: "Qm...",
  reward_amount: 1000000,
  deadline: new Date().toISOString(),
});
```

## Wallet Support

### ArgentX

- Most popular Starknet wallet
- Chrome/Firefox extension
- Install: https://www.argent.xyz/argent-x/

### Braavos

- Feature-rich Starknet wallet
- Chrome/Firefox extension
- Install: https://braavos.app/

## Token Management

### Storage

Tokens are stored in localStorage:

- `access_token` - Short-lived JWT for API requests
- `refresh_token` - Long-lived token for refreshing access
- `user_address` - Connected wallet address
- `user_role` - Selected role (creator, node, admin)

### Refresh Flow

```typescript
// Automatically refresh expired tokens
const refreshToken = localStorage.getItem("refresh_token");
const newTokens = await authAPI.refreshToken(refreshToken);
setTokens(newTokens.access_token, refreshToken);
```

### Logout

```typescript
// Clear all auth data
await authAPI.logout(refreshToken);
clearTokens();
```

## Environment Variables

Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STARKNET_NETWORK=sepolia
```

## Testing

### With Mock Wallet

For development without a real wallet:

1. Install a Starknet wallet extension
2. Create a test account
3. Use Sepolia testnet
4. Get test ETH from faucet

### With Backend

1. Ensure backend is running on `http://localhost:8000`
2. Database should be seeded with test data
3. Check backend logs for authentication events

## Security Considerations

1. **JWT Tokens** - Stored in localStorage (consider httpOnly cookies for production)
2. **CORS** - Backend must allow frontend origin
3. **HTTPS** - Use HTTPS in production
4. **Token Expiry** - Implement automatic refresh
5. **Signature Verification** - Backend verifies wallet signatures

## Troubleshooting

### Wallet Not Detected

- Install ArgentX or Braavos extension
- Refresh the page after installation
- Check browser console for errors

### Authentication Failed

- Check backend is running
- Verify API URL in .env.local
- Check network tab for API errors
- Ensure wallet is connected to correct network

### Token Expired

- Tokens are automatically refreshed
- If refresh fails, user must reconnect wallet
- Check refresh token in localStorage

## API Endpoints Used

- `POST /api/v1/auth/challenge` - Get signing challenge
- `POST /api/v1/auth/authenticate` - Authenticate with signature
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user data
- `POST /api/v1/auth/logout` - Invalidate tokens

## Next Steps

1. **Route Protection** - Add middleware to protect dashboard routes
2. **Token Refresh** - Implement automatic token refresh
3. **Error Handling** - Add global error boundary
4. **Loading States** - Improve loading UX
5. **Wallet Switching** - Handle wallet account changes
6. **Network Switching** - Handle network changes

## Files Created/Modified

### New Files

- `src/lib/api-client.ts` - API client with all backend endpoints
- `src/contexts/AuthContext.tsx` - Global auth state management
- `src/hooks/useWallet.ts` - Starknet wallet integration
- `src/components/WalletConnectButton.tsx` - Reusable wallet button
- `.env.example` - Environment variables template

### Modified Files

- `src/app/layout.tsx` - Added AuthProvider wrapper
- `src/app/dashboard/page.tsx` - Added auth checks and wallet prompt
- `src/components/HeroSection.tsx` - Use WalletConnectButton
- `src/components/Footer.tsx` - Use WalletConnectButton

## Support

For issues or questions:

1. Check browser console for errors
2. Review backend logs
3. Verify environment variables
4. Test with different wallet providers
