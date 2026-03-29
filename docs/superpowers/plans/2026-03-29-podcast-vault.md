# Podcast Vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a podcast knowledge extraction system on Graphiti that extracts structured insights from transcripts, connects them across guests and podcasts, enriches referenced studies, and powers topic/guest query pages.

**Architecture:** A `podcast_vault/` package with: Pydantic entity/edge types for the podcast domain, a transcript chunking + insight extraction layer, show notes URL parser, Graphiti ingestion config, a research enrichment module for referenced studies/books, and a Cypher query layer for topic pages, guest profiles, and cross-podcast comparisons.

**Tech Stack:** Python 3.11+, Graphiti (graphiti_core), Pydantic v2, Neo4j 5.26+, pytest + pytest-asyncio

---

## File Structure

```
podcast_vault/
    __init__.py
    entity_types.py       # 7 Pydantic entity models + ENTITY_TYPES dict
    edge_types.py         # 8 edge models + EDGE_TYPES dict + EDGE_TYPE_MAP
    extract.py            # Data classes, chunking, extraction prompt, format helpers
    show_notes.py         # ShowNoteLink, URL extraction, classification
    ingest.py             # Graphiti ingestion config, helpers, extraction instructions
    enrich.py             # EnrichedStudy, EnrichmentTask, enrichment queries
    queries.py            # 6 query functions for frontend

tests/
    podcast_vault/
        __init__.py
        test_entity_types.py
        test_edge_types.py
        test_extract.py
        test_show_notes.py
        test_ingest.py
        test_enrich.py
        test_queries.py
```

---

### Task 1: Entity Types

**Files:**
- Create: `podcast_vault/__init__.py`
- Create: `podcast_vault/entity_types.py`
- Create: `tests/podcast_vault/__init__.py`
- Create: `tests/podcast_vault/test_entity_types.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_entity_types.py
from pydantic import BaseModel

from podcast_vault.entity_types import (
    ENTITY_TYPES,
    Book,
    Guest,
    Podcast,
    Product,
    Protocol,
    Study,
    Topic,
)


class TestEntityTypes:
    def test_guest_defaults(self):
        g = Guest()
        assert g.expertise is None
        assert g.credentials is None

    def test_guest_with_values(self):
        g = Guest(expertise='neuroscience', credentials='PhD, Stanford')
        assert g.expertise == 'neuroscience'
        assert g.credentials == 'PhD, Stanford'

    def test_podcast_defaults(self):
        p = Podcast()
        assert p.host is None

    def test_podcast_with_values(self):
        p = Podcast(host='Andrew Huberman')
        assert p.host == 'Andrew Huberman'

    def test_topic_defaults(self):
        t = Topic()
        assert t.domain is None

    def test_topic_with_values(self):
        t = Topic(domain='neuroscience')
        assert t.domain == 'neuroscience'

    def test_study_defaults(self):
        s = Study()
        assert s.authors is None
        assert s.year is None
        assert s.journal is None
        assert s.doi is None

    def test_study_with_values(self):
        s = Study(authors='Sramek et al.', year='2000', journal='Physiol Res', doi='10.1234/test')
        assert s.authors == 'Sramek et al.'
        assert s.doi == '10.1234/test'

    def test_book_defaults(self):
        b = Book()
        assert b.author is None

    def test_product_defaults(self):
        p = Product()
        assert p.product_type is None

    def test_product_with_values(self):
        p = Product(product_type='supplement')
        assert p.product_type == 'supplement'

    def test_protocol_defaults(self):
        p = Protocol()
        assert p.category is None
        assert p.difficulty is None

    def test_protocol_with_values(self):
        p = Protocol(category='cold_exposure', difficulty='beginner')
        assert p.category == 'cold_exposure'
        assert p.difficulty == 'beginner'

    def test_all_are_pydantic_models(self):
        for model_cls in [Guest, Podcast, Topic, Study, Book, Product, Protocol]:
            assert issubclass(model_cls, BaseModel)

    def test_all_fields_optional(self):
        for model_cls in [Guest, Podcast, Topic, Study, Book, Product, Protocol]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None, (
                    f'{model_cls.__name__}.{field_name} is not optional'
                )

    def test_entity_types_dict_has_7_entries(self):
        assert len(ENTITY_TYPES) == 7
        assert ENTITY_TYPES['Guest'] is Guest
        assert ENTITY_TYPES['Podcast'] is Podcast
        assert ENTITY_TYPES['Topic'] is Topic
        assert ENTITY_TYPES['Study'] is Study
        assert ENTITY_TYPES['Book'] is Book
        assert ENTITY_TYPES['Product'] is Product
        assert ENTITY_TYPES['Protocol'] is Protocol
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_entity_types.py -v --noconftest`
Expected: FAIL — `ModuleNotFoundError: No module named 'podcast_vault'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/__init__.py
```

```python
# tests/podcast_vault/__init__.py
```

