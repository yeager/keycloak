#!/usr/bin/env python3
"""
Validate that all translation setup is ready (without requiring API key)
"""

import sys
from pathlib import Path

def main():
    print("🔍 Validating Keycloak Translation Setup")
    print("=" * 50)
    
    repo_path = Path("/Volumes/Extern disk/keycloak-fix")
    
    # Check files exist
    files_to_check = [
        "translate_admin_ui.py",
        "translate_all.py", 
        "analyze_translations.py",
        "setup_translation.sh",
        "README_TRANSLATION.md"
    ]
    
    print("📁 Required files:")
    all_files_ok = True
    for file_name in files_to_check:
        file_path = repo_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file_name} ({size} bytes)")
        else:
            print(f"   ❌ {file_name} (missing)")
            all_files_ok = False
    
    # Check English source file
    english_admin = repo_path / "js/apps/admin-ui/maven-resources/theme/keycloak.v2/admin/messages/messages_en.properties"
    print(f"\n📖 Source file:")
    if english_admin.exists():
        line_count = sum(1 for _ in open(english_admin, 'r', encoding='utf-8'))
        print(f"   ✅ Admin UI English: {line_count} lines")
    else:
        print(f"   ❌ Admin UI English file missing")
        all_files_ok = False
    
    # Check target directory exists
    target_dir = repo_path / "js/apps/admin-ui/maven-resources-community/theme/keycloak.v2/admin/messages"
    print(f"\n📁 Target directory:")
    if target_dir.exists():
        print(f"   ✅ {target_dir}")
    else:
        print(f"   ⚠️  Will be created: {target_dir}")
    
    # Check git config
    print(f"\n🔧 Git configuration:")
    try:
        import subprocess
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True, cwd=repo_path)
        if result.returncode == 0:
            print(f"   ✅ user.name: {result.stdout.strip()}")
        else:
            print(f"   ⚠️  user.name not set")
        
        result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True, cwd=repo_path)
        if result.returncode == 0:
            print(f"   ✅ user.email: {result.stdout.strip()}")
        else:
            print(f"   ⚠️  user.email not set")
    except Exception as e:
        print(f"   ❌ Git check failed: {e}")
    
    # Check Python dependencies
    print(f"\n🐍 Python dependencies:")
    try:
        import requests
        print(f"   ✅ requests module available")
    except ImportError:
        print(f"   ❌ requests module missing (run: pip3 install requests)")
        all_files_ok = False
    
    # Check API key status
    print(f"\n🔑 API key status:")
    try:
        result = subprocess.run(['security', 'find-generic-password', '-s', 'deepl-api', '-a', 'deepl-api', '-w'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ DeepL API key found in keychain")
        else:
            print(f"   ❌ DeepL API key not in keychain")
            print(f"       Add with: security add-generic-password -s deepl-api -a deepl-api -w 'YOUR_KEY'")
    except Exception as e:
        print(f"   ❌ Keychain check failed: {e}")
    
    print(f"\n📊 Translation Status Summary:")
    print(f"   🎯 Primary target: Admin UI (3776 strings)")
    print(f"   📝 New file needed: messages_sv.properties")
    print(f"   🌍 Language: English → Swedish")
    print(f"   🤖 Translation engine: DeepL Pro API")
    
    if all_files_ok:
        print(f"\n✅ Setup validation successful!")
        print(f"\n🚀 Ready to translate once DeepL API key is added!")
        print(f"\nNext step: ./setup_translation.sh")
    else:
        print(f"\n❌ Setup validation failed - missing required files")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())