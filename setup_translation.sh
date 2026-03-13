#!/bin/bash
set -e

echo "🔧 Setting up Keycloak Swedish Translation Environment"
echo "======================================================="

REPO_PATH="/Volumes/Extern disk/keycloak-fix"
cd "$REPO_PATH"

# Check if DeepL API key exists
echo "1. Checking DeepL API key..."
if security find-generic-password -s deepl-api -a deepl-api -w >/dev/null 2>&1; then
    echo "✅ DeepL API key found in keychain"
else
    echo "❌ DeepL API key not found in keychain"
    echo ""
    echo "To add your DeepL API key to keychain:"
    echo "security add-generic-password -s deepl-api -a deepl-api -w 'YOUR_API_KEY'"
    echo ""
    echo "Get your API key from: https://www.deepl.com/pro-api"
    echo "Account: bosse@danielnylander.se"
    exit 1
fi

# Install Python dependencies
echo "2. Installing Python dependencies..."
python3 -m pip install requests --quiet

# Check repo structure
echo "3. Checking repository structure..."
echo "English files found:"
find . -name "messages_en.properties" | head -5

echo ""
echo "Existing Swedish files:"
find . -name "messages_sv.properties" | head -5

echo ""
echo "4. Analysis of translation status:"
echo "=================================="

echo "Admin UI (Priority 1):"
EN_ADMIN_UI="js/apps/admin-ui/maven-resources/theme/keycloak.v2/admin/messages/messages_en.properties"
SV_ADMIN_UI="js/apps/admin-ui/maven-resources-community/theme/keycloak.v2/admin/messages/messages_sv.properties"

if [ -f "$EN_ADMIN_UI" ]; then
    EN_COUNT=$(wc -l < "$EN_ADMIN_UI")
    echo "  English: $EN_COUNT strings"
    
    if [ -f "$SV_ADMIN_UI" ]; then
        SV_COUNT=$(wc -l < "$SV_ADMIN_UI")
        echo "  Swedish: $SV_COUNT strings"
    else
        echo "  Swedish: 0 strings (file does not exist)"
    fi
else
    echo "  ERROR: English admin UI file not found!"
    exit 1
fi

echo ""
echo "Other translation files (need verification):"

FILES=(
    "themes/src/main/resources/theme/base/login/messages"
    "themes/src/main/resources/theme/base/account/messages"
    "themes/src/main/resources/theme/base/email/messages"
    "themes/src/main/resources/theme/base/admin/messages"
)

for file_path in "${FILES[@]}"; do
    EN_FILE="${file_path}/messages_en.properties"
    SV_FILE="${file_path/resources/resources-community}/messages_sv.properties"
    
    if [ -f "$EN_FILE" ]; then
        EN_COUNT=$(wc -l < "$EN_FILE")
        if [ -f "$SV_FILE" ]; then
            SV_COUNT=$(wc -l < "$SV_FILE")
            if [ "$SV_COUNT" -eq "$EN_COUNT" ]; then
                STATUS="✅ Complete"
            else
                MISSING=$((EN_COUNT - SV_COUNT))
                STATUS="⚠️  Missing $MISSING strings"
            fi
        else
            STATUS="❌ No Swedish file"
        fi
        echo "  $(basename $(dirname $EN_FILE)): $EN_COUNT EN → $SV_COUNT SV ($STATUS)"
    fi
done

echo ""
echo "5. Git status:"
git config user.name "Daniel Nylander"
git config user.email "daniel@danielnylander.se"
echo "Git configured for Daniel Nylander"

echo ""
echo "🎯 Ready to translate! Run: python3 translate_admin_ui.py"
echo ""