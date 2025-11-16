#!/bin/bash
# Setup Apache Jena Fuseki (RDF Database)

echo "========================================================================"
echo "  Installing Apache Jena Fuseki"
echo "========================================================================"

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Installing..."
    brew install openjdk@17
else
    echo "✅ Java found: $(java -version 2>&1 | head -n 1)"
fi

# Download Fuseki
FUSEKI_VERSION="5.0.0"
FUSEKI_DIR="apache-jena-fuseki-${FUSEKI_VERSION}"
FUSEKI_TAR="${FUSEKI_DIR}.tar.gz"

if [ ! -d "$FUSEKI_DIR" ]; then
    echo ""
    echo "Downloading Fuseki ${FUSEKI_VERSION}..."
    curl -LO "https://dlcdn.apache.org/jena/binaries/${FUSEKI_TAR}"

    echo "Extracting..."
    tar -xzf "$FUSEKI_TAR"
    rm "$FUSEKI_TAR"
fi

cd "$FUSEKI_DIR"

echo ""
echo "========================================================================"
echo "  Starting Fuseki Server"
echo "========================================================================"
echo ""
echo "Web UI will be at: http://localhost:3030"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================================================"
echo ""

# Start Fuseki server
./fuseki-server --update --mem /feekg
