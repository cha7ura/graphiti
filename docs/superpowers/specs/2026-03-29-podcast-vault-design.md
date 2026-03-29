# Podcast Vault — Design Spec

## Overview

A knowledge extraction and cross-referencing system built on Graphiti for long-form podcast episodes. Extracts structured insights (claims, frameworks, protocols, stories, opinions, recommendations) from transcripts with timestamps, connects them via a knowledge graph, and enables topic pages, guest profiles, agreement/disagreement detection, and cross-podcast comparisons.

Target podcasts: Diary of a CEO, Modern Wisdom (Chris Williamson), Lex Fridman, Huberman Lab, and similar long-form interview shows.

## Architecture: Approach B (Pre-Process + Graphiti)

A pre-processing layer extracts structured insights from transcripts before feeding them to Graphiti. Each insight becomes one Graphiti episode. Graphiti handles entity resolution (same guest across podcasts), topic linking, and contradiction detection. A research enrichment agent runs post-ingestion to fill in study metadata and process show note links.

No Graphiti core changes required.

---

## Data Flow

```
Your Transcription Project (Whisper)
    |
    v
Full transcript + word-level timestamps + episode metadata
    |
    v
+----------------------------------+
|  podcast_vault/extract.py        |  <- LLM insight extraction
|  Chunks transcript -> extracts   |
|  structured insights with        |
|  timestamps, guest, topic,       |
|  insight_type, references        |
+----------------------------------+
    |
    v
Structured insights (list of ExtractedInsight)
    |
    v
+----------------------------------+
|  podcast_vault/ingest.py         |  <- Feeds insights to Graphiti
|  Each insight -> add_episode()   |
|  Graphiti handles dedup,         |
|  entity resolution, edges        |
+----------------------------------+
    |
    v
+----------------------------------+
|  podcast_vault/show_notes.py     |  <- Parse show notes URLs
|  Extracts + classifies links     |
|  from YouTube descriptions       |
+----------------------------------+
    |
    v
+----------------------------------+
|  podcast_vault/enrich.py         |  <- Research enrichment agent
|  Finds referenced papers/books   |
|  via web search, extracts        |
|  summary + conclusion, feeds     |
|  back into Graphiti              |
+----------------------------------+
    |
    v
+----------------------------------+
|  podcast_vault/queries.py        |  <- Query layer for frontend
|  Topic pages, guest profiles,    |
|  agreement/disagreement finder,  |
|  cross-podcast comparisons       |
+----------------------------------+
```

Key design choice: **each extracted insight becomes one Graphiti episode.** A 2-hour podcast with 30 insights = 30 episodes, each with its own timestamp range, guest attribution, and topic. Graphiti then connects them via entity resolution.

---

## Data Sources

- **Input**: Transcribed podcast episodes from a separate transcription project (Whisper)
- **Metadata per episode**: podcast name, episode title, episode number, YouTube ID, publish date, guest names, host name
- **Optional**: YouTube description / show notes (for URL extraction)
- **Transcript format**: Word-level segments with start/end timestamps in seconds

---

## Entity Types

```python
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
```

| Type | What it captures | Cross-podcast value |
|---|---|---|
| Guest | The expert making claims | Same guest on Huberman + DOAC = merged entity |
| Podcast | The show itself | Group by show, compare across shows |
| Topic | Subject areas | Topic pages aggregate all claims from all guests |
| Study | Referenced research | Same study cited by multiple guests gets deduped |
| Book | Book recommendations | "5 guests recommended this book" |
| Product | Supplements, tools | Track what products experts recommend |
| Protocol | Actionable methods | Compare different guests' routines |

Topic nodes are **auto-created by Graphiti** during extraction. When a guest talks about "dopamine", "sleep", "cold exposure" — these become Topic entities. Graphiti deduplicates "cold plunge" and "cold exposure" into the same entity over time.

---

## Edge Types

```python
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
```

### Edge Type Map

```python
EDGE_TYPE_MAP = {
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

### Example Graph

When Huberman says "Cold exposure for 2 minutes increases dopamine by 250%, based on the Sramek 2000 study" at 14:23 in episode #142:

```
(Andrew Huberman) --[MAKES_CLAIM]--> (Dopamine)
    fact: "Cold exposure for 2 min increases dopamine by 250%"
    start_time: "14:23", end_time: "16:05"
    youtube_url: "https://youtube.com/watch?v=xyz&t=863"

(Andrew Huberman) --[APPEARS_ON]--> (Huberman Lab)
    episode_title: "#142: Cold Exposure Benefits"

(Andrew Huberman) --[REFERENCES_STUDY]--> (Sramek et al. 2000)
    context: "supports_claim"

(Dopamine) --[RELATED_TO]--> (Cold Exposure)
    relationship: "improves"
```

When a **different guest** on Lex Fridman talks about the same topic, Graphiti creates new edges from the new guest to the same deduped Topic nodes — enabling cross-podcast comparison.

---

## Insight Extraction Layer

### Input Format

```python
@dataclass
class TranscriptSegment:
    text: str
    start_time: float    # seconds
    end_time: float      # seconds

