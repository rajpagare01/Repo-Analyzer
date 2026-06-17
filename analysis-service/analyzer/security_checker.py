import re

# Severity Levels
CRITICAL = "CRITICAL"
HIGH = "HIGH"
MEDIUM = "MEDIUM"

# Regex Patterns
PATTERNS = {
    "hardcodedPasswords": {
        "regex": re.compile(r'(password|db_password|admin_password|root_password|mysql\.password)\s*[:=]\s*["\'][^"\']+["\']', re.IGNORECASE),
        "severity": HIGH,
        "type": "HARDCODED_PASSWORD"
    },
    "apiKeys": {
        "regex": re.compile(r'(api_key|apikey|access_token|auth_token|bearer_token|client_secret)\s*[:=]\s*["\'][^"\']+["\']', re.IGNORECASE),
        "severity": HIGH,
        "type": "API_KEY"
    },
    "awsKeys": {
        "regex": re.compile(r'(AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key)'),
        "severity": CRITICAL,
        "type": "AWS_CREDENTIAL"
    },
    "jwtSecrets": {
        "regex": re.compile(r'(jwt_secret|jwt\.key|secretKey|jwtSigningKey)\s*[:=]', re.IGNORECASE),
        "severity": HIGH,
        "type": "JWT_SECRET"
    },
    "databaseCredentials": {
        "regex": re.compile(r'(spring\.datasource\.password|database\.password|db\.password)\s*[:=]', re.IGNORECASE),
        "severity": HIGH,
        "type": "DATABASE_CREDENTIAL"
    },
    "sensitiveVariables": {
        "regex": re.compile(r'(SECRET_KEY|PRIVATE_KEY|API_SECRET|TOKEN|CLIENT_SECRET)\s*[:=]'),
        "severity": MEDIUM,
        "type": "SENSITIVE_VAR"
    },
    "privateKeys": {
        "regex": re.compile(r'(-----BEGIN RSA PRIVATE KEY-----|-----BEGIN PRIVATE KEY-----|-----BEGIN OPENSSH PRIVATE KEY-----)'),
        "severity": CRITICAL,
        "type": "PRIVATE_KEY"
    }
}

DANGEROUS_CONFIG_FILES = {
    '.env', '.env.local', 'application.properties', 'application.yml', 
    'config.json', 'settings.json', 'secrets.json'
}

def scan_for_secrets(file_name: str, content: str) -> dict:
    """
    Scans a single file's content for secrets.
    Returns counts and a list of findings (without the actual secret).
    """
    results = {
        'hardcodedPasswords': 0,
        'apiKeys': 0,
        'awsKeys': 0,
        'jwtSecrets': 0,
        'databaseCredentials': 0,
        'dangerousConfigs': 0,
        'sensitiveVariables': 0,
        'privateKeys': 0,
        'findings': []
    }
    
    # Check for dangerous config file
    if file_name in DANGEROUS_CONFIG_FILES:
        # Just flag the file itself if it contains ANY secret pattern below
        # We will increment dangerousConfigs if we find anything inside it.
        is_dangerous_config = True
    else:
        is_dangerous_config = False

    found_in_config = False

    for category, meta in PATTERNS.items():
        matches = meta["regex"].findall(content)
        if matches:
            count = len(matches)
            results[category] += count
            
            if is_dangerous_config:
                found_in_config = True

            # Add one finding per file/category to avoid exploding the array
            results['findings'].append({
                "type": meta["type"],
                "severity": meta["severity"],
                "file": file_name
            })
            
    if found_in_config:
        results['dangerousConfigs'] += 1
        results['findings'].append({
            "type": "DANGEROUS_CONFIG",
            "severity": HIGH,
            "file": file_name
        })

    return results
