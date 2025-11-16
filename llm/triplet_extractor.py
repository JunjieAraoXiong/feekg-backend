"""
Financial Triplet Extraction

Implements NVIDIA GraphRAG triplet extraction pattern:
- Text → LLM → Structured triplets → Graph database
- Achieves 98% accuracy with fine-tuned Llama-3 8B
- Handles financial domain-specific entity/event recognition
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from .nemotron_client import NemotronClient


class TripletExtractor:
    """
    Extract knowledge triplets from financial text

    Based on NVIDIA GraphRAG methodology:
    1. Prompt engineering for financial domain
    2. LLM-based extraction (Nemotron/Llama-3)
    3. Post-processing and validation
    4. Graph database ingestion
    """

    def __init__(self, client: Optional[NemotronClient] = None):
        """
        Initialize triplet extractor

        Args:
            client: NemotronClient instance (creates new if not provided)
        """
        self.client = client or NemotronClient()

        # Financial event types from FE-EKG taxonomy
        self.event_types = {
            'regulatory_pressure', 'liquidity_crisis', 'debt_default',
            'credit_downgrade', 'asset_sale', 'restructuring',
            'market_reaction', 'contagion', 'government_intervention'
        }

        # Financial relationship types
        self.relation_types = {
            'EVOLVES_TO', 'CAUSES', 'IMPACTS', 'TARGETS_ENTITY',
            'HAS_RISK_TYPE', 'MITIGATES', 'AMPLIFIES', 'PRECEDES'
        }

    def extract_from_text(
        self,
        text: str,
        source: Optional[str] = None,
        date: Optional[str] = None,
        model: str = 'meta/llama-3.1-8b-instruct'
    ) -> List[Dict]:
        """
        Extract triplets from financial text

        Args:
            text: Input text (news article, report, etc.)
            source: Source identifier (URL, document ID)
            date: Publication date (YYYY-MM-DD)
            model: LLM model to use

        Returns:
            List of triplet dicts with structure:
            {
                'subject': str,
                'subject_type': str,  # 'entity' or 'event'
                'predicate': str,
                'object': str,
                'object_type': str,
                'confidence': float,
                'context': str,
                'source': str,
                'date': str
            }
        """
        # Construct domain-specific prompt
        prompt = self._build_extraction_prompt(text)

        # Call LLM
        try:
            response = self.client.generate_text(
                prompt=prompt,
                model=model,
                max_tokens=2048,
                temperature=0.1
            )

            # Parse response
            raw_triplets = self._parse_llm_response(response['text'])

            # Post-process and validate
            validated_triplets = []
            for triplet in raw_triplets:
                validated = self._validate_and_enrich_triplet(
                    triplet, text, source, date
                )
                if validated:
                    validated_triplets.append(validated)

            return validated_triplets

        except Exception as e:
            print(f"Warning: Triplet extraction failed: {e}")
            return []

    def extract_events(
        self,
        text: str,
        source: Optional[str] = None,
        date: Optional[str] = None
    ) -> List[Dict]:
        """
        Extract financial events from text

        Returns:
            List of event dicts matching FE-EKG Event schema:
            {
                'type': str,
                'date': str,
                'actor': str,
                'target': str,
                'description': str,
                'source': str,
                'confidence': float
            }
        """
        prompt = f"""Extract financial events from the following text.

For each event, identify:
- Event type (e.g., debt_default, credit_downgrade, regulatory_pressure)
- Date (if mentioned)
- Actor (who initiated the event)
- Target (who/what was affected)
- Brief description

Return as JSON array: [{{"type": "...", "date": "...", "actor": "...", "target": "...", "description": "..."}}]

Text:
{text}