```python
# podcast_vault/entity_types.py
from pydantic import BaseModel, Field


class Guest(BaseModel):
    """Podcast guest or host who makes claims and shares insights"""
    expertise: str | None = Field(
        default=None,
        description='Primary field: neuroscience, psychology, fitness, business, medicine',
    )
    credentials: str | None = Field(
        default=None,
        description='PhD, MD, Professor at Stanford, CEO of X, etc.',
    )


class Podcast(BaseModel):
    """A podcast show (not an episode -- the show itself)"""
    host: str | None = Field(
        default=None,
        description='Primary host name: Andrew Huberman, Steven Bartlett, Lex Fridman',
    )


class Topic(BaseModel):
    """A subject area discussed -- brain health, dopamine, sleep, weight loss, fasting"""
    domain: str | None = Field(
        default=None,
        description='health, neuroscience, psychology, fitness, nutrition, business, relationships, productivity',
    )


class Study(BaseModel):
    """A scientific study or research paper referenced by a guest"""
    authors: str | None = Field(
        default=None,
        description='Lead author or author list: "Sramek et al.", "Walker & Stickgold"',
    )
    year: str | None = Field(default=None, description='Publication year if mentioned')
    journal: str | None = Field(default=None, description='Journal name if mentioned')
    doi: str | None = Field(default=None, description='DOI if found by research enrichment agent')


class Book(BaseModel):
    """A book recommended or referenced by a guest"""
    author: str | None = Field(default=None, description='Book author')


class Product(BaseModel):
    """A supplement, tool, device, or product mentioned by a guest"""
    product_type: str | None = Field(
        default=None,
        description='supplement, device, app, tool, food, protocol',
    )


class Protocol(BaseModel):
    """A specific actionable routine or method"""
    category: str | None = Field(
        default=None,
        description='sleep, exercise, nutrition, cold_exposure, breathing, meditation, supplement_stack',
    )
    difficulty: str | None = Field(
        default=None,
        description='beginner, intermediate, advanced',
    )


ENTITY_TYPES: dict[str, type[BaseModel]] = {
    'Guest': Guest,
    'Podcast': Podcast,
    'Topic': Topic,
    'Study': Study,
    'Book': Book,
    'Product': Product,
    'Protocol': Protocol,
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_entity_types.py -v --noconftest`
Expected: All 16 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/__init__.py podcast_vault/entity_types.py tests/podcast_vault/__init__.py tests/podcast_vault/test_entity_types.py
git commit -m "feat: add podcast vault entity types"
```

---

### Task 2: Edge Types and Edge Type Map

**Files:**
- Create: `podcast_vault/edge_types.py`
- Create: `tests/podcast_vault/test_edge_types.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_edge_types.py
from pydantic import BaseModel

from podcast_vault.edge_types import (
    EDGE_TYPE_MAP,
    EDGE_TYPES,
    AppearsOn,
    DescribesProtocol,
    MakesClaim,
    RecommendsBook,
    RecommendsProduct,
    ReferencesStudy,
    RelatesTo,
    SupportsProtocol,
)


class TestEdgeTypes:
    def test_makes_claim_defaults(self):
        e = MakesClaim()
        assert e.insight_type is None
        assert e.confidence is None
        assert e.start_time is None
        assert e.end_time is None
        assert e.youtube_url is None

    def test_makes_claim_with_values(self):
        e = MakesClaim(
            insight_type='claim',
            confidence='high',
            start_time='14:23',
            end_time='16:05',
            youtube_url='https://youtube.com/watch?v=xyz&t=863',
        )
        assert e.insight_type == 'claim'
        assert e.youtube_url == 'https://youtube.com/watch?v=xyz&t=863'

    def test_describes_protocol_defaults(self):
        e = DescribesProtocol()
        assert e.start_time is None
        assert e.end_time is None
        assert e.youtube_url is None

    def test_references_study_defaults(self):
        e = ReferencesStudy()
        assert e.context is None

    def test_recommends_book_defaults(self):
        e = RecommendsBook()
        assert e.strength is None

    def test_recommends_product_defaults(self):
        e = RecommendsProduct()
        assert e.usage is None

    def test_relates_to_defaults(self):
        e = RelatesTo()
        assert e.relationship is None

    def test_appears_on_defaults(self):
        e = AppearsOn()
        assert e.episode_title is None
        assert e.episode_number is None
        assert e.episode_date is None
        assert e.youtube_id is None

    def test_appears_on_with_values(self):
        e = AppearsOn(
            episode_title='#142: Cold Exposure',
            episode_number='142',
            episode_date='2024-03-15',
            youtube_id='dQw4w9WgXcQ',
        )
        assert e.episode_title == '#142: Cold Exposure'
        assert e.youtube_id == 'dQw4w9WgXcQ'

    def test_supports_protocol_defaults(self):
        e = SupportsProtocol()
        assert e.strength is None

    def test_all_are_pydantic_models(self):
        for model_cls in [
            MakesClaim, DescribesProtocol, ReferencesStudy, RecommendsBook,
            RecommendsProduct, RelatesTo, AppearsOn, SupportsProtocol,
        ]:
            assert issubclass(model_cls, BaseModel)

    def test_all_fields_optional(self):
        for model_cls in [
            MakesClaim, DescribesProtocol, ReferencesStudy, RecommendsBook,
            RecommendsProduct, RelatesTo, AppearsOn, SupportsProtocol,
        ]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None


class TestEdgeTypeDicts:
    def test_edge_types_has_8_entries(self):
        assert len(EDGE_TYPES) == 8
        assert EDGE_TYPES['MakesClaim'] is MakesClaim
        assert EDGE_TYPES['AppearsOn'] is AppearsOn
        assert EDGE_TYPES['SupportsProtocol'] is SupportsProtocol

    def test_edge_type_map_has_10_entries(self):
        assert len(EDGE_TYPE_MAP) == 10

    def test_guest_topic_edges(self):
        assert EDGE_TYPE_MAP[('Guest', 'Topic')] == ['MakesClaim']

    def test_guest_podcast_edges(self):
        assert EDGE_TYPE_MAP[('Guest', 'Podcast')] == ['AppearsOn']

    def test_guest_study_edges(self):
        assert EDGE_TYPE_MAP[('Guest', 'Study')] == ['ReferencesStudy']

    def test_topic_topic_edges(self):
        assert EDGE_TYPE_MAP[('Topic', 'Topic')] == ['RelatesTo']

    def test_study_protocol_edges(self):
        assert EDGE_TYPE_MAP[('Study', 'Protocol')] == ['SupportsProtocol']
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_edge_types.py -v --noconftest`
Expected: FAIL — `ModuleNotFoundError: No module named 'podcast_vault.edge_types'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/edge_types.py
from pydantic import BaseModel, Field


class MakesClaim(BaseModel):
    """Guest makes a factual claim or gives advice"""
    insight_type: str | None = Field(default=None, description='claim, advice, tip, warning, recommendation')
    confidence: str | None = Field(default=None, description='high, medium, low')
    start_time: str | None = Field(default=None, description='YouTube timestamp, e.g. "14:23"')
    end_time: str | None = Field(default=None, description='YouTube timestamp, e.g. "16:05"')
    youtube_url: str | None = Field(default=None, description='Full YouTube URL with timestamp')


class DescribesProtocol(BaseModel):
    """Guest describes a specific protocol or routine"""
    start_time: str | None = Field(default=None, description='YouTube timestamp')
    end_time: str | None = Field(default=None, description='YouTube timestamp')
    youtube_url: str | None = Field(default=None, description='Full YouTube URL with timestamp')


