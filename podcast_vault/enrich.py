from dataclasses import dataclass


@dataclass
class EnrichedStudy:
    """A study with metadata filled in by the enrichment agent."""
    original_name: str
    title: str | None = None
    authors: str | None = None
    year: str | None = None
    journal: str | None = None
    doi: str | None = None
    abstract: str | None = None
    conclusion: str | None = None
    url: str | None = None


@dataclass
class EnrichmentTask:
    """A task for the enrichment agent to process."""
    entity_uuid: str
    entity_name: str
    entity_type: str          # Study, Book, Product
    search_query: str
    source: str               # transcript_reference, show_notes_link
    show_note_url: str | None


UNENRICHED_STUDIES_QUERY = """
    MATCH (s:Study {group_id: $group_id})
    WHERE s.attributes.doi IS NULL OR s.attributes.doi = ''
    RETURN s.uuid AS uuid, s.name AS name, s.attributes AS attributes
    LIMIT 50
"""

UNENRICHED_BOOKS_QUERY = """
    MATCH (b:Book {group_id: $group_id})
    WHERE b.attributes.author IS NULL OR b.attributes.author = ''
    RETURN b.uuid AS uuid, b.name AS name, b.attributes AS attributes
    LIMIT 50
"""
