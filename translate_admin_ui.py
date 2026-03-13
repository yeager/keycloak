#!/usr/bin/env python3
"""Translate Keycloak admin-ui messages_en.properties to Swedish using DeepL Pro API."""
import json, os, re, subprocess, time, sys

EN_FILE = "js/apps/admin-ui/maven-resources/theme/keycloak.v2/admin/messages/messages_en.properties"
SV_DIR = "js/apps/admin-ui/maven-resources-community/theme/keycloak.v2/admin/messages"
SV_FILE = os.path.join(SV_DIR, "messages_sv.properties")

BATCH_SIZE = 50
DELAY = 0.5  # seconds between batches

# Get DeepL key
def get_deepl_key():
    result = subprocess.run(["security", "find-generic-password", "-s", "deepl-api", "-w"],
                          capture_output=True, text=True)
    return result.stdout.strip()

# Placeholder protection: wrap in XML tags that DeepL preserves
def protect_placeholders(text):
    """Replace placeholders with XML tags DeepL won't translate."""
    protected = text
    placeholders = []
    
    # Match {0}, {1}, etc.
    for m in re.finditer(r'\{(\d+)\}', protected):
        placeholders.append(m.group())
    
    # Match {{name}}, {{0}}, etc.
    for m in re.finditer(r'\{\{[^}]+\}\}', protected):
        placeholders.append(m.group())
    
    # Replace with indexed XML tags
    idx = 0
    for m in re.finditer(r'(\{\{[^}]+\}\}|\{\d+\})', protected):
        tag = f'<x id="{idx}"/>'
        protected = protected.replace(m.group(), tag, 1)
        idx += 1
    
    return protected, placeholders

def restore_placeholders(text, placeholders):
    """Restore placeholders from XML tags."""
    result = text
    for i, ph in enumerate(placeholders):
        patterns = [
            f'<x id="{i}"/>',
            f'<x id="{i}" />',
            f'<x id="{i}">',
            f'<x id = "{i}"/>',
        ]
        for pat in patterns:
            result = result.replace(pat, ph)
    # Clean up any remaining XML artifacts
    result = re.sub(r'</?x[^>]*>', '', result)
    return result

def parse_properties(filepath):
    """Parse Java .properties file, handling multi-line values."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        # Skip comments and empty lines
        if not line or line.startswith('#') or line.startswith('!'):
            i += 1
            continue
        
        # Find key=value
        m = re.match(r'^([^=]+?)=(.*)$', line)
        if not m:
            i += 1
            continue
        
        key = m.group(1).strip()
        value = m.group(2)
        
        # Handle continuation lines (ending with \)
        while value.endswith('\\') and i + 1 < len(lines):
            value = value[:-1]  # remove trailing backslash
            i += 1
            value += lines[i].rstrip('\n').lstrip()
        
        entries.append((key, value))
        i += 1
    
    return entries

def should_translate(value):
    """Check if a value needs translation."""
    if not value or not value.strip():
        return False
    # Skip pure placeholders
    if re.match(r'^[\s{}\d.,]+$', value):
        return False
    # Skip URLs
    if value.startswith('http://') or value.startswith('https://'):
        return False
    # Skip values that are just technical terms
    if value.strip() in ('LDAP', 'SAML', 'OAuth', 'OIDC', 'JWT', 'TLS', 'SSL', 'UUID'):
        return False
    return True

def post_process(text):
    """Fix common DeepL issues with Keycloak terminology."""
    replacements = {
        'redaktör': 'redigerare',
        'Redaktör': 'Redigerare',
        # Keep technical terms
        'verklighetssfär': 'realm',
        'Verklighetssfär': 'Realm',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def translate_batch(texts, deepl_key):
    """Translate a batch of texts via DeepL API."""
    import urllib.request
    
    # Protect placeholders
    protected = []
    all_placeholders = []
    for text in texts:
        p_text, phs = protect_placeholders(text)
        protected.append(p_text)
        all_placeholders.append(phs)
    
    payload = json.dumps({
        "text": protected,
        "source_lang": "EN",
        "target_lang": "SV",
        "tag_handling": "xml",
        "preserve_formatting": True
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://api.deepl.com/v2/translate",
        data=payload,
        headers={
            "Authorization": f"DeepL-Auth-Key {deepl_key}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    
    translations = []
    for i, t in enumerate(result['translations']):
        text = restore_placeholders(t['text'], all_placeholders[i])
        text = post_process(text)
        translations.append(text)
    
    return translations

def validate(en_entries, sv_entries):
    """Validate translations."""
    issues = []
    sv_dict = dict(sv_entries)
    
    for key, en_val in en_entries:
        sv_val = sv_dict.get(key)
        if not sv_val:
            issues.append(f"MISSING: {key}")
            continue
        
        # Check placeholders
        en_phs = set(re.findall(r'\{\{[^}]+\}\}|\{\d+\}', en_val))
        sv_phs = set(re.findall(r'\{\{[^}]+\}\}|\{\d+\}', sv_val))
        if en_phs != sv_phs:
            issues.append(f"PLACEHOLDER MISMATCH: {key} EN={en_phs} SV={sv_phs}")
        
        # Check escaped quotes
        en_quotes = en_val.count("''")
        sv_quotes = sv_val.count("''")
        if en_quotes > 0 and sv_quotes == 0:
            issues.append(f"MISSING ESCAPED QUOTES: {key}")
    
    return issues

def main():
    deepl_key = get_deepl_key()
    if not deepl_key:
        print("ERROR: DeepL API key not found in keychain")
        sys.exit(1)
    
    print(f"Parsing {EN_FILE}...")
    entries = parse_properties(EN_FILE)
    print(f"Found {len(entries)} entries")
    
    # Split into translatable and non-translatable
    to_translate = []
    skip = []
    for key, val in entries:
        if should_translate(val):
            to_translate.append((key, val))
        else:
            skip.append((key, val))
    
    print(f"To translate: {len(to_translate)}, Skip: {len(skip)}")
    
    # Batch translate
    sv_entries = list(skip)  # Keep non-translated values as-is
    
    total_batches = (len(to_translate) + BATCH_SIZE - 1) // BATCH_SIZE
    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(to_translate))
        batch = to_translate[start:end]
        
        keys = [k for k, v in batch]
        values = [v for k, v in batch]
        
        print(f"Batch {batch_num + 1}/{total_batches} ({len(batch)} strings)...", end=" ", flush=True)
        
        try:
            translated = translate_batch(values, deepl_key)
            for i, key in enumerate(keys):
                sv_entries.append((key, translated[i]))
            print("✓")
        except Exception as e:
            print(f"✗ ERROR: {e}")
            # Keep English as fallback
            for key, val in batch:
                sv_entries.append((key, val))
        
        if batch_num < total_batches - 1:
            time.sleep(DELAY)
    
    # Sort by original order
    en_order = {key: i for i, (key, _) in enumerate(entries)}
    sv_entries.sort(key=lambda x: en_order.get(x[0], 99999))
    
    # Write output
    os.makedirs(SV_DIR, exist_ok=True)
    with open(SV_FILE, 'w', encoding='utf-8') as f:
        for key, val in sv_entries:
            f.write(f"{key}={val}\n")
    
    print(f"\nWrote {len(sv_entries)} entries to {SV_FILE}")
    
    # Validate
    print("\nValidating...")
    issues = validate(entries, sv_entries)
    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues[:20]:
            print(f"  {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("✓ All validations passed!")
    
    return len(issues)

if __name__ == "__main__":
    sys.exit(main())
