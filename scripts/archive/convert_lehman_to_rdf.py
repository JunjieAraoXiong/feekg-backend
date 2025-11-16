#!/usr/bin/env python3
"""
Convert Lehman Brothers Case Study to RDF Triples

Converts the FE-EKG knowledge graph to RDF and uploads to AllegroGraph.

Usage:
    python scripts/convert_lehman_to_rdf.py
    python scripts/convert_lehman_to_rdf.py --output results/lehman_graph.ttl
    python scripts/convert_lehman_to_rdf.py --upload  # Upload to AllegroGraph
"""

import os
import sys
import json
import argparse
from datetime import datetime
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.graph_backend import get_connection
from config.allegrograph_https_backend import AllegroGraphHTTPSBackend


def convert_lehman_to_rdf(output_file: str = 'results/lehman_graph.ttl', upload: bool = False):
    """
    Convert Lehman Brothers case study from Neo4j to RDF

    Args:
        output_file: Output Turtle file path
        upload: Whether to upload to AllegroGraph
    """

    print("\n" + "=" * 70)
    print("  Convert Lehman Brothers Case Study to RDF")
    print("=" * 70)

    # Connect to graph database
    print(f"\n1. Connecting to graph database...")
    try:
        backend = get_connection()
        print(f"   ✅ Connected to {backend.__class__.__name__}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n   Please load Lehman data first:")
        print("   ./venv/bin/python ingestion/load_lehman.py")
        sys.exit(1)

    # Create RDF graph
    print(f"\n2. Creating RDF graph...")

    g = Graph()

    # Define namespaces
    FEEKG = Namespace("http://feekg.org/ontology#")
    LEHMAN = Namespace("http://feekg.org/lehman/")

    g.bind("feekg", FEEKG)
    g.bind("lehman", LEHMAN)
    g.bind("xsd", XSD)

    # Get data from Neo4j
    print(f"\n3. Fetching data from Neo4j...")

    # Get entities
    query_entities = """
    MATCH (e:Entity)
    RETURN e.entityId AS id, e.name AS name, e.type AS type
    ORDER BY e.entityId
    """
    entities = backend.execute_query(query_entities)
    print(f"   ✅ Fetched {len(entities)} entities")

    # Get events
    query_events = """
    MATCH (ev:Event)
    RETURN ev.eventId AS id, ev.date AS date, ev.type AS type,
           ev.actor AS actor, ev.target AS target,
           ev.headline AS headline, ev.description AS description,
           ev.source AS source, ev.sentiment AS sentiment
    ORDER BY ev.date, ev.eventId
    """
    events = backend.execute_query(query_events)
    print(f"   ✅ Fetched {len(events)} events")

    # Get risks
    query_risks = """
    MATCH (r:Risk)
    RETURN r.riskId AS id, r.type AS type, r.severity AS severity,
           r.likelihood AS likelihood, r.description AS description
    ORDER BY r.riskId
    """
    risks = backend.execute_query(query_risks)
    print(f"   ✅ Fetched {len(risks)} risks")

    # Get entity-event relationships
    query_entity_event = """
    MATCH (e:Entity)-[r:INVOLVES]->(ev:Event)
    RETURN e.entityId AS entity, ev.eventId AS event, type(r) AS rel_type
    """
    entity_event_links = backend.execute_query(query_entity_event)
    print(f"   ✅ Fetched {len(entity_event_links)} entity-event links")

    # Get event evolution relationships
    query_evolution = """
    MATCH (ev1:Event)-[r:EVOLVES_TO]->(ev2:Event)
    RETURN ev1.eventId AS from, ev2.eventId AS to,
           r.score AS score, r.method AS method,
           r.temporal AS temporal, r.entity AS entity,
           r.semantic AS semantic, r.topic AS topic,
           r.causality AS causality, r.emotional AS emotional
    """
    evolution_links = backend.execute_query(query_evolution)
    print(f"   ✅ Fetched {len(evolution_links)} evolution links")

    # Get event-risk relationships
    query_event_risk = """
    MATCH (ev:Event)-[r]->(risk:Risk)
    RETURN ev.eventId AS event, risk.riskId AS risk, type(r) AS rel_type
    """
    event_risk_links = backend.execute_query(query_event_risk)
    print(f"   ✅ Fetched {len(event_risk_links)} event-risk links")

    # Convert entities to RDF
    print(f"\n4. Converting entities to RDF...")
    for entity in entities:
        entity_uri = LEHMAN[entity['id']]

        g.add((entity_uri, RDF.type, FEEKG.Entity))
        g.add((entity_uri, FEEKG.entityId, Literal(entity['id'])))
        g.add((entity_uri, FEEKG.name, Literal(entity['name'])))
        g.add((entity_uri, FEEKG.entityType, Literal(entity['type'])))

    print(f"   ✅ Converted {len(entities)} entities")

    # Convert events to RDF
    print(f"\n5. Converting events to RDF...")
    for event in events:
        event_uri = LEHMAN[event['id']]

        g.add((event_uri, RDF.type, FEEKG.Event))
        g.add((event_uri, FEEKG.eventId, Literal(event['id'])))
        g.add((event_uri, FEEKG.date, Literal(event['date'])))
        g.add((event_uri, FEEKG.eventType, Literal(event['type'])))
        g.add((event_uri, FEEKG.actor, Literal(event['actor'])))
        if event['target']:
            g.add((event_uri, FEEKG.target, Literal(event['target'])))
        g.add((event_uri, FEEKG.headline, Literal(event['headline'])))
        g.add((event_uri, FEEKG.description, Literal(event['description'])))
        g.add((event_uri, FEEKG.source, Literal(event['source'])))
        g.add((event_uri, FEEKG.sentiment, Literal(event['sentiment'], datatype=XSD.float)))

    print(f"   ✅ Converted {len(events)} events")

    # Convert risks to RDF
    print(f"\n6. Converting risks to RDF...")
    for risk in risks:
        risk_uri = LEHMAN[risk['id']]

        g.add((risk_uri, RDF.type, FEEKG.Risk))
        g.add((risk_uri, FEEKG.riskId, Literal(risk['id'])))
        g.add((risk_uri, FEEKG.riskType, Literal(risk['type'])))
        g.add((risk_uri, FEEKG.severity, Literal(risk['severity'])))
        g.add((risk_uri, FEEKG.likelihood, Literal(risk['likelihood'], datatype=XSD.float)))
        g.add((risk_uri, FEEKG.description, Literal(risk['description'])))

    print(f"   ✅ Converted {len(risks)} risks")

    # Convert entity-event links to RDF
    print(f"\n7. Converting entity-event relationships...")
    for link in entity_event_links:
        entity_uri = LEHMAN[link['entity']]
        event_uri = LEHMAN[link['event']]

        g.add((entity_uri, FEEKG.involves, event_uri))

    print(f"   ✅ Converted {len(entity_event_links)} entity-event links")

    # Convert evolution links to RDF
    print(f"\n8. Converting evolution relationships...")
    for idx, link in enumerate(evolution_links):
        from_uri = LEHMAN[link['from']]
        to_uri = LEHMAN[link['to']]
        link_uri = LEHMAN[f"{link['from']}_to_{link['to']}"]

        g.add((link_uri, RDF.type, FEEKG.EvolutionLink))
        g.add((link_uri, FEEKG.fromEvent, from_uri))
        g.add((link_uri, FEEKG.toEvent, to_uri))
        g.add((link_uri, FEEKG.score, Literal(link['score'], datatype=XSD.float)))
        g.add((link_uri, FEEKG.method, Literal(link['method'])))

        # Add component scores
        if link['temporal']:
            g.add((link_uri, FEEKG.temporalScore, Literal(link['temporal'], datatype=XSD.float)))
        if link['entity']:
            g.add((link_uri, FEEKG.entityScore, Literal(link['entity'], datatype=XSD.float)))
        if link['semantic']:
            g.add((link_uri, FEEKG.semanticScore, Literal(link['semantic'], datatype=XSD.float)))
        if link['causality']:
            g.add((link_uri, FEEKG.causalityScore, Literal(link['causality'], datatype=XSD.float)))

    print(f"   ✅ Converted {len(evolution_links)} evolution links")

    # Convert event-risk links to RDF
    print(f"\n9. Converting event-risk relationships...")
    for link in event_risk_links:
        event_uri = LEHMAN[link['event']]
        risk_uri = LEHMAN[link['risk']]

        g.add((event_uri, FEEKG.triggers, risk_uri))

    print(f"   ✅ Converted {len(event_risk_links)} event-risk links")

    # Count total triples
    total_triples = len(g)
    print(f"\n   📊 Total RDF triples: {total_triples}")

    # Save to file
    print(f"\n10. Saving RDF graph...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    g.serialize(destination=output_file, format='turtle')
    file_size = os.path.getsize(output_file)

    print(f"   ✅ Saved to: {output_file}")
    print(f"   📦 File size: {file_size:,} bytes")

    # Also save in other formats
    xml_file = output_file.replace('.ttl', '.xml')
    g.serialize(destination=xml_file, format='xml')
    print(f"   ✅ Saved RDF/XML: {xml_file}")

    nt_file = output_file.replace('.ttl', '.nt')
    g.serialize(destination=nt_file, format='nt')
    print(f"   ✅ Saved N-Triples: {nt_file}")

    # Upload to AllegroGraph if requested
    if upload:
        print(f"\n11. Uploading to AllegroGraph...")

        ag = AllegroGraphHTTPSBackend()

        # Test connection
        print("   Testing connection...")
        if not ag.test_connection():
            print("   ❌ Cannot connect to AllegroGraph")
            print("   ⚠️  RDF files saved locally, but upload failed")
        else:
            print("   ✅ Connected to AllegroGraph")

            # Check if repository exists
            if not ag.repository_exists():
                print(f"   Creating repository '{ag.repo}'...")
                if not ag.create_repository():
                    print("   ❌ Failed to create repository")
                    return
                print(f"   ✅ Repository created")

            # Clear existing data
            print("   Clearing existing data...")
            ag.clear_repository()

            # Upload Turtle file
            print(f"   Uploading {total_triples} triples...")
            if ag.upload_turtle_file(output_file):
                count = ag.get_triple_count()
                print(f"   ✅ Upload successful! Triple count: {count}")
            else:
                print("   ❌ Upload failed")

    # Print summary
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    print(f"\n✅ Lehman Brothers RDF graph created successfully!")
    print(f"\nRDF Statistics:")
    print(f"  - Total triples: {total_triples}")
    print(f"  - Entities: {len(entities)}")
    print(f"  - Events: {len(events)}")
    print(f"  - Risks: {len(risks)}")
    print(f"  - Evolution links: {len(evolution_links)}")
    print(f"\nOutput files:")
    print(f"  - Turtle: {output_file}")
    print(f"  - RDF/XML: {xml_file}")
    print(f"  - N-Triples: {nt_file}")

    if upload:
        print(f"\nAllegroGraph:")
        print(f"  - Repository: {ag.repo}")
        print(f"  - URL: {ag.base_url}")

    print(f"\nNext steps:")
    print(f"  1. Query with SPARQL: python scripts/query_lehman_sparql.py")
    print(f"  2. Generate visuals: python scripts/visualize_lehman.py")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Convert Lehman Brothers case study to RDF')
    parser.add_argument('--output',
                       default='results/lehman_graph.ttl',
                       help='Output Turtle file (default: results/lehman_graph.ttl)')
    parser.add_argument('--upload',
                       action='store_true',
                       help='Upload to AllegroGraph via HTTPS')

    args = parser.parse_args()

    convert_lehman_to_rdf(args.output, args.upload)


if __name__ == '__main__':
    main()
