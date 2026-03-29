from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from news_analysis.queries import (
    find_contradictions,
    find_recurring_patterns,
    find_source_disagreements,
    get_entity_timeline,
)


@pytest.fixture
def mock_driver():
    driver = AsyncMock()
    driver.execute_query = AsyncMock(return_value=[])
    return driver


class TestGetEntityTimeline:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        await get_entity_timeline(mock_driver, 'Ranil Wickremesinghe')
        mock_driver.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_passes_entity_name(self, mock_driver):
        await get_entity_timeline(mock_driver, 'Ranil Wickremesinghe')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['entity_name'] == 'Ranil Wickremesinghe'

    @pytest.mark.asyncio
    async def test_default_group_id(self, mock_driver):
        await get_entity_timeline(mock_driver, 'Test')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['group_id'] == 'sri-lanka-news'

    @pytest.mark.asyncio
    async def test_custom_group_id(self, mock_driver):
        await get_entity_timeline(mock_driver, 'Test', group_id='custom-group')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['group_id'] == 'custom-group'

    @pytest.mark.asyncio
    async def test_with_edge_type_filter(self, mock_driver):
        await get_entity_timeline(
            mock_driver, 'Test', edge_types=['HOLDS_POSITION', 'MAKES_STATEMENT']
        )
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'e.name IN $edge_types' in query

    @pytest.mark.asyncio
    async def test_without_edge_type_filter(self, mock_driver):
        await get_entity_timeline(mock_driver, 'Test')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'e.name IN $edge_types' not in query

    @pytest.mark.asyncio
    async def test_returns_driver_results(self, mock_driver):
        mock_driver.execute_query.return_value = [
            {'uuid': '1', 'relation': 'HOLDS_POSITION', 'fact': 'Is president'}
        ]
        result = await get_entity_timeline(mock_driver, 'Test')
        assert len(result) == 1
        assert result[0]['relation'] == 'HOLDS_POSITION'

    @pytest.mark.asyncio
    async def test_query_orders_by_valid_at(self, mock_driver):
        await get_entity_timeline(mock_driver, 'Test')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'ORDER BY e.valid_at ASC' in query


class TestFindContradictions:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        await find_contradictions(mock_driver)
        mock_driver.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_filters_expired_edges(self, mock_driver):
        await find_contradictions(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'old_edge.expired_at IS NOT NULL' in query

    @pytest.mark.asyncio
    async def test_matches_newer_edge(self, mock_driver):
        await find_contradictions(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'new_edge.created_at >= old_edge.expired_at' in query
        assert 'new_edge.expired_at IS NULL' in query

    @pytest.mark.asyncio
    async def test_with_entity_filter(self, mock_driver):
        await find_contradictions(mock_driver, entity_name='Ranil')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'n.name = $entity_name' in query

    @pytest.mark.asyncio
    async def test_without_entity_filter(self, mock_driver):
        await find_contradictions(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert '$entity_name' not in query

    @pytest.mark.asyncio
    async def test_with_since_filter(self, mock_driver):
        since = datetime(2024, 1, 1, tzinfo=timezone.utc)
        await find_contradictions(mock_driver, since=since)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'old_edge.expired_at >= $since' in query

    @pytest.mark.asyncio
    async def test_without_since_filter(self, mock_driver):
        await find_contradictions(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert '$since' not in query

    @pytest.mark.asyncio
    async def test_orders_by_expired_at_desc(self, mock_driver):
        await find_contradictions(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'ORDER BY old_edge.expired_at DESC' in query


class TestFindRecurringPatterns:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        await find_recurring_patterns(mock_driver)
        mock_driver.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_default_min_occurrences(self, mock_driver):
        await find_recurring_patterns(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['min_occurrences'] == 2

    @pytest.mark.asyncio
    async def test_custom_min_occurrences(self, mock_driver):
        await find_recurring_patterns(mock_driver, min_occurrences=3)
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['min_occurrences'] == 3

    @pytest.mark.asyncio
    async def test_with_entity_filter(self, mock_driver):
        await find_recurring_patterns(mock_driver, entity_name='DMC')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'n.name = $entity_name' in query

    @pytest.mark.asyncio
    async def test_without_entity_filter(self, mock_driver):
        await find_recurring_patterns(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert '$entity_name' not in query

    @pytest.mark.asyncio
    async def test_query_groups_by_year(self, mock_driver):
        await find_recurring_patterns(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'year' in query.lower()

    @pytest.mark.asyncio
    async def test_query_orders_by_occurrences(self, mock_driver):
        await find_recurring_patterns(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'ORDER BY' in query


class TestFindSourceDisagreements:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        await find_source_disagreements(mock_driver)
        mock_driver.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_filters_reports_value_edges(self, mock_driver):
        await find_source_disagreements(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'REPORTS_VALUE' in query

    @pytest.mark.asyncio
    async def test_requires_different_sources(self, mock_driver):
        await find_source_disagreements(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'source1.uuid <> source2.uuid' in query

    @pytest.mark.asyncio
    async def test_filters_non_expired_edges(self, mock_driver):
        await find_source_disagreements(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'e1.expired_at IS NULL' in query
        assert 'e2.expired_at IS NULL' in query

    @pytest.mark.asyncio
    async def test_with_target_filter(self, mock_driver):
        await find_source_disagreements(mock_driver, target_name='Inflation Rate')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'target.name = $target_name' in query

    @pytest.mark.asyncio
    async def test_without_target_filter(self, mock_driver):
        await find_source_disagreements(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert '$target_name' not in query
