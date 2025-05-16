#!/usr/bin/env python3
"""
License Key Generator for Tailor Shop Management System
This tool allows the developer to generate license keys for customers
"""

import os
import sys
import datetime
import argparse
import base64
import hashlib
import json
import uuid

# Add the project root directory to the path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Try to use the actual LicenseManager class to generate compatible keys
try:
    from src.utils.license_manager import LicenseManager
    license_manager = LicenseManager()
except ImportError:
    # Fallback implementation if the import fails
    class FallbackLicenseManager:
        def generate_license_key(self, is_trial=False):
            # Generate a random component
            random_part = base64.b32encode(os.urandom(5)).decode('utf-8').replace('=', '')
            
            # Get timestamp
            timestamp = datetime.datetime.now().strftime("%y%m%d")
            
            # Create prefix based on license type
            prefix = "TRIAL" if is_trial else "MGM"
            
            # Combine parts
            license_key = f"{prefix}-{timestamp}-{random_part}"
            
            return license_key
    
    license_manager = FallbackLicenseManager()

def generate_license_key(is_trial=False, batch_count=1):
    """Generate license keys"""
    keys = []
    for _ in range(batch_count):
        keys.append(license_manager.generate_license_key(is_trial=is_trial))
    return keys

def save_keys_to_file(keys, filename):
    """Save generated keys to a file"""
    with open(filename, 'w') as f:
        for key in keys:
            f.write(f"{key}\n")

def main():
    """Main function for the license key generator"""
    parser = argparse.ArgumentParser(description='Generate license keys for Tailor Shop Management System')
    parser.add_argument('-t', '--trial', action='store_true', help='Generate trial license keys')
    parser.add_argument('-c', '--count', type=int, default=1, help='Number of keys to generate')
    parser.add_argument('-o', '--output', type=str, default='license_keys.txt', help='Output file for the generated keys')
    args = parser.parse_args()
    
    # Generate keys
    keys = generate_license_key(is_trial=args.trial, batch_count=args.count)
    
    # Display keys
    key_type = "Trial" if args.trial else "Full"
    print(f"\nGenerated {len(keys)} {key_type} License Keys:\n")
    for i, key in enumerate(keys, 1):
        print(f"{i}. {key}")
    
    # Save keys to file
    save_keys_to_file(keys, args.output)
    print(f"\nKeys saved to {args.output}")
    
    if args.trial:
        print("\nNOTE: Trial keys will expire 30 days after activation")
    
    print("\nInstructions:")
    print("1. Provide these keys to your customers")
    print("2. Each key can only be used on one computer")
    print("3. Keys are tied to the hardware of the machine where they are activated")

if __name__ == "__main__":
    main() 