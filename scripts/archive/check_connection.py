"""
Test AllegroGraph connection for FEEKG.
Verifies credentials and repository access.
"""

import sys
import os
import time
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.secrets import get_ag_connection, get_masked_config


def check_connection():
    """
    Test AllegroGraph connection and return status.

    Returns:
        dict: Connection status with details
    """
    result = {
        'agraph_ok': False,
        'repo': None,
        'size': None,
        'latency_ms': None,
        'error': None
    }

    print("=" * 60)
    print("FEEKG - AllegroGraph Connection Test")
    print("=" * 60)

    # Show masked config
    print("\n📋 Configuration:")
    masked = get_masked_config()
    for key, value in masked.items():
        print(f"  {key}: {value}")

    # Test connection
    print("\n🔌 Testing connection...")
    conn = None

    try:
        start_time = time.time()

        # Get connection
        conn = get_ag_connection()

        # Test basic query
        size = conn.size()

        end_time = time.time()
        latency = round((end_time - start_time) * 1000, 2)

        # Success!
        result['agraph_ok'] = True
        result['repo'] = masked['ag_repo']
        result['size'] = size
        result['latency_ms'] = latency

        print(f"✅ Connected successfully!")
        print(f"   Repository: {masked['ag_repo']}")
        print(f"   Current size: {size} triples")
        print(f"   Latency: {latency} ms")

        # Test a simple query
        print("\n🔍 Testing SPARQL query...")
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        result_iter = conn.prepareTupleQuery(query).evaluate()

        for row in result_iter:
            count = row.getValue("count")
            print(f"   Triple count (via query): {count}")

        print("\n✅ All tests passed!")

    except Exception as e:
        result['error'] = str(e)
        print(f"\n❌ Connection failed: {e}")
        return result

    finally:
        if conn:
            conn.close()
            print("\n🔒 Connection closed.")

    return result


def save_result(result, output_path='logs/agraph_connection.json'):
    """Save test result to JSON file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    print("\n")

    # Run connection test
    result = check_connection()

    # Save result
    save_result(result)

    # Exit with appropriate code
    if result['agraph_ok']:
        print("\n" + "=" * 60)
        print("✅ FE-EKG AllegroGraph connection is ready!")
        print("=" * 60 + "\n")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Connection test failed. Please check your .env file.")
        print("=" * 60 + "\n")
        sys.exit(1)
