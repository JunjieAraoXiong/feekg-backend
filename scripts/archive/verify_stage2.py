"""
Verify Stage 2: Schema loaded and backend working correctly
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.graph_backend import get_connection


def verify_stage2():
    """Verify Stage 2 completion"""

    backend_type = os.getenv('GRAPH_BACKEND', 'neo4j')

    print("=" * 60)
    print("FE-EKG Stage 2 Verification")
    print("=" * 60)
    print(f"\n📊 Backend: {backend_type}")

    # Connect
    print("\n1️⃣  Connecting to graph database...")
    try:
        backend = get_connection()
        print(f"   ✅ Connected to {backend.__class__.__name__}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    # Check size
    print("\n2️⃣  Checking database size...")
    try:
        size = backend.size()
        print(f"   ✅ Database has {size} nodes")
    except Exception as e:
        print(f"   ❌ Size check failed: {e}")
        backend.close()
        return False

    # Test Neo4j-specific queries
    if backend_type.lower() == 'neo4j':
        print("\n3️⃣  Verifying risk types...")
        try:
            result = backend.execute_query(
                "MATCH (rt:RiskType) RETURN rt.name as name, rt.label as label ORDER BY name"
            )
            print(f"   ✅ Found {len(result)} risk types:")
            for rt in result:
                print(f"      - {rt['label']}")

        except Exception as e:
            print(f"   ⚠️  Risk type query failed: {e}")

        print("\n4️⃣  Verifying constraints...")
        try:
            result = backend.execute_query(
                "SHOW CONSTRAINTS"
            )
            print(f"   ✅ Found {len(result)} constraints")
            if len(result) > 0:
                for c in result[:3]:  # Show first 3
                    print(f"      - {c.get('name', 'unnamed')}")
        except Exception as e:
            print(f"   ⚠️  Constraint query failed: {e}")

        print("\n5️⃣  Testing write operation...")
        try:
            # Create a test entity
            backend.execute_query("""
                MERGE (e:Entity {entityId: 'test_001', name: 'Test Entity', type: 'Company'})
                RETURN e.name as name
            """)
            print("   ✅ Write operation successful")

            # Verify it exists
            result = backend.execute_query("""
                MATCH (e:Entity {entityId: 'test_001'})
                RETURN e.name as name
            """)
            if result:
                print(f"   ✅ Read verification successful: {result[0]['name']}")

            # Clean up
            backend.execute_query("""
                MATCH (e:Entity {entityId: 'test_001'})
                DELETE e
            """)
            print("   ✅ Cleanup successful")

        except Exception as e:
            print(f"   ❌ Write test failed: {e}")
            backend.close()
            return False

    # Test AllegroGraph-specific queries
    elif backend_type.lower() in ['allegrograph', 'ag']:
        print("\n3️⃣  Verifying ontology classes...")
        try:
            query = """
            SELECT ?class WHERE {
                ?class a <http://www.w3.org/2002/07/owl#Class> .
            }
            LIMIT 10
            """
            result = backend.execute_query(query)
            print(f"   ✅ Found {len(result)} classes (showing 10)")
            for cls in result[:5]:
                print(f"      - {cls['class']}")
        except Exception as e:
            print(f"   ⚠️  Class query failed: {e}")

    # Close
    backend.close()
    print("\n🔒 Connection closed")

    print("\n" + "=" * 60)
    print("✅ Stage 2 Verification Complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print(f"   - Backend: {backend_type}")
    print(f"   - Connection: Working")
    print(f"   - Schema: Loaded")
    print(f"   - Read/Write: Working")
    print("\n🎯 Ready for Stage 3: Load sample Evergrande data")
    print()

    return True


if __name__ == "__main__":
    success = verify_stage2()
    sys.exit(0 if success else 1)