class ReferencesStudy(BaseModel):
    """Guest or claim references a scientific study"""
    context: str | None = Field(default=None, description='supports_claim, contradicts_claim, background')


class RecommendsBook(BaseModel):
    """Guest recommends or references a book"""
    strength: str | None = Field(default=None, description='strong, casual, mentioned')


class RecommendsProduct(BaseModel):
    """Guest recommends or mentions a product/supplement"""
    usage: str | None = Field(default=None, description='daily, occasionally, for_specific_purpose')


class RelatesTo(BaseModel):
    """Connects topics to each other"""
    relationship: str | None = Field(default=None, description='causes, improves, inhibits, part_of, requires')


class AppearsOn(BaseModel):
    """Guest appears on a podcast episode"""
    episode_title: str | None = Field(default=None, description='The specific episode title')
    episode_number: str | None = Field(default=None, description='Episode number if available')
    episode_date: str | None = Field(default=None, description='Publication date of the episode')
    youtube_id: str | None = Field(default=None, description='YouTube video ID')


class SupportsProtocol(BaseModel):
    """A study provides evidence for a protocol"""
    strength: str | None = Field(default=None, description='strong, moderate, weak')


EDGE_TYPES: dict[str, type[BaseModel]] = {
    'MakesClaim': MakesClaim,
    'DescribesProtocol': DescribesProtocol,
    'ReferencesStudy': ReferencesStudy,
    'RecommendsBook': RecommendsBook,
    'RecommendsProduct': RecommendsProduct,
    'RelatesTo': RelatesTo,
    'AppearsOn': AppearsOn,
    'SupportsProtocol': SupportsProtocol,
}

