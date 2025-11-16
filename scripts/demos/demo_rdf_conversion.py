#!/usr/bin/env python3
"""
Demo: Convert FE-EKG to RDF using RDFLib

Uses RDFLib (pure Python) - no external database needed!
"""

import json
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD, RDFS


def convert_to_rdf():
    """Convert FE-EKG data to RDF using RDFLib"""

    print("=" * 70)
    print("  Converting FE-EKG to RDF (using RDFLib)")
    print("=" * 70)

    # Create RDF graph
    g = Graph()

    # Define namespaces
    FEEKG = Namespace("http://feekg.org/ontology#")
    g.bind("feekg", FEEKG)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # Load JSON data
    print("\n1. Loading data/evergrande_crisis.json...")
    with open('data/evergrande_crisis.json', 'r') as f:
        data = json.load(f)

    print(f"   Events: {len(data['events'])}")
    print(f"   Entities: {len(data['entities'])}")
    print(f"   Risks: {len(data['risks'])}")

    # Convert entities to RDF
    print("\n2. Converting entities to RDF triples...")
    for entity in data['entities']:
        entity_uri = FEEKG[entity['entityId']]

        # Type
        g.add((entity_uri, RDF.type, FEEKG.Entity))

        # Properties
        g.add((entity_uri, FEEKG.name, Literal(entity['name'])))
        g.add((entity_uri, FEEKG.entityType, Literal(entity['type'])))

        if 'sector' in entity:
            g.add((entity_uri, FEEKG.sector, Literal(entity['sector'])))

    print(f"   ✅ Added {len(data['entities'])} entities")

    # Convert events to RDF
    print("\n3. Converting events to RDF triples...")
    for event in data['events']:
        event_uri = FEEKG[event['eventId']]

        # Type
        g.add((event_uri, RDF.type, FEEKG.Event))

        # Properties
        g.add((event_uri, FEEKG.eventType, Literal(event['type'])))
        g.add((event_uri, FEEKG.date, Literal(event['date'], datatype=XSD.date)))

        if 'description' in event:
            g.add((event_uri, FEEKG.description, Literal(event['description'])))

        # Relationships
        if 'actor' in event:
            actor_uri = FEEKG[event['actor']]
            g.add((event_uri, FEEKG.hasActor, actor_uri))

        if 'target' in event:
            target_uri = FEEKG[event['target']]
            g.add((event_uri, FEEKG.hasTarget, target_uri))

    print(f"   ✅ Added {len(data['events'])} events")

    # Convert risks to RDF
    print("\n4. Converting risks to RDF triples...")
    for risk in data['risks']:
        risk_uri = FEEKG[risk['riskId']]

        # Type
        g.add((risk_uri, RDF.type, FEEKG.Risk))

        # Properties
        g.add((risk_uri, FEEKG.riskType, Literal(risk['riskType'])))
        g.add((risk_uri, FEEKG.score, Literal(risk['initialScore'], datatype=XSD.float)))
        g.add((risk_uri, FEEKG.severity, Literal(risk['severity'])))

        # Target entity
        if 'targetEntity' in risk:
            entity_uri = FEEKG[risk['targetEntity']]
            g.add((risk_uri, FEEKG.targetsEntity, entity_uri))

    print(f"   ✅ Added {len(data['risks'])} risks")

    # Add evolution links (from Neo4j or computed)
    print("\n5. Adding evolution relationships...")
    evolution_count = 0
    # Load from results if available
    evolution_file = 'results/evolution_links.json'
    if os.path.exists(evolution_file):
        with open(evolution_file, 'r') as f:
            evolution_data = json.load(f)

        for link in evolution_data.get('links', [])[:20]:  # First 20 for demo
            from_uri = FEEKG[link['from']]
            to_uri = FEEKG[link['to']]

            # Direct relationship
            g.add((from_uri, FEEKG.evolvesTo, to_uri))

            # Reified relationship with scores
            edge_id = f"{link['from']}_to_{link['to']}"
            edge_uri = FEEKG[edge_id]

            g.add((edge_uri, RDF.type, FEEKG.EvolutionLink))
            g.add((edge_uri, FEEKG.fromEvent, from_uri))
            g.add((edge_uri, FEEKG.toEvent, to_uri))
            g.add((edge_uri, FEEKG.score, Literal(link['score'], datatype=XSD.float)))

            if 'causality' in link.get('components', {}):
                g.add((edge_uri, FEEKG.causality,
                      Literal(link['components']['causality'], datatype=XSD.float)))

            evolution_count += 1

        print(f"   ✅ Added {evolution_count} evolution links")
    else:
        print(f"   ⚠️  No evolution links file found (run evolution/run_evolution.py first)")

    # Show stats
    print("\n" + "=" * 70)
    print("  RDF Graph Created Successfully!")
    print("=" * 70)
    print(f"\n📊 Statistics:")
    print(f"   Total triples: {len(g)}")
    print(f"   Entities: {len(data['entities'])}")
    print(f"   Events: {len(data['events'])}")
    print(f"   Risks: {len(data['risks'])}")
    print(f"   Evolution links: {evolution_count}")

    # Save to Turtle file
    output_file = 'results/feekg_graph.ttl'
    print(f"\n6. Saving to {output_file}...")
    g.serialize(destination=output_file, format='turtle')
    print(f"   ✅ Saved RDF graph to {output_file}")

    # Save to other formats
    print("\n7. Saving to additional formats...")
    g.serialize(destination='results/feekg_graph.xml', format='xml')
    g.serialize(destination='results/feekg_graph.nt', format='nt')
    print(f"   ✅ Saved XML format to results/feekg_graph.xml")
    print(f"   ✅ Saved N-Triples to results/feekg_graph.nt")

    # Demo SPARQL query
    print("\n" + "=" * 70)
    print("  Demo SPARQL Queries")
    print("=" * 70)

    # Query 1: All events
    print("\n1. Query: Get all events with their types")
    query1 = """
    PREFIX feekg: <http://feekg.org/ontology#>

    SELECT ?event ?type ?date
    WHERE {
        ?event a feekg:Event .
        ?event feekg:eventType ?type .
        ?event feekg:date ?date .
    }
    ORDER BY ?date
    LIMIT 5
    """

    results1 = g.query(query1)
    for i, row in enumerate(results1, 1):
        print(f"   {i}. {row.type} on {row.date}")

    # Query 2: Entity risks
    print("\n2. Query: Get entity risks")
    query2 = """
    PREFIX feekg: <http://feekg.org/ontology#>

    SELECT ?entityName ?riskType ?score
    WHERE {
        ?risk a feekg:Risk .
        ?risk feekg:targetsEntity ?entity .
        ?risk feekg:riskType ?riskType .
        ?risk feekg:score ?score .
        ?entity feekg:name ?entityName .
    }
    ORDER BY DESC(?score)
    LIMIT 5
    """

    results2 = g.query(query2)
    for i, row in enumerate(results2, 1):
        print(f"   {i}. {row.entityName}: {row.riskType} (score: {row.score})")

    # Query 3: Evolution chains
    if evolution_count > 0:
        print("\n3. Query: Get evolution chains")
        query3 = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?fromType ?toType ?score
        WHERE {
            ?link a feekg:EvolutionLink .
            ?link feekg:fromEvent ?fromEvent .
            ?link feekg:toEvent ?toEvent .
            ?link feekg:score ?score .
            ?fromEvent feekg:eventType ?fromType .
            ?toEvent feekg:eventType ?toType .
        }
        ORDER BY DESC(?score)
        LIMIT 5
        """

        results3 = g.query(query3)
        for i, row in enumerate(results3, 1):
            print(f"   {i}. {row.fromType} → {row.toType} (score: {row.score})")

    # Show sample Turtle output
    print("\n" + "=" * 70)
    print("  Sample Turtle Output")
    print("=" * 70)
    print("\nFirst 30 lines of results/feekg_graph.ttl:\n")

    with open(output_file, 'r') as f:
        for i, line in enumerate(f, 1):
            if i <= 30:
                print(f"  {line.rstrip()}")
            else:
                break

    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    print("\n✅ RDF conversion complete!")
    print(f"\n📁 Output files:")
    print(f"   • results/feekg_graph.ttl (Turtle format)")
    print(f"   • results/feekg_graph.xml (RDF/XML format)")
    print(f"   • results/feekg_graph.nt (N-Triples format)")
    print(f"\n💡 You can:")
    print(f"   • Import into any RDF database (Jena, Virtuoso, etc.)")
    print(f"   • Query with SPARQL")
    print(f"   • Share as standard RDF data")
    print(f"   • Integrate with semantic web applications")
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    convert_to_rdf()
