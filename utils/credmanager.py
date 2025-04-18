#!/usr/bin/env python3
"""
Credential Manager utility for the job applicator application.

Handles secure storage and retrieval of user credentials.
"""

import base64
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Import and use our common logger setup
from utils.commonutil import set_logger
logger = set_logger("CredentialManager")

# Constants
DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"
CREDENTIALS_FILE = DEFAULT_DATA_DIR / "usr_creds.json"


def get_encryption_key(password: Optional[str] = None) -> bytes:
    """
    Generate or retrieve encryption key for credential encryption.

    Args:
        password: Optional password for key derivation. If not provided,
                 will use environment variable or default password.

    Returns:
        bytes: The encryption key
    """
    # Use provided password, environment variable, or default
    if password is None:
        password = os.environ.get(
            "JOB_APPLICATOR_SECRET", "default-secret-please-change-in-production"
        )

    # Convert password to bytes
    password_bytes = password.encode("utf-8")

    # Use a static salt
    # In production, this should be stored securely and consistently
    salt = os.environ.get("JOB_APPLICATOR_SALT", "job-applicator-salt").encode("utf-8")

    # Generate key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    # Derive key from password
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key


def encrypt_data(data: str, key: Optional[bytes] = None) -> str:
    """
    Encrypt string data using Fernet symmetric encryption.

    Args:
        data: String data to encrypt
        key: Optional encryption key. If not provided, will be generated.

    Returns:
        str: Encrypted data as a string
    """
    if key is None:
        key = get_encryption_key()

    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode("utf-8"))
    return encrypted_data.decode("utf-8")


def decrypt_data(encrypted_data: str, key: Optional[bytes] = None) -> str:
    """
    Decrypt Fernet-encrypted data.

    Args:
        encrypted_data: Encrypted string to decrypt
        key: Optional encryption key. If not provided, will be generated.

    Returns:
        str: Decrypted data as a string
    """
    if key is None:
        key = get_encryption_key()

    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data.encode("utf-8"))
    return decrypted_data.decode("utf-8")


