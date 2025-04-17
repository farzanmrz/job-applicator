#!/usr/bin/env python3
"""
Test suite for the CredentialManager class in utils/common.py
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Adjust path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import CredentialManager, encrypt_data, decrypt_data, get_encryption_key

class TestCredentialManager(unittest.TestCase):
    """
    Test cases for the CredentialManager class
    """
    
    def setUp(self):
        """
        Set up test environment with a temporary credentials file
        """
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        
        # Initialize credential manager with temp file
        self.cred_manager = CredentialManager(Path(self.temp_file.name))
        
        # Test platforms and credentials
        self.test_platform = "test-platform"
        self.test_username = "test-user"
        self.test_password = "test-password123"
    
    def tearDown(self):
        """
        Clean up after tests
        """
        # Remove temp file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_encryption_decryption(self):
        """
        Test that encryption and decryption work correctly
        """
        test_data = "This is sensitive data"
        key = get_encryption_key("test-password")
        
        # Encrypt the data
        encrypted = encrypt_data(test_data, key)
        
        # Encrypted data should be different from original
        self.assertNotEqual(test_data, encrypted)
        
        # Decrypt the data
        decrypted = decrypt_data(encrypted, key)
        
        # Decrypted data should match original
        self.assertEqual(test_data, decrypted)
    
    def test_store_and_retrieve_credentials(self):
        """
        Test storing and retrieving credentials
        """
        # Store credentials
        success = self.cred_manager.store_credentials(
            self.test_platform, 
            self.test_username, 
            self.test_password
        )
        self.assertTrue(success)
        
        # Retrieve credentials
        creds = self.cred_manager.get_credentials(self.test_platform)
        
        # Verify retrieved credentials
        self.assertIsNotNone(creds)
        self.assertEqual(creds["username"], self.test_username)
        self.assertEqual(creds["password"], self.test_password)
    
    def test_delete_credentials(self):
        """
        Test deleting credentials
        """
        # Store credentials
        self.cred_manager.store_credentials(
            self.test_platform, 
            self.test_username, 
            self.test_password
        )
        
        # Verify credentials exist
        creds = self.cred_manager.get_credentials(self.test_platform)
        self.assertIsNotNone(creds)
        
        # Delete credentials
        success = self.cred_manager.delete_credentials(self.test_platform)
        self.assertTrue(success)
        
        # Verify credentials no longer exist
        creds = self.cred_manager.get_credentials(self.test_platform)
        self.assertIsNone(creds)
    
    def test_list_platforms(self):
        """
        Test listing platforms with stored credentials
        """
        # Initially should be empty
        platforms = self.cred_manager.list_platforms()
        self.assertEqual(len(platforms), 0)
        
        # Store credentials for multiple platforms
        self.cred_manager.store_credentials("platform1", "user1", "pass1")
        self.cred_manager.store_credentials("platform2", "user2", "pass2")
        self.cred_manager.store_credentials("platform3", "user3", "pass3")
        
        # Check all platforms are listed
        platforms = self.cred_manager.list_platforms()
        self.assertEqual(len(platforms), 3)
        self.assertIn("platform1", platforms)
        self.assertIn("platform2", platforms)
        self.assertIn("platform3", platforms)
    
    def test_credentials_file_format(self):
        """
        Test that the credentials file has the correct format
        """
        # Store a credential
        self.cred_manager.store_credentials(
            self.test_platform, 
            self.test_username, 
            self.test_password
        )
        
        # Read the file directly to check structure
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
        
        # Check structure
        self.assertIn("credential_sets", data)
        self.assertIn("platform_mappings", data)
        self.assertIn(self.test_platform, data["platform_mappings"])
        
        # Get the credential ID
        cred_id = data["platform_mappings"][self.test_platform]
        
        # Check that the credential exists
        self.assertIn(cred_id, data["credential_sets"])

if __name__ == "__main__":
    unittest.main()
