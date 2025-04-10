import json
import os
import time
import base64
import uuid
import importlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AppCreds:
    """Manages secure storage of user credentials for various platforms."""

    # Predefined list of supported platforms
    SUPPORTED_PLATFORMS = [
        "linkedin", "handshake", "indeed", "workday_common", "others"
    ]

    def __init__(self):
        self.credentials_file = "data/creds.json"
        os.makedirs("data", exist_ok=True)
        # Use a fixed salt for development purposes
        # In production, this should be stored securely or derived from user input
        self._salt = b'job_applicator_salt_value'
        self._key = self._get_encryption_key()
        
    def _get_encryption_key(self):
        """Generate encryption key using PBKDF2."""
        # In a real app, this would use a user password or system-derived secret
        password = b"job_applicator_secret_key"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
        
    def _encrypt_data(self, data):
        """Encrypt sensitive data."""
        f = Fernet(self._key)
        return f.encrypt(json.dumps(data).encode()).decode()
        
    def _decrypt_data(self, encrypted_data):
        """Decrypt sensitive data."""
        f = Fernet(self._key)
        return json.loads(f.decrypt(encrypted_data.encode()).decode())
    
    def _ensure_file(self):
        """Create credentials file if it doesn't exist."""
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, "w") as f:
                json.dump({
                    "credential_sets": {},
                    "platform_mappings": {}
                }, f)
    
    
    def save_credential_set(self, set_id, name, username, password, platforms):
        """Save a credential set and link it to platforms."""
        self._ensure_file()
        
        # Read existing data
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {
                "credential_sets": {},
                "platform_mappings": {}
            }
        
        # Generate new set ID if needed
        if not set_id:
            set_id = str(uuid.uuid4())
        
        # Prepare and encrypt credentials
        creds = {
            "username": username,
            "password": password,
            "saved_at": time.time(),
            "name": name
        }
        
        # Store encrypted credential set
        data["credential_sets"][set_id] = self._encrypt_data(creds)
        
        # Update platform mappings
        for platform in platforms:
            # Remove platform from any existing mappings
            for existing_platform, existing_set_id in list(data["platform_mappings"].items()):
                if existing_platform == platform and existing_set_id != set_id:
                    del data["platform_mappings"][platform]
            
            # Add new mapping
            data["platform_mappings"][platform] = set_id
        
        # Save to file
        with open(self.credentials_file, "w") as f:
            json.dump(data, f)
            
        return set_id
    
    def get_credential_set(self, set_id):
        """Get a credential set by ID."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
                
            if set_id in data.get("credential_sets", {}):
                encrypted_creds = data["credential_sets"][set_id]
                return self._decrypt_data(encrypted_creds)
            else:
                return None
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def get_all_credential_sets(self):
        """Get all credential sets with their linked platforms."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
            
            result = {}
            platform_mappings = data.get("platform_mappings", {})
            
            # Group platforms by credential set
            set_to_platforms = {}
            for platform, set_id in platform_mappings.items():
                if set_id not in set_to_platforms:
                    set_to_platforms[set_id] = []
                set_to_platforms[set_id].append(platform)
            
            # Get credential sets with their platforms
            for set_id, encrypted_creds in data.get("credential_sets", {}).items():
                creds = self._decrypt_data(encrypted_creds)
                creds["platforms"] = set_to_platforms.get(set_id, [])
                result[set_id] = creds
            
            return result
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def remove_credential_set(self, set_id):
        """Remove a credential set and its platform mappings."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
            
            # Remove credential set
            if set_id in data.get("credential_sets", {}):
                del data["credential_sets"][set_id]
            
            # Remove platform mappings for this set
            for platform, mapped_set_id in list(data.get("platform_mappings", {}).items()):
                if mapped_set_id == set_id:
                    del data["platform_mappings"][platform]
            
            # Save changes
            with open(self.credentials_file, "w") as f:
                json.dump(data, f)
            
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False
    
    def get_creds(self, platform):
        """Get the credential set associated with a platform."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
            
            platform_mappings = data.get("platform_mappings", {})
            if platform in platform_mappings:
                set_id = platform_mappings[platform]
                if set_id in data.get("credential_sets", {}):
                    creds = self._decrypt_data(data["credential_sets"][set_id])
                    creds["set_id"] = set_id
                    return creds
            
            return None
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def get_mapped_platforms(self):
        """Get all platforms that have credentials mapped to them."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
            
            return list(data.get("platform_mappings", {}).keys())
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_unmapped_platforms(self):
        """Get all platforms that don't have credentials mapped to them."""
        mapped = set(self.get_mapped_platforms())
        return [p for p in self.SUPPORTED_PLATFORMS if p not in mapped]

    # Legacy methods for backward compatibility
    def save_creds(self, platform, username, password):
        """Legacy method: Save credentials for a specific platform."""
        return self.save_credential_set(
            set_id=None,
            name=f"{platform.title()} Credentials",
            username=username,
            password=password,
            platforms=[platform]
        )
    
    def get_creds(self, platform):
        """Get the credential set associated with a platform."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
            
            platform_mappings = data.get("platform_mappings", {})
            if platform in platform_mappings:
                set_id = platform_mappings[platform]
                if set_id in data.get("credential_sets", {}):
                    creds = self._decrypt_data(data["credential_sets"][set_id])
                    creds["set_id"] = set_id
                    return creds
            
            return None
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def remove_creds(self, platform):
        """Legacy method: Remove credentials for a specific platform."""
        self._ensure_file()
        
        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
            
            if platform in data.get("platform_mappings", {}):
                set_id = data["platform_mappings"][platform]
                del data["platform_mappings"][platform]
                
                # If no other platforms use this set, remove it
                other_platforms = False
                for p, s in data.get("platform_mappings", {}).items():
                    if s == set_id:
                        other_platforms = True
                        break
                
                if not other_platforms and set_id in data.get("credential_sets", {}):
                    del data["credential_sets"][set_id]
                
                with open(self.credentials_file, "w") as f:
                    json.dump(data, f)
                
                return True
            
            return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False
    
    def get_platforms(self):
        """Legacy method: Get list of platforms with saved credentials."""
        return self.get_mapped_platforms()
        
    def get_all_platforms(self):
        """Get all supported platforms."""
        return self.SUPPORTED_PLATFORMS