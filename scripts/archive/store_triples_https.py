"""
Store Knowledge Graph Triples to AllegroGraph via HTTPS

Adapted from original scripts to use HTTPS REST API instead of port 10035.
Uses the allegrograph_https_backend to bypass firewall issues.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.allegrograph_https_backend import AllegroGraphHTTPSBackend
from dotenv import load_dotenv

load_dotenv()


# Namespace for our knowledge graph
FEEKG_NS = "http://feekg.org/ontology#"


def store_sample_triples():
    """
    Store sample financial event triples to AllegroGraph.

    This demonstrates how to store triples using the HTTPS backend
    instead of the blocked port 10035 connection.
    """

    print("=" * 70)
    print("Store Triples to AllegroGraph via HTTPS")
    print("=" * 70)
    print()

    # Initialize HTTPS backend
    ag = AllegroGraphHTTPSBackend()

    # Test connection
    print("1. Testing connection...")
    if not ag.test_connection():
        print("   ❌ Connection failed")
        print("   Check your .env file for AG_URL, AG_USER, AG_PASS")
        return False
    print("   ✅ Connected!")
    print()

    # Check if repository exists
    print(f"2. Checking repository '{ag.repo}'...")
    if not ag.repository_exists():
        print(f"   Repository not found. Creating '{ag.repo}'...")
        if ag.create_repository():
            print("   ✅ Repository created!")
        else:
            print("   ❌ Failed to create repository")
            return False
    else:
        print(f"   ✅ Repository exists")

    # Get initial count
    initial_count = ag.get_triple_count()
    print(f"   Current triple count: {initial_count}")
    print()

    # Sample triples from Evergrande crisis
    sample_triples = [
        # Format: (subject, predicate, object)
        (f"{FEEKG_NS}evt_debt_default_001",
         f"{FEEKG_NS}hasActor",
         f"{FEEKG_NS}ent_evergrande"),

        (f"{FEEKG_NS}evt_debt_default_001",
         f"{FEEKG_NS}hasTarget",
         f"{FEEKG_NS}ent_minsheng"),

        (f"{FEEKG_NS}evt_debt_default_001",
         f"{FEEKG_NS}eventType",
         f"{FEEKG_NS}DebtDefault"),

        (f"{FEEKG_NS}risk_liquidity_001",
         f"{FEEKG_NS}targetsEntity",
         f"{FEEKG_NS}ent_evergrande"),

        (f"{FEEKG_NS}risk_liquidity_001",
         f"{FEEKG_NS}riskType",
         f"{FEEKG_NS}LiquidityRisk"),
    ]

    # Store triples
    print("3. Storing sample triples...")
    stored_count = 0
    for subject, predicate, obj in sample_triples:
        if ag.add_triple(subject, predicate, obj):
            print(f"   ✅ Stored: {subject.split('#')[1]} --> "
                  f"{predicate.split('#')[1]} --> {obj.split('#')[1]}")
            stored_count += 1
        else:
            print(f"   ❌ Failed: {subject} {predicate} {obj}")
    print()

    # Get final count
    final_count = ag.get_triple_count()
    print("=" * 70)
    print("Storage Complete!")
    print("=" * 70)
    print(f"✅ Triples stored in this session: {stored_count}")
    print(f"✅ Total triples in repository: {final_count}")
    print(f"✅ New triples added: {final_count - initial_count}")
    print()

    # Show sample SPARQL query
    print("Sample SPARQL query:")
    print("-" * 70)
    query = f"""
PREFIX feekg: <{FEEKG_NS}>