EDGE_TYPE_MAP: dict[tuple[str, str], list[str]] = {
    ('Guest', 'Topic'): ['MakesClaim'],
    ('Guest', 'Protocol'): ['DescribesProtocol'],
    ('Guest', 'Study'): ['ReferencesStudy'],
    ('Guest', 'Book'): ['RecommendsBook'],
    ('Guest', 'Product'): ['RecommendsProduct'],
    ('Guest', 'Podcast'): ['AppearsOn'],
    ('Topic', 'Topic'): ['RelatesTo'],
    ('Protocol', 'Topic'): ['RelatesTo'],
    ('Study', 'Protocol'): ['SupportsProtocol'],
    ('Study', 'Topic'): ['RelatesTo'],
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_edge_types.py -v --noconftest`
Expected: All 19 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/edge_types.py tests/podcast_vault/test_edge_types.py
git commit -m "feat: add podcast vault edge types and edge type map"
```

---

### Task 3: Extraction Data Classes and Chunking

**Files:**
- Create: `podcast_vault/extract.py`
- Create: `tests/podcast_vault/test_extract.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_extract.py
from datetime import datetime, timezone

from podcast_vault.extract import (
    INSIGHT_EXTRACTION_PROMPT,
    VALID_INSIGHT_TYPES,
    EpisodeTranscript,
    ExtractedInsight,
    TranscriptSegment,
    chunk_transcript,
    format_chunk_for_prompt,
)


class TestTranscriptSegment:
    def test_creation(self):
        seg = TranscriptSegment(text='Hello world', start_time=0.0, end_time=5.0)
        assert seg.text == 'Hello world'
        assert seg.start_time == 0.0
        assert seg.end_time == 5.0


class TestEpisodeTranscript:
    def test_required_fields(self):
        ep = EpisodeTranscript(
            podcast_name='Huberman Lab',
            episode_title='#142: Cold Exposure',
            youtube_id='abc123',
            published_date=datetime(2024, 3, 15, tzinfo=timezone.utc),
            guests=['Dr. Peter Attia'],
            host='Andrew Huberman',
            segments=[],
        )
        assert ep.podcast_name == 'Huberman Lab'
        assert ep.guests == ['Dr. Peter Attia']

    def test_optional_fields_default_none(self):
        ep = EpisodeTranscript(
            podcast_name='Test',
            episode_title='Test',
            youtube_id='test',
            published_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            guests=[],
            host='Host',
            segments=[],
        )
        assert ep.episode_number is None
        assert ep.description is None

    def test_optional_fields_with_values(self):
        ep = EpisodeTranscript(
            podcast_name='Test',
            episode_title='Test',
            youtube_id='test',
            published_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            guests=[],
            host='Host',
            segments=[],
            episode_number='142',
            description='Show notes here',
        )
        assert ep.episode_number == '142'
        assert ep.description == 'Show notes here'


class TestExtractedInsight:
    def test_required_fields(self):
        insight = ExtractedInsight(
            insight_type='claim',
            text='Cold exposure increases dopamine',
            guest='Andrew Huberman',
            topics=['dopamine', 'cold exposure'],
            start_time=863.0,
            end_time=965.0,
        )
        assert insight.insight_type == 'claim'
        assert insight.topics == ['dopamine', 'cold exposure']

    def test_optional_fields_default_empty(self):
        insight = ExtractedInsight(
            insight_type='claim',
            text='Test',
            guest='Test',
            topics=['test'],
            start_time=0.0,
            end_time=10.0,
        )
        assert insight.referenced_studies == []
        assert insight.referenced_books == []
        assert insight.referenced_products == []
        assert insight.protocol_name is None

    def test_with_references(self):
        insight = ExtractedInsight(
            insight_type='claim',
            text='Test',
            guest='Test',
            topics=['test'],
            start_time=0.0,
            end_time=10.0,
            referenced_studies=['Sramek et al. 2000'],
            referenced_books=['Why We Sleep by Matthew Walker'],
            referenced_products=['AG1'],
            protocol_name='Cold Exposure Protocol',
        )
        assert insight.referenced_studies == ['Sramek et al. 2000']
        assert insight.protocol_name == 'Cold Exposure Protocol'


class TestValidInsightTypes:
    def test_has_six_types(self):
        assert len(VALID_INSIGHT_TYPES) == 6

    def test_expected_types(self):
        for t in ['claim', 'framework', 'protocol', 'story', 'opinion', 'recommendation']:
            assert t in VALID_INSIGHT_TYPES


class TestInsightExtractionPrompt:
    def test_not_empty(self):
        assert len(INSIGHT_EXTRACTION_PROMPT) > 0

    def test_contains_placeholders(self):
        assert '{speakers}' in INSIGHT_EXTRACTION_PROMPT
        assert '{chunk_text}' in INSIGHT_EXTRACTION_PROMPT

    def test_contains_insight_types(self):
        assert 'claim' in INSIGHT_EXTRACTION_PROMPT
        assert 'framework' in INSIGHT_EXTRACTION_PROMPT
        assert 'protocol' in INSIGHT_EXTRACTION_PROMPT
        assert 'story' in INSIGHT_EXTRACTION_PROMPT
        assert 'opinion' in INSIGHT_EXTRACTION_PROMPT
        assert 'recommendation' in INSIGHT_EXTRACTION_PROMPT


class TestChunkTranscript:
    def test_empty_segments_returns_empty(self):
        assert chunk_transcript([]) == []

    def test_short_transcript_single_chunk(self):
        segments = [
            TranscriptSegment(text='Hello', start_time=0.0, end_time=60.0),
            TranscriptSegment(text='World', start_time=60.0, end_time=120.0),
        ]
        chunks = chunk_transcript(segments, chunk_duration=300.0)
        assert len(chunks) == 1
        assert len(chunks[0]) == 2

    def test_long_transcript_multiple_chunks(self):
        # 10 segments, each 60s = 600s total. With 300s chunks, expect 2-3 chunks.
        segments = [
            TranscriptSegment(text=f'Seg {i}', start_time=i * 60.0, end_time=(i + 1) * 60.0)
            for i in range(10)
        ]
        chunks = chunk_transcript(segments, chunk_duration=300.0, overlap_duration=30.0)
        assert len(chunks) >= 2

    def test_chunks_have_overlap(self):
        segments = [
            TranscriptSegment(text=f'Seg {i}', start_time=i * 60.0, end_time=(i + 1) * 60.0)
            for i in range(10)
        ]
        chunks = chunk_transcript(segments, chunk_duration=300.0, overlap_duration=60.0)
        if len(chunks) >= 2:
            # Last segment of chunk 0 should overlap with first segment of chunk 1
            chunk0_end_times = {seg.end_time for seg in chunks[0]}
            chunk1_start_times = {seg.start_time for seg in chunks[1]}
            # There should be at least one segment in common
            chunk0_segs = set(id(s) for s in chunks[0])
            chunk1_segs = set(id(s) for s in chunks[1])
            assert len(chunk0_segs & chunk1_segs) > 0

    def test_does_not_mutate_input(self):
        segments = [
            TranscriptSegment(text='A', start_time=0.0, end_time=60.0),
            TranscriptSegment(text='B', start_time=60.0, end_time=120.0),
        ]
        original_len = len(segments)
        chunk_transcript(segments)
        assert len(segments) == original_len


class TestFormatChunkForPrompt:
    def test_contains_speakers(self):
        chunk = [TranscriptSegment(text='Hello', start_time=0.0, end_time=5.0)]
        result = format_chunk_for_prompt(chunk, ['Andrew Huberman', 'Peter Attia'])
        assert 'Andrew Huberman' in result
        assert 'Peter Attia' in result

    def test_contains_timestamps(self):
        chunk = [TranscriptSegment(text='Hello world', start_time=100.0, end_time=200.0)]
        result = format_chunk_for_prompt(chunk, ['Host'])
        assert '100s' in result
        assert '200s' in result
        assert 'Hello world' in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_extract.py -v --noconftest`
Expected: FAIL — `ModuleNotFoundError: No module named 'podcast_vault.extract'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/extract.py
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TranscriptSegment:
    """A single segment from Whisper transcription."""
    text: str
    start_time: float  # seconds
    end_time: float    # seconds


@dataclass
class EpisodeTranscript:
    """Full transcript and metadata for a podcast episode."""
    podcast_name: str
    episode_title: str
    youtube_id: str
    published_date: datetime
    guests: list[str]
    host: str
    segments: list[TranscriptSegment]
    episode_number: str | None = None
    description: str | None = None


@dataclass
class ExtractedInsight:
    """A single structured insight extracted from a transcript chunk."""
    insight_type: str
    text: str
    guest: str
    topics: list[str]
    start_time: float
    end_time: float
    referenced_studies: list[str] = field(default_factory=list)
    referenced_books: list[str] = field(default_factory=list)
    referenced_products: list[str] = field(default_factory=list)
    protocol_name: str | None = None


VALID_INSIGHT_TYPES = [
    'claim',
    'framework',
    'protocol',
    'story',
    'opinion',
    'recommendation',
]


INSIGHT_EXTRACTION_PROMPT = """\
You are extracting structured insights from a podcast transcript chunk.

SPEAKERS:
{speakers}

TRANSCRIPT CHUNK (timestamps in seconds):
{chunk_text}

Extract every distinct insight. An insight is one of:
- **claim**: A factual assertion ("X causes Y", "doing X increases Y by Z%")
- **framework**: A mental model or structured thinking pattern ("The 80/20 rule for...")
- **protocol**: A specific actionable routine with steps ("Every morning I do X then Y then Z")
- **story**: A personal anecdote or experience ("When I was at Stanford...")
- **opinion**: A subjective viewpoint ("I think X is the biggest...")
- **recommendation**: Explicitly recommending a book, product, tool, or practice

For each insight extract:
1. insight_type: one of the types above
2. text: the insight as a clean, self-contained statement (not a quote — rewrite for clarity)
3. guest: who said it (use the speaker name from SPEAKERS)
4. topics: 1-3 topic labels (use consistent naming: "sleep", "dopamine", not "sleeping" or "dopaminergic pathways")
5. start_time: timestamp in seconds where the insight begins
6. end_time: timestamp in seconds where it ends
7. referenced_studies: any papers/studies mentioned (author + year if available)
8. referenced_books: any books mentioned (title + author)
9. referenced_products: any supplements, tools, devices, apps mentioned
10. protocol_name: if this is a protocol, give it a clear name

RULES:
- Only extract what was explicitly said — do not infer or add information
- Merge multi-sentence insights into one clean statement
- Use the exact timestamp range where the insight was discussed
- If a study is mentioned without full details, include what was said ("a Harvard study on sleep")
- One insight per distinct claim/idea — don't bundle multiple claims\
"""


def chunk_transcript(
    segments: list[TranscriptSegment],
    chunk_duration: float = 300.0,
    overlap_duration: float = 30.0,
) -> list[list[TranscriptSegment]]:
    """Split transcript segments into overlapping time-based chunks.

    Each chunk covers approximately chunk_duration seconds with
    overlap_duration seconds of overlap between consecutive chunks.
    Does not mutate the input.
    """
    if not segments:
        return []

    chunks: list[list[TranscriptSegment]] = []
    chunk_start = segments[0].start_time

    while True:
        chunk_end = chunk_start + chunk_duration

        chunk_segments = [
            seg for seg in segments
            if seg.start_time < chunk_end and seg.end_time > chunk_start
        ]

        if not chunk_segments:
            break

        chunks.append(chunk_segments)

        chunk_start += chunk_duration - overlap_duration

        if chunk_start >= segments[-1].end_time:
            break

    return chunks


def format_chunk_for_prompt(
    chunk: list[TranscriptSegment],
    speakers: list[str],
) -> str:
    """Format a chunk of transcript segments for the extraction prompt."""
    speakers_str = ', '.join(speakers)
    chunk_lines = [
        f'[{seg.start_time:.0f}s - {seg.end_time:.0f}s] {seg.text}'
        for seg in chunk
    ]
    chunk_text = '\n'.join(chunk_lines)
    return INSIGHT_EXTRACTION_PROMPT.format(
        speakers=speakers_str,
        chunk_text=chunk_text,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_extract.py -v --noconftest`
Expected: All 18 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/extract.py tests/podcast_vault/test_extract.py
git commit -m "feat: add transcript extraction data classes, chunking, and prompt"
```

---

### Task 4: Show Notes Parser

**Files:**
- Create: `podcast_vault/show_notes.py`
- Create: `tests/podcast_vault/test_show_notes.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_show_notes.py
from podcast_vault.show_notes import (
    ShowNoteLink,
    classify_url,
    extract_context,
    extract_show_note_links,
    get_product_links,
    get_study_links,
)


class TestClassifyUrl:
    def test_pubmed_is_study(self):
        assert classify_url('https://pubmed.ncbi.nlm.nih.gov/12345') == 'study'

    def test_doi_is_study(self):
        assert classify_url('https://doi.org/10.1234/test') == 'study'

    def test_nature_is_study(self):
        assert classify_url('https://nature.com/articles/s41586-023') == 'study'

    def test_arxiv_is_study(self):
        assert classify_url('https://arxiv.org/abs/2301.00001') == 'study'

    def test_amazon_is_product(self):
        assert classify_url('https://amazon.com/dp/B08N5WRWNW') == 'product'

    def test_thorne_is_product(self):
        assert classify_url('https://thorne.com/products/magnesium') == 'product'

    def test_momentous_is_product(self):
        assert classify_url('https://momentous.com/products/creatine') == 'product'

    def test_wikipedia_is_guest_bio(self):
        assert classify_url('https://en.wikipedia.org/wiki/Andrew_Huberman') == 'guest_bio'

    def test_twitter_is_guest_bio(self):
        assert classify_url('https://twitter.com/hubaborlelab') == 'guest_bio'

    def test_x_com_is_guest_bio(self):
        assert classify_url('https://x.com/hubermanlab') == 'guest_bio'

    def test_unknown_is_other(self):
        assert classify_url('https://example.com/page') == 'other'

    def test_case_insensitive(self):
        assert classify_url('https://PUBMED.NCBI.NLM.NIH.GOV/12345') == 'study'


class TestExtractContext:
    def test_extracts_surrounding_text(self):
        text = 'Check out this study: https://doi.org/10.1234 for more info'
        url = 'https://doi.org/10.1234'
        context = extract_context(text, url, context_chars=20)
        assert url in context
        assert 'study' in context

    def test_url_not_found_returns_empty(self):
        assert extract_context('some text', 'https://missing.com') == ''

    def test_handles_url_at_start(self):
        text = 'https://doi.org/10.1234 is a great paper'
        context = extract_context(text, 'https://doi.org/10.1234', context_chars=50)
        assert 'great paper' in context


class TestExtractShowNoteLinks:
    def test_empty_description_returns_empty(self):
        assert extract_show_note_links('') == []

    def test_none_description_returns_empty(self):
        assert extract_show_note_links(None) == []

    def test_extracts_single_url(self):
        desc = 'Study reference: https://pubmed.ncbi.nlm.nih.gov/12345'
        links = extract_show_note_links(desc)
        assert len(links) == 1
        assert links[0].url == 'https://pubmed.ncbi.nlm.nih.gov/12345'
        assert links[0].link_type == 'study'

    def test_extracts_multiple_urls(self):
        desc = (
            'Resources:\n'
            'Paper: https://doi.org/10.1234/test\n'
            'Supplement: https://thorne.com/magnesium\n'
            'Guest: https://twitter.com/guest'
        )
        links = extract_show_note_links(desc)
        assert len(links) == 3
        types = {link.link_type for link in links}
        assert types == {'study', 'product', 'guest_bio'}

    def test_links_have_context(self):
        desc = 'Referenced paper: https://doi.org/10.1234 about sleep'
        links = extract_show_note_links(desc)
        assert len(links) == 1
        assert len(links[0].context) > 0


class TestFilterHelpers:
    def test_get_study_links(self):
        links = [
            ShowNoteLink(url='https://doi.org/10.1234', link_type='study', context=''),
            ShowNoteLink(url='https://amazon.com/book', link_type='product', context=''),
            ShowNoteLink(url='https://nature.com/article', link_type='study', context=''),
        ]
        studies = get_study_links(links)
        assert len(studies) == 2
        assert all(s.link_type == 'study' for s in studies)

    def test_get_product_links(self):
        links = [
            ShowNoteLink(url='https://doi.org/10.1234', link_type='study', context=''),
            ShowNoteLink(url='https://amazon.com/book', link_type='product', context=''),
        ]
        products = get_product_links(links)
        assert len(products) == 1
        assert products[0].link_type == 'product'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_show_notes.py -v --noconftest`
Expected: FAIL — `ModuleNotFoundError: No module named 'podcast_vault.show_notes'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/show_notes.py
import re
from dataclasses import dataclass


@dataclass
class ShowNoteLink:
    """A URL extracted from podcast show notes / YouTube description."""
    url: str
    link_type: str   # study, product, guest_bio, other
    context: str     # Surrounding text from show notes


LINK_TYPE_PATTERNS: dict[str, list[str]] = {
    'study': [
        r'pubmed\.ncbi\.nlm\.nih\.gov',
        r'doi\.org',
        r'nature\.com',
        r'sciencedirect\.com',
        r'ncbi\.nlm\.nih\.gov',
        r'scholar\.google\.com',
        r'cell\.com',
        r'thelancet\.com',
        r'bmj\.com',
        r'jamanetwork\.com',
        r'arxiv\.org',
    ],
    'product': [
        r'amazon\.com',
        r'iherb\.com',
        r'thorne\.com',
        r'momentous\.com',
        r'athleticgreens\.com',
        r'drinkag1\.com',
    ],
    'guest_bio': [
        r'wikipedia\.org',
        r'twitter\.com',
        r'x\.com',
        r'linkedin\.com',
        r'instagram\.com',
    ],
}

URL_REGEX = re.compile(
    r'https?://[^\s<>\"\'\)\]]+',
    re.IGNORECASE,
)


def classify_url(url: str) -> str:
    """Classify a URL into a link type based on domain patterns."""
    for link_type, patterns in LINK_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return link_type
    return 'other'


def extract_context(text: str, url: str, context_chars: int = 100) -> str:
    """Extract surrounding text around a URL for context."""
    idx = text.find(url)
    if idx == -1:
        return ''
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(url) + context_chars)
    return text[start:end].strip()


