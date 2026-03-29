from datetime import datetime, timezone

from news_analysis.ingest import (
    PHASE_1_ENTITY_TYPES,
    PHASE_1_GROUP_ID,
    PHASE_1_INSTRUCTIONS,
    PHASE_2_EDGE_TYPES,
    PHASE_2_ENTITY_TYPES,
    PHASE_2_GROUP_ID,
    PHASE_2_INSTRUCTIONS,
    build_episode_name,
    build_source_description,
    sort_articles_chronologically,
)


class TestIngestionConfig:
    def test_phase_1_entity_types_has_5_types(self):
        assert len(PHASE_1_ENTITY_TYPES) == 5
        assert 'Person' in PHASE_1_ENTITY_TYPES
        assert 'Organization' in PHASE_1_ENTITY_TYPES
        assert 'Location' in PHASE_1_ENTITY_TYPES
        assert 'Policy' in PHASE_1_ENTITY_TYPES
        assert 'Event' in PHASE_1_ENTITY_TYPES

    def test_phase_2_entity_types_has_9_types(self):
        assert len(PHASE_2_ENTITY_TYPES) == 9
        assert 'Politician' in PHASE_2_ENTITY_TYPES
        assert 'GovernmentBody' in PHASE_2_ENTITY_TYPES
        assert 'PoliticalParty' in PHASE_2_ENTITY_TYPES
        assert 'EconomicIndicator' in PHASE_2_ENTITY_TYPES
        assert 'NewsOutlet' in PHASE_2_ENTITY_TYPES

    def test_phase_2_edge_types_has_8_types(self):
        assert len(PHASE_2_EDGE_TYPES) == 8

    def test_phase_1_instructions_not_empty(self):
        assert len(PHASE_1_INSTRUCTIONS) > 0
        assert 'Sri Lankan' in PHASE_1_INSTRUCTIONS

    def test_phase_2_instructions_not_empty(self):
        assert len(PHASE_2_INSTRUCTIONS) > 0
        assert 'ENTITY EXTRACTION' in PHASE_2_INSTRUCTIONS
        assert 'TEMPORAL RULES' in PHASE_2_INSTRUCTIONS
        assert 'SOURCE ATTRIBUTION' in PHASE_2_INSTRUCTIONS

    def test_group_ids_are_different(self):
        assert PHASE_1_GROUP_ID != PHASE_2_GROUP_ID

    def test_group_ids_are_valid(self):
        """Graphiti group_ids must be alphanumeric with dashes/underscores"""
        import re
        for gid in [PHASE_1_GROUP_ID, PHASE_2_GROUP_ID]:
            assert re.match(r'^[a-zA-Z0-9_-]+$', gid), f'Invalid group_id: {gid}'


class TestHelperFunctions:
    def test_build_episode_name(self):
        result = build_episode_name('Daily Mirror', 'art_123')
        assert result == 'Daily-Mirror_art_123'

    def test_build_episode_name_strips_spaces(self):
        result = build_episode_name('Ada Derana', '456')
        assert result == 'Ada-Derana_456'

    def test_build_source_description(self):
        result = build_source_description('Headline Here', 'Daily Mirror', 'politics')
        assert 'Headline Here' in result
        assert 'Daily Mirror' in result
        assert 'politics' in result

    def test_build_source_description_no_category(self):
        result = build_source_description('Headline', 'Outlet', None)
        assert 'Headline' in result
        assert 'Outlet' in result

    def test_sort_articles_chronologically(self):
        articles = [
            {'published_date': datetime(2024, 3, 1, tzinfo=timezone.utc), 'id': 'c'},
            {'published_date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'id': 'a'},
            {'published_date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'id': 'b'},
        ]
        sorted_arts = sort_articles_chronologically(articles)
        assert sorted_arts[0]['id'] == 'a'
        assert sorted_arts[1]['id'] == 'b'
        assert sorted_arts[2]['id'] == 'c'

    def test_sort_articles_does_not_mutate_original(self):
        articles = [
            {'published_date': datetime(2024, 3, 1, tzinfo=timezone.utc), 'id': 'c'},
            {'published_date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'id': 'a'},
        ]
        sort_articles_chronologically(articles)
        assert articles[0]['id'] == 'c'
