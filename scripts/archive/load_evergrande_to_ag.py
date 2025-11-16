"""
Load Evergrande Crisis Data to AllegroGraph FEEKG Repository

Reads data/evergrande_crisis.json and uploads as RDF triples
to the FEEKG repository in mycatalog.
"""

import json
import requests
from requests.auth import HTTPBasicAuth

# AllegroGraph configuration
AG_URL = "https://qa-agraph.nelumbium.ai/catalogs/mycatalog/repositories/FEEKG"
AG_USER = "sadmin"
AG_PASS = "279H-Dt<>,YU"

# Namespace
FEEKG_NS = "http://feekg.org/ontology#"


def add_triple(subject, predicate, obj, is_literal=False):
    """Add a single triple to AllegroGraph"""
    if is_literal:
        ntriple = f'<{subject}> <{predicate}> "{obj}" .\n'
    else:
        ntriple = f'<{subject}> <{predicate}> <{obj}> .\n'

    response = requests.post(
        f'{AG_URL}/statements',
        data=ntriple,
        headers={'Content-Type': 'text/plain'},
        auth=HTTPBasicAuth(AG_USER, AG_PASS)
    )
    return response.status_code in [200, 201, 204]


def load_evergrande_data():
    """Load Evergrande crisis data from JSON and upload to AllegroGraph"""

    print("=" * 80)
    print("Loading Evergrande Crisis Data to AllegroGraph")
    print("=" * 80)

    # Load JSON data
    print("\n1. Loading JSON data...")
    with open('data/evergrande_crisis.json', 'r') as f:
        data = json.load(f)

    events = data.get('events', [])
    entities = data.get('entities', [])
    risks = data.get('risks', [])

    print(f"   ✓ Events: {len(events)}")
    print(f"   ✓ Entities: {len(entities)}")
    print(f"   ✓ Risks: {len(risks)}")

    triple_count = 0

    # Load Entities
    print("\n2. Loading entities...")
    for entity in entities:
        eid = entity['entityId']
        uri = f"{FEEKG_NS}{eid}"

        # Type
        add_triple(uri, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                  f"{FEEKG_NS}Entity")
        triple_count += 1

        # Properties
        add_triple(uri, f"{FEEKG_NS}label", entity['name'], is_literal=True)
        triple_count += 1

        add_triple(uri, f"{FEEKG_NS}entityType", entity['type'], is_literal=True)
        triple_count += 1

        if 'description' in entity:
            add_triple(uri, f"{FEEKG_NS}description",
                      entity['description'], is_literal=True)
            triple_count += 1

    print(f"   ✓ Loaded {len(entities)} entities ({triple_count} triples)")

    # Load Events
    print("\n3. Loading events...")
    event_triple_count = 0
    for event in events:
        eid = event['eventId']
        uri = f"{FEEKG_NS}{eid}"

        # Type
        add_triple(uri, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                  f"{FEEKG_NS}Event")
        event_triple_count += 1

        # Properties
        add_triple(uri, f"{FEEKG_NS}eventType", event['type'], is_literal=True)
        event_triple_count += 1

        add_triple(uri, f"{FEEKG_NS}date", event['date'], is_literal=True)
        event_triple_count += 1

        if 'description' in event:
            add_triple(uri, f"{FEEKG_NS}description",
                      event['description'], is_literal=True)
            event_triple_count += 1

        # Relationships
        if 'actor' in event:
            add_triple(uri, f"{FEEKG_NS}actor", f"{FEEKG_NS}{event['actor']}")
            event_triple_count += 1

        if 'target' in event:
            add_triple(uri, f"{FEEKG_NS}involves", f"{FEEKG_NS}{event['target']}")
            event_triple_count += 1

    triple_count += event_triple_count
    print(f"   ✓ Loaded {len(events)} events ({event_triple_count} triples)")

    # Load Risks
    print("\n4. Loading risks...")
    risk_triple_count = 0
    for risk in risks:
        rid = risk['riskId']
        uri = f"{FEEKG_NS}{rid}"

        # Type
        add_triple(uri, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                  f"{FEEKG_NS}Risk")
        risk_triple_count += 1

        # Properties
        add_triple(uri, f"{FEEKG_NS}type", risk['type'], is_literal=True)
        risk_triple_count += 1

        add_triple(uri, f"{FEEKG_NS}severity", risk['severity'], is_literal=True)
        risk_triple_count += 1

        add_triple(uri, f"{FEEKG_NS}score", str(risk['score']), is_literal=True)
        risk_triple_count += 1

        # Target entity
        if 'targetEntity' in risk:
            add_triple(uri, f"{FEEKG_NS}involves",
                      f"{FEEKG_NS}{risk['targetEntity']}")
            risk_triple_count += 1

    triple_count += risk_triple_count
    print(f"   ✓ Loaded {len(risks)} risks ({risk_triple_count} triples)")

    # Load Evolution Links (if available)
    print("\n5. Loading evolution links...")
    evolution_file = 'results/evolution_links.json'
    try:
        with open(evolution_file, 'r') as f:
            evolution_data = json.load(f)

        links = evolution_data.get('links', [])
        link_triple_count = 0

        for link in links[:20]:  # Load top 20 evolution links
            from_uri = f"{FEEKG_NS}{link['from']}"
            to_uri = f"{FEEKG_NS}{link['to']}"

            # Main evolution link
            add_triple(from_uri, f"{FEEKG_NS}evolvesTo", to_uri)
            link_triple_count += 1

            # Score as property (simplified - in reality would use reification)
            # For now, just add the main link

        triple_count += link_triple_count
        print(f"   ✓ Loaded {len(links[:20])} evolution links ({link_triple_count} triples)")
    except FileNotFoundError:
        print(f"   ⚠  Evolution links file not found, skipping...")

    # Summary
    print("\n" + "=" * 80)
    print(f"✅ Success! Loaded {triple_count} triples to AllegroGraph")
    print("=" * 80)

    # Verify
    print("\nVerifying upload...")
    response = requests.get(
        f'{AG_URL}/size',
        auth=HTTPBasicAuth(AG_USER, AG_PASS)
    )
    if response.status_code == 200:
        total_triples = int(response.text)
        print(f"Total triples in repository: {total_triples:,}")


if __name__ == '__main__':
    load_evergrande_data()
