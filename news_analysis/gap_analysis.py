from dataclasses import dataclass, field
from typing import Any

# Try to import from ingest; fall back to local constant if not available yet.
try:
    from news_analysis.ingest import PHASE_1_GROUP_ID
except ImportError:
    PHASE_1_GROUP_ID = 'sri-lanka-news-discovery'


@dataclass
class GapAnalysisResult:
    """Container for gap analysis query results."""

    edge_types: list[dict[str, Any]] = field(default_factory=list)
    entity_distribution: list[dict[str, Any]] = field(default_factory=list)
    key_entities: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    temporal_coverage: list[dict[str, Any]] = field(default_factory=list)
    person_roles: list[dict[str, Any]] = field(default_factory=list)


ANALYSIS_QUERIES: dict[str, dict[str, str]] = {
    'edge_types': {
        'description': 'Edge types extracted organically — what relationships dominate?',
        'cypher': """
            MATCH ()-[e:RELATES_TO]->()
            WHERE e.group_id = $group_id
            RETURN e.name AS edge_type, count(e) AS freq
            ORDER BY freq DESC LIMIT 30
        """,
    },
    'entity_distribution': {
        'description': 'Entity label distribution',
        'cypher': """
            MATCH (n:Entity {group_id: $group_id})
            UNWIND labels(n) AS label
            WITH label WHERE label <> 'Entity'
            RETURN label, count(*) AS count
            ORDER BY count DESC
        """,
    },
    'key_entities': {
        'description': 'Most connected entities (key players)',
        'cypher': """
            MATCH (n:Entity {group_id: $group_id})-[e:RELATES_TO]-()
            RETURN n.name AS name, labels(n) AS labels, count(e) AS connections
            ORDER BY connections DESC LIMIT 30
        """,
    },
    'contradictions': {
        'description': 'Contradictions already detected (edges with expired_at)',
        'cypher': """
            MATCH ()-[e:RELATES_TO]->()
            WHERE e.group_id = $group_id AND e.expired_at IS NOT NULL
            RETURN e.name AS edge_type, e.fact AS fact,
                   e.valid_at AS valid_at, e.expired_at AS expired_at
            ORDER BY e.expired_at DESC LIMIT 30
        """,
    },
    'temporal_coverage': {
        'description': 'Temporal coverage per edge type',
        'cypher': """
            MATCH ()-[e:RELATES_TO]->()
            WHERE e.group_id = $group_id
            RETURN e.name AS edge_type,
                   count(e) AS total,
                   count(e.valid_at) AS has_valid_at,
                   count(e.invalid_at) AS has_invalid_at,
                   count(e.expired_at) AS has_expired_at
            ORDER BY total DESC LIMIT 20
        """,
    },
    'person_roles': {
        'description': 'Person entities — which should be reclassified as Politician?',
        'cypher': """
            MATCH (p:Person {group_id: $group_id})
            RETURN p.name AS name, p.summary AS summary, p.attributes AS attributes
            ORDER BY p.name LIMIT 50
        """,
    },
}


async def run_gap_analysis(
    driver,
    group_id: str = PHASE_1_GROUP_ID,
) -> GapAnalysisResult:
    """Run all gap analysis queries against the graph and return results."""
    result = GapAnalysisResult()

    for query_name, query_def in ANALYSIS_QUERIES.items():
        records = await driver.execute_query(
            query_def['cypher'],
            group_id=group_id,
        )
        setattr(result, query_name, records)

    return result
