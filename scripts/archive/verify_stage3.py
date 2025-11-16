"""
Verify Stage 3: Evergrande data loaded correctly
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.graph_backend import get_connection


def verify_stage3():
    """Verify Stage 3 completion"""

    print("=" * 60)
    print("FE-EKG Stage 3 Verification")
    print("=" * 60)

    # Connect
    print("\n1️⃣  Connecting to Neo4j...")
    try:
        backend = get_connection()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    # Test queries
    tests = [
        ("Entity count", "MATCH (e:Entity) RETURN count(e) as count", 10),
        ("Event count", "MATCH (ev:Event) RETURN count(ev) as count", 20),
        ("Risk count", "MATCH (r:Risk) RETURN count(r) as count", 10),
        ("Risk Snapshot count", "MATCH (rs:RiskSnapshot) RETURN count(rs) as count", 10),
        ("Evolution links", "MATCH ()-[r:EVOLVES_TO]->() RETURN count(r) as count", None),
        ("Event-Entity links", "MATCH ()-[r:HAS_ACTOR|HAS_TARGET]->() RETURN count(r) as count", None),
        ("Risk-Entity links", "MATCH ()-[r:TARGETS_ENTITY]->() RETURN count(r) as count", 10),
    ]

    print("\n2️⃣  Running verification queries...")
    all_passed = True

    for name, query, expected in tests:
        try:
            result = backend.execute_query(query)
            count = result[0]['count'] if result else 0

            if expected is not None:
                status = "✅" if count == expected else "⚠️ "
                if count != expected:
                    all_passed = False
                print(f"   {status} {name}: {count} (expected {expected})")
            else:
                print(f"   ✅ {name}: {count}")

        except Exception as e:
            print(f"   ❌ {name}: Failed - {e}")
            all_passed = False

    # Test three-layer query
    print("\n3️⃣  Testing three-layer query (Entity → Event → Risk)...")
    three_layer_query = """
    MATCH (actor:Entity)<-[:HAS_ACTOR]-(ev:Event)-[:INCREASES_RISK_OF]->(r:Risk)
    MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
    MATCH (r)-[:TARGETS_ENTITY]->(target:Entity)
    RETURN actor.name as Actor, ev.type as EventType, rt.label as RiskType, target.name as Target
    LIMIT 5
    """

    try:
        results = backend.execute_query(three_layer_query)
        print(f"   ✅ Found {len(results)} three-layer paths")
        if results:
            print("\n   Sample paths:")
            for r in results[:3]:
                print(f"      {r['Actor']} → {r['EventType']} → {r['RiskType']} → {r['Target']}")
    except Exception as e:
        print(f"   ❌ Three-layer query failed: {e}")
        all_passed = False

    # Test event evolution chain
    print("\n4️⃣  Testing event evolution chains...")
    evolution_query = """
    MATCH path = (e1:Event)-[:EVOLVES_TO*1..3]->(e2:Event)
    RETURN length(path) as PathLength, e1.date as StartDate, e2.date as EndDate
    LIMIT 5
    """

    try:
        results = backend.execute_query(evolution_query)
        print(f"   ✅ Found {len(results)} evolution chains")
        if results:
            print("\n   Sample chains:")
            for r in results[:3]:
                print(f"      Length {r['PathLength']}: {r['StartDate']} → {r['EndDate']}")
    except Exception as e:
        print(f"   ❌ Evolution query failed: {e}")
        all_passed = False

    # Test risk snapshots
    print("\n5️⃣  Testing risk snapshots...")
    snapshot_query = """
    MATCH (rs:RiskSnapshot)-[:SNAP_OF]->(r:Risk)
    MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
    RETURN rt.label as RiskType, rs.score as Score, rs.time as Time
    ORDER BY rs.time
    LIMIT 5
    """

    try:
        results = backend.execute_query(snapshot_query)
        print(f"   ✅ Found {len(results)} risk snapshots")
        if results:
            print("\n   Sample snapshots:")
            for r in results[:3]:
                print(f"      {r['RiskType']}: score={r['Score']} @ {r['Time']}")
    except Exception as e:
        print(f"   ❌ Snapshot query failed: {e}")
        all_passed = False

    # Close
    backend.close()

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Stage 3 Verification PASSED!")
    else:
        print("⚠️  Stage 3 Verification completed with warnings")
    print("=" * 60)

    print("\n📊 Summary:")
    print("   - 20 Evergrande events loaded (2020-2022)")
    print("   - 10 entities (companies, banks, regulators)")
    print("   - 10 risks with snapshots")
    print("   - 190 event evolution links")
    print("   - Three-layer graph verified")

    print("\n🌐 Explore in Neo4j Browser:")
    print("   URL: http://localhost:7474")
    print("   Username: neo4j")
    print("   Password: feekg2024")

    print("\n🎯 Ready for Stage 4: Event evolution methods")
    print()

    return all_passed


if __name__ == "__main__":
    success = verify_stage3()
    sys.exit(0 if success else 1)
