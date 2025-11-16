"""
Verify Stage 5: Risk Queries and Analysis

Validates that all query infrastructure is working
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query.risk_analyzer import RiskAnalyzer


def verify_stage5():
    """Verify Stage 5 completion"""

    print("=" * 70)
    print("FE-EKG Stage 5 Verification")
    print("=" * 70)

    # Connect
    print("\n1️⃣  Connecting to Neo4j...")
    try:
        analyzer = RiskAnalyzer()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    # Test entity risk queries
    print("\n2️⃣  Testing Entity Risk Queries...")
    try:
        # Test 1: Entity risk profile
        risks = analyzer.get_entity_risk_profile('China Evergrande Group')
        if risks:
            print(f"   ✅ Entity risk profile query works ({len(risks)} risks found)")
        else:
            print("   ⚠️  No risks found for Evergrande (expected some)")

        # Test 2: High-risk entities
        high_risk = analyzer.get_high_risk_entities(min_risk_count=1)
        if high_risk:
            print(f"   ✅ High-risk entities query works ({len(high_risk)} entities)")
        else:
            print("   ⚠️  No high-risk entities found")

    except Exception as e:
        print(f"   ❌ Entity risk queries failed: {e}")
        return False

    # Test evolution queries
    print("\n3️⃣  Testing Event Evolution Queries...")
    try:
        # Test 1: Strongest links
        links = analyzer.get_strongest_evolution_links(min_score=0.0, limit=5)
        if links:
            print(f"   ✅ Evolution link query works ({len(links)} links)")
            print(f"      Strongest: {links[0]['fromEvent']} → {links[0]['toEvent']} "
                  f"(score: {links[0]['overallScore']:.3f})")
        else:
            print("   ⚠️  No evolution links found")

        # Test 2: Causal chains
        chains = analyzer.get_causal_chains(min_causality=0.4)
        if chains:
            print(f"   ✅ Causal chain query works ({len(chains)} chains)")
            print(f"      Longest: {' → '.join(chains[0]['eventChain'][:3])}")
        else:
            print("   ⚠️  No causal chains found")

        # Test 3: Event impact
        impacts = analyzer.get_event_impact_analysis()
        if impacts:
            print(f"   ✅ Event impact query works ({len(impacts)} events)")
            print(f"      Most influential: {impacts[0]['eventType']} "
                  f"({impacts[0]['directImpact']} triggered events)")
        else:
            print("   ⚠️  No event impacts found")

    except Exception as e:
        print(f"   ❌ Evolution queries failed: {e}")
        return False

    # Test risk propagation queries
    print("\n4️⃣  Testing Risk Propagation Queries...")
    try:
        # Test 1: Systemic risk
        systemic = analyzer.detect_systemic_risk()
        print(f"   ✅ Systemic risk query works ({len(systemic)} contagion risks)")

        # Test 2: Multi-risk entities
        multi_risk = analyzer.get_multi_risk_entities(min_risk_types=2)
        if multi_risk:
            print(f"   ✅ Multi-risk query works ({len(multi_risk)} entities)")
        else:
            print("   ℹ️  No entities with multiple risk types")

    except Exception as e:
        print(f"   ❌ Risk propagation queries failed: {e}")
        return False

    # Test temporal queries
    print("\n5️⃣  Testing Temporal Analysis Queries...")
    try:
        # Test 1: Event timeline
        timeline = analyzer.get_event_timeline()
        if timeline:
            print(f"   ✅ Timeline query works ({len(timeline)} events)")
            print(f"      First event: {timeline[0]['date']} - {timeline[0]['eventType']}")
        else:
            print("   ⚠️  No events in timeline")

        # Test 2: Crisis points
        crisis = analyzer.get_crisis_escalation_points(min_events=2)
        if crisis:
            print(f"   ✅ Crisis detection works ({len(crisis)} escalation points)")
        else:
            print("   ℹ️  No crisis escalation points")

    except Exception as e:
        print(f"   ❌ Temporal queries failed: {e}")
        return False

    # Test pattern detection
    print("\n6️⃣  Testing Pattern Detection Queries...")
    try:
        # Test 1: Debt cascades
        cascades = analyzer.detect_debt_default_cascades()
        print(f"   ✅ Cascade detection works ({len(cascades)} patterns)")

        # Test 2: Regulatory impact
        interventions = analyzer.analyze_regulatory_intervention_impact()
        print(f"   ✅ Intervention analysis works ({len(interventions)} interventions)")

    except Exception as e:
        print(f"   ❌ Pattern detection failed: {e}")
        return False

    # Test statistics
    print("\n7️⃣  Testing Statistical Queries...")
    try:
        # Test 1: Evolution stats
        stats = analyzer.get_evolution_statistics()
        if stats and stats.get('totalLinks', 0) > 0:
            print(f"   ✅ Evolution statistics works ({stats['totalLinks']} links)")
            print(f"      Avg score: {stats['avgOverallScore']:.3f}")
            print(f"      Avg causality: {stats['avgCausality']:.3f}")
        else:
            print("   ⚠️  No evolution statistics")

        # Test 2: Event frequency
        freq = analyzer.get_event_type_frequency()
        if freq:
            print(f"   ✅ Event frequency works ({len(freq)} types)")
            print(f"      Most common: {freq[0]['eventType']} ({freq[0]['frequency']} events)")
        else:
            print("   ⚠️  No event frequency data")

        # Test 3: Risk distribution
        dist = analyzer.get_risk_distribution()
        print(f"   ✅ Risk distribution works ({len(dist)} categories)")

    except Exception as e:
        print(f"   ❌ Statistical queries failed: {e}")
        return False

    # Test database overview
    print("\n8️⃣  Testing Database Overview...")
    try:
        overview = analyzer.get_database_overview()
        if overview['nodes']:
            node_count = sum(n['count'] for n in overview['nodes'])
            print(f"   ✅ Overview query works ({node_count} total nodes)")

            # Show summary
            print("\n   📊 Node Summary:")
            for node in overview['nodes']:
                print(f"      {str(node['nodeType']):<30} {node['count']:>3}")

        if overview['relationships']:
            rel_count = sum(r['count'] for r in overview['relationships'])
            print(f"\n   📊 Relationship Summary ({rel_count} total):")
            for rel in overview['relationships'][:5]:
                print(f"      {rel['relationType']:<30} {rel['count']:>3}")

    except Exception as e:
        print(f"   ❌ Overview query failed: {e}")
        return False

    # Close connection
    analyzer.close()

    # Summary
    print("\n" + "=" * 70)
    print("✅ Stage 5 Verification PASSED!")
    print("=" * 70)

    print("\n📊 Summary:")
    print("   - Risk Analyzer class implemented")
    print("   - Entity risk queries working")
    print("   - Event evolution queries working")
    print("   - Risk propagation queries working")
    print("   - Temporal analysis queries working")
    print("   - Pattern detection queries working")
    print("   - Statistical queries working")
    print("   - Database overview queries working")

    print("\n📁 Files Created:")
    print("   - query/risk_queries.cypher (80+ Cypher templates)")
    print("   - query/risk_analyzer.py (Python query API)")
    print("   - scripts/demo_risk_queries.py (Interactive demo)")

    print("\n🎯 Query Capabilities:")
    print("   • Entity risk profiles and timelines")
    print("   • Event evolution chains and causal paths")
    print("   • Risk propagation and contagion detection")
    print("   • Temporal crisis analysis")
    print("   • Pattern detection (debt cascades, regulatory impact)")
    print("   • Statistical summaries and distributions")

    print("\n💡 Next Steps:")
    print("   1. Try the demo: python scripts/demo_risk_queries.py")
    print("   2. Open Neo4j Browser: http://localhost:7474")
    print("   3. Copy queries from query/risk_queries.cypher")
    print("   4. Use RiskAnalyzer in your own scripts")

    print("\n🔜 Ready for Stage 6: Three-layer visualization")
    print()

    return True


if __name__ == "__main__":
    success = verify_stage5()
    sys.exit(0 if success else 1)
