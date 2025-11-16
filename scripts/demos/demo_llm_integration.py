#!/usr/bin/env python3
"""
Demo: LLM/Nemotron Integration

Demonstrates:
1. Triplet extraction from financial news
2. Enhanced semantic similarity with embeddings
3. Event/entity extraction
4. Comparison with baseline methods

Requirements:
- NVIDIA_API_KEY in .env
- Get API key from: https://build.nvidia.com
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import TripletExtractor, NemotronClient, SemanticScorer


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_triplet_extraction():
    """Demo triplet extraction from financial news"""
    print_header("1. TRIPLET EXTRACTION")

    sample_text = """
    China Evergrande Group, once China's largest property developer, defaulted on
    its offshore bonds in December 2021. The default triggered a liquidity crisis
    that spread to other property developers. Standard & Poor's downgraded
    Evergrande's credit rating to 'selective default'. The Chinese government
    intervened to prevent systemic financial contagion.
    """

    try:
        extractor = TripletExtractor()

        print("\n📝 Input Text:")
        print(sample_text.strip())

        print("\n🔗 Extracted Triplets:")
        triplets = extractor.extract_from_text(sample_text, source='demo')

        if not triplets:
            print("   (No triplets extracted - check NVIDIA_API_KEY)")
            return

        for i, t in enumerate(triplets, 1):
            print(f"\n   {i}. {t['subject']} --[{t['predicate']}]--> {t['object']}")
            print(f"      Type: {t['subject_type']} → {t['object_type']}")
            print(f"      Confidence: {t['confidence']:.2f}")

        print(f"\n✅ Total triplets extracted: {len(triplets)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 To use LLM features, set NVIDIA_API_KEY in .env")
        print("   Get your API key from: https://build.nvidia.com")


def demo_event_extraction():
    """Demo event extraction"""
    print_header("2. EVENT EXTRACTION")

    sample_text = """
    On August 20, 2020, the Chinese government introduced the 'Three Red Lines'
    policy, tightening regulations on property developers. China Evergrande Group
    struggled to meet these requirements. By September 2021, Evergrande missed
    bond payments, causing credit rating downgrades. The People's Bank of China
    injected liquidity in December 2021 to stabilize the market.
    """

    try:
        extractor = TripletExtractor()

        print("\n📝 Input Text:")
        print(sample_text.strip())

        print("\n📅 Extracted Events:")
        events = extractor.extract_events(sample_text, source='demo')

        if not events:
            print("   (No events extracted - check NVIDIA_API_KEY)")
            return

        for i, event in enumerate(events, 1):
            print(f"\n   {i}. {event.get('type', 'unknown').upper()}")
            print(f"      Date: {event.get('date', 'N/A')}")
            print(f"      Actor: {event.get('actor', 'N/A')}")
            print(f"      Target: {event.get('target', 'N/A')}")
            print(f"      Description: {event.get('description', 'N/A')}")

        print(f"\n✅ Total events extracted: {len(events)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_entity_extraction():
    """Demo entity extraction"""
    print_header("3. ENTITY EXTRACTION")

    sample_text = """
    China Evergrande Group, based in Shenzhen, is China's second-largest property
    developer. The People's Bank of China (PBOC) and the China Banking and Insurance
    Regulatory Commission (CBIRC) are key regulators. Standard & Poor's and Fitch
    Ratings downgraded Evergrande's credit rating. China Minsheng Bank is among
    the exposed creditors.
    """

    try:
        extractor = TripletExtractor()

        print("\n📝 Input Text:")
        print(sample_text.strip())

        print("\n🏢 Extracted Entities:")
        entities = extractor.extract_entities(sample_text)

        if not entities:
            print("   (No entities extracted - check NVIDIA_API_KEY)")
            return

        for i, entity in enumerate(entities, 1):
            print(f"\n   {i}. {entity['name']}")
            print(f"      Type: {entity['type']}")
            print(f"      Mentions: {entity.get('mentions', 0)}")
            print(f"      Context: {entity.get('context', 'N/A')}")

        print(f"\n✅ Total entities extracted: {len(entities)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_semantic_similarity():
    """Demo enhanced semantic similarity"""
    print_header("4. SEMANTIC SIMILARITY (Embedding-Based)")

    event_a = {
        'type': 'debt_default',
        'description': 'China Evergrande Group defaulted on offshore bonds'
    }

    event_b = {
        'type': 'credit_downgrade',
        'description': 'Credit rating agencies downgraded Evergrande to junk status'
    }

    event_c = {
        'type': 'regulatory_pressure',
        'description': 'Government introduced new property market regulations'
    }

    try:
        scorer = SemanticScorer()

        print("\n📊 Event Comparison:")
        print(f"\n   Event A: {event_a['type']}")
        print(f"   → {event_a['description']}")

        print(f"\n   Event B: {event_b['type']}")
        print(f"   → {event_b['description']}")

        print(f"\n   Event C: {event_c['type']}")
        print(f"   → {event_c['description']}")

        print("\n🔍 Similarity Scores:")
        sim_ab = scorer.compute_event_similarity(event_a, event_b)
        print(f"\n   Event A ↔ Event B: {sim_ab:.3f}")
        print(f"   (Related events in same crisis)")

        sim_ac = scorer.compute_event_similarity(event_a, event_c)
        print(f"\n   Event A ↔ Event C: {sim_ac:.3f}")
        print(f"   (Different event types)")

        print("\n📈 Multi-faceted Analysis (A ↔ B):")
        detailed = scorer.compute_event_evolution_similarity(event_a, event_b)
        print(f"   Description similarity: {detailed['description']:.3f}")
        print(f"   Type similarity: {detailed['type']:.3f}")
        print(f"   Overall score: {detailed['overall']:.3f}")

        print(f"\n💾 Cache: {scorer.get_cache_size()} embeddings cached")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_baseline_comparison():
    """Compare embedding-based vs keyword-based similarity"""
    print_header("5. BASELINE COMPARISON")

    print("\n⚠️  This comparison requires evolution/methods.py")
    print("    Skipping for now - will be integrated in evolution module")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  FE-EKG LLM/Nemotron Integration Demo")
    print("=" * 70)
    print("\n  Demonstrates NVIDIA NIM integration for:")
    print("  • Automatic triplet extraction from financial news")
    print("  • Event and entity recognition")
    print("  • Enhanced semantic similarity with embeddings")
    print("\n" + "=" * 70)

    # Check API key
    api_key = os.getenv('NVIDIA_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("\n⚠️  WARNING: NVIDIA_API_KEY not configured!")
        print("\n   To run this demo:")
        print("   1. Get API key from: https://build.nvidia.com")
        print("   2. Add to .env: NVIDIA_API_KEY=your_key_here")
        print("\n   Demos will show expected behavior but may fail.\n")
    else:
        print(f"\n✅ NVIDIA_API_KEY configured: {api_key[:10]}...")

    # Run demos
    demo_triplet_extraction()
    demo_event_extraction()
    demo_entity_extraction()
    demo_semantic_similarity()
    demo_baseline_comparison()

    # Summary
    print_header("SUMMARY")
    print("\n✅ LLM integration module ready!")
    print("\n📚 Next steps:")
    print("   1. Get NVIDIA API key from: https://build.nvidia.com")
    print("   2. Update .env with your API key")
    print("   3. Run this demo again to test functionality")
    print("   4. Integrate with evolution module (replace keyword matching)")
    print("   5. Add API endpoints for LLM features")
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
