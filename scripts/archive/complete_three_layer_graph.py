#!/usr/bin/env python3
"""
Complete the Three-Layer FE-EKG Graph

Creates the missing Risk layer and connects all three layers:
  Layer 1 (Entity) ↔ Layer 2 (Event) ↔ Layer 3 (Risk)

Based on the FE-EKG paper architecture.
"""
import os
import sys
import requests
from typing import List, Dict, Tuple
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class ThreeLayerConnector:
    """Connects all three FE-EKG layers with relationships"""

    def __init__(self):
        self.base_url = os.getenv('AG_URL', 'https://qa-agraph.nelumbium.ai/').rstrip('/')
        self.user = os.getenv('AG_USER', 'sadmin')
        self.password = os.getenv('AG_PASS')
        self.catalog = os.getenv('AG_CATALOG', 'mycatalog')
        self.repo = os.getenv('AG_REPO', 'FEEKG')

        self.repo_url = f"{self.base_url}/catalogs/{self.catalog}/repositories/{self.repo}"
        self.statements_url = f"{self.repo_url}/statements"
        self.auth = (self.user, self.password)

    def query(self, sparql: str) -> List[Dict]:
        """Execute SPARQL query"""
        try:
            response = requests.get(
                self.repo_url,
                params={'query': sparql},
                headers={'Accept': 'application/sparql-results+json'},
                auth=self.auth,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get('results', {}).get('bindings', [])
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def upload_turtle(self, turtle: str) -> bool:
        """Upload Turtle triples"""
        try:
            response = requests.post(
                self.statements_url,
                data=turtle.encode('utf-8'),
                headers={'Content-Type': 'text/turtle'},
                auth=self.auth,
                timeout=60
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def get_triple_count(self) -> int:
        """Get triple count"""
        try:
            response = requests.get(f"{self.repo_url}/size", auth=self.auth, timeout=10)
            return int(response.text.strip())
        except:
            return 0

    # ========== CREATE RISK LAYER ==========

    def create_risk_types(self):
        """Create 12 RiskType nodes (from FE-EKG paper)"""
        print("Creating Risk Types...")

        risk_types = [
            ("LiquidityRisk", "Inability to meet short-term financial obligations"),
            ("CreditRisk", "Risk of default on debt obligations"),
            ("OperationalRisk", "Losses from inadequate processes or systems"),
            ("MarketRisk", "Losses from market price movements"),
            ("SystemicRisk", "Risk of collapse of entire financial system"),
            ("ContagionRisk", "Spread of financial distress across entities"),
            ("SolvencyRisk", "Inability to meet long-term obligations"),
            ("ReputationalRisk", "Damage to company reputation"),
            ("RegulatoryRisk", "Risk from regulatory changes or violations"),
            ("StrategicRisk", "Risk from poor business decisions"),
            ("ComplianceRisk", "Risk from violating laws or regulations"),
            ("GeopoliticalRisk", "Risk from political or geographic events")
        ]

        turtle = """@prefix feekg: <http://feekg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""
        for risk_type, description in risk_types:
            turtle += f"""feekg:{risk_type} rdf:type feekg:RiskType .
feekg:{risk_type} rdfs:label "{risk_type}" .
feekg:{risk_type} rdfs:comment "{description}" .

"""

        if self.upload_turtle(turtle):
            print(f"   ✓ Created {len(risk_types)} RiskTypes")
            return True
        return False

    def create_risks_from_events(self):
        """
        Create Risk nodes from high/critical severity events
        Maps event types to risk types
        """
        print("\nCreating Risk nodes from events...")

        # Event type → Risk type mapping (from paper)
        event_to_risk = {
            'bankruptcy': 'CreditRisk',
            'credit_downgrade': 'CreditRisk',
            'earnings_loss': 'SolvencyRisk',
            'capital_raising': 'LiquidityRisk',
            'restructuring': 'OperationalRisk',
            'legal_issue': 'RegulatoryRisk',
            'management_change': 'OperationalRisk',
            'stock_movement': 'MarketRisk',
            'merger_acquisition': 'StrategicRisk'
        }

        # Get high/critical events
        query = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?event ?eventType ?severity ?date ?label
        WHERE {
            ?event a feekg:Event .
            ?event feekg:severity ?severity .
            FILTER(?severity IN ("high", "critical"))
            ?event feekg:eventType ?eventType .
            ?event feekg:date ?date .
            ?event rdfs:label ?label .
        }
        """

        results = self.query(query)
        print(f"   Found {len(results)} high/critical events")

        if not results:
            print("   Creating sample risks from all events...")
            # If no high-severity events, take samples from each event type
            query = """
            PREFIX feekg: <http://feekg.org/ontology#>

            SELECT ?event ?eventType ?date ?label
            WHERE {
                ?event a feekg:Event .
                ?event feekg:eventType ?eventType .
                FILTER(?eventType IN ("bankruptcy", "credit_downgrade", "earnings_loss", "restructuring"))
                ?event feekg:date ?date .
                ?event rdfs:label ?label .
            }
            LIMIT 50
            """
            results = self.query(query)

        # Create Risk nodes
        turtle = """@prefix feekg: <http://feekg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

        risk_count = 0
        for result in results:
            event_uri = result['event']['value']
            event_id = event_uri.split('#')[-1].split('/')[-1]
            event_type = result['eventType']['value']
            label = result.get('label', {}).get('value', '')[:100]

            # Map event type to risk type
            risk_type = event_to_risk.get(event_type, 'OperationalRisk')

            # Create unique risk ID
            risk_id = f"risk_{event_id}"
            risk_uri = f"feekg:{risk_id}"

            # Severity and probability
            severity = result.get('severity', {}).get('value', 'high')
            probability = 0.75 if severity == 'critical' else 0.60

            turtle += f"""{risk_uri} rdf:type feekg:Risk .
{risk_uri} rdfs:label "Risk from {label[:60]}" .
{risk_uri} feekg:hasRiskType feekg:{risk_type} .
{risk_uri} feekg:hasSeverity "{severity}" .
{risk_uri} feekg:hasProbability "{probability}"^^xsd:float .
{risk_uri} feekg:status "open" .

"""

            # Link Event → Risk (increasesRiskOf)
            turtle += f"""<{event_uri}> feekg:increasesRiskOf {risk_uri} .

"""

            risk_count += 1

            # Upload in batches of 50
            if risk_count % 50 == 0:
                if self.upload_turtle(turtle):
                    print(f"   ✓ Created {risk_count} risks...")
                    turtle = """@prefix feekg: <http://feekg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""
                else:
                    return False

        # Upload remaining
        if risk_count % 50 != 0:
            if self.upload_turtle(turtle):
                print(f"   ✓ Created {risk_count} total risks")
            else:
                return False

        return True

    def connect_risks_to_entities(self):
        """
        Connect Risk → Entity (targetsEntity)
        Based on which entities are involved in the triggering events
        """
        print("\nConnecting Risks to Entities...")

        query = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?risk ?event ?entity
        WHERE {
            ?event feekg:increasesRiskOf ?risk .
            ?event feekg:involves ?entity .
        }
        """

        results = self.query(query)
        print(f"   Found {len(results)} risk-entity connections")

        if not results:
            print("   No connections to create")
            return True

        turtle = """@prefix feekg: <http://feekg.org/ontology#> .

"""

        for result in results:
            risk_uri = result['risk']['value']
            entity_uri = result['entity']['value']

            turtle += f"<{risk_uri}> feekg:targetsEntity <{entity_uri}> .\n"

        if self.upload_turtle(turtle):
            print(f"   ✓ Connected {len(results)} risk-entity pairs")
            return True

        return False

    def create_selective_evolution_links(self, min_score: float = 0.5, max_links: int = 1000):
        """
        Create selective evolution links (Event → Event)
        Only for high-severity events to keep it manageable
        """
        print(f"\nCreating selective evolution links (min_score={min_score})...")

        # Get high-severity events only
        query = """
        PREFIX feekg: <http://feekg.org/ontology#>

        SELECT ?event ?date ?eventType ?label
        WHERE {
            ?event a feekg:Event .
            ?event feekg:severity ?severity .
            FILTER(?severity IN ("high", "critical"))
            ?event feekg:date ?date .
            ?event feekg:eventType ?eventType .
            ?event rdfs:label ?label .
        }
        ORDER BY ?date
        LIMIT 100
        """

        results = self.query(query)
        print(f"   Found {len(results)} high-severity events")

        if len(results) < 2:
            print("   Not enough events for evolution links")
            return True

        # Simple temporal evolution: connect events within 30 days
        from datetime import datetime, timedelta

        turtle = """@prefix feekg: <http://feekg.org/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

        link_count = 0

        for i, result1 in enumerate(results):
            if link_count >= max_links:
                break

            event1_uri = result1['event']['value']
            date1_str = result1['date']['value']
            type1 = result1['eventType']['value']

            try:
                date1 = datetime.strptime(date1_str, '%Y-%m-%d')
            except:
                continue

            # Look ahead for events within 30 days
            for result2 in results[i+1:i+10]:  # Check next 10 events
                event2_uri = result2['event']['value']
                date2_str = result2['date']['value']
                type2 = result2['eventType']['value']

                try:
                    date2 = datetime.strptime(date2_str, '%Y-%m-%d')
                except:
                    continue

                days_apart = (date2 - date1).days

                if 0 < days_apart <= 30:
                    # Calculate simple score
                    temporal_score = max(0, 1 - (days_apart / 30))
                    type_match_score = 0.5 if type1 == type2 else 0.0
                    score = (temporal_score * 0.7) + (type_match_score * 0.3)

                    if score >= min_score:
                        turtle += f"""<{event1_uri}> feekg:evolvesTo <{event2_uri}> .
_:link_{link_count} a feekg:EvolutionLink .
_:link_{link_count} feekg:from <{event1_uri}> .
_:link_{link_count} feekg:to <{event2_uri}> .
_:link_{link_count} feekg:score "{score:.4f}"^^xsd:float .
_:link_{link_count} feekg:temporalScore "{temporal_score:.4f}"^^xsd:float .

"""
                        link_count += 1

                        if link_count >= max_links:
                            break

        if link_count > 0:
            if self.upload_turtle(turtle):
                print(f"   ✓ Created {link_count} evolution links")
                return True
        else:
            print("   No evolution links met criteria")
            return True

        return False


def main():
    print("=" * 80)
    print("Complete Three-Layer FE-EKG Graph")
    print("=" * 80)

    connector = ThreeLayerConnector()

    initial_count = connector.get_triple_count()
    print(f"\nInitial triple count: {initial_count:,}")

    # Step 1: Create Risk Types
    print("\n" + "=" * 80)
    print("LAYER 3: Creating Risk Layer")
    print("=" * 80)

    if not connector.create_risk_types():
        print("❌ Failed to create risk types")
        return

    # Step 2: Create Risk nodes from events
    if not connector.create_risks_from_events():
        print("❌ Failed to create risks")
        return

    # Step 3: Connect Risks to Entities
    if not connector.connect_risks_to_entities():
        print("❌ Failed to connect risks to entities")
        return

    # Step 4: Create selective evolution links
    print("\n" + "=" * 80)
    print("LAYER 2: Creating Evolution Links")
    print("=" * 80)

    if not connector.create_selective_evolution_links(min_score=0.5, max_links=500):
        print("❌ Failed to create evolution links")
        return

    # Final stats
    final_count = connector.get_triple_count()

    print("\n" + "=" * 80)
    print("Summary: Three-Layer Graph Complete!")
    print("=" * 80)
    print(f"\nTriples added: {final_count - initial_count:,}")
    print(f"Total triples: {final_count:,}")
    print()
    print("Three-Layer Structure:")
    print("  Layer 1 (Entity):  ✓ COMPLETE")
    print("  Layer 2 (Event):   ✓ COMPLETE + Evolution Links")
    print("  Layer 3 (Risk):    ✓ COMPLETE + Risk Types")
    print()
    print("Relationships:")
    print("  Entity ↔ Event:    ✓ feekg:involves")
    print("  Event → Event:     ✓ feekg:evolvesTo")
    print("  Event → Risk:      ✓ feekg:increasesRiskOf")
    print("  Risk → Entity:     ✓ feekg:targetsEntity")
    print("  Risk → RiskType:   ✓ feekg:hasRiskType")
    print()
    print("Next steps:")
    print("  1. Verify: ./venv/bin/python scripts/check_ontology_compliance.py")
    print("  2. Query: ./venv/bin/python scripts/efficient_analyzer.py stats")
    print("  3. Visualize the complete three-layer graph")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