def extract_show_note_links(description: str | None) -> list[ShowNoteLink]:
    """Parse URLs from YouTube description and classify them."""
    if not description:
        return []

    urls = URL_REGEX.findall(description)
    links: list[ShowNoteLink] = []

    for url in urls:
        url = url.rstrip('.,;:!?)')
        link_type = classify_url(url)
        context = extract_context(description, url)
        links.append(ShowNoteLink(url=url, link_type=link_type, context=context))

    return links


def get_study_links(links: list[ShowNoteLink]) -> list[ShowNoteLink]:
    """Filter to only study/research links."""
    return [link for link in links if link.link_type == 'study']


def get_product_links(links: list[ShowNoteLink]) -> list[ShowNoteLink]:
    """Filter to only product links."""
    return [link for link in links if link.link_type == 'product']
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_show_notes.py -v --noconftest`
Expected: All 17 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/show_notes.py tests/podcast_vault/test_show_notes.py
git commit -m "feat: add show notes URL parser and classifier"
```

---

### Task 5: Ingestion Config

**Files:**
- Create: `podcast_vault/ingest.py`
- Create: `tests/podcast_vault/test_ingest.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_ingest.py
import re

from podcast_vault.ingest import (
    EDGE_TYPE_MAP,
    EDGE_TYPES,
    ENTITY_TYPES,
    GRAPHITI_EXTRACTION_INSTRUCTIONS,
    GROUP_ID_PREFIX,
    build_episode_name,
    build_group_id,
    build_source_description,
    build_youtube_url,
    format_timestamp,
)


class TestIngestionConfig:
    def test_entity_types_has_7(self):
        assert len(ENTITY_TYPES) == 7

    def test_edge_types_has_8(self):
        assert len(EDGE_TYPES) == 8

    def test_edge_type_map_has_10(self):
        assert len(EDGE_TYPE_MAP) == 10

    def test_extraction_instructions_not_empty(self):
        assert len(GRAPHITI_EXTRACTION_INSTRUCTIONS) > 0
        assert 'Guest' in GRAPHITI_EXTRACTION_INSTRUCTIONS
        assert 'Topic' in GRAPHITI_EXTRACTION_INSTRUCTIONS
        assert 'Study' in GRAPHITI_EXTRACTION_INSTRUCTIONS

    def test_group_id_prefix(self):
        assert GROUP_ID_PREFIX == 'podcast'


class TestHelpers:
    def test_build_episode_name(self):
        result = build_episode_name('Huberman Lab', 'abc123', 863)
        assert result == 'Huberman-Lab_abc123_863'

    def test_build_episode_name_no_spaces(self):
        result = build_episode_name('DOAC', 'xyz', 0)
        assert result == 'DOAC_xyz_0'

    def test_build_source_description(self):
        result = build_source_description(
            episode_title='#142: Cold Exposure',
            podcast_name='Huberman Lab',
            guest='Peter Attia',
            start_time='14:23',
            end_time='16:05',
            youtube_url='https://youtube.com/watch?v=abc&t=863',
        )
        assert '#142: Cold Exposure' in result
        assert 'Huberman Lab' in result
        assert 'Peter Attia' in result
        assert '14:23' in result
        assert '16:05' in result
        assert 'https://youtube.com/watch?v=abc&t=863' in result

    def test_build_youtube_url(self):
        result = build_youtube_url('abc123', 863)
        assert result == 'https://youtube.com/watch?v=abc123&t=863'

    def test_build_youtube_url_zero(self):
        result = build_youtube_url('xyz', 0)
        assert result == 'https://youtube.com/watch?v=xyz&t=0'

    def test_format_timestamp_minutes(self):
        assert format_timestamp(125.0) == '2:05'

    def test_format_timestamp_hours(self):
        assert format_timestamp(3725.0) == '1:02:05'

    def test_format_timestamp_zero(self):
        assert format_timestamp(0.0) == '0:00'

    def test_format_timestamp_exact_hour(self):
        assert format_timestamp(3600.0) == '1:00:00'

    def test_build_group_id(self):
        assert build_group_id('Huberman Lab') == 'podcast-huberman-lab'

    def test_build_group_id_apostrophe(self):
        assert build_group_id("Lex Fridman's Podcast") == 'podcast-lex-fridmans-podcast'

    def test_build_group_id_valid_chars(self):
        gid = build_group_id('Diary of a CEO')
        assert re.match(r'^[a-zA-Z0-9_-]+$', gid)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_ingest.py -v --noconftest`
