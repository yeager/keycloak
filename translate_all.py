#!/usr/bin/env python3
"""
Complete Keycloak Swedish Translation Script
Handles all translation files: admin-ui, login, account, email, admin themes
"""

import sys
from pathlib import Path
from translate_admin_ui import KeycloakTranslator

def get_translation_files():
    """Get all translation file pairs that need work."""
    repo_path = Path("/Volumes/Extern disk/keycloak-fix")
    
    files = [
        {
            "name": "Admin UI",
            "priority": 1,
            "english": repo_path / "js/apps/admin-ui/maven-resources/theme/keycloak.v2/admin/messages/messages_en.properties",
            "swedish": repo_path / "js/apps/admin-ui/maven-resources-community/theme/keycloak.v2/admin/messages/messages_sv.properties",
            "description": "Main admin interface (3700+ strings)"
        },
        {
            "name": "Login Theme",
            "priority": 2,
            "english": repo_path / "themes/src/main/resources/theme/base/login/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/login/messages/messages_sv.properties",
            "description": "Login pages and authentication flows"
        },
        {
            "name": "Account Theme",
            "priority": 2,
            "english": repo_path / "themes/src/main/resources/theme/base/account/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/account/messages/messages_sv.properties",
            "description": "User account management pages"
        },
        {
            "name": "Email Theme",
            "priority": 2,
            "english": repo_path / "themes/src/main/resources/theme/base/email/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/email/messages/messages_sv.properties",
            "description": "Email templates and notifications"
        },
        {
            "name": "Admin Theme",
            "priority": 2,
            "english": repo_path / "themes/src/main/resources/theme/base/admin/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/admin/messages/messages_sv.properties",
            "description": "Admin theme templates"
        }
    ]
    
    return files

def analyze_translation_status(files):
    """Analyze what needs to be translated."""
    print("🔍 Analyzing translation status...")
    print("=" * 60)
    
    needs_work = []
    
    for file_info in files:
        english_file = file_info["english"]
        swedish_file = file_info["swedish"]
        name = file_info["name"]
        
        if not english_file.exists():
            print(f"❌ {name}: English file missing!")
            continue
        
        # Parse properties to get accurate counts
        translator = KeycloakTranslator()
        en_props = translator.parse_properties(english_file)
        en_count = len(en_props)
        
        if not swedish_file.exists():
            print(f"🆕 {name}: {en_count} strings (NEW FILE NEEDED)")
            file_info["status"] = "new"
            file_info["missing"] = en_count
            needs_work.append(file_info)
        else:
            sv_props = translator.parse_properties(swedish_file)
            sv_count = len(sv_props)
            
            if sv_count < en_count:
                missing = en_count - sv_count
                print(f"⚠️  {name}: {sv_count}/{en_count} strings ({missing} missing)")
                file_info["status"] = "incomplete"
                file_info["missing"] = missing
                needs_work.append(file_info)
            else:
                print(f"✅ {name}: {sv_count}/{en_count} strings (complete)")
                file_info["status"] = "complete"
    
    return needs_work

def translate_file(translator, file_info):
    """Translate a single file."""
    name = file_info["name"]
    english_file = file_info["english"]
    swedish_file = file_info["swedish"]
    
    print(f"\n🔄 Translating {name}...")
    print(f"   From: {english_file.name}")
    print(f"   To:   {swedish_file.name}")
    
    try:
        if file_info["status"] == "incomplete":
            # For incomplete files, we need to merge existing translations
            print("   Mode: Updating existing file with missing translations")
            translator.update_incomplete_translation(english_file, swedish_file)
        else:
            # For new files, translate everything
            print("   Mode: Creating new complete translation")
            translator.translate_properties(english_file, swedish_file)
        
        # Validate the result
        translator.validate_translation(english_file, swedish_file)
        print(f"✅ {name} completed successfully!")
        
    except Exception as e:
        print(f"❌ {name} failed: {e}")
        raise

def main():
    # Get all translation files
    files = get_translation_files()
    
    # Analyze what needs work
    needs_work = analyze_translation_status(files)
    
    if not needs_work:
        print("\n🎉 All translations are complete!")
        return
    
    print(f"\n📋 Translation Plan:")
    print("=" * 40)
    total_strings = 0
    for file_info in needs_work:
        status_text = "NEW" if file_info["status"] == "new" else f"+{file_info['missing']}"
        total_strings += file_info["missing"]
        print(f"• {file_info['name']}: {status_text} strings")
        print(f"  {file_info['description']}")
    
    print(f"\nTotal new translations needed: {total_strings}")
    
    # Confirm before proceeding
    print(f"\n⚠️  This will make {total_strings} API calls to DeepL Pro")
    response = input("Continue with translation? [y/N]: ").strip().lower()
    if response != 'y':
        print("Translation cancelled.")
        return
    
    # Initialize translator
    translator = KeycloakTranslator()
    
    # Sort by priority (1 = highest)
    needs_work.sort(key=lambda x: x["priority"])
    
    # Translate each file
    for file_info in needs_work:
        translate_file(translator, file_info)
    
    print("\n🎉 All translations completed!")
    print("\n📋 Next steps:")
    print("1. Review the translations for quality")
    print("2. Test in Keycloak development environment")
    print("3. Commit changes: git add . && git commit -m 'i18n(sv): Complete Swedish translations'")
    print("4. Push to branch: git push origin swedish-translation-update")

if __name__ == "__main__":
    main()