class CredentialManager:
    """
    Manages secure storage and retrieval of user credentials.
    """

    def __init__(self, creds_file: Optional[Path] = None):
        """
        Initialize the credential manager.

        Args:
            creds_file: Optional path to credentials file. If not provided,
                      uses the default location.
        """
        self.creds_file = creds_file or CREDENTIALS_FILE
        self.encryption_key = get_encryption_key()
        self._ensure_credentials_file()

    def _ensure_credentials_file(self) -> None:
        """Ensure the credentials file exists with proper structure."""
        if not self.creds_file.exists():
            # Create parent directories if they don't exist
            self.creds_file.parent.mkdir(parents=True, exist_ok=True)

            # Create empty credentials file with proper structure
            initial_data = {"credential_sets": {}, "platform_mappings": {}}

            with open(self.creds_file, "w") as f:
                json.dump(initial_data, f)

            logger.info(f"Created new credentials file at {self.creds_file}")

    def _load_credentials_data(self) -> Dict[str, Any]:
        """Load the credentials data from file."""
        try:
            with open(self.creds_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading credentials data: {e}")
            return {"credential_sets": {}, "platform_mappings": {}}

    def _save_credentials_data(self, data: Dict[str, Any]) -> bool:
        """Save the credentials data to file."""
        try:
            with open(self.creds_file, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            logger.error(f"Error saving credentials data: {e}")
            return False

    def store_credentials(
        self, platforms: List[str], username: str, password: str
    ) -> bool:
        """
        Store credentials for specific platforms.

        Args:
            platforms: List of platform names (e.g., ["linkedin", "indeed"])
            username: Username or email
            password: Password

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load existing data
            creds_data = self._load_credentials_data()

            # Create credential object
            cred_object = {"username": username, "password": password}

            # Convert to JSON string
            cred_json = json.dumps(cred_object)

            # Encrypt the JSON string
            encrypted_cred = encrypt_data(cred_json, self.encryption_key)

            # Generate unique ID for this credential set
            cred_id = str(uuid.uuid4())

            # Store encrypted credentials
            creds_data["credential_sets"][cred_id] = encrypted_cred

            # Map each platform to credential ID
            for platform in platforms:
                platform = platform.lower()
                creds_data["platform_mappings"][platform] = cred_id

            # Save updated data
            success = self._save_credentials_data(creds_data)
            if success:
                platform_list = ", ".join(platforms)
                logger.info(f"Stored credentials for {platform_list}")

            return success

        except Exception as e:
            platform_list = ", ".join(platforms)
            logger.error(f"Error storing credentials for {platform_list}: {e}")
            return False

    def get_credentials(self, platform: str) -> Optional[Dict[str, str]]:
        """
        Retrieve credentials for a specific platform.

        Args:
            platform: Platform name (e.g., "linkedin", "indeed")

        Returns:
            Optional[Dict[str, str]]: Dictionary with username and password,
                                     or None if not found or error
        """
        try:
            # Load existing data
            creds_data = self._load_credentials_data()

            # Get credential ID for platform
            platform = platform.lower()
            cred_id = creds_data["platform_mappings"].get(platform)
            if not cred_id:
                logger.warning(f"No credentials found for platform {platform}")
                return None

            # Get encrypted credentials
            encrypted_cred = creds_data["credential_sets"].get(cred_id)
            if not encrypted_cred:
                logger.warning(f"Credential ID {cred_id} not found in credential sets")
                return None

            # Decrypt credentials
            decrypted_json = decrypt_data(encrypted_cred, self.encryption_key)

            # Parse JSON
            credentials = json.loads(decrypted_json)
            return credentials

        except Exception as e:
            logger.error(f"Error retrieving credentials for {platform}: {e}")
            return None

    def delete_credentials(self, platform: str) -> bool:
        """
        Delete credentials mapping for a specific platform.
        If this is the last platform using a credential set, the set is also deleted.

        Args:
            platform: Platform name to delete credentials for

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load existing data
            creds_data = self._load_credentials_data()

            # Get credential ID for platform
            platform = platform.lower()
            cred_id = creds_data["platform_mappings"].get(platform)
            if not cred_id:
                logger.warning(f"No credentials found for platform {platform}")
                return False

            # Remove platform mapping
            del creds_data["platform_mappings"][platform]

            # Check if this credential set is still used by any other platform
            still_used = False
            for other_platform, other_cred_id in creds_data[
                "platform_mappings"
            ].items():
                if other_cred_id == cred_id:
                    still_used = True
                    break

            # If not used anymore, remove the credential set
            if not still_used and cred_id in creds_data["credential_sets"]:
                del creds_data["credential_sets"][cred_id]
                logger.info(f"Removed credential set {cred_id} as it's no longer used")

            # Save updated data
            success = self._save_credentials_data(creds_data)
            if success:
                logger.info(f"Deleted credentials for {platform}")

            return success

        except Exception as e:
            logger.error(f"Error deleting credentials for {platform}: {e}")
            return False

    def list_platforms(self) -> List[str]:
        """
        List all platforms with stored credentials.

        Returns:
            list: List of platform names
        """
        try:
            creds_data = self._load_credentials_data()
            return list(creds_data["platform_mappings"].keys())
        except Exception as e:
            logger.error(f"Error listing platforms: {e}")
            return []

    def get_available_platforms(self) -> List[str]:
        """
        Get list of available platforms that don't have credentials mapped yet.

        Returns:
            list: List of available platform names
        """
        try:
            # All possible platforms
            all_platforms = [
                "linkedin",
                "indeed",
                "glassdoor",
                "monster",
                "ziprecruiter",
            ]

            # Platforms that already have credentials
            mapped_platforms = self.list_platforms()

            # Return platforms that don't have credentials yet
            return [p for p in all_platforms if p not in mapped_platforms]
        except Exception as e:
            logger.error(f"Error getting available platforms: {e}")
            return []

    def get_credential_sets_with_platforms(self) -> List[Dict[str, Any]]:
        """
        Get all credential sets with their associated platforms.

        Returns:
            list: List of dictionaries with credential details and platforms
        """
        try:
            creds_data = self._load_credentials_data()
            result = []

            # Create a reverse mapping from credential IDs to platforms
            cred_to_platforms = {}
            for platform, cred_id in creds_data["platform_mappings"].items():
                if cred_id not in cred_to_platforms:
                    cred_to_platforms[cred_id] = []
                cred_to_platforms[cred_id].append(platform)

            # For each credential set, get its details and platforms
            for cred_id, encrypted_cred in creds_data["credential_sets"].items():
                # Decrypt credentials
                decrypted_json = decrypt_data(encrypted_cred, self.encryption_key)
                credentials = json.loads(decrypted_json)

                # Get platforms this credential set is used for
                platforms = cred_to_platforms.get(cred_id, [])

                # Create result object
                cred_info = {
                    "id": cred_id,
                    "username": credentials["username"],
                    "password": credentials["password"],
                    "platforms": platforms,
                }

                result.append(cred_info)

            return result
        except Exception as e:
            logger.error(f"Error getting credential sets with platforms: {e}")
            return []

    def cleanup_orphaned_credentials(self) -> bool:
        """
        Clean up any orphaned credential sets that don't have platform mappings.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load existing data
            creds_data = self._load_credentials_data()

            # Get all credential IDs that are mapped to platforms
            mapped_cred_ids = set(creds_data["platform_mappings"].values())

            # Get all credential IDs in the credential sets
            all_cred_ids = set(creds_data["credential_sets"].keys())

            # Find orphaned credential IDs (those without mappings)
            orphaned_cred_ids = all_cred_ids - mapped_cred_ids

            # If no orphaned credentials, nothing to do
            if not orphaned_cred_ids:
                return True

            # Remove orphaned credential sets
            for cred_id in orphaned_cred_ids:
                del creds_data["credential_sets"][cred_id]
                logger.info(f"Removed orphaned credential with ID {cred_id}")

            # Save updated data
            success = self._save_credentials_data(creds_data)
            return success

        except Exception as e:
            logger.error(f"Error cleaning up orphaned credentials: {e}")
            return False


# Helper function to easily get credentials for a platform
def get_platform_credentials(platform: str) -> Optional[Dict[str, str]]:
    """
    Convenience function to get credentials for a platform.

    Args:
        platform: Platform name (e.g., "linkedin", "indeed")

    Returns:
        Optional[Dict[str, str]]: Credentials or None if not found
    """
    cred_manager = CredentialManager()
    return cred_manager.get_credentials(platform)