Expected: FAIL — `ImportError: cannot import name 'ENTITY_TYPES' from 'podcast_vault.ingest'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/ingest.py
from podcast_vault.edge_types import EDGE_TYPE_MAP, EDGE_TYPES
from podcast_vault.entity_types import ENTITY_TYPES

# Re-export for convenience
ENTITY_TYPES = ENTITY_TYPES
EDGE_TYPES = EDGE_TYPES
EDGE_TYPE_MAP = EDGE_TYPE_MAP

GROUP_ID_PREFIX = 'podcast'

GRAPHITI_EXTRACTION_INSTRUCTIONS = """\
You are analyzing structured insights extracted from podcast episodes.
Each insight comes from a specific guest at a specific timestamp.

ENTITY EXTRACTION:
- The person making the claim/insight is a Guest entity
- Subject areas (dopamine, sleep, cold exposure, etc.) are Topic entities
- Referenced papers are Study entities — include author and year if available
- Referenced books are Book entities — include author if available
- Supplements, devices, tools, apps are Product entities
- Actionable routines with steps are Protocol entities
- The podcast show name is a Podcast entity

RELATIONSHIP RULES:
- A guest making a claim about a topic = MakesClaim edge
- A guest describing a routine = DescribesProtocol edge
- When a guest cites a study = ReferencesStudy edge
- Book/product recommendations = RecommendsBook / RecommendsProduct edge
- Topic-to-topic connections (e.g., sleep improves memory) = RelatesTo edge

TEMPORAL RULES:
- Set valid_at to the episode publication date
- Timestamps are stored in edge attributes, not in valid_at\
"""


def build_episode_name(podcast_name: str, youtube_id: str, start_time: int) -> str:
    """Build a unique episode name for a single insight."""
    sanitized = podcast_name.replace(' ', '-')
    return f'{sanitized}_{youtube_id}_{start_time}'


def build_source_description(
    episode_title: str,
    podcast_name: str,
    guest: str,
    start_time: str,
    end_time: str,
    youtube_url: str,
) -> str:
    """Build a source description with full provenance."""
    return (
        f"Insight from '{episode_title}' on {podcast_name}, "
        f"guest: {guest}, "
        f"timestamp: {start_time}-{end_time}, "
        f"youtube: {youtube_url}"
    )


def build_youtube_url(youtube_id: str, start_seconds: int) -> str:
    """Build a YouTube URL with timestamp parameter."""
    return f'https://youtube.com/watch?v={youtube_id}&t={start_seconds}'


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f'{hours}:{minutes:02d}:{secs:02d}'
    return f'{minutes}:{secs:02d}'


def build_group_id(podcast_name: str) -> str:
    """Build a group_id from podcast name."""
    slug = podcast_name.lower().replace(' ', '-').replace("'", '')
    return f'{GROUP_ID_PREFIX}-{slug}'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_ingest.py -v --noconftest`
