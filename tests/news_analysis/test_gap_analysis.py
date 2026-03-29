import pytest

from news_analysis.gap_analysis import (
    ANALYSIS_QUERIES,
    GapAnalysisResult,
)


class TestGapAnalysisQueries:
    def test_analysis_queries_has_all_keys(self):
        expected_keys = [
            'edge_types',
            'entity_distribution',
            'key_entities',
            'contradictions',
            'temporal_coverage',
            'person_roles',
        ]
        for key in expected_keys:
            assert key in ANALYSIS_QUERIES, f'Missing analysis query: {key}'

    def test_each_query_has_cypher_and_description(self):
        for name, query_def in ANALYSIS_QUERIES.items():
            assert 'cypher' in query_def, f'{name} missing cypher'
            assert 'description' in query_def, f'{name} missing description'
            assert len(query_def['cypher']) > 0, f'{name} has empty cypher'
            assert len(query_def['description']) > 0, f'{name} has empty description'

    def test_edge_types_query_contains_relates_to(self):
        assert 'RELATES_TO' in ANALYSIS_QUERIES['edge_types']['cypher']

    def test_contradictions_query_filters_expired(self):
        assert 'expired_at IS NOT NULL' in ANALYSIS_QUERIES['contradictions']['cypher']

    def test_entity_distribution_query_filters_group(self):
        assert 'group_id' in ANALYSIS_QUERIES['entity_distribution']['cypher']

    def test_gap_analysis_result_structure(self):
        result = GapAnalysisResult(
            edge_types=[{'edge_type': 'SUPPORTS', 'freq': 10}],
            entity_distribution=[{'label': 'Person', 'count': 50}],
            key_entities=[],
            contradictions=[],
            temporal_coverage=[],
            person_roles=[],
        )
        assert result.edge_types[0]['freq'] == 10
        assert result.entity_distribution[0]['label'] == 'Person'