Events (JSON):"""

        try:
            response = self.client.generate_text(
                prompt=prompt,
                max_tokens=2048,
                temperature=0.1
            )

            events = self._parse_json_response(response['text'])

            # Enrich with metadata
            for event in events:
                event['source'] = source or 'unknown'
                event['extracted_at'] = datetime.utcnow().isoformat()
                event['confidence'] = 0.85  # Default confidence

                # Normalize event type
                event['type'] = self._normalize_event_type(event.get('type', 'unknown'))

            return events

        except Exception as e:
            print(f"Warning: Event extraction failed: {e}")
            return []

    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Extract financial entities from text

        Args:
            text: Input text
            entity_types: Filter by types (e.g., ['company', 'bank', 'regulator'])

        Returns:
            List of entity dicts:
            {
                'name': str,
                'type': str,
                'mentions': int,
                'context': str
            }
        """
        entity_filter = ""
        if entity_types:
            entity_filter = f"\nEntity types to extract: {', '.join(entity_types)}"

        prompt = f"""Extract financial entities from the following text.

For each entity, identify:
- Name (official name)
- Type (company, bank, regulator, government, etc.)
- Context (brief description of their role)
{entity_filter}

Return as JSON array: [{{"name": "...", "type": "...", "context": "..."}}]

Text:
{text}

Entities (JSON):"""

        try:
            response = self.client.generate_text(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.1
            )

            entities = self._parse_json_response(response['text'])

            # Count mentions
            for entity in entities:
                entity['mentions'] = text.lower().count(entity['name'].lower())

            return entities

        except Exception as e:
            print(f"Warning: Entity extraction failed: {e}")
            return []

    def _build_extraction_prompt(self, text: str) -> str:
        """Construct prompt for triplet extraction"""
        return f"""You are a financial knowledge graph expert. Extract knowledge triplets from the following text.

For each relationship, identify:
- Subject (entity or event)
- Predicate (relationship type: EVOLVES_TO, CAUSES, IMPACTS, etc.)
- Object (entity or event)

Focus on:
- Financial events and their evolution
- Entity relationships
- Risk propagation
- Causal relationships

Return ONLY a valid JSON array with this exact format:
[{{"subject": "China Evergrande", "predicate": "CAUSES", "object": "liquidity crisis"}}]

Text:
{text}

JSON triplets:"""

    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parse LLM response into triplet list"""
        # Try to find JSON array in response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            try:
                triplets = json.loads(json_match.group())
                if isinstance(triplets, list):
                    return triplets
            except json.JSONDecodeError:
                pass

        # Fallback: try line-by-line parsing
        return self._parse_fallback(response_text)

    def _parse_json_response(self, response_text: str) -> List[Dict]:
        """Parse JSON array from LLM response"""
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
        return []

    def _parse_fallback(self, response_text: str) -> List[Dict]:
        """Fallback parser for non-JSON responses"""
        triplets = []
        # Simple pattern: "Subject PREDICATE Object"
        pattern = r'([A-Z][^→-]+)\s*(?:→|->|CAUSES|IMPACTS|EVOLVES_TO)\s*([A-Z][^.;]+)'
        matches = re.findall(pattern, response_text)

        for subject, obj in matches:
            triplets.append({
                'subject': subject.strip(),
                'predicate': 'RELATES_TO',
                'object': obj.strip()
            })

        return triplets

    def _validate_and_enrich_triplet(
        self,
        triplet: Dict,
        original_text: str,
        source: Optional[str],
        date: Optional[str]
    ) -> Optional[Dict]:
        """
        Validate and enrich triplet with metadata

        Returns:
            Enriched triplet or None if invalid
        """
        # Check required fields
        if not all(k in triplet for k in ['subject', 'predicate', 'object']):
            return None

        # Normalize predicate
        predicate = triplet['predicate'].upper().replace(' ', '_')
        if predicate not in self.relation_types:
            # Map common variations
            predicate_map = {
                'LEADS_TO': 'EVOLVES_TO',
                'RESULTS_IN': 'CAUSES',
                'AFFECTS': 'IMPACTS',
                'TRIGGERS': 'CAUSES'
            }
            predicate = predicate_map.get(predicate, 'RELATES_TO')

        # Determine subject/object types
        subject_type = self._infer_node_type(triplet['subject'])
        object_type = self._infer_node_type(triplet['object'])

        # Compute confidence based on context
        confidence = self._compute_confidence(triplet, original_text)

        return {
            'subject': triplet['subject'].strip(),
            'subject_type': subject_type,
            'predicate': predicate,
            'object': triplet['object'].strip(),
            'object_type': object_type,
            'confidence': confidence,
            'context': triplet.get('context', ''),
            'source': source or 'unknown',
            'date': date or datetime.utcnow().strftime('%Y-%m-%d')
        }

    def _infer_node_type(self, node_text: str) -> str:
        """Infer whether node is entity or event"""
        # Simple heuristic: events are usually lowercase/phrases, entities are proper nouns
        event_keywords = ['crisis', 'default', 'downgrade', 'pressure', 'sale', 'restructuring']

        text_lower = node_text.lower()
        if any(kw in text_lower for kw in event_keywords):
            return 'event'

        # Check if it's a proper noun (capitalized)
        if node_text[0].isupper() and any(c.isupper() for c in node_text[1:]):
            return 'entity'

        return 'event'

    def _compute_confidence(self, triplet: Dict, original_text: str) -> float:
        """
        Compute confidence score for triplet

        Based on:
        - Presence in original text
        - Predicate strength
        - Context clarity
        """
        confidence = 0.5  # Base confidence

        # Check if subject and object appear in text
        text_lower = original_text.lower()
        if triplet['subject'].lower() in text_lower:
            confidence += 0.2
        if triplet['object'].lower() in text_lower:
            confidence += 0.2

        # Strong predicates get bonus
        strong_predicates = ['CAUSES', 'EVOLVES_TO', 'IMPACTS']
        if triplet['predicate'] in strong_predicates:
            confidence += 0.1

        return min(1.0, confidence)

    def _normalize_event_type(self, event_type: str) -> str:
        """Normalize event type to FE-EKG taxonomy"""
        event_type_lower = event_type.lower().replace(' ', '_')

        # Direct match
        if event_type_lower in self.event_types:
            return event_type_lower

        # Fuzzy matching
        type_map = {
            'default': 'debt_default',
            'downgrade': 'credit_downgrade',
            'regulation': 'regulatory_pressure',
            'crisis': 'liquidity_crisis',
            'intervention': 'government_intervention',
            'sale': 'asset_sale',
            'contagion': 'contagion',
            'market': 'market_reaction'
        }

        for key, value in type_map.items():
            if key in event_type_lower:
                return value

        return 'unknown'


# Example usage
if __name__ == '__main__':
    # Sample financial news text
    sample_text = """
    China Evergrande Group, once China's largest property developer, defaulted on
    its offshore bonds in December 2021. The default triggered a liquidity crisis
    that spread to other property developers. Standard & Poor's downgraded
    Evergrande's credit rating to 'selective default'. The Chinese government
    intervened to prevent systemic financial contagion.
    """

    try:
        extractor = TripletExtractor()

        print("=== Triplet Extraction ===")
        triplets = extractor.extract_from_text(sample_text, source='sample')
        for t in triplets:
            print(f"{t['subject']} --[{t['predicate']}]--> {t['object']} (conf: {t['confidence']:.2f})")

        print("\n=== Event Extraction ===")
        events = extractor.extract_events(sample_text)
        for e in events:
            print(f"- {e['type']}: {e.get('description', 'N/A')}")

        print("\n=== Entity Extraction ===")
        entities = extractor.extract_entities(sample_text)
        for ent in entities:
            print(f"- {ent['name']} ({ent['type']})")

    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use this extractor, set NVIDIA_API_KEY in .env")