Expected: All 16 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/ingest.py tests/podcast_vault/test_ingest.py
git commit -m "feat: add podcast vault ingestion config and helpers"
```

---

### Task 6: Research Enrichment Data Structures and Queries

**Files:**
- Create: `podcast_vault/enrich.py`
- Create: `tests/podcast_vault/test_enrich.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_enrich.py
from podcast_vault.enrich import (
    UNENRICHED_BOOKS_QUERY,
    UNENRICHED_STUDIES_QUERY,
    EnrichedStudy,
    EnrichmentTask,
)


class TestEnrichedStudy:
    def test_creation_minimal(self):
        s = EnrichedStudy(original_name='Sramek et al. 2000')
        assert s.original_name == 'Sramek et al. 2000'
        assert s.title is None
        assert s.doi is None
        assert s.abstract is None
        assert s.conclusion is None
        assert s.url is None

    def test_creation_full(self):
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


class TestEnrichmentTask:
    def test_creation(self):
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

    def test_creation_from_show_notes(self):
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


class TestEnrichmentQueries:
    def test_unenriched_studies_query_not_empty(self):
        assert len(UNENRICHED_STUDIES_QUERY) > 0
        assert 'Study' in UNENRICHED_STUDIES_QUERY
        assert 'group_id' in UNENRICHED_STUDIES_QUERY
        assert 'doi' in UNENRICHED_STUDIES_QUERY

    def test_unenriched_books_query_not_empty(self):
        assert len(UNENRICHED_BOOKS_QUERY) > 0
        assert 'Book' in UNENRICHED_BOOKS_QUERY
        assert 'group_id' in UNENRICHED_BOOKS_QUERY
        assert 'author' in UNENRICHED_BOOKS_QUERY
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_enrich.py -v --noconftest`
Expected: FAIL — `ModuleNotFoundError: No module named 'podcast_vault.enrich'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/enrich.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_enrich.py -v --noconftest`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/enrich.py tests/podcast_vault/test_enrich.py
git commit -m "feat: add research enrichment data structures and queries"
```

---

### Task 7: Query Layer

**Files:**
- Create: `podcast_vault/queries.py`
- Create: `tests/podcast_vault/test_queries.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/podcast_vault/test_queries.py
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_driver():
    driver = AsyncMock()
    driver.execute_query = AsyncMock(return_value=[])
    return driver


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_queries.py -v --noconftest`
Expected: FAIL — `ModuleNotFoundError: No module named 'podcast_vault.queries'`

- [ ] **Step 3: Write minimal implementation**

