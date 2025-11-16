"""
NVIDIA NIM Client for Nemotron Model Access

Provides interface to NVIDIA NIM microservices for:
- Nemotron model inference
- Embedding generation
- Triplet extraction
"""

import os
import json
import requests
from typing import List, Dict, Optional, Union
from datetime import datetime


class NemotronClient:
    """
    Client for NVIDIA NIM API

    Supports:
    - Text generation (Nemotron-4 340B, Llama-3 8B)
    - Embedding generation (NV-Embed-v2)
    - Custom fine-tuned models
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize NVIDIA NIM client

        Args:
            api_key: NVIDIA API key (from env if not provided)
            base_url: NIM endpoint URL (from env if not provided)
        """
        self.api_key = api_key or os.getenv('NVIDIA_API_KEY')
        self.base_url = base_url or os.getenv('NVIDIA_NIM_URL', 'https://integrate.api.nvidia.com/v1')

        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment or parameters")

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def generate_text(
        self,
        prompt: str,
        model: str = 'meta/llama-3.1-8b-instruct',
        max_tokens: int = 1024,
        temperature: float = 0.2,
        **kwargs
    ) -> Dict:
        """
        Generate text using NIM

        Args:
            prompt: Input prompt
            model: Model identifier
            max_tokens: Maximum response tokens
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional generation parameters

        Returns:
            Response dict with 'text' and metadata
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
            'temperature': temperature,
            **kwargs
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                'text': data['choices'][0]['message']['content'],
                'model': data.get('model'),
                'tokens': data.get('usage', {})
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"NIM API request failed: {e}")

    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        model: str = 'nvidia/nv-embedqa-e5-v5',
        input_type: str = 'passage'
    ) -> List[List[float]]:
        """
        Generate embeddings using NIM

        Args:
            texts: Single text or list of texts
            model: Embedding model identifier
            input_type: 'query' or 'passage'

        Returns:
            List of embedding vectors
        """
        url = f"{self.base_url}/embeddings"

        if isinstance(texts, str):
            texts = [texts]

        payload = {
            'model': model,
            'input': texts,
            'input_type': input_type
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            return [item['embedding'] for item in data['data']]
        except requests.exceptions.RequestException as e:
            raise Exception(f"NIM embeddings request failed: {e}")

    def extract_triplets_raw(
        self,
        text: str,
        model: str = 'meta/llama-3.1-8b-instruct',
        domain: str = 'financial'
    ) -> Dict:
        """
        Extract knowledge triplets from text using fine-tuned model

        This is a raw extraction - use TripletExtractor for higher-level interface

        Args:
            text: Input text to extract from
            model: Model identifier (use fine-tuned model for best results)
            domain: Domain context ('financial', 'general')

        Returns:
            Response with extracted triplets
        """
        # Construct prompt following NVIDIA GraphRAG pattern
        prompt = f"""Extract knowledge triplets from the following {domain} text.

For each relationship, identify:
- Subject (entity or event)
- Predicate (relationship type)
- Object (entity or event)

Return as JSON array: [{{"subject": "...", "predicate": "...", "object": "..."}}]

Text:
{text}

Triplets:"""

        response = self.generate_text(
            prompt=prompt,
            model=model,
            max_tokens=2048,
            temperature=0.1  # Low temperature for structured output
        )

        return response

    def compute_similarity(
        self,
        text1: str,
        text2: str,
        model: str = 'nvidia/nv-embedqa-e5-v5'
    ) -> float:
        """
        Compute semantic similarity between two texts

        Args:
            text1: First text
            text2: Second text
            model: Embedding model

        Returns:
            Cosine similarity score (0.0-1.0)
        """
        embeddings = self.generate_embeddings([text1, text2], model=model)

        # Cosine similarity
        import numpy as np
        vec1 = np.array(embeddings[0])
        vec2 = np.array(embeddings[1])

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(max(0.0, min(1.0, similarity)))  # Clamp to [0, 1]

    def health_check(self) -> Dict:
        """
        Check NIM API health

        Returns:
            Status dict
        """
        try:
            # Try a minimal generation request
            response = self.generate_text(
                prompt="Hello",
                max_tokens=10,
                temperature=0.0
            )
            return {
                'status': 'healthy',
                'model': response.get('model'),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Example usage
if __name__ == '__main__':
    # This requires NVIDIA_API_KEY in environment
    try:
        client = NemotronClient()

        # Test health
        health = client.health_check()
        print(f"Health: {health['status']}")

        # Test generation
        response = client.generate_text("What is financial risk?", max_tokens=100)
        print(f"\nGeneration: {response['text'][:100]}...")

        # Test embeddings
        emb = client.generate_embeddings("Financial risk assessment")
        print(f"\nEmbedding dimension: {len(emb[0])}")

        # Test similarity
        sim = client.compute_similarity(
            "Evergrande defaults on debt",
            "China Evergrande missed bond payment"
        )
        print(f"\nSimilarity: {sim:.3f}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use this client, set NVIDIA_API_KEY in .env")
        print("Get your API key from: https://build.nvidia.com")
