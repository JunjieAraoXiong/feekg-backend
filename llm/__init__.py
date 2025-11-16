"""
FE-EKG LLM Integration Module

Integrates NVIDIA NIM and Nemotron for:
1. Triplet extraction from financial news
2. Enhanced semantic similarity
3. Natural language query interface
4. Event classification and entity recognition
"""

from .triplet_extractor import TripletExtractor
from .nemotron_client import NemotronClient
from .semantic_scorer import SemanticScorer

__all__ = ['TripletExtractor', 'NemotronClient', 'SemanticScorer']