```python
# podcast_vault/queries.py
from typing import Any


async def get_topic_page(
    driver,
    topic_name: str,
    group_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Get all claims, protocols, studies, and products related to a topic."""
    group_filter = 'AND n.group_id IN $group_ids' if group_ids else ''

    params: dict[str, Any] = {'topic_name': topic_name}
    if group_ids:
        params['group_ids'] = group_ids

    query = f"""
        MATCH (g:Guest)-[e:RELATES_TO {{name: 'MAKES_CLAIM'}}]->(t:Topic)
        WHERE t.name = $topic_name {group_filter}
        OPTIONAL MATCH (g)-[ref:RELATES_TO {{name: 'REFERENCES_STUDY'}}]->(s:Study)
        OPTIONAL MATCH (t)-[rel:RELATES_TO {{name: 'RELATES_TO'}}]->(sub:Topic)
        RETURN g.name AS guest,
               e.fact AS fact,
               e.attributes AS claim_attributes,
               e.episodes AS episodes,
               s.name AS study_name,
               s.attributes AS study_attributes,
               sub.name AS related_topic,
               rel.attributes AS relation_attributes
        ORDER BY g.name
    """

    return await driver.execute_query(query, **params)


async def get_guest_profile(
    driver,
    guest_name: str,
) -> list[dict[str, Any]]:
    """Get a guest's full profile — appearances, claims, protocols, recommendations."""
    query = """
        MATCH (g:Guest {name: $guest_name})-[e:RELATES_TO]->(target)
        RETURN e.name AS relation,
               e.fact AS fact,
               e.attributes AS attributes,
               e.episodes AS episodes,
               target.name AS target_name,
               labels(target) AS target_labels
        ORDER BY e.name, e.valid_at ASC
    """

    return await driver.execute_query(query, guest_name=guest_name)


async def find_agreements_and_disagreements(
    driver,
    topic_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find topics where multiple guests agree or disagree."""
    topic_filter = 'AND t.name = $topic_name' if topic_name else ''

    params: dict[str, Any] = {}
    if topic_name:
        params['topic_name'] = topic_name

    query = f"""
        MATCH (g:Guest)-[e:RELATES_TO {{name: 'MAKES_CLAIM'}}]->(t:Topic)
        WHERE e.expired_at IS NOT NULL {topic_filter}

        MATCH (g2:Guest)-[e2:RELATES_TO {{name: 'MAKES_CLAIM'}}]->(t)
        WHERE e2.created_at >= e.expired_at
          AND e2.expired_at IS NULL
          AND g2.uuid <> g.uuid

        RETURN t.name AS topic,
               g.name AS original_guest,
               e.fact AS original_claim,
               e.attributes AS original_attributes,
               g2.name AS contradicting_guest,
               e2.fact AS contradicting_claim,
               e2.attributes AS contradicting_attributes,
               e.expired_at AS expired_at
        ORDER BY e.expired_at DESC
    """

    return await driver.execute_query(query, **params)


async def get_cross_podcast_insights(
    driver,
    guest_name: str,
) -> list[dict[str, Any]]:
    """Find what a guest said across different podcast appearances."""
    query = """
        MATCH (g:Guest {name: $guest_name})-[a:RELATES_TO {name: 'APPEARS_ON'}]->(p:Podcast)
        MATCH (g)-[e:RELATES_TO {name: 'MAKES_CLAIM'}]->(t:Topic)
        RETURN p.name AS podcast,
               a.attributes AS appearance_attributes,
               t.name AS topic,
               e.fact AS claim,
               e.attributes AS claim_attributes,
               e.valid_at AS valid_at
        ORDER BY p.name, e.valid_at ASC
    """

    return await driver.execute_query(query, guest_name=guest_name)


async def get_most_referenced_studies(
    driver,
    group_ids: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Find studies referenced by the most guests across podcasts."""
    group_filter = 'AND g.group_id IN $group_ids' if group_ids else ''

    params: dict[str, Any] = {'limit': limit}
    if group_ids:
        params['group_ids'] = group_ids

    query = f"""
        MATCH (g:Guest)-[e:RELATES_TO {{name: 'REFERENCES_STUDY'}}]->(s:Study)
        {group_filter}
        WITH s, count(DISTINCT g) AS guest_count,
             collect(DISTINCT g.name) AS citing_guests,
             collect(DISTINCT e.attributes) AS reference_contexts
        RETURN s.name AS study_name,
               s.attributes AS study_attributes,
               guest_count,
               citing_guests,
               reference_contexts
        ORDER BY guest_count DESC
        LIMIT $limit
    """

    return await driver.execute_query(query, **params)


async def get_protocol_comparison(
    driver,
    topic_name: str,
) -> list[dict[str, Any]]:
    """Find all protocols related to a topic and compare across guests."""
    query = """
        MATCH (g:Guest)-[e:RELATES_TO {name: 'DESCRIBES_PROTOCOL'}]->(p:Protocol)
        MATCH (p)-[:RELATES_TO {name: 'RELATES_TO'}]->(t:Topic)
        WHERE t.name = $topic_name
        RETURN g.name AS guest,
               p.name AS protocol_name,
               p.attributes AS protocol_attributes,
               e.fact AS description,
               e.attributes AS edge_attributes
        ORDER BY g.name
    """

    return await driver.execute_query(query, topic_name=topic_name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/test_queries.py -v --noconftest`
Expected: All 17 tests PASS

- [ ] **Step 5: Commit**

```bash
git add podcast_vault/queries.py tests/podcast_vault/test_queries.py
git commit -m "feat: add query layer for topic pages, guest profiles, and comparisons"
```

---

### Task 8: README and Final Integration

**Files:**
- Create: `podcast_vault/README.md`

- [ ] **Step 1: Run all tests**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/podcast_vault/ -v --noconftest`
Expected: All tests PASS

- [ ] **Step 2: Run linter**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && ruff check podcast_vault/ tests/podcast_vault/`
Expected: No errors (fix any that appear with `ruff check --fix`)

- [ ] **Step 3: Create README**

Create `podcast_vault/README.md` with:
- Project overview and purpose
- Data flow diagram (text-based)
- Quick start showing: how to create an EpisodeTranscript, chunk it, format for prompt extraction, ingest insights into Graphiti
- Entity type and edge type reference tables
- Query layer usage examples for each of the 6 queries
- Show notes processing example
- Research enrichment overview
- Project structure listing
- How to run tests

- [ ] **Step 4: Commit README**

```bash
git add podcast_vault/README.md
git commit -m "docs: add README for podcast vault module"
```

- [ ] **Step 5: Push branch**

```bash
git push -u origin feature/podcast-vault
```
