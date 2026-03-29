"""Tests for podcast_vault.enrich module."""

from podcast_vault.enrich import (
    UNENRICHED_BOOKS_QUERY,
    UNENRICHED_STUDIES_QUERY,
    EnrichedStudy,
    EnrichmentTask,
)

# ── EnrichedStudy ────────────────────────────────────────────────────────────


def test_enriched_study_minimal():
    s = EnrichedStudy(original_name='Sramek et al. 2000')
    assert s.original_name == 'Sramek et al. 2000'
    assert s.title is None
    assert s.doi is None
    assert s.abstract is None
    assert s.conclusion is None
    assert s.url is None


def test_enriched_study_full():
    s = EnrichedStudy(
        original_name='Sramek et al. 2000',
        title='Human physiological responses to immersion into water',
        authors='Sramek P, Simeckova M, Jansky L',
        year='2000',
        journal='Physiol Res',
        doi='10.33549/physiolres.930000',
        abstract='We studied the effect of cold water immersion...',
        conclusion='Cold water immersion significantly increases dopamine...',
        url='https://pubmed.ncbi.nlm.nih.gov/11191359/',
    )
    assert s.title == 'Human physiological responses to immersion into water'
    assert s.doi == '10.33549/physiolres.930000'


# ── EnrichmentTask ───────────────────────────────────────────────────────────


def test_enrichment_task_creation():
    task = EnrichmentTask(
        entity_uuid='abc-123',
        entity_name='Sramek et al. 2000',
        entity_type='Study',
        search_query='Sramek 2000 cold water immersion dopamine',
        source='transcript_reference',
        show_note_url=None,
    )
    assert task.entity_uuid == 'abc-123'
    assert task.entity_type == 'Study'
    assert task.show_note_url is None


def test_enrichment_task_from_show_notes():
    task = EnrichmentTask(
        entity_uuid='def-456',
        entity_name='Sleep study',
        entity_type='Study',
        search_query='sleep study',
        source='show_notes_link',
        show_note_url='https://pubmed.ncbi.nlm.nih.gov/12345',
    )
    assert task.source == 'show_notes_link'
    assert task.show_note_url == 'https://pubmed.ncbi.nlm.nih.gov/12345'


# ── Enrichment Queries ───────────────────────────────────────────────────────


def test_unenriched_studies_query_not_empty():
    assert len(UNENRICHED_STUDIES_QUERY) > 0
    assert 'Study' in UNENRICHED_STUDIES_QUERY
    assert 'group_id' in UNENRICHED_STUDIES_QUERY
    assert 'doi' in UNENRICHED_STUDIES_QUERY


def test_unenriched_books_query_not_empty():
    assert len(UNENRICHED_BOOKS_QUERY) > 0
    assert 'Book' in UNENRICHED_BOOKS_QUERY
    assert 'group_id' in UNENRICHED_BOOKS_QUERY
    assert 'author' in UNENRICHED_BOOKS_QUERY
