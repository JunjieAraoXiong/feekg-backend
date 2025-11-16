"""
Store Knowledge Graph Triples to AllegroGraph (Native Client)

Adapted from provided scripts to use correct HTTPS connection (port 443).
Uses franz.openrdf native client instead of REST API.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from franz.openrdf.connect import ag_connect
    from franz.openrdf.vocabulary.rdf import RDF
    from franz.openrdf.vocabulary.xmlschema import XMLSchema
    ALLEGROGRAPH_AVAILABLE = True
except ImportError:
    print("❌ AllegroGraph Python client not installed!")
    print("Install with: pip install agraph-python pycurl")
    ALLEGROGRAPH_AVAILABLE = False
    sys.exit(1)


# AllegroGraph connection settings from environment
AG_HOST = os.getenv('AG_URL', 'https://qa-agraph.nelumbium.ai/')
if ':443' not in AG_HOST and AG_HOST.startswith('https://'):
    AG_HOST = AG_HOST.rstrip('/') + ':443'

AG_USER = os.getenv('AG_USER', 'sadmin')
AG_PASSWORD = os.getenv('AG_PASS')
AG_REPOSITORY = os.getenv('AG_REPO', 'KG_200203')  # Use existing repo

# Namespace for our knowledge graph
FEEKG_NS = "http://feekg.org/ontology#"
ENTITY_NS = FEEKG_NS + "entity/"
RELATION_NS = FEEKG_NS + "relation/"


def create_uri(namespace, name):
    """Create a URI from namespace and name."""
    # Clean up name for URI
    clean_name = name.replace(" ", "_").replace("'", "").replace(".", "")
    return namespace + clean_name


def connect_to_allegrograph():
    """Connect to AllegroGraph and return repository connection."""
    print(f"Connecting to AllegroGraph at {AG_HOST}...")
    print(f"Repository: {AG_REPOSITORY}")
    print()

    try:
        # Use ag_connect with HTTPS URL and port 443
        # This works through firewalls that block port 10035
        conn = ag_connect(
            AG_REPOSITORY,
            user=AG_USER,
            host=AG_HOST,  # Full HTTPS URL with :443
            password=AG_PASSWORD
        )

        print(f"✅ Connected to {AG_REPOSITORY}")
        print(f"✅ Current triple count: {conn.size()}")
        print()

        return conn

    except Exception as e:
        print(f"❌ Failed to connect to AllegroGraph: {e}")
        raise


def store_triple(conn, entity1, relation, entity2):
    """Store a single triple in AllegroGraph."""
    # Create URIs for subject, predicate, object
    subject_uri = conn.createURI(create_uri(ENTITY_NS, entity1))
    predicate_uri = conn.createURI(create_uri(RELATION_NS, relation))
    object_uri = conn.createURI(create_uri(ENTITY_NS, entity2))

    # Add the triple
    conn.add(subject_uri, predicate_uri, object_uri)

    # Also add type information
    entity_type = conn.createURI(FEEKG_NS + "Entity")
    conn.add(subject_uri, RDF.TYPE, entity_type)
    conn.add(object_uri, RDF.TYPE, entity_type)

    return (subject_uri, predicate_uri, object_uri)


def store_evergrande_triples(conn):
    """
    Store sample Evergrande crisis triples.

    Returns:
        Number of triples stored
    """
    print("=" * 70)
    print("Storing Evergrande Crisis Triples")
    print("=" * 70)
    print()

    # Sample triples from Evergrande crisis
    sample_triples = [
        # Events
        ("Evergrande", "defaulted_on", "Offshore_Bond"),
        ("Evergrande", "suspended_payment_to", "Minsheng_Bank"),
        ("Evergrande", "missed_payment_to", "CITIC_Bank"),
        ("Evergrande", "delayed_interest_on", "Dollar_Bond"),

        # Entities and relationships
        ("Evergrande", "owes_to", "Minsheng_Bank"),
        ("Evergrande", "has_risk", "Liquidity_Risk"),
        ("Evergrande", "triggered", "Credit_Downgrade"),
        ("Evergrande", "operates_in", "Real_Estate_Sector"),

        # Risk propagation
        ("Liquidity_Risk", "leads_to", "Credit_Risk"),
        ("Credit_Risk", "affects", "Market_Stability"),
        ("Market_Stability", "impacts", "Financial_System"),

        # Bank exposure
        ("Minsheng_Bank", "exposed_to", "Evergrande"),
        ("CITIC_Bank", "exposed_to", "Evergrande"),
        ("China_Construction_Bank", "exposed_to", "Evergrande"),
    ]

    initial_count = conn.size()
    stored_count = 0

    for entity1, relation, entity2 in sample_triples:
        try:
            store_triple(conn, entity1, relation, entity2)
            print(f"  ✅ Stored: {entity1} --[{relation}]--> {entity2}")
            stored_count += 1
        except Exception as e:
            print(f"  ❌ Failed: {entity1} --[{relation}]--> {entity2}")
            print(f"     Error: {e}")

    print()
    final_count = conn.size()
    new_triples = final_count - initial_count

    print("=" * 70)
    print("Storage Complete!")
    print("=" * 70)
    print(f"✅ Triples stored in this session: {stored_count}")
    print(f"✅ New triples added to repository: {new_triples}")
    print(f"✅ Total triples in repository: {final_count}")
    print()

    return stored_count


def query_stored_triples(conn):
    """
    Query and display stored triples.
    """
    print("=" * 70)
    print("Querying Stored Triples")
    print("=" * 70)
    print()

    # SPARQL query to get our triples
    query = f"""
    PREFIX feekg: <{FEEKG_NS}>
    PREFIX entity: <{ENTITY_NS}>
    PREFIX relation: <{RELATION_NS}>

    SELECT ?subject ?predicate ?object
    WHERE {{
        ?subject ?predicate ?object .
        FILTER(STRSTARTS(STR(?subject), "{ENTITY_NS}"))
    }}
    LIMIT 15
    """

    print("Executing SPARQL query...")
    print()

    try:
        result = conn.prepareTupleQuery(query=query).evaluate()

        print("Results:")
        print("-" * 70)

        count = 0
        for binding in result:
            subject = str(binding.getValue('subject')).split('/')[-1]
            predicate = str(binding.getValue('predicate')).split('/')[-1]
            obj = str(binding.getValue('object')).split('/')[-1]

            print(f"  {count + 1:2}. {subject} --[{predicate}]--> {obj}")
            count += 1

        print("-" * 70)
        print(f"✅ Found {count} triples")
        print()

    except Exception as e:
        print(f"❌ Query failed: {e}")


def load_from_neo4j(conn):
    """
    Load data from Neo4j and store as triples in AllegroGraph.
    """
    print("=" * 70)
    print("Loading from Neo4j")
    print("=" * 70)
    print()

    try:
        from config.graph_backend import Neo4jBackend

        print("Connecting to Neo4j...")
        neo4j = Neo4jBackend()
        neo4j.connect()
        print("✅ Connected to Neo4j")
        print()

        # Get evolution links
        print("Loading evolution links from Neo4j...")
        query = """
        MATCH (e1:Event)-[r:EVOLVES_TO]->(e2:Event)
        RETURN e1.eventId as from_event, e2.eventId as to_event, r.score as score
        LIMIT 20
        """

        results = neo4j.execute_query(query)
        print(f"✅ Found {len(results)} evolution links")
        print()

        # Store as triples
        print("Storing evolution links as triples...")
        initial_count = conn.size()

        for row in results:
            try:
                store_triple(conn, row['from_event'], 'evolves_to', row['to_event'])
                print(f"  ✅ {row['from_event']} --[evolves_to]--> {row['to_event']}")
            except Exception as e:
                print(f"  ❌ Failed: {e}")

        final_count = conn.size()
        new_triples = final_count - initial_count

        print()
        print("=" * 70)
        print("Neo4j Integration Complete!")
        print("=" * 70)
        print(f"✅ Evolution links processed: {len(results)}")
        print(f"✅ New triples added: {new_triples}")
        print(f"✅ Total triples: {final_count}")
        print()

        neo4j.close()

    except Exception as e:
        print(f"❌ Neo4j integration failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    if not ALLEGROGRAPH_AVAILABLE:
        return

    print("=" * 70)
    print("FEEKG: Store Triples to AllegroGraph (Native Client)")
    print("=" * 70)
    print()

    # Connect to AllegroGraph
    try:
        conn = connect_to_allegrograph()
    except Exception as e:
        print(f"❌ Failed to connect to AllegroGraph: {e}")
        sys.exit(1)

    # Choose mode
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mode',
        choices=['sample', 'neo4j', 'query'],
        default='sample',
        help='Operation mode'
    )
    args = parser.parse_args()

    try:
        if args.mode == 'sample':
            # Store sample triples
            store_evergrande_triples(conn)
            query_stored_triples(conn)

        elif args.mode == 'neo4j':
            # Load from Neo4j
            load_from_neo4j(conn)

        elif args.mode == 'query':
            # Just query existing data
            query_stored_triples(conn)

    finally:
        # Always close connection
        conn.close()
        print("✅ Connection closed")

    print()
    print("=" * 70)
    print("Sample SPARQL query to run in AllegroGraph UI:")
    print("-" * 70)
    print(f"""
PREFIX entity: <{ENTITY_NS}>
PREFIX relation: <{RELATION_NS}>

SELECT ?subject ?predicate ?object
WHERE {{
    ?subject ?predicate ?object .
    FILTER(STRSTARTS(STR(?subject), "{ENTITY_NS}"))
}}
LIMIT 20
""")
    print("-" * 70)
    print()
    print(f"Access your data at: {AG_HOST}")
    print(f"Repository: {AG_REPOSITORY}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