@dataclass
class EpisodeTranscript:
    podcast_name: str
    episode_title: str
    youtube_id: str
    published_date: datetime
    guests: list[str]
    host: str
    segments: list[TranscriptSegment]
    episode_number: str | None = None
    description: str | None = None
```

### Extraction Pipeline

1. Chunk transcript into ~5 min windows with 30s overlap
2. LLM extracts insights from each chunk
3. Parse show notes for URLs
4. Merge overlapping insights across chunk boundaries
5. Output: `list[ExtractedInsight]` ready for Graphiti

### Extracted Insight Structure

```python
@dataclass
class ExtractedInsight:
    insight_type: str              # claim, framework, protocol, story, opinion, recommendation
    text: str                      # The insight in clean prose
    guest: str                     # Who said it
    topics: list[str]              # Topics covered
    start_time: float              # Timestamp in seconds
    end_time: float                # Timestamp in seconds
    referenced_studies: list[str]  # ["Sramek et al. 2000"]
    referenced_books: list[str]    # ["Why We Sleep by Matthew Walker"]
    referenced_products: list[str] # ["AG1", "Whoop band"]
    protocol_name: str | None      # If insight describes a protocol
```

### Extraction Prompt

```
You are extracting structured insights from a podcast transcript chunk.

SPEAKERS:
{speakers}

TRANSCRIPT CHUNK (timestamps in seconds):
{chunk_text}

Extract every distinct insight. An insight is one of:
- **claim**: A factual assertion ("X causes Y", "doing X increases Y by Z%")
- **framework**: A mental model or structured thinking pattern
- **protocol**: A specific actionable routine with steps
- **story**: A personal anecdote or experience
- **opinion**: A subjective viewpoint
- **recommendation**: Explicitly recommending a book, product, tool, or practice

For each insight extract:
1. insight_type: one of the types above
2. text: clean, self-contained statement (rewrite for clarity, not a raw quote)
3. guest: who said it
4. topics: 1-3 topic labels (consistent naming: "sleep" not "sleeping")
5. start_time / end_time: timestamps in seconds
6. referenced_studies: papers mentioned (author + year if available)
7. referenced_books: books mentioned (title + author)
8. referenced_products: supplements, tools, devices, apps mentioned
9. protocol_name: if a protocol, give it a clear name

RULES:
- Only extract what was explicitly said
- One insight per distinct claim/idea
- Use exact timestamp ranges
```

### How Insights Feed Into Graphiti

Each ExtractedInsight becomes one `add_episode()` call:

```python
await graphiti.add_episode(
    name=f"{podcast_name}_{youtube_id}_{int(start_time)}",
    episode_body=insight.text,
    source_description="Insight from '{title}' on {podcast}, guest: {guest}, timestamp: {start}-{end}, youtube: {url}",
    reference_time=episode.published_date,
    source=EpisodeType.text,
    group_id=f"podcast-{slugified_podcast_name}",
    entity_types=ENTITY_TYPES,
    edge_types=EDGE_TYPES,
    edge_type_map=EDGE_TYPE_MAP,
    custom_extraction_instructions=GRAPHITI_EXTRACTION_INSTRUCTIONS,
)
```

---

## Show Notes Processing

### URL Extraction and Classification

Parse URLs from YouTube descriptions and classify them by domain pattern:

| Pattern | Classification |
|---|---|
| pubmed.ncbi, doi.org, nature.com, cell.com, bmj.com, jamanetwork.com, arxiv.org | study |
| amazon.com, iherb.com, thorne.com, momentous.com, drinkag1.com | product |
| wikipedia.org, twitter.com, linkedin.com, instagram.com | guest_bio |
| Everything else | other |

```python
@dataclass
class ShowNoteLink:
    url: str
    link_type: str    # study, product, guest_bio, other
    context: str      # Surrounding text from show notes
```

Show notes are ingested as a separate Graphiti episode linked to the same podcast, enabling entity resolution between transcript-referenced studies and show-note-linked studies.

---

## Research Enrichment Agent

Runs post-ingestion to fill in Study/Book metadata and process show note URLs.

### Flow

1. Query graph for Study nodes with missing DOI/journal/abstract
2. For each unenriched study:
   a. Web search: "{authors} {year} {title keywords}"
   b. If PubMed/DOI found -> fetch abstract + conclusion
   c. Update Study node attributes (doi, journal)
   d. Ingest abstract as new episode linked to the Study
3. Query graph for Book nodes with missing author
4. For each unenriched book:
   a. Web search for book metadata
   b. Update Book node attributes
5. Process show note links:
   a. Study links -> fetch paper, extract metadata, merge with existing Study nodes
   b. Product links -> enrich Product nodes

### Data Structures

```python
@dataclass
class EnrichedStudy:
    original_name: str        # What the guest said
    title: str | None         # Full paper title
    authors: str | None       # Full author list
    year: str | None
    journal: str | None
    doi: str | None
    abstract: str | None
    conclusion: str | None
    url: str | None

@dataclass
class EnrichmentTask:
    entity_uuid: str
    entity_name: str
    entity_type: str          # Study, Book, Product
    search_query: str
    source: str               # transcript_reference, show_notes_link
    show_note_url: str | None
