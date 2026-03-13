# Keycloak Swedish Translation Guide

## Current Status

✅ **Analysis Complete** - Ready for translation  
❌ **DeepL API Key Missing** - Need to add to keychain first

## Summary

- **Admin UI**: 0/3776 strings (NEW FILE NEEDED) 🎯 **PRIMARY TARGET**
- **Login Theme**: 494/494 strings (✅ Complete, minor placeholder issues)
- **Account Theme**: 351/350 strings (✅ Complete)  
- **Email Theme**: 65/65 strings (✅ Complete, placeholder issues)
- **Admin Theme**: 74/74 strings (✅ Complete, minor placeholder issues)

**Total DeepL API calls needed: ~3776**

## Setup Instructions

### 1. Add DeepL API Key

```bash
# Get your API key from: https://www.deepl.com/pro-api
# Account: bosse@danielnylander.se
security add-generic-password -s deepl-api -a deepl-api -w 'YOUR_DEEPL_API_KEY'
```

### 2. Verify Setup

```bash
cd "/Volumes/Extern disk/keycloak-fix"
./setup_translation.sh
```

### 3. Run Translation

```bash
# For admin-ui only (main target):
python3 translate_admin_ui.py

# For all files (admin-ui + fixes for existing):
python3 translate_all.py

# Analysis only (no API calls):
python3 analyze_translations.py
```

## Translation Rules Applied

### Technical Terms (Keep in English)
- LDAP, SAML, OAuth, OIDC, OpenID Connect
- RBAC, UUID, HTTP, HTTPS, TLS, SSL, JWT
- realm, scope, token, session, federation, provider

### Keycloak-Specific Swedish Translations
- "client" → "klient" (Keycloak context)
- "flow" → "flöde"
- "permission" → "behörighet"  
- "role" → "roll"
- "group" → "grupp"
- "user" → "användare"
- "credential" → "autentiseringsuppgift"
- "editor" → "redigerare" (NOT "redaktör")

### Placeholder Protection
- `{0}`, `{1}` → preserved exactly
- `{{name}}`, `{{0}}` → preserved exactly
- `''` (escaped quotes) → preserved exactly
- `\n` line breaks → preserved

## Files Created

### Translation Scripts
- `translate_admin_ui.py` - Main admin UI translation (3776 strings)
- `translate_all.py` - Complete translation workflow
- `analyze_translations.py` - Status analysis (no API calls)
- `setup_translation.sh` - Environment verification

### Test Files  
- `test_translate.py` - Small sample test
- `test_sample_en.properties` - Test input (10 strings)

## Git Workflow

```bash
cd "/Volumes/Extern disk/keycloak-fix"

# Verify git config
git config user.name "Daniel Nylander"
git config user.email "daniel@danielnylander.se"

# After translation:
git add .
git commit -m "i18n(sv): Complete admin-ui Swedish translation (3776 strings)"
git push origin swedish-translation-update
```

## Validation

The scripts include comprehensive validation:

1. **Key count verification** - Every English key exists in Swedish
2. **Placeholder preservation** - All `{placeholders}` are preserved  
3. **Line count comparison** - Swedish file matches English structure
4. **Technical term handling** - Swedish rules applied correctly

## Expected Output

After successful translation:

```
js/apps/admin-ui/maven-resources-community/theme/keycloak.v2/admin/messages/messages_sv.properties
```

This file will contain 3776 Swedish translations following Keycloak conventions.

## DeepL API Configuration

- **Endpoint**: `https://api.deepl.com/v2/translate` (Pro API)
- **Batch size**: 50 strings per request
- **Rate limiting**: 1 second between batches
- **Features used**: `preserve_formatting`, `tag_handling: html`

## Troubleshooting

### "API key not found"
```bash
security add-generic-password -s deepl-api -a deepl-api -w 'YOUR_KEY'
```

### "Permission denied"  
```bash
chmod +x *.sh *.py
```

### "Module not found"
```bash
python3 -m pip install requests
```

## Quality Assurance

1. **Before commit**: Run `python3 analyze_translations.py`
2. **Test sample**: Use `test_translate.py` with API key first
3. **Manual review**: Check sample translations for quality
4. **Keycloak test**: Verify in development environment

---

**Ready for translation once DeepL API key is available!** 🚀