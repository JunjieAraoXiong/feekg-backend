"""
Load FE-EKG schema into the configured graph database.
Supports both Neo4j and AllegroGraph backends.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.graph_backend import get_connection


def load_schema():
    """Load schema into configured backend"""

    backend_type = os.getenv('GRAPH_BACKEND', 'neo4j')

    print("=" * 60)
    print("FE-EKG Schema Loader")
    print("=" * 60)
    print(f"\n📊 Backend: {backend_type}")

    # Get backend connection
    print("\n🔌 Connecting to graph database...")
    try:
        backend = get_connection()
        print(f"✅ Connected to {backend.__class__.__name__}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    # Determine schema file
    if backend_type.lower() == 'neo4j':
        schema_path = 'ontology/neo4j_schema.cypher'
    else:
        schema_path = 'ontology/feekg_minimal.ttl'

    print(f"\n📁 Schema file: {schema_path}")

    # Check if file exists
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        backend.close()
        return False

    # Load schema
    print("\n📥 Loading schema...")
    start_time = time.time()

    try:
        backend.load_schema(schema_path)
        elapsed = time.time() - start_time
        print(f"✅ Schema loaded successfully ({elapsed:.2f}s)")
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        backend.close()
        return False

    # Verify by checking size
    print("\n🔍 Verifying schema...")
    try:
        if backend_type.lower() == 'neo4j':
            # Count risk types
            result = backend.execute_query(
                "MATCH (rt:RiskType) RETURN count(rt) as count"
            )
            risk_type_count = result[0]['count'] if result else 0
            print(f"   Risk types created: {risk_type_count}")

            # Count constraints
            result = backend.execute_query(
                "SHOW CONSTRAINTS YIELD name RETURN count(name) as count"
            )
            constraint_count = result[0]['count'] if result else 0
            print(f"   Constraints created: {constraint_count}")

        else:  # AllegroGraph
            size = backend.size()
            print(f"   Total triples: {size}")

            # Count classes
            query = """
            SELECT (COUNT(DISTINCT ?class) AS ?count) WHERE {
                ?class a <http://www.w3.org/2002/07/owl#Class> .
            }
            """
            result = backend.execute_query(query)
            class_count = result[0]['count'] if result else 0
            print(f"   Classes defined: {class_count}")

        print("\n✅ Schema verification passed!")

    except Exception as e:
        print(f"⚠️  Verification warning: {e}")

    # Close connection
    backend.close()
    print("\n🔒 Connection closed")

    print("\n" + "=" * 60)
    print("✅ Schema loading complete!")
    print("=" * 60)
    print()

    return True


if __name__ == "__main__":
    success = load_schema()
    sys.exit(0 if success else 1)
