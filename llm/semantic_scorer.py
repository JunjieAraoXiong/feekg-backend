"""
Enhanced Semantic Similarity using Nemotron Embeddings

Replaces simple keyword matching with deep learning embeddings:
- NV-Embed-v2 for high-quality semantic similarity
- Financial domain-specific scoring
- Multi-modal similarity (events, entities, risks)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from .nemotron_client import NemotronClient


class SemanticScorer:
    """
    Compute semantic similarity using Nemotron embeddings

    Replaces evolution/methods.py keyword-based semantic scoring
    with embedding-based approach for higher accuracy
    """

    def __init__(self, client: Optional[NemotronClient] = None):
        """
        Initialize semantic scorer

        Args:
            client: NemotronClient instance (creates new if not provided)
        """
        self.client = client or NemotronClient()
        self._embedding_cache = {}  # Cache embeddings to reduce API calls

    def compute_event_similarity(
        self,
        event_a: Dict,
        event_b: Dict,
        use_cache: bool = True
    ) -> float:
        """
        Compute semantic similarity between two events

        Args:
            event_a: Event dict with 'type', 'description', etc.
            event_b: Event dict
            use_cache: Use embedding cache

        Returns:
            Similarity score (0.0-1.0)
        """
        # Construct event representations
        text_a = self._event_to_text(event_a)
        text_b = self._event_to_text(event_b)

        # Compute similarity
        return self.compute_text_similarity(text_a, text_b, use_cache=use_cache)

    def compute_text_similarity(
        self,
        text_a: str,
        text_b: str,
        use_cache: bool = True
    ) -> float:
        """
        Compute semantic similarity between two texts

        Args:
            text_a: First text
            text_b: Second text
            use_cache: Use embedding cache

        Returns:
            Cosine similarity score (0.0-1.0)
        """
        # Get embeddings
        emb_a = self._get_embedding(text_a, use_cache=use_cache)
        emb_b = self._get_embedding(text_b, use_cache=use_cache)

        # Compute cosine similarity
        return self._cosine_similarity(emb_a, emb_b)

    def compute_batch_similarity(
        self,
        texts: List[str],
        query: str
    ) -> List[float]:
        """
        Compute similarity between query and multiple texts

        Args:
            texts: List of texts to compare
            query: Query text

        Returns:
            List of similarity scores
        """
        # Get query embedding
        query_emb = self._get_embedding(query, use_cache=True)

        # Get text embeddings in batch
        text_embs = self._get_embeddings_batch(texts)

        # Compute similarities
        similarities = []
        for text_emb in text_embs:
            sim = self._cosine_similarity(query_emb, text_emb)
            similarities.append(sim)

        return similarities

    def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find top-k most similar texts to query

        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of results to return

        Returns:
            List of (index, similarity) tuples, sorted by similarity
        """
        similarities = self.compute_batch_similarity(candidates, query)

        # Get top-k indices
        indexed_scores = [(i, score) for i, score in enumerate(similarities)]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return indexed_scores[:top_k]

    def compute_event_evolution_similarity(
        self,
        event_a: Dict,
        event_b: Dict
    ) -> Dict[str, float]:
        """
        Compute multi-faceted similarity for event evolution

        Returns:
            Dict with different similarity aspects:
            {
                'description': float,  # Description similarity
                'type': float,         # Event type similarity
                'overall': float       # Weighted combination
            }
        """
        # Description similarity
        desc_a = event_a.get('description', '')
        desc_b = event_b.get('description', '')
        desc_sim = self.compute_text_similarity(desc_a, desc_b) if desc_a and desc_b else 0.0

        # Event type similarity
        type_a = event_a.get('type', '')
        type_b = event_b.get('type', '')
        type_sim = self.compute_text_similarity(type_a, type_b) if type_a and type_b else 0.0

        # Weighted combination
        overall = 0.7 * desc_sim + 0.3 * type_sim

        return {
            'description': desc_sim,
            'type': type_sim,
            'overall': overall
        }

    def compute_entity_similarity(
        self,
        entity_a: Dict,
        entity_b: Dict
    ) -> float:
        """
        Compute similarity between two entities

        Args:
            entity_a: Entity dict with 'name', 'type', etc.
            entity_b: Entity dict

        Returns:
            Similarity score (0.0-1.0)
        """
        # Exact name match gets perfect score
        if entity_a.get('name') == entity_b.get('name'):
            return 1.0

        # Otherwise compute semantic similarity
        text_a = f"{entity_a.get('name', '')} {entity_a.get('type', '')}"
        text_b = f"{entity_b.get('name', '')} {entity_b.get('type', '')}"

        return self.compute_text_similarity(text_a, text_b)

    def _event_to_text(self, event: Dict) -> str:
        """
        Convert event dict to text representation

        Args:
            event: Event dict

        Returns:
            Text representation for embedding
        """
        parts = []

        if 'type' in event:
            parts.append(f"Event type: {event['type']}")

        if 'description' in event:
            parts.append(event['description'])

        if 'actor' in event and 'target' in event:
            parts.append(f"{event['actor']} affects {event['target']}")

        return " ".join(parts)

    def _get_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Get embedding for text (with caching)

        Args:
            text: Input text
            use_cache: Use cache

        Returns:
            Embedding vector as numpy array
        """
        # Check cache
        if use_cache and text in self._embedding_cache:
            return self._embedding_cache[text]

        # Generate embedding
        embeddings = self.client.generate_embeddings([text], input_type='passage')
        embedding = np.array(embeddings[0])

        # Cache it
        if use_cache:
            self._embedding_cache[text] = embedding

        return embedding

    def _get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts in batch

        Args:
            texts: List of texts

        Returns:
            List of embedding vectors
        """
        # Check cache first
        uncached_texts = []
        uncached_indices = []

        embeddings = [None] * len(texts)

        for i, text in enumerate(texts):
            if text in self._embedding_cache:
                embeddings[i] = self._embedding_cache[text]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.client.generate_embeddings(uncached_texts, input_type='passage')

            for i, emb in zip(uncached_indices, new_embeddings):
                emb_array = np.array(emb)
                embeddings[i] = emb_array
                self._embedding_cache[texts[i]] = emb_array

        return embeddings

    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Cosine similarity (0.0-1.0)
        """
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)

        # Clamp to [0, 1]
        return float(max(0.0, min(1.0, similarity)))

    def clear_cache(self):
        """Clear embedding cache"""
        self._embedding_cache.clear()

    def get_cache_size(self) -> int:
        """Get number of cached embeddings"""
        return len(self._embedding_cache)


# Example usage
if __name__ == '__main__':
    try:
        scorer = SemanticScorer()

        # Example events
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

        print("=== Event Similarity ===")
        sim_ab = scorer.compute_event_similarity(event_a, event_b)
        print(f"Event A ↔ Event B: {sim_ab:.3f}")

        sim_ac = scorer.compute_event_similarity(event_a, event_c)
        print(f"Event A ↔ Event C: {sim_ac:.3f}")

        print("\n=== Multi-faceted Similarity ===")
        detailed = scorer.compute_event_evolution_similarity(event_a, event_b)
        print(f"Description: {detailed['description']:.3f}")
        print(f"Type: {detailed['type']:.3f}")
        print(f"Overall: {detailed['overall']:.3f}")

        print(f"\nCache size: {scorer.get_cache_size()} embeddings")

    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use this scorer, set NVIDIA_API_KEY in .env")
