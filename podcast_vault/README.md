# Podcast Vault

A knowledge extraction system built on [Graphiti](https://github.com/getzep/graphiti) that turns long-form podcast transcripts into a structured, queryable knowledge graph. Inspired by [MFMVault](https://www.mfmvault.com/).

## Target Podcasts

- Diary of a CEO (DOAC)
- Chris Williamson / Modern Wisdom
- Lex Fridman Podcast
- Huberman Lab

## Data Flow

```
YouTube Video
    │
    ▼
┌──────────────┐
│   Whisper     │  word-level timestamps
│ Transcription │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Chunking    │  5-min overlapping windows
│ (extract.py)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ LLM Insight   │  structured JSON per insight
│  Extraction   │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│   Graphiti    │────▶│     Neo4j       │
│ add_episode() │     │ Knowledge Graph  │
└──────┬───────┘     └────────┬────────┘
       │                      │
       ▼                      ▼
┌──────────────┐     ┌─────────────────┐
│  Show Notes   │     │   Query Layer   │
│  Enrichment   │     │  (queries.py)   │
└──────────────┘     └─────────────────┘
```

## Quick Start

### 1. Create a Transcript

```python
from datetime import datetime, timezone
from podcast_vault.extract import EpisodeTranscript, TranscriptSegment, chunk_transcript, format_chunk_for_prompt

transcript = EpisodeTranscript(
    podcast_name='Huberman Lab',
    episode_title='#142: Cold Exposure for Health',
    youtube_id='dQw4w9WgXcQ',
    published_date=datetime(2024, 3, 15, tzinfo=timezone.utc),
    guests=['Dr. Susanna Søberg'],
    host='Andrew Huberman',
    segments=[
        TranscriptSegment(text='Today we discuss cold exposure...', start_time=0.0, end_time=30.0),
        TranscriptSegment(text='The Søberg principle states...', start_time=30.0, end_time=60.0),
        # ... more segments from Whisper
    ],
)
```

### 2. Chunk and Extract

```python
# Split into ~5min chunks with 30s overlap
chunks = chunk_transcript(transcript.segments, chunk_duration=300.0, overlap_duration=30.0)

# Format each chunk for LLM extraction
for chunk in chunks:
    prompt = format_chunk_for_prompt(chunk, [transcript.host] + transcript.guests)
    # Send prompt to LLM → get back structured insights
```

### 3. Ingest into Graphiti

```python
from graphiti_core import Graphiti
from podcast_vault.ingest import (
    ENTITY_TYPES, EDGE_TYPES, EDGE_TYPE_MAP,
    GRAPHITI_EXTRACTION_INSTRUCTIONS,
    build_episode_name, build_source_description, build_youtube_url,
    format_timestamp, build_group_id,
)

graphiti = Graphiti(uri, user, password)

# Each extracted insight becomes an episode
await graphiti.add_episode(
    name=build_episode_name('Huberman Lab', 'dQw4w9WgXcQ', 863),
    episode_body=insight.text,
    source_description=build_source_description(
        episode_title='#142: Cold Exposure',
        podcast_name='Huberman Lab',
        guest='Dr. Susanna Søberg',
        start_time=format_timestamp(863.0),
        end_time=format_timestamp(965.0),
        youtube_url=build_youtube_url('dQw4w9WgXcQ', 863),
    ),
    group_id=build_group_id('Huberman Lab'),
    entity_types=list(ENTITY_TYPES.values()),
    edge_types=list(EDGE_TYPES.values()),
    edge_type_map=EDGE_TYPE_MAP,
    custom_extraction_instructions=GRAPHITI_EXTRACTION_INSTRUCTIONS,
)
```

### 4. Parse Show Notes

```python
from podcast_vault.show_notes import extract_show_note_links, get_study_links

links = extract_show_note_links(youtube_description)
studies = get_study_links(links)
# Each study link can feed into the enrichment pipeline
```

### 5. Query the Graph

```python
from podcast_vault.queries import get_topic_page, get_guest_profile

# Everything guests said about cold exposure
results = await get_topic_page(driver, 'cold exposure')

# Full profile of a guest across all appearances
profile = await get_guest_profile(driver, 'Dr. Andrew Huberman')
```

## Entity Types

| Entity | Key Fields | Description |
|--------|-----------|-------------|
| Guest | expertise, credentials | Podcast guest or host |
| Podcast | host | A podcast show (not episode) |
| Topic | domain | Subject area: sleep, dopamine, fasting |
| Study | authors, year, journal, doi | Scientific paper referenced |
| Book | author | Book recommended or referenced |
| Product | product_type | Supplement, device, app, tool |
| Protocol | category, difficulty | Actionable routine or method |

## Edge Types

| Edge | Source → Target | Key Fields | Description |
|------|----------------|-----------|-------------|
| MakesClaim | Guest → Topic | insight_type, confidence, start/end_time, youtube_url | Guest makes a factual claim |
| DescribesProtocol | Guest → Protocol | start/end_time, youtube_url | Guest describes a routine |
| ReferencesStudy | Guest → Study | context | Guest cites a paper |
| RecommendsBook | Guest → Book | strength | Guest recommends a book |
| RecommendsProduct | Guest → Product | usage | Guest mentions a product |
| AppearsOn | Guest → Podcast | episode_title, episode_number, episode_date, youtube_id | Guest appearance |
| RelatesTo | Topic → Topic | relationship | Topic connections |
| SupportsProtocol | Study → Protocol | strength | Study supports a protocol |

## Query Layer

Six async query functions power frontend pages:

```python
from podcast_vault.queries import (
    get_topic_page,                    # Topic page: all claims, studies, protocols
    get_guest_profile,                 # Guest page: appearances, claims, recommendations
    find_agreements_and_disagreements, # Where guests agree or disagree
    get_cross_podcast_insights,        # What a guest said across different shows
    get_most_referenced_studies,       # Most-cited studies across all podcasts
    get_protocol_comparison,           # Compare protocols for the same goal
)

# Topic page — e.g., "What do experts say about cold exposure?"
results = await get_topic_page(driver, 'cold exposure')

# Agreements & disagreements — uses Graphiti's temporal edges
# (expired_at marks when a newer claim superseded an older one)
debates = await find_agreements_and_disagreements(driver, topic_name='fasting')

# Cross-podcast — same guest on Huberman Lab vs DOAC
insights = await get_cross_podcast_insights(driver, 'Dr. Peter Attia')

# Most referenced studies across all ingested podcasts
top_studies = await get_most_referenced_studies(driver, limit=10)

# Protocol comparison — different sleep protocols from different guests
protocols = await get_protocol_comparison(driver, 'sleep')
```

## Research Enrichment

Studies and books mentioned in podcasts often lack full metadata. The enrichment module provides data structures and Cypher queries to find unenriched entities:

```python
from podcast_vault.enrich import (
    EnrichedStudy,          # Full metadata after enrichment
    EnrichmentTask,         # Task for the enrichment agent
    UNENRICHED_STUDIES_QUERY,  # Find studies missing DOI
    UNENRICHED_BOOKS_QUERY,    # Find books missing author
)
```

The enrichment pipeline:
1. Query Neo4j for Study/Book nodes missing key metadata (doi, author)
2. Create `EnrichmentTask` objects with search queries
3. Use web search / PubMed API to find full metadata
4. Update graph nodes with `EnrichedStudy` data

## Project Structure

```
podcast_vault/
    __init__.py
    entity_types.py    # 7 Pydantic entity models
    edge_types.py      # 8 edge models + EDGE_TYPE_MAP
    extract.py         # Transcript chunking + extraction prompt
    show_notes.py      # URL extraction and classification
    ingest.py          # Graphiti ingestion config and helpers
    enrich.py          # Research enrichment data structures
    queries.py         # 6 Cypher query functions

tests/podcast_vault/
    __init__.py
    test_entity_types.py
    test_edge_types.py
    test_extract.py
    test_show_notes.py
    test_ingest.py
    test_enrich.py
    test_queries.py
```

## Running Tests

```bash
# From project root — uses programmatic invocation to handle sys.path
python -c "
import sys
sys.path.insert(0, '.')
import pytest
sys.exit(pytest.main(['tests/podcast_vault/', '--noconftest', '-v']))
"

# Lint
ruff check podcast_vault/ tests/podcast_vault/
```

> **Note:** The `--noconftest` flag is required because the root `conftest.py` imports FalkorDB which may not be installed. The programmatic invocation with `sys.path.insert` ensures `podcast_vault` is importable despite `pythonpath` not being read from `pytest.ini` when `--noconftest` is used.
