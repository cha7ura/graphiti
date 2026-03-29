# News Timeline Analysis

A system built on [Graphiti](https://github.com/getzep/graphiti) to track contradictions, temporal patterns, and source disagreements in Sri Lankan news articles.

Uses Graphiti's bi-temporal edge model to preserve full history of political statements, economic data, policy positions, and recurring events — enabling timeline views, flip-flop detection, and year-over-year comparisons.

## Two-Phase Approach

### Phase 1: Discovery (Loose Schema)

Ingest a sample of articles with 5 broad entity types (`Person`, `Organization`, `Location`, `Policy`, `Event`) and no custom edge types. Let Graphiti extract relationships organically, then analyze what emerges.

### Phase 2: Production (Refined Schema)

Based on Phase 1 findings, re-ingest with 9 refined entity types, 8 typed edges, and source-aware design into a separate graph partition.

## Quick Start

### Prerequisites

- Python 3.11+
- Neo4j 5.26+ running locally or remotely
- OpenAI API key (for Graphiti's LLM extraction and embeddings)
- Graphiti installed: `pip install graphiti-core`

### Phase 1: Discovery Ingestion

```python
import asyncio
from datetime import datetime, timezone

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from news_analysis.ingest import (
    PHASE_1_ENTITY_TYPES,
    PHASE_1_GROUP_ID,
    PHASE_1_INSTRUCTIONS,
    build_episode_name,
    build_source_description,
)

async def main():
    graphiti = Graphiti(
        "bolt://localhost:7687",
        "neo4j",
        "password",
    )
    await graphiti.build_indices_and_constraints()

    article = {
        "id": "art_001",
        "title": "President announces new economic policy",
        "body": "President Wickremesinghe announced today that...",
        "outlet": "Daily Mirror",
        "published_date": datetime(2024, 3, 15, tzinfo=timezone.utc),
        "category": "politics",
    }

    await graphiti.add_episode(
        name=build_episode_name(article["outlet"], article["id"]),
        episode_body=article["body"],
        source_description=build_source_description(
            article["title"], article["outlet"], article["category"]
        ),
        reference_time=article["published_date"],
        source=EpisodeType.text,
        group_id=PHASE_1_GROUP_ID,
        entity_types=PHASE_1_ENTITY_TYPES,
        custom_extraction_instructions=PHASE_1_INSTRUCTIONS,
    )

asyncio.run(main())
```

### Gap Analysis (Between Phases)

After ingesting a sample, analyze what the graph looks like:

```python
from news_analysis.gap_analysis import run_gap_analysis

# driver = graphiti.driver
results = await run_gap_analysis(driver)

# What edge types were extracted?
for row in results.edge_types:
    print(f"{row['edge_type']}: {row['freq']}")

# Which entities are most connected?
for row in results.key_entities:
    print(f"{row['name']} ({row['labels']}): {row['connections']} connections")

# Any contradictions already detected?
for row in results.contradictions:
    print(f"{row['edge_type']}: {row['fact']} (expired {row['expired_at']})")
```

### Phase 2: Production Ingestion

```python
from graphiti_core.nodes import EpisodeType, RawEpisode

from news_analysis.edge_types import EDGE_TYPE_MAP
from news_analysis.ingest import (
    PHASE_2_EDGE_TYPES,
    PHASE_2_ENTITY_TYPES,
    PHASE_2_GROUP_ID,
    PHASE_2_INSTRUCTIONS,
    sort_articles_chronologically,
)

# Sort chronologically for correct temporal invalidation
articles_sorted = sort_articles_chronologically(articles)

raw_episodes = [
    RawEpisode(
        name=f"{a['outlet'].replace(' ', '-')}_{a['id']}",
        content=a["body"],
        source_description=f"News article: '{a['title']}' from {a['outlet']}",
        reference_time=a["published_date"],
        source=EpisodeType.text,
    )
    for a in articles_sorted
]

await graphiti.add_episode_bulk(
    bulk_episodes=raw_episodes,
    group_id=PHASE_2_GROUP_ID,
    entity_types=PHASE_2_ENTITY_TYPES,
    edge_types=PHASE_2_EDGE_TYPES,
    edge_type_map=EDGE_TYPE_MAP,
    custom_extraction_instructions=PHASE_2_INSTRUCTIONS,
)
```

## Querying the Graph

### Entity Timeline

Get the full temporal history of any entity:

```python
from news_analysis.queries import get_entity_timeline

timeline = await get_entity_timeline(driver, "Ranil Wickremesinghe")

for edge in timeline:
    status = "EXPIRED" if edge["expired_at"] else "CURRENT"
    print(f"[{status}] {edge['valid_at']} | {edge['relation']} -> {edge['target']}: {edge['fact']}")
```

Example output:
```
[CURRENT]  2022-07-21 | HOLDS_POSITION -> President
[CURRENT]  2022-07-21 | BELONGS_TO_PARTY -> UNP
[EXPIRED]  2023-03-15 | MAKES_STATEMENT -> Tax Reform: "will not increase VAT"
[CURRENT]  2023-11-20 | MAKES_STATEMENT -> Tax Reform: "VAT increase necessary"
```

### Contradiction Finder

Find political flip-flops and changed positions:

```python
from news_analysis.queries import find_contradictions

contradictions = await find_contradictions(driver, entity_name="Ranil Wickremesinghe")

for c in contradictions:
    print(f"{c['entity']} on {c['target']}:")
    print(f"  BEFORE ({c['old_valid_at']}): {c['old_fact']}")
    print(f"  AFTER  ({c['new_valid_at']}): {c['new_fact']}")
    print()
```

### Recurring Patterns

Find stories that repeat year over year:

```python
from news_analysis.queries import find_recurring_patterns

patterns = await find_recurring_patterns(driver, min_occurrences=2)

for p in patterns:
    print(f"{p['entity']} -> {p['target']} ({p['relation']})")
    for occ in p["occurrences"]:
        print(f"  {occ['year']}: {occ['fact']}")
```

Example output:
```
Disaster Management Centre -> Annual Flood Damage (REPORTS_VALUE)
  2022: Flood damage estimated at Rs 3.2 billion
  2023: Flood damage estimated at Rs 5.1 billion
  2024: Flood damage estimated at Rs 8.7 billion
```

### Source Disagreements

Find cases where different sources report different values:

```python
from news_analysis.queries import find_source_disagreements

disagreements = await find_source_disagreements(driver, target_name="Inflation Rate")

for d in disagreements:
    print(f"{d['indicator']}:")
    print(f"  {d['source_a']}: {d['claim_a']}")
    print(f"  {d['source_b']}: {d['claim_b']}")
```

## Entity Types

### Phase 1 (Discovery)

| Type | Purpose |
|---|---|
| `Person` | Any named individual |
| `Organization` | Parties, government bodies, companies, NGOs |
| `Location` | Districts, provinces, cities, countries |
| `Policy` | Laws, bills, agreements, reforms |
| `Event` | Protests, elections, disasters, incidents |

### Phase 2 (Production)

| Type | Purpose |
|---|---|
| `Politician` | Elected officials, ministers, party leaders |
| `GovernmentBody` | Ministries, departments, commissions, courts |
| `PoliticalParty` | SLPP, SJB, UNP, JVP/NPP, SLFP, TNA, etc. |
| `EconomicIndicator` | Inflation, GDP, debt ratio, forex reserves |
| `Policy` | Tax reforms, IMF programs, constitutional amendments |
| `Event` | Elections, protests, disasters, scandals |
| `Location` | Sri Lankan and international locations |
| `InternationalEntity` | IMF, World Bank, UN, foreign governments |
| `NewsOutlet` | News publications and media organizations |

## Edge Types

| Edge | Connects | Tracks |
|---|---|---|
| `HoldsPosition` | Politician -> GovernmentBody | Career timeline |
| `MakesStatement` | Person/Org -> Topic | What was said, when, in what context |
| `SupportsPolicy` | Person/Party -> Policy | Policy stance with strength |
| `OpposesPolicy` | Person/Party -> Policy | Opposition stance with strength |
| `ReportsValue` | Source -> EconomicIndicator | Who reported what value |
| `BelongsToParty` | Politician -> PoliticalParty | Party membership and role |
| `InvolvedInEvent` | Person/Org/Party -> Event | Role in events |
| `EnforcesPolicy` | GovernmentBody -> Policy | Implementation status |

## How Contradictions Work

Graphiti's bi-temporal edge model tracks 4 timestamps per edge:

| Field | Meaning |
|---|---|
| `created_at` | When the record was created in the graph |
| `valid_at` | When the real-world fact became true |
| `invalid_at` | When the real-world fact stopped being true |
| `expired_at` | When new information superseded this edge |

When a new article contradicts an old fact, Graphiti:
1. Detects the contradiction via LLM deduplication
2. Marks the old edge with `expired_at = now`
3. Creates the new edge with fresh `valid_at`
4. **Keeps both edges** in the graph

This means you can always query the full history and build timelines.

## Source-Aware Design

When multiple sources report different values for the same thing, the source is modeled as the edge's **source node**, not as an attribute:

```
(Central Bank) --[REPORTS_VALUE]--> (Inflation Rate)  value="4.2%"
(Opposition)   --[REPORTS_VALUE]--> (Inflation Rate)  value="11.3%"
```

Different source nodes prevent Graphiti from incorrectly deduplicating legitimate disagreements.

## Project Structure

```
news_analysis/
    __init__.py
    entity_types.py      # Phase 1 + Phase 2 Pydantic entity models
    edge_types.py        # Edge type models + edge type map
    ingest.py            # Ingestion config, instructions, helpers
    gap_analysis.py      # Cypher queries for Phase 1 analysis
    queries.py           # Timeline, contradiction, pattern, disagreement queries
```

## Running Tests

```bash
python -m pytest tests/news_analysis/ -v --noconftest
```

## Design Docs

- [Design Spec](../docs/superpowers/specs/2026-03-29-sri-lanka-news-timeline-analysis-design.md)
- [Implementation Plan](../docs/superpowers/plans/2026-03-29-news-timeline-analysis.md)
