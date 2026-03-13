#!/usr/bin/env python3
"""
Test script for Keycloak translation
"""

import sys
from pathlib import Path

# Import our translator class
sys.path.append(str(Path(__file__).parent))
from translate_admin_ui import KeycloakTranslator

def main():
    repo_path = Path("/Volumes/Extern disk/keycloak-fix")
    test_english = repo_path / "test_sample_en.properties"
    test_swedish = repo_path / "test_sample_sv.properties"
    
    if not test_english.exists():
        print(f"ERROR: Test file not found: {test_english}")
        sys.exit(1)
    
    print("Testing with sample file...")
    translator = KeycloakTranslator()
    
    try:
        translator.translate_properties(test_english, test_swedish)
        translator.validate_translation(test_english, test_swedish)
        
        print("\n--- Test Results ---")
        print("English sample:")
        with open(test_english) as f:
            print(f.read())
        
        print("\nSwedish translation:")
        with open(test_swedish) as f:
            print(f.read())
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()