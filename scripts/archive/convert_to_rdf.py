#!/usr/bin/env python3
"""
Convert FE-EKG from Neo4j to RDF/AllegroGraph

Options:
1. Read from Neo4j, write to AllegroGraph
2. Read from JSON, write to AllegroGraph
3. Export to Turtle (.ttl) file
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rdf_backend import RDFBackend
from config.graph_backend import Neo4jBackend


def convert_from_neo4j():
    """
    Read data from Neo4j and convert to RDF in AllegroGraph
    """
    print("=" * 70)
    print("  Converting Neo4j → RDF (AllegroGraph)")
    print("=" * 70)

    # Connect to Neo4j
    print("\n1. Connecting to Neo4j...")
    neo4j = Neo4jBackend()

    # Connect to AllegroGraph
    print("2. Connecting to AllegroGraph...")
    rdf = RDFBackend()
    if not rdf.connect():
        print("❌ Cannot connect to AllegroGraph. Check credentials in .env")
        return

    try:
        # Get all events from Neo4j
        print("\n3. Fetching events from Neo4j...")
        events_query = """
        MATCH (e:Event)
        OPTIONAL MATCH (e)-[:TRIGGERED_BY]->(actor:Entity)
        OPTIONAL MATCH (e)-[:IMPACTS]->(target:Entity)
        RETURN e.eventId as eventId, e.type as type, e.date as date,
               e.description as description,
               actor.entityId as actor, target.entityId as target
        """
        events = neo4j.execute_query(events_query)
        print(f"   Found {len(events)} events")

        # Convert events to RDF
        print("4. Converting events to RDF triples...")
        for event in events:
            rdf.create_event_triple(event)

        # Get all entities
        print("\n5. Fetching entities from Neo4j...")
        entities_query = """
        MATCH (e:Entity)
        RETURN e.entityId as entityId, e.name as name,
               e.type as type, e.sector as sector
        """
        entities = neo4j.execute_query(entities_query)
        print(f"   Found {len(entities)} entities")

        # Convert entities to RDF
        print("6. Converting entities to RDF triples...")
        for entity in entities:
            rdf.create_entity_triple(entity)

        # Get all risks
        print("\n7. Fetching risks from Neo4j...")
        risks_query = """
        MATCH (r:Risk)-[:TARGETS_ENTITY]->(e:Entity)
        MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
        RETURN r.riskId as riskId, rt.label as type, r.score as score,
               r.severity as severity, e.entityId as targetEntity
        """
        risks = neo4j.execute_query(risks_query)
        print(f"   Found {len(risks)} risks")

        # Convert risks to RDF
        print("8. Converting risks to RDF triples...")
        for risk in risks:
            rdf.create_risk_triple(risk)

        # Get evolution links
        print("\n9. Fetching evolution links from Neo4j...")
        evolution_query = """
        MATCH (e1:Event)-[r:EVOLVES_TO]->(e2:Event)
        RETURN e1.eventId as fromEvent, e2.eventId as toEvent,
               r.score as score, r.causality as causality,
               r.temporal as temporal, r.semantic as semantic
        """
        links = neo4j.execute_query(evolution_query)
        print(f"   Found {len(links)} evolution links")

        # Convert evolution links to RDF
        print("10. Converting evolution links to RDF triples...")
        for link in links:
            metadata = {
                'causality': link.get('causality', 0.0),
                'temporal': link.get('temporal', 0.0),
                'semantic': link.get('semantic', 0.0)
            }
            rdf.create_evolution_triple(
                link['fromEvent'],
                link['toEvent'],
                link['score'],
                metadata
            )

        # Show stats
        print("\n" + "=" * 70)
        print("  Conversion Complete!")
        print("=" * 70)
        stats = rdf.get_stats()
        print(f"\n✅ Total RDF triples: {stats['total_triples']}")
        print(f"✅ Repository: {stats['repository']}")

    finally:
        neo4j.close()
        rdf.close()


def convert_from_json():
    """
    Read from data/evergrande_crisis.json and convert to RDF
    """
    print("=" * 70)
    print("  Converting JSON → RDF (AllegroGraph)")
    print("=" * 70)

    # Load JSON data
    print("\n1. Loading data/evergrande_crisis.json...")
    with open('data/evergrande_crisis.json', 'r') as f:
        data = json.load(f)

    print(f"   Events: {len(data['events'])}")
    print(f"   Entities: {len(data['entities'])}")
    print(f"   Risks: {len(data['risks'])}")

    # Connect to AllegroGraph
    print("\n2. Connecting to AllegroGraph...")
    rdf = RDFBackend()
    if not rdf.connect():
        print("❌ Cannot connect to AllegroGraph. Check credentials in .env")
        return

    try:
        # Convert entities
        print("\n3. Converting entities to RDF...")
        for entity in data['entities']:
            rdf.create_entity_triple(entity)

        # Convert events
        print("4. Converting events to RDF...")
        for event in data['events']:
            rdf.create_event_triple(event)

        # Convert risks
        print("5. Converting risks to RDF...")
        for risk in data['risks']:
            rdf.create_risk_triple(risk)

        # Show stats
        print("\n" + "=" * 70)
        print("  Conversion Complete!")
        print("=" * 70)
        stats = rdf.get_stats()
        print(f"\n✅ Total RDF triples: {stats['total_triples']}")
        print(f"✅ Repository: {stats['repository']}")

    finally:
        rdf.close()


def export_to_turtle():
    """
    Export AllegroGraph data to Turtle file
    """
    print("=" * 70)
    print("  Exporting RDF to Turtle (.ttl)")
    print("=" * 70)

    # Connect to AllegroGraph
    print("\n1. Connecting to AllegroGraph...")
    rdf = RDFBackend()
    if not rdf.connect():
        print("❌ Cannot connect to AllegroGraph. Check credentials in .env")
        return

    try:
        output_file = 'results/feekg_graph.ttl'
        print(f"\n2. Exporting to {output_file}...")
        rdf.export_to_turtle(output_file)

        print("\n✅ Export complete!")
        print(f"\nYou can now:")
        print(f"  • View: cat {output_file}")
        print(f"  • Import to other RDF databases")
        print(f"  • Share as standard RDF data")

    finally:
        rdf.close()


def test_sparql_queries():
    """
    Test some SPARQL queries on RDF data
    """
    print("=" * 70)
    print("  Testing SPARQL Queries")
    print("=" * 70)

    rdf = RDFBackend()
    if not rdf.connect():
        print("❌ Cannot connect to AllegroGraph. Check credentials in .env")
        return

    try:
        # Query 1: All events
        print("\n1. Query: Get all events")
        query1 = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?event ?type ?date
        WHERE {
            ?event a feekg:Event .
            ?event feekg:eventType ?type .
            ?event feekg:date ?date .
        }
        ORDER BY ?date
        """
        results1 = rdf.query_sparql(query1)
        print(f"   Found {len(results1)} events")
        for r in results1[:3]:
            print(f"   - {r.get('type')} on {r.get('date')}")

        # Query 2: Evolution chains
        print("\n2. Query: Get evolution chains")
        query2 = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?from ?to ?score
        WHERE {
            ?link a feekg:EvolutionLink .
            ?link feekg:fromEvent ?fromEvent .
            ?link feekg:toEvent ?toEvent .
            ?link feekg:score ?score .
            ?fromEvent feekg:eventType ?from .
            ?toEvent feekg:eventType ?to .
        }
        ORDER BY DESC(?score)
        LIMIT 5
        """
        results2 = rdf.query_sparql(query2)
        print(f"   Found {len(results2)} evolution links")
        for r in results2:
            print(f"   - {r.get('from')} → {r.get('to')} (score: {r.get('score')})")

        # Query 3: Entity risks
        print("\n3. Query: Get entity risks")
        query3 = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?entity ?risk ?score
        WHERE {
            ?riskNode a feekg:Risk .
            ?riskNode feekg:targetsEntity ?entityNode .
            ?riskNode feekg:riskType ?risk .
            ?riskNode feekg:score ?score .
            ?entityNode feekg:name ?entity .
        }
        ORDER BY DESC(?score)
        LIMIT 5
        """
        results3 = rdf.query_sparql(query3)
        print(f"   Found {len(results3)} risks")
        for r in results3:
            print(f"   - {r.get('entity')}: {r.get('risk')} (score: {r.get('score')})")

    finally:
        rdf.close()


def main():
    """Main menu"""
    print("\n" + "=" * 70)
    print("  FE-EKG: Convert to RDF")
    print("=" * 70)
    print("\nOptions:")
    print("  1. Convert from Neo4j to RDF")
    print("  2. Convert from JSON to RDF")
    print("  3. Export RDF to Turtle (.ttl)")
    print("  4. Test SPARQL queries")
    print("  5. Exit")

    choice = input("\nSelect option (1-5): ").strip()

    if choice == '1':
        convert_from_neo4j()
    elif choice == '2':
        convert_from_json()
    elif choice == '3':
        export_to_turtle()
    elif choice == '4':
        test_sparql_queries()
    elif choice == '5':
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()
