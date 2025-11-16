"""
Simple connection test without full AllegroGraph setup.
Tests basic connectivity and credential loading.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 60)
print("FEEKG - Simple Connectivity Test")
print("=" * 60)

# Test 1: Load environment variables
print("\n1️⃣  Testing .env loading...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✅ dotenv loaded")
except Exception as e:
    print(f"   ❌ Failed to load dotenv: {e}")
    sys.exit(1)

# Test 2: Check required variables
print("\n2️⃣  Checking environment variables...")
required_vars = ['AG_URL', 'AG_USER', 'AG_PASS', 'AG_REPO']
for var in required_vars:
    value = os.getenv(var)
    if value:
        masked = f"{var}={value[:3]}***" if var == 'AG_PASS' else f"{var}={value}"
        print(f"   ✅ {masked}")
    else:
        print(f"   ❌ {var} is missing")
        sys.exit(1)

# Test 3: Import AllegroGraph client
print("\n3️⃣  Testing AllegroGraph Python client import...")
try:
    from franz.openrdf.connect import ag_connect
    print("   ✅ agraph-python imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Test 4: Load config module
print("\n4️⃣  Testing config module...")
try:
    from config.secrets import get_masked_config
    config = get_masked_config()
    print(f"   ✅ Config loaded:")
    for key, value in config.items():
        print(f"      {key}: {value}")
except Exception as e:
    print(f"   ❌ Failed to load config: {e}")
    sys.exit(1)

# Test 5: DNS resolution
print("\n5️⃣  Testing DNS resolution...")
try:
    import socket
    host = os.getenv('AG_URL').replace('https://', '').replace('http://', '').rstrip('/')
    ip = socket.gethostbyname(host)
    print(f"   ✅ {host} resolves to {ip}")
except Exception as e:
    print(f"   ❌ DNS resolution failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All basic tests passed!")
print("=" * 60)
print("\n⚠️  Note: Actual AllegroGraph connection may require:")
print("   - Network access to the AG server")
print("   - Correct firewall rules")
print("   - Valid credentials")
print("\nIf the full connection test hangs, check:")
print("   1. Network connectivity to qa-agraph.nelumbium.ai")
print("   2. Port 10035 is accessible")
print("   3. Credentials are correct")
print()
