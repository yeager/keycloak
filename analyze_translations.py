#!/usr/bin/env python3
"""
Analyze Keycloak Swedish translation status without requiring API key
"""

import sys
from pathlib import Path
import re

class TranslationAnalyzer:
    def parse_properties(self, file_path: Path):
        """Parse .properties file handling multi-line values."""
        if not file_path.exists():
            return []
            
        properties = []
        current_key = None
        current_value = ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check if this is a continuation line
                if current_key and (not '=' in line or line.startswith(' ') or line.startswith('\t')):
                    # Continuation of previous value
                    if current_value.endswith('\\'):
                        current_value = current_value[:-1] + line.strip()
                    else:
                        current_value += '\n' + line.strip()
                    continue
                
                # Save previous key-value if exists
                if current_key:
                    # Clean up backslash continuations
                    final_value = current_value.replace('\\\n', '').replace('\\\\', '\\')
                    properties.append((current_key, final_value))
                
                # Parse new key=value line
                if '=' in line:
                    key, value = line.split('=', 1)
                    current_key = key.strip()
                    current_value = value
                else:
                    current_key = None
                    current_value = ""
        
        # Don't forget the last property
        if current_key:
            final_value = current_value.replace('\\\n', '').replace('\\\\', '\\')
            properties.append((current_key, final_value))
        
        return properties
    
    def analyze_placeholders(self, text):
        """Analyze placeholders in text."""
        placeholders = set()
        placeholders.update(re.findall(r'\{[^}]+\}', text))
        placeholders.update(re.findall(r'\{\{[^}]+\}\}', text))
        return placeholders
    
    def detailed_file_analysis(self, english_path, swedish_path):
        """Perform detailed analysis of translation files."""
        print(f"\n📊 Detailed Analysis: {english_path.name}")
        print("=" * 60)
        
        en_props = {k: v for k, v in self.parse_properties(english_path)}
        
        if not swedish_path.exists():
            print(f"❌ Swedish file does not exist: {swedish_path}")
            print(f"📝 Need to create: {len(en_props)} new translations")
            return
        
        sv_props = {k: v for k, v in self.parse_properties(swedish_path)}
        
        print(f"📈 Statistics:")
        print(f"   English strings: {len(en_props)}")
        print(f"   Swedish strings: {len(sv_props)}")
        
        missing_keys = set(en_props.keys()) - set(sv_props.keys())
        extra_keys = set(sv_props.keys()) - set(en_props.keys())
        
        if missing_keys:
            print(f"   Missing in Swedish: {len(missing_keys)}")
            if len(missing_keys) <= 10:
                print("   Missing keys:", list(missing_keys)[:10])
            else:
                print("   Sample missing keys:", list(missing_keys)[:5], "...")
        
        if extra_keys:
            print(f"   Extra in Swedish: {len(extra_keys)}")
            
        # Check for placeholder mismatches
        placeholder_issues = 0
        for key in set(en_props.keys()) & set(sv_props.keys()):
            en_placeholders = self.analyze_placeholders(en_props[key])
            sv_placeholders = self.analyze_placeholders(sv_props[key])
            
            if en_placeholders != sv_placeholders:
                placeholder_issues += 1
                if placeholder_issues <= 3:  # Show first few examples
                    print(f"   ⚠️  Placeholder mismatch in '{key}':")
                    print(f"      EN: {en_placeholders}")
                    print(f"      SV: {sv_placeholders}")
        
        if placeholder_issues > 3:
            print(f"   ⚠️  Total placeholder issues: {placeholder_issues}")
        
        # Calculate completion percentage
        if len(en_props) > 0:
            completion = (len(sv_props) - len(extra_keys)) / len(en_props) * 100
            print(f"   🎯 Completion: {completion:.1f}%")

def main():
    repo_path = Path("/Volumes/Extern disk/keycloak-fix")
    
    print("🔍 Keycloak Swedish Translation Analysis")
    print("=" * 60)
    
    # Define all translation files
    files_to_check = [
        {
            "name": "Admin UI (Priority 1)",
            "english": repo_path / "js/apps/admin-ui/maven-resources/theme/keycloak.v2/admin/messages/messages_en.properties",
            "swedish": repo_path / "js/apps/admin-ui/maven-resources-community/theme/keycloak.v2/admin/messages/messages_sv.properties",
        },
        {
            "name": "Login Theme",
            "english": repo_path / "themes/src/main/resources/theme/base/login/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/login/messages/messages_sv.properties",
        },
        {
            "name": "Account Theme",
            "english": repo_path / "themes/src/main/resources/theme/base/account/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/account/messages/messages_sv.properties",
        },
        {
            "name": "Email Theme",
            "english": repo_path / "themes/src/main/resources/theme/base/email/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/email/messages/messages_sv.properties",
        },
        {
            "name": "Admin Theme",
            "english": repo_path / "themes/src/main/resources/theme/base/admin/messages/messages_en.properties",
            "swedish": repo_path / "themes/src/main/resources-community/theme/base/admin/messages/messages_sv.properties",
        }
    ]
    
    analyzer = TranslationAnalyzer()
    total_missing = 0
    
    # Quick overview
    print("📋 Overview:")
    print("-" * 40)
    
    for file_info in files_to_check:
        english_file = file_info["english"]
        swedish_file = file_info["swedish"]
        name = file_info["name"]
        
        if not english_file.exists():
            print(f"❌ {name}: English file missing")
            continue
            
        en_count = len(analyzer.parse_properties(english_file))
        
        if swedish_file.exists():
            sv_count = len(analyzer.parse_properties(swedish_file))
            missing = max(0, en_count - sv_count)
            total_missing += missing
            
            if missing == 0:
                status = "✅ Complete"
            else:
                status = f"⚠️  Missing {missing}"
                
            print(f"{name}: {sv_count}/{en_count} strings ({status})")
        else:
            total_missing += en_count
            print(f"{name}: 0/{en_count} strings (❌ Missing file)")
    
    print(f"\n📊 Summary: {total_missing} total translations needed")
    
    # Detailed analysis
    for file_info in files_to_check:
        if file_info["english"].exists():
            analyzer.detailed_file_analysis(file_info["english"], file_info["swedish"])
    
    print(f"\n🎯 Ready for DeepL Translation!")
    print(f"Total API calls needed: ~{total_missing}")

if __name__ == "__main__":
    main()