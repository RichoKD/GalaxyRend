"""Test script for authentication implementation."""
import asyncio
import json
from app.auth.jwt_handler import jwt_handler
from app.auth.starknet_auth import starknet_authenticator


async def test_authentication_flow():
    """Test the authentication flow components."""
    print("Testing GalaxyRend Authentication Implementation")
    print("=" * 50)
    
    # Test 1: JWT Token Creation and Verification
    print("\n1. Testing JWT Token Creation and Verification")
    test_address = "0x1234567890abcdef1234567890abcdef12345678"
    
    try:
        # Create access token
        access_token = jwt_handler.create_access_token(test_address)
        print(f"✓ Access token created: {access_token[:50]}...")
        
        # Create refresh token
        refresh_token = jwt_handler.create_refresh_token(test_address)
        print(f"✓ Refresh token created: {refresh_token[:50]}...")
        
        # Verify tokens
        access_payload = jwt_handler.verify_token(access_token)
        refresh_payload = jwt_handler.verify_token(refresh_token)
        
        if access_payload and refresh_payload:
            print("✓ Tokens verified successfully")
            print(f"  Access token payload: {json.dumps(access_payload, indent=2, default=str)}")
            print(f"  Refresh token payload: {json.dumps(refresh_payload, indent=2, default=str)}")
        else:
            print("✗ Token verification failed")
            
    except Exception as e:
        print(f"✗ JWT test failed: {e}")
    
    # Test 2: Challenge Generation
    print("\n2. Testing Challenge Generation")
    try:
        challenge = starknet_authenticator.generate_challenge(test_address)
        print("✓ Challenge generated successfully")
        print(f"  Challenge: {json.dumps(challenge, indent=2)}")
        
        # Test signature verification (mock)
        signature = ["0x1", "0x2"]  # Mock signature
        timestamp = int(challenge["timestamp"])
        
        is_valid = await starknet_authenticator.verify_signature(
            test_address,
            challenge["message"],
            signature,
            timestamp
        )
        
        if is_valid:
            print("✓ Signature verification completed (using mock verification)")
        else:
            print("! Signature verification returned False (expected for mock)")
            
    except Exception as e:
        print(f"✗ Challenge test failed: {e}")
    
    # Test 3: Challenge Cleanup
    print("\n3. Testing Challenge Cleanup")
    try:
        starknet_authenticator.cleanup_expired_challenges()
        print("✓ Challenge cleanup completed")
    except Exception as e:
        print(f"✗ Challenge cleanup failed: {e}")
    
    print("\n" + "=" * 50)
    print("Authentication implementation test completed!")
    print("\nNext steps:")
    print("1. Update .env with proper JWT_SECRET_KEY")
    print("2. Test with real StarkNet wallet integration")
    print("3. Set up Redis for production challenge storage")
    print("4. Implement proper StarkNet signature verification")


if __name__ == "__main__":
    asyncio.run(test_authentication_flow())