```

### Enrichment Queries

```cypher
-- Find studies that need enrichment
MATCH (s:Study {group_id: $group_id})
WHERE s.attributes.doi IS NULL OR s.attributes.doi = ''
RETURN s.uuid AS uuid, s.name AS name, s.attributes AS attributes
LIMIT 50

-- Find books that need enrichment
MATCH (b:Book {group_id: $group_id})
WHERE b.attributes.author IS NULL OR b.attributes.author = ''
RETURN b.uuid AS uuid, b.name AS name, b.attributes AS attributes
LIMIT 50
```

---

## Query Layer

### 6.1 Topic Page

Powers pages like "/topic/cold-exposure" — aggregates all claims, protocols, studies, and products related to a topic across all guests and podcasts.

```python
async def get_topic_page(driver, topic_name, group_ids=None):
    """Returns: claims (with guest, timestamp, youtube_url), protocols,
    referenced studies, recommended products, related sub-topics."""
```

Example output for "Cold Exposure":
```
claims:
  - guest: "Andrew Huberman", fact: "2 min cold increases dopamine 250%",
    youtube_url: "...&t=863", podcast: "Huberman Lab"
  - guest: "Wim Hof", fact: "Cold exposure strengthens immune system",
    youtube_url: "...&t=1205", podcast: "DOAC"

protocols:
  - name: "Deliberate Cold Exposure Protocol", guest: "Andrew Huberman"

studies:
  - name: "Sramek et al. 2000", referenced_by: ["Huberman", "Rhonda Patrick"]

related_topics:
  - "Dopamine" (improves), "Immune System" (improves), "Brown Fat" (activates)
```

### 6.2 Guest Profile

Powers pages like "/guest/andrew-huberman" — everything a guest has said across all appearances.

```python
async def get_guest_profile(driver, guest_name):
    """Returns: appearances (podcasts + episodes), claims grouped by topic,
    protocols, book/product recommendations, referenced studies."""
```

### 6.3 Agreement / Disagreement Finder

Where multiple guests agree or disagree on the same topic.

```python
async def find_agreements_and_disagreements(driver, topic_name=None):
    """Returns: agreements (multiple guests, similar claims, same topic),
    disagreements (Graphiti-detected contradictions between guests)."""
```

Example for "Fasting":
```
agreements:
  - "Time-restricted eating improves metabolic health"
    - Andrew Huberman (Huberman Lab #89, 23:15)
    - Peter Attia (Lex Fridman #321, 1:04:22)

disagreements:
  - Huberman: "16:8 fasting is optimal for most people"
    vs Attia: "Extended fasting has diminishing returns for most"
```

### 6.4 Cross-Podcast Comparison

When the same guest appears on multiple podcasts.

```python
async def get_cross_podcast_insights(driver, guest_name):
    """Returns: insights grouped by podcast appearance,
    new claims vs repeated claims, evolved positions."""
```

### 6.5 Study Impact

Most referenced studies across all podcasts.

```python
async def get_most_referenced_studies(driver, group_ids=None, limit=20):
    """Returns: studies ranked by number of guest references,
    with enriched metadata and citing guests."""
```

### 6.6 Protocol Comparison

Compare different guests' protocols for the same goal.

```python
async def get_protocol_comparison(driver, topic_name):
    """Returns: all protocols related to a topic, grouped by guest,
    with timestamps and youtube links."""
```

### Query Summary

| Query | Frontend Page |
|---|---|
| `get_topic_page` | /topic/cold-exposure |
| `get_guest_profile` | /guest/andrew-huberman |
| `find_agreements_and_disagreements` | Comparison section on topic pages |
| `get_cross_podcast_insights` | Guest page: cross-appearance analysis |
| `get_most_referenced_studies` | /research — most cited papers |
| `get_protocol_comparison` | /protocols/morning-routine — side-by-side |

---

## Project Structure

```
podcast_vault/
    __init__.py
    entity_types.py       # 7 Pydantic entity models + ENTITY_TYPES dict
    edge_types.py         # 8 edge models + EDGE_TYPES dict + EDGE_TYPE_MAP
    extract.py            # TranscriptSegment, EpisodeTranscript, ExtractedInsight,
                          #   chunking, extraction prompt, format helpers
    show_notes.py         # ShowNoteLink, URL extraction, classification
    ingest.py             # Graphiti ingestion config, helpers, extraction instructions
    enrich.py             # Research enrichment agent, EnrichedStudy, EnrichmentTask
    queries.py            # 6 query functions for frontend
```

---

## How This Differs from News Analysis

| Aspect | News Analysis | Podcast Vault |
|---|---|---|
| Input | Full news articles | Pre-extracted insights from transcripts |
| Core value | Contradiction detection over time | Knowledge aggregation across sources |
| Temporal focus | When facts changed | When insights were shared (timestamps) |
| Source model | NewsOutlet as entity | Guest as entity (the expert, not the show) |
| Cross-source | Same story, different outlets | Same guest, different podcasts |
| Enrichment | None | Web search for referenced papers/books |
| Frontend anchor | Entity timeline | Topic pages + guest profiles |
