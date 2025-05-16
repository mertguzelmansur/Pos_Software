import os
import json
import hashlib
import uuid
import datetime
import base64

class LicenseManager:
    """
    Manages software license validation and storage
    """
    def __init__(self):
        # Path to the license file
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.license_file = os.path.join(self.base_dir, "license.json")
        
        # Hardware identifier
        self.machine_id = self._get_machine_id()
        
    def _get_machine_id(self):
        """Get a unique hardware identifier for this machine"""
        try:
            # Get a UUID based on the hardware
            machine_id = str(uuid.getnode())
            return machine_id
        except:
            # Fallback if we can't get hardware ID
            return "unknown"
    
    def is_license_valid(self):
        """Check if the license is valid and not expired"""
        if not os.path.exists(self.license_file):
            return False
            
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
                
            # Check if license is bound to this machine
            if license_data.get("machine_id") != self.machine_id:
                return False
                
            # Check if license has expired
            if "expiry_date" in license_data:
                expiry_date = datetime.datetime.strptime(license_data["expiry_date"], "%Y-%m-%d")
                if expiry_date < datetime.datetime.now():
                    return False
            
            # Verify license key
            stored_hash = license_data.get("key_hash")
            computed_hash = self._hash_key(license_data.get("license_key", ""))
            
            return stored_hash == computed_hash
        except Exception as e:
            print(f"Error validating license: {e}")
            return False
    
    def activate_license(self, license_key):
        """
        Validate and store the license key
        Returns True if successful, False otherwise
        """
        if not license_key or not self._is_key_valid(license_key):
            return False
            
        try:
            # License data to store
            license_data = {
                "license_key": license_key,
                "key_hash": self._hash_key(license_key),
                "activation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "machine_id": self.machine_id
            }
            
            # Add expiry date if this is a time-limited key
            if license_key.startswith("TRIAL-"):
                # Trial license valid for 1 day instead of 30 days
                expiry_date = datetime.datetime.now() + datetime.timedelta(days=1)
                license_data["expiry_date"] = expiry_date.strftime("%Y-%m-%d")
                
            # Save license data
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f)
                
            return True
        except Exception as e:
            print(f"Error activating license: {e}")
            return False
    
    def _is_key_valid(self, license_key):
        """
        Validate the license key format and check if it's a genuine key
        In a real system, you would implement more sophisticated validation
        """
        if not license_key or len(license_key) < 10:
            return False
            
        # Example validation logic:
        # 1. Check if key follows expected format
        if not (license_key.startswith("MGM-") or license_key.startswith("TRIAL-")):
            return False
            
        # 2. Simple checksum validation (replace with a proper algorithm)
        parts = license_key.split('-')
        if len(parts) < 3:
            return False
            
        # This is a very basic validation - in production you'd want 
        # something much more secure with proper cryptographic verification
        return True
    
    def _hash_key(self, license_key):
        """Create a hash of the license key for secure storage"""
        if not license_key:
            return ""
            
        # Create a salted hash of the license key
        salt = "MGM_TAILOR_POS"  # Change this to something unique
        hash_input = (license_key + salt).encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()
        
    def get_license_info(self):
        """Get information about the current license"""
        if not os.path.exists(self.license_file):
            return {
                "status": "Not Licensed",
                "activation_date": "",
                "expiry_date": "",
                "is_trial": False
            }
            
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
                
            is_trial = license_data.get("license_key", "").startswith("TRIAL-")
            
            return {
                "status": "Active" if self.is_license_valid() else "Invalid",
                "activation_date": license_data.get("activation_date", ""),
                "expiry_date": license_data.get("expiry_date", ""),
                "is_trial": is_trial
            }
        except Exception:
            return {
                "status": "Error",
                "activation_date": "",
                "expiry_date": "",
                "is_trial": False
            }
    
    def generate_license_key(self, is_trial=False):
        """
        Generate a license key (for use by the developer/vendor)
        This would normally be a separate tool, not included in the customer software
        """
        # Generate a random component
        random_part = base64.b32encode(os.urandom(5)).decode('utf-8').replace('=', '')
        
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%y%m%d")
        
        # Create prefix based on license type
        prefix = "TRIAL" if is_trial else "MGM"
        
        # Combine parts
        license_key = f"{prefix}-{timestamp}-{random_part}"
        
        return license_key 