SELECT ?subject ?predicate ?object
WHERE {{
    ?subject ?predicate ?object .
    FILTER(STRSTARTS(STR(?subject), "{FEEKG_NS}"))
}}
LIMIT 10
"""
    print(query)
    print("-" * 70)
    print()

    # Try the query
    print("4. Testing SPARQL query...")
    results = ag.query_sparql(query)
    if 'error' in results:
        print(f"   ❌ Query failed: {results['error']}")
    else:
        print(f"   ✅ Query successful!")
        if 'results' in results and 'bindings' in results['results']:
            bindings = results['results']['bindings']
            print(f"   Found {len(bindings)} results")
            for i, binding in enumerate(bindings[:3], 1):
                print(f"   {i}. {binding}")
    print()

    print(f"✅ Access your data at: {ag.base_url}")
    print(f"✅ Repository: {ag.repo}")
    print()

    return True


def load_from_neo4j_and_store():
    """
    Load data from Neo4j and store as triples in AllegroGraph.

    This integrates with your existing Neo4j data.
    """
    from config.graph_backend import Neo4jBackend

    print("=" * 70)
    print("Load from Neo4j and Store in AllegroGraph")
    print("=" * 70)
    print()

    # Connect to Neo4j
    print("1. Connecting to Neo4j...")
    neo4j = Neo4jBackend()
    try:
        neo4j.connect()
        print("   ✅ Connected to Neo4j")
    except Exception as e:
        print(f"   ❌ Neo4j connection failed: {e}")
        return False

    # Connect to AllegroGraph
    print("2. Connecting to AllegroGraph...")
    ag = AllegroGraphHTTPSBackend()
    if not ag.test_connection():
        print("   ❌ AllegroGraph connection failed")
        neo4j.close()
        return False
    print("   ✅ Connected to AllegroGraph")
    print()

    # Get events from Neo4j
    print("3. Loading events from Neo4j...")
    query = """
    MATCH (e:Event)
    OPTIONAL MATCH (e)-[:HAS_ACTOR]->(actor:Entity)
    OPTIONAL MATCH (e)-[:HAS_TARGET]->(target:Entity)
    RETURN e.eventId as eventId, e.type as eventType,
           actor.entityId as actorId, target.entityId as targetId
    LIMIT 10
    """
    events = neo4j.execute_query(query)
    print(f"   Found {len(events)} events")
    print()

    # Store as triples
    print("4. Converting to RDF triples...")
    stored_count = 0
    for event in events:
        event_id = event['eventId']
        event_uri = f"{FEEKG_NS}{event_id}"

        # Event type triple
        if event['eventType']:
            ag.add_triple(
                event_uri,
                f"{FEEKG_NS}eventType",
                f"{FEEKG_NS}{event['eventType']}"
            )
            stored_count += 1

        # Actor relationship
        if event.get('actorId'):
            ag.add_triple(
                event_uri,
                f"{FEEKG_NS}hasActor",
                f"{FEEKG_NS}{event['actorId']}"
            )
            stored_count += 1

        # Target relationship
        if event.get('targetId'):
            ag.add_triple(
                event_uri,
                f"{FEEKG_NS}hasTarget",
                f"{FEEKG_NS}{event['targetId']}"
            )
            stored_count += 1

    print(f"   ✅ Stored {stored_count} triples")
    print()

    # Get final stats
    triple_count = ag.get_triple_count()
    print("=" * 70)
    print("Integration Complete!")
    print("=" * 70)
    print(f"✅ Neo4j events processed: {len(events)}")
    print(f"✅ Triples stored: {stored_count}")
    print(f"✅ Total triples in AllegroGraph: {triple_count}")
    print()

    # Cleanup
    neo4j.close()

    return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Store triples to AllegroGraph via HTTPS'
    )
    parser.add_argument(
        '--mode',
        choices=['sample', 'neo4j'],
        default='sample',
        help='Storage mode: sample (demo data) or neo4j (from Neo4j database)'
    )

    args = parser.parse_args()

    try:
        if args.mode == 'sample':
            success = store_sample_triples()
        else:
            success = load_from_neo4j_and_store()

        if success:
            print("✅ Success!")
            sys.exit(0)
        else:
            print("❌ Failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
