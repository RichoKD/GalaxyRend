"""StarkNet wallet authentication using signature verification."""
import os
import time
import hashlib
from typing import Dict, Optional
from app.services.starknet_client import get_starknet_client
import logging

logger = logging.getLogger(__name__)


class StarkNetAuthenticator:
    """Handles StarkNet wallet-based authentication."""
    
    def __init__(self):
        self.challenge_expiry = 300  # 5 minutes
        self.challenges = {}  # In production, use Redis
    
    def generate_challenge(self, address: str) -> Dict[str, str]:
        """Generate authentication challenge for wallet signing."""
        timestamp = int(time.time())
        nonce = os.urandom(16).hex()
        
        # Create a shorter message for signing
        message_data = f"{address}:{timestamp}:{nonce}"
        
        # Create hash for signing (StarkNet-compatible)
        message_hash = self._create_message_hash(message_data)
        
        # Human-readable message for display
        display_message = (
            f"GalaxyRend Authentication\n"
            f"Address: {address}\n"
            f"Timestamp: {timestamp}\n"
            f"Nonce: {nonce}\n"
            f"Please sign this message to authenticate."
        )
        
        challenge_data = {
            "message": message_hash,  # Short hash for signing
            "display_message": display_message,  # Human-readable version
            "raw_data": message_data,  # Original data for verification
            "timestamp": str(timestamp),
            "nonce": nonce,
            "expires_at": str(timestamp + self.challenge_expiry)
        }
        
        # Store challenge temporarily (in production, use Redis with TTL)
        self.challenges[address] = challenge_data
        
        logger.info(f"Generated authentication challenge for address: {address}")
        return challenge_data
    
    def _create_message_hash(self, message_data: str) -> str:
        """Create a short hash suitable for StarkNet signing."""
        # Create SHA256 hash and take first 31 bytes (248 bits) to fit in felt
        hash_bytes = hashlib.sha256(message_data.encode('utf-8')).digest()
        # Convert to hex and ensure it fits in a StarkNet felt (< 2^252)
        hash_hex = hash_bytes[:31].hex()
        return f"0x{hash_hex}"
    
    async def verify_signature(
        self, 
        address: str, 
        message: str, 
        signature: list,
        timestamp: int
    ) -> bool:
        """Verify wallet signature against message."""
        try:
            # Check timestamp validity
            current_time = int(time.time())
            if current_time - timestamp > self.challenge_expiry:
                logger.warning(f"Challenge expired for address: {address}")
                return False
            
            # Check if challenge exists
            stored_challenge = self.challenges.get(address)
            if not stored_challenge:
                logger.warning(f"No challenge found for address: {address}")
                return False
            
            # Verify the message matches the stored challenge hash
            if stored_challenge["message"] != message:
                logger.warning(f"Message hash mismatch for address: {address}")
                return False
            
            # Verify signature using StarkNet client
            starknet_client = get_starknet_client()
            
            # Verify the signature
            is_valid = await self._verify_starknet_signature(
                address, message, signature, starknet_client
            )
            
            if is_valid:
                # Clean up used challenge
                self.challenges.pop(address, None)
                logger.info(f"Successfully verified signature for address: {address}")
            else:
                logger.warning(f"Signature verification failed for address: {address}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying signature for {address}: {e}")
            return False
    
    async def _verify_starknet_signature(
        self, 
        address: str, 
        message_hash: str, 
        signature: list,
        starknet_client
    ) -> bool:
        """Verify StarkNet signature."""
        try:
            # Basic validation
            if not signature or len(signature) != 2:
                logger.warning(f"Invalid signature format for {address}")
                return False
            
            # Check if the address format is valid
            if not address.startswith("0x"):
                return False
            
            # Convert signature components to integers
            try:
                r = int(signature[0], 16) if isinstance(signature[0], str) else signature[0]
                s = int(signature[1], 16) if isinstance(signature[1], str) else signature[1]
            except (ValueError, TypeError):
                logger.warning(f"Invalid signature format for {address}")
                return False
            
            # TODO: Implement actual StarkNet signature verification
            # This would involve calling the account contract's is_valid_signature function
            # For now, we'll validate the format and return True for development
            
            logger.warning("Using placeholder signature verification - implement proper verification for production")
            return True
            
        except Exception as e:
            logger.error(f"Error in StarkNet signature verification: {e}")
            return False
    
    def cleanup_expired_challenges(self):
        """Clean up expired challenges."""
        current_time = int(time.time())
        expired_addresses = []
        
        for address, challenge in self.challenges.items():
            if current_time > int(challenge["expires_at"]):
                expired_addresses.append(address)
        
        for address in expired_addresses:
            self.challenges.pop(address, None)
            logger.info(f"Cleaned up expired challenge for address: {address}")


# Global authenticator instance
starknet_authenticator = StarkNetAuthenticator()
