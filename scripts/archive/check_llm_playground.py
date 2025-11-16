#!/usr/bin/env python3
"""
Check LLM Playground Repository

Examines the llm-playground-1 repository to see what's configured
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv('AG_URL', 'https://qa-agraph.nelumbium.ai/').rstrip('/')
user = os.getenv('AG_USER', 'sadmin')
password = os.getenv('AG_PASS')
auth = (user, password)

print("=" * 70)
print("LLM Playground Repository Check")
print("=" * 70)
print()

# Check if llm-playground-1 exists
print("1. Checking if llm-playground-1 exists...")

# List all repositories
try:
    response = requests.get(
        f'{base_url}/repositories',
        auth=auth,
        timeout=10
    )
    response.raise_for_status()

    repos = []
    for line in response.text.split('\n'):
        if line.startswith('id:'):
            repo_name = line.split(':', 1)[1].strip()
            repos.append(repo_name)

    if 'llm-playground-1' in repos:
        print("   ✓ llm-playground-1 EXISTS")
    else:
        print("   ✗ llm-playground-1 NOT FOUND")
        print(f"\n   Available repositories:")
        for repo in repos[:10]:
            print(f"      - {repo}")
        print("\n   To create LLM playground:")
        print("   1. Go to AllegroGraph web UI")
        print("   2. Click 'CREATE LLM PLAYGROUND' button")
        print("   3. Enter your OpenAI API key")
        exit(0)

except Exception as e:
    print(f"   ✗ Error checking repositories: {e}")
    exit(1)

# Check size of llm-playground-1
print("\n2. Checking llm-playground-1 size...")
try:
    response = requests.get(
        f'{base_url}/repositories/llm-playground-1/size',
        auth=auth,
        timeout=10
    )
    response.raise_for_status()
    count = int(response.text.strip())

    if count == 0:
        print(f"   ✓ Repository exists but is EMPTY (0 triples)")
        print("   This is normal for a fresh LLM playground")
    else:
        print(f"   ✓ Repository has {count:,} triples")

except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Check for LLM-specific data structures
print("\n3. Checking for LLM features...")

queries = {
    "Vector Database entries": "SELECT (COUNT(*) as ?c) WHERE { ?s ?p ?o . FILTER(CONTAINS(STR(?p), 'vector')) }",
    "NLQ query examples": "SELECT (COUNT(*) as ?c) WHERE { ?s a ?type . FILTER(CONTAINS(STR(?type), 'NLQ')) }",
    "SHACL shapes": "SELECT (COUNT(*) as ?c) WHERE { ?s a <http://www.w3.org/ns/shacl#NodeShape> . }",
}

for name, query in queries.items():
    try:
        response = requests.get(
            f'{base_url}/repositories/llm-playground-1',
            params={'query': query},
            headers={'Accept': 'application/sparql-results+json'},
            auth=auth,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        count = result['results']['bindings'][0]['c']['value']
        status = "✓" if int(count) > 0 else "✗"
        print(f"   {status} {name}: {count}")
    except Exception as e:
        print(f"   ? {name}: Unable to check")

# Summary and recommendations
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)

if count == 0:
    print("""
✓ llm-playground-1 repository exists and is ready to use!

Next steps to enable LLM features:

1. Open AllegroGraph WebView:
   https://qa-agraph.nelumbium.ai/repositories/llm-playground-1

2. Load some sample data OR copy data from FEEKG:
   - Option A: Copy FEEKG data to llm-playground-1
   - Option B: Enable LLM features directly in FEEKG

3. Create NLQ Vector Database:
   - In WebView, select "Natural Language (NL) to SPARQL"
   - Click "CREATE NLQ VDB & SHACL SHAPES"
   - Enter your OpenAI API key

4. Start asking natural language questions!

Recommended: Use FEEKG directly with LLM features
(llm-playground-1 is just for testing)
""")
else:
    print(f"""
✓ llm-playground-1 has {count:,} triples

The repository is already populated!
You can start using LLM features if configured.
""")

print("=" * 70)
