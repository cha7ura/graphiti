"""Tests for podcast_vault.queries module."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_driver():
    driver = AsyncMock()
    driver.execute_query = AsyncMock(return_value=[])
    return driver


# ── get_topic_page ───────────────────────────────────────────────────────────


class TestGetTopicPage:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        from podcast_vault.queries import get_topic_page
        await get_topic_page(mock_driver, 'Cold Exposure')
        assert mock_driver.execute_query.call_count >= 1

    @pytest.mark.asyncio
    async def test_passes_topic_name(self, mock_driver):
        from podcast_vault.queries import get_topic_page
        await get_topic_page(mock_driver, 'Dopamine')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['topic_name'] == 'Dopamine'

    @pytest.mark.asyncio
    async def test_query_matches_claims(self, mock_driver):
        from podcast_vault.queries import get_topic_page
        await get_topic_page(mock_driver, 'Test')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'MAKES_CLAIM' in query or 'RELATES_TO' in query


# ── get_guest_profile ────────────────────────────────────────────────────────


class TestGetGuestProfile:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        from podcast_vault.queries import get_guest_profile
        await get_guest_profile(mock_driver, 'Andrew Huberman')
        assert mock_driver.execute_query.call_count >= 1

    @pytest.mark.asyncio
    async def test_passes_guest_name(self, mock_driver):
        from podcast_vault.queries import get_guest_profile
        await get_guest_profile(mock_driver, 'Peter Attia')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['guest_name'] == 'Peter Attia'


# ── find_agreements_and_disagreements ────────────────────────────────────────


class TestFindAgreementsAndDisagreements:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        from podcast_vault.queries import find_agreements_and_disagreements
        await find_agreements_and_disagreements(mock_driver)
        assert mock_driver.execute_query.call_count >= 1

    @pytest.mark.asyncio
    async def test_with_topic_filter(self, mock_driver):
        from podcast_vault.queries import find_agreements_and_disagreements
        await find_agreements_and_disagreements(mock_driver, topic_name='Fasting')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'topic_name' in query or call_kwargs.kwargs.get('topic_name') == 'Fasting'

    @pytest.mark.asyncio
    async def test_finds_expired_edges(self, mock_driver):
        from podcast_vault.queries import find_agreements_and_disagreements
        await find_agreements_and_disagreements(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'expired_at' in query


# ── get_cross_podcast_insights ───────────────────────────────────────────────


class TestGetCrossPodcastInsights:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        from podcast_vault.queries import get_cross_podcast_insights
        await get_cross_podcast_insights(mock_driver, 'Andrew Huberman')
        assert mock_driver.execute_query.call_count >= 1

    @pytest.mark.asyncio
    async def test_passes_guest_name(self, mock_driver):
        from podcast_vault.queries import get_cross_podcast_insights
        await get_cross_podcast_insights(mock_driver, 'Lex Fridman')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['guest_name'] == 'Lex Fridman'


# ── get_most_referenced_studies ──────────────────────────────────────────────


class TestGetMostReferencedStudies:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        from podcast_vault.queries import get_most_referenced_studies
        await get_most_referenced_studies(mock_driver)
        assert mock_driver.execute_query.call_count >= 1

    @pytest.mark.asyncio
    async def test_default_limit(self, mock_driver):
        from podcast_vault.queries import get_most_referenced_studies
        await get_most_referenced_studies(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['limit'] == 20

    @pytest.mark.asyncio
    async def test_custom_limit(self, mock_driver):
        from podcast_vault.queries import get_most_referenced_studies
        await get_most_referenced_studies(mock_driver, limit=5)
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['limit'] == 5

    @pytest.mark.asyncio
    async def test_query_counts_references(self, mock_driver):
        from podcast_vault.queries import get_most_referenced_studies
        await get_most_referenced_studies(mock_driver)
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'REFERENCES_STUDY' in query
        assert 'count' in query.lower()


# ── get_protocol_comparison ──────────────────────────────────────────────────


class TestGetProtocolComparison:
    @pytest.mark.asyncio
    async def test_basic_call(self, mock_driver):
        from podcast_vault.queries import get_protocol_comparison
        await get_protocol_comparison(mock_driver, 'sleep')
        assert mock_driver.execute_query.call_count >= 1

    @pytest.mark.asyncio
    async def test_passes_topic_name(self, mock_driver):
        from podcast_vault.queries import get_protocol_comparison
        await get_protocol_comparison(mock_driver, 'cold_exposure')
        call_kwargs = mock_driver.execute_query.call_args
        assert call_kwargs.kwargs['topic_name'] == 'cold_exposure'

    @pytest.mark.asyncio
    async def test_query_matches_protocols(self, mock_driver):
        from podcast_vault.queries import get_protocol_comparison
        await get_protocol_comparison(mock_driver, 'sleep')
        call_kwargs = mock_driver.execute_query.call_args
        query = call_kwargs.args[0]
        assert 'Protocol' in query or 'DESCRIBES_PROTOCOL' in query
