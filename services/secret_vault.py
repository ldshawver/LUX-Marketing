"""
SecretVault - Encryption service for secure storage of API keys and secrets
"""
import os
import base64
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class SecretVault:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self):
        """Initialize the vault with a master key from environment"""
        self._cipher = None
        self._initialize_cipher()
    
    def _initialize_cipher(self):
        """Create or load the encryption cipher"""
        # Get master key from environment or generate one
        master_key = os.environ.get('ENCRYPTION_MASTER_KEY')
        
        if not master_key:
            # Generate a new key for development
            # In production, this should be set in environment
            logger.warning("ENCRYPTION_MASTER_KEY not found, generating new key")
            key = Fernet.generate_key()
            self._cipher = Fernet(key)
            logger.info(f"Generated new encryption key. Add to secrets: {key.decode()}")
        else:
            # Use existing master key
            try:
                self._cipher = Fernet(master_key.encode())
            except Exception as e:
                logger.error(f"Failed to load master key: {e}")
                # Fallback to generated key
                key = Fernet.generate_key()
                self._cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self._cipher.encrypt(plaintext.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string
        
        Args:
            encrypted_text: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode())
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def mask_secret(self, secret: str, show_chars: int = 4) -> str:
        """
        Mask a secret for display purposes
        
        Args:
            secret: The secret to mask
            show_chars: Number of characters to show at the end
            
        Returns:
            Masked string (e.g., "sk-***abc123")
        """
        if not secret or len(secret) <= show_chars:
            return "****"
        
        return f"{secret[:2]}***{secret[-show_chars:]}"
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt all values in a dictionary
        
        Args:
            data: Dictionary with string values to encrypt
            
        Returns:
            Dictionary with encrypted values
        """
        if not data:
            return {}
        
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                encrypted[key] = self.encrypt(value)
            else:
                encrypted[key] = value
        
        return encrypted
    
    def decrypt_dict(self, data: dict) -> dict:
        """
        Decrypt all values in a dictionary
        
        Args:
            data: Dictionary with encrypted string values
            
        Returns:
            Dictionary with decrypted values
        """
        if not data:
            return {}
        
        decrypted = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                try:
                    decrypted[key] = self.decrypt(value)
                except:
                    # If decryption fails, value might not be encrypted
                    decrypted[key] = value
            else:
                decrypted[key] = value
        
        return decrypted


# Global instance
vault = SecretVault()
