"""
Simple AllegroGraph HTTPS Test

Tests if we can store and query triples using an existing repository.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.allegrograph_https_backend import AllegroGraphHTTPSBackend


def main():
    print("=" * 70)
    print("Simple AllegroGraph HTTPS Test")
    print("=" * 70)
    print()

    # Initialize
    ag = AllegroGraphHTTPSBackend()

    # Step 1: Test connection
    print("1. Testing connection to AllegroGraph...")
    if not ag.test_connection():
        print("   ❌ Connection failed")
        return False
    print(f"   ✅ Connected to {ag.base_url}")
    print()

    # Step 2: List available repositories
    print("2. Listing available repositories...")
    repos = ag.list_repositories()
    print(f"   Found {len(repos)} repositories:")
    for i, repo in enumerate(repos[:10], 1):
        print(f"   {i:2}. {repo}")
    if len(repos) > 10:
        print(f"   ... and {len(repos) - 10} more")
    print()

    # Step 3: Check current repository
    print(f"3. Checking configured repository: '{ag.repo}'...")
    if ag.repository_exists():
        print(f"   ✅ Repository '{ag.repo}' exists")
        count = ag.get_triple_count()
        print(f"   Current triple count: {count}")
        can_use = True
    else:
        print(f"   ⚠️  Repository '{ag.repo}' not found")
        print(f"   Attempting to create...")
        if ag.create_repository():
            print(f"   ✅ Created '{ag.repo}'")
            can_use = True
        else:
            print(f"   ❌ Cannot create '{ag.repo}'")
            print(f"   This may require admin permissions")
            can_use = False
    print()

    if not can_use:
        print("=" * 70)
        print("Summary")
        print("=" * 70)
        print("✅ HTTPS connection works!")
        print("✅ Can list repositories")
        print("❌ Cannot create new repository (permission issue)")
        print()
        print("Options:")
        print("1. Ask admin to create 'feekg_dev' repository")
        print("2. Use an existing repository (modify .env AG_REPO)")
        print("3. Use alternative: Fuseki or RDFLib")
        return False

    # Step 4: Try uploading a simple Turtle file
    print("4. Testing data upload...")

    # Create simple Turtle content
    turtle_content = """
@prefix feekg: <http://feekg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

feekg:test_event_001 rdf:type feekg:Event .
feekg:test_event_001 feekg:eventType feekg:DebtDefault .
feekg:test_event_001 feekg:hasActor feekg:test_entity_001 .
"""

    initial_count = ag.get_triple_count()
    if ag.upload_turtle(turtle_content):
        print("   ✅ Upload successful")
        new_count = ag.get_triple_count()
        print(f"   Triples added: {new_count - initial_count}")
    else:
        print("   ❌ Upload failed")
        return False
    print()

    # Step 5: Try SPARQL query
    print("5. Testing SPARQL query...")
    query = """
PREFIX feekg: <http://feekg.org/ontology#>

SELECT ?event ?type
WHERE {
    ?event a feekg:Event .
    ?event feekg:eventType ?type .
}
LIMIT 5
"""

    results = ag.query_sparql(query)
    if 'error' in results:
        print(f"   ❌ Query failed: {results['error']}")
        return False
    else:
        print("   ✅ Query successful")
        if 'results' in results and 'bindings' in results['results']:
            bindings = results['results']['bindings']
            print(f"   Found {len(bindings)} results")
            for binding in bindings:
                event = binding.get('event', {}).get('value', 'N/A')
                type_val = binding.get('type', {}).get('value', 'N/A')
                print(f"     - {event.split('#')[-1]} -> {type_val.split('#')[-1]}")
    print()

    # Step 6: Final stats
    final_count = ag.get_triple_count()

    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)
    print(f"✅ HTTPS connection: Working")
    print(f"✅ Repository access: {ag.repo}")
    print(f"✅ Data upload: Working")
    print(f"✅ SPARQL queries: Working")
    print(f"✅ Total triples: {final_count}")
    print()
    print("🎉 AllegroGraph HTTPS backend is fully functional!")
    print()
    print("Next steps:")
    print("1. Use scripts/store_triples_https.py to load real data")
    print("2. Use scripts/convert_to_rdf.py to convert Neo4j data")
    print("3. Query via AllegroGraph web interface:")
    print(f"   {ag.base_url}")
    print()

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
