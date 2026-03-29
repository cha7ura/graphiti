# Sri Lanka News Timeline Analysis — Design Spec

## Overview

A system built on Graphiti to track contradictions, temporal patterns, and source disagreements in Sri Lankan news articles. Uses Graphiti's bi-temporal edge model to preserve full history of political statements, economic data, policy positions, and recurring events — enabling timeline views, flip-flop detection, and year-over-year comparisons.

## Approach: Two-Phase Discovery

### Phase 1 — Discovery Run (Loose Schema)
- Ingest a sample of articles with broad entity types
- No custom edge types — let Graphiti extract organically
- Analyze the resulting graph to discover dominant patterns

### Phase 2 — Production Run (Refined Schema)
- Define rich entity types and constrained edge types based on Phase 1 findings
- Re-ingest all articles with the refined schema into a separate group
- Build query layer for timelines, contradictions, and patterns

---

## Data Sources

- **Input**: Scraped Sri Lankan news articles
- **Reliable metadata per article**: title, body, publication date, news outlet name
- **Optional metadata**: author/journalist, article category/section

---

## Phase 1: Discovery Schema

### Entity Types

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    """Any named individual mentioned in news articles"""
    role: str | None = Field(default=None, description="Role if mentioned (politician, official, activist, etc.)")

class Organization(BaseModel):
    """Political parties, government bodies, companies, NGOs, international orgs"""
    org_type: str | None = Field(default=None, description="Type: political_party, government, military, ngo, company, international")

class Location(BaseModel):
    """Districts, provinces, cities, countries referenced in articles"""
    location_type: str | None = Field(default=None, description="Type: country, province, district, city, area")

class Policy(BaseModel):
    """Laws, bills, agreements, economic policies, reforms"""
    domain: str | None = Field(default=None, description="Domain: economic, social, constitutional, foreign, environmental")

class Event(BaseModel):
    """Protests, elections, disasters, diplomatic events, incidents"""
    event_type: str | None = Field(default=None, description="Type: election, protest, disaster, diplomatic, legislative, scandal")
```

### Edge Types
None — let Graphiti extract freely.

### Ingestion Config

```python
PHASE_1_INSTRUCTIONS = """
You are analyzing Sri Lankan news articles. Extract all named entities
and relationships. Pay special attention to:
- Politicians and their stated positions/opinions
- Economic figures and who is reporting them
- Government decisions and policy changes
- References to past events or previous statements
"""

await graphiti.add_episode(
    name=f"{article['outlet']}_{article['id']}",
    episode_body=article['body'],
    source_description=f"News article: '{article['title']}' from {article['outlet']}",
    reference_time=article['published_date'],
    source=EpisodeType.text,
    group_id="sri-lanka-news-discovery",
    entity_types=PHASE_1_ENTITY_TYPES,
    custom_extraction_instructions=PHASE_1_INSTRUCTIONS,
)
```

### Gap Analysis Queries

Run after Phase 1 ingestion to inform Phase 2 schema design:

```python
async def run_gap_analysis(driver: GraphDriver):
    analyses = {}

    # 1. Edge types extracted organically — what relationships dominate?
    analyses['edge_types'] = await driver.execute_query("""
        MATCH ()-[e:RELATES_TO]->()
        RETURN e.name AS edge_type, count(e) AS freq
        ORDER BY freq DESC LIMIT 30
    """)

    # 2. Entity label distribution
    analyses['entity_distribution'] = await driver.execute_query("""
        MATCH (n:Entity {group_id: 'sri-lanka-news-discovery'})
        UNWIND labels(n) AS label
        WITH label WHERE label <> 'Entity'
        RETURN label, count(*) AS count
        ORDER BY count DESC
    """)

    # 3. Most connected entities (key players)
    analyses['key_entities'] = await driver.execute_query("""
        MATCH (n:Entity {group_id: 'sri-lanka-news-discovery'})-[e:RELATES_TO]-()
        RETURN n.name, labels(n), count(e) AS connections
        ORDER BY connections DESC LIMIT 30
    """)

    # 4. Contradictions already detected
    analyses['contradictions'] = await driver.execute_query("""
        MATCH ()-[e:RELATES_TO]->()
        WHERE e.expired_at IS NOT NULL
        RETURN e.name, e.fact, e.valid_at, e.expired_at
        ORDER BY e.expired_at DESC LIMIT 30
    """)

    # 5. Temporal coverage per edge type
    analyses['temporal_coverage'] = await driver.execute_query("""
        MATCH ()-[e:RELATES_TO]->()
        RETURN e.name AS edge_type,
               count(e) AS total,
               count(e.valid_at) AS has_valid_at,
               count(e.invalid_at) AS has_invalid_at,
               count(e.expired_at) AS has_expired_at
        ORDER BY total DESC LIMIT 20
    """)

    # 6. Person entities — which should be reclassified as Politician?
    analyses['person_roles'] = await driver.execute_query("""
        MATCH (p:Person {group_id: 'sri-lanka-news-discovery'})
        RETURN p.name, p.summary, p.attributes
        ORDER BY p.name LIMIT 50
    """)

    return analyses
```

---

## Phase 2: Production Schema

### Entity Types

```python
class Politician(BaseModel):
    """Elected officials, ministers, party leaders, presidential candidates"""
    party: str | None = Field(default=None, description="Current political party name")
    title: str | None = Field(default=None, description="Honorific: Hon., Dr., etc.")

class GovernmentBody(BaseModel):
    """Ministries, departments, commissions, courts, parliament"""
    body_type: str | None = Field(default=None, description="ministry, department, commission, court, parliament, central_bank")
    jurisdiction: str | None = Field(default=None, description="national, provincial, or district level")

class PoliticalParty(BaseModel):
    """SLPP, SJB, UNP, JVP/NPP, SLFP, TNA, etc."""
    coalition: str | None = Field(default=None, description="Coalition or alliance name if part of one")

class EconomicIndicator(BaseModel):
    """Inflation rate, GDP, debt-to-GDP ratio, forex reserves, etc."""
    indicator_type: str | None = Field(default=None, description="inflation, gdp, debt_ratio, reserves, unemployment, interest_rate, exchange_rate")
    unit: str | None = Field(default=None, description="percentage, USD, LKR, billions, etc.")

class Policy(BaseModel):
    """Tax reforms, IMF programs, trade agreements, constitutional amendments"""
    domain: str | None = Field(default=None, description="economic, constitutional, foreign, social, environmental, military")
    status: str | None = Field(default=None, description="proposed, enacted, repealed, under_review")

class Event(BaseModel):
    """Elections, protests, disasters, diplomatic meetings, scandals"""
    event_type: str | None = Field(default=None, description="election, protest, disaster, diplomatic, legislative, scandal, crisis")
    recurring: bool | None = Field(default=None, description="True if this is a recurring event (annual budget, yearly floods, etc.)")

class Location(BaseModel):
    """Sri Lankan districts, provinces, cities, and international locations"""
    location_type: str | None = Field(default=None, description="country, province, district, city, area")

class InternationalEntity(BaseModel):
    """IMF, World Bank, UN, foreign governments involved in SL affairs"""
    entity_type: str | None = Field(default=None, description="multilateral, foreign_government, ngo, donor_agency")

class NewsOutlet(BaseModel):
    """News publication or media organization"""
    outlet_type: str | None = Field(default=None, description="newspaper, tv, online, wire_service, state_media")
    language: str | None = Field(default=None, description="Primary language: sinhala, tamil, english")
```

### Edge Types

```python
class HoldsPosition(BaseModel):
    """Politician holds a government position (Minister, MP, President, etc.)"""
    position_title: str | None = Field(default=None, description="The specific position: President, Minister of Finance, MP for Colombo, etc.")

class MakesStatement(BaseModel):
    """A person or org makes a public claim, promise, or assertion"""
    context: str | None = Field(default=None, description="Context: interview, parliament, press_conference, rally, social_media")
    topic: str | None = Field(default=None, description="What the statement is about: economy, policy, opposition, etc.")

class SupportsPolicy(BaseModel):
    """Person or party publicly supports a policy or position"""
    strength: str | None = Field(default=None, description="strong, conditional, lukewarm")

class OpposesPolicy(BaseModel):
    """Person or party publicly opposes a policy or position"""
    strength: str | None = Field(default=None, description="strong, conditional, lukewarm")

class ReportsValue(BaseModel):
    """A source reports a specific value for an economic indicator"""
    reported_value: str | None = Field(default=None, description="The actual value reported: '12.5%', 'USD 3.2 billion', etc.")
    reporting_source: str | None = Field(default=None, description="Who reported it: CBSL, IMF, Ministry of Finance, opposition claim")

class BelongsToParty(BaseModel):
    """Politician is a member of a political party"""
    role_in_party: str | None = Field(default=None, description="leader, deputy_leader, member, spokesperson")

class InvolvedInEvent(BaseModel):
    """Person, org, or party is involved in an event"""
    role: str | None = Field(default=None, description="organizer, participant, target, responder, critic")

class EnforcesPolicy(BaseModel):
    """Government body implements or enforces a policy"""
    enforcement_status: str | None = Field(default=None, description="implementing, partially_implementing, blocking, reviewing")
```

### Edge Type Map (Entity Pair Constraints)

```python
edge_type_map = {
    ("Politician", "GovernmentBody"): ["HoldsPosition"],
    ("Politician", "Policy"): ["SupportsPolicy", "OpposesPolicy"],
    ("Politician", "PoliticalParty"): ["BelongsToParty"],
    ("Politician", "Event"): ["InvolvedInEvent", "MakesStatement"],
    ("Politician", "EconomicIndicator"): ["MakesStatement", "ReportsValue"],
    ("PoliticalParty", "Policy"): ["SupportsPolicy", "OpposesPolicy"],
    ("PoliticalParty", "Event"): ["InvolvedInEvent"],
    ("GovernmentBody", "EconomicIndicator"): ["ReportsValue"],
    ("GovernmentBody", "Policy"): ["EnforcesPolicy"],
    ("GovernmentBody", "Event"): ["InvolvedInEvent"],
    ("InternationalEntity", "EconomicIndicator"): ["ReportsValue"],
    ("InternationalEntity", "Policy"): ["SupportsPolicy", "OpposesPolicy"],
    ("NewsOutlet", "EconomicIndicator"): ["ReportsValue"],
    ("NewsOutlet", "Event"): ["InvolvedInEvent"],
    ("NewsOutlet", "Politician"): ["MakesStatement"],
}
```

### Phase 2 Ingestion Config

```python
PHASE_2_INSTRUCTIONS = """
You are analyzing Sri Lankan news articles for a political accountability
and economic tracking system. Follow these rules:

ENTITY EXTRACTION:
- Classify elected officials, ministers, and party leaders as Politician
- Classify CBSL, ministries, courts as GovernmentBody
- When an article quotes someone, extract the quoted person as the source
  entity, NOT the news outlet
- Extract the news outlet itself as a NewsOutlet entity
- Economic figures (inflation, GDP, debt) are EconomicIndicator entities
- IMF, World Bank, foreign governments are InternationalEntity

TEMPORAL RULES:
- When a politician makes a statement, set valid_at to the article date
- When a statement contradicts a previous position, the LLM dedup will
  handle invalidation automatically
- For economic values, always extract the reporting period if mentioned
  (e.g., "Q3 2024 inflation" -> valid_at = 2024-07-01)
- For recurring events (annual budget, monsoon floods), extract each
  occurrence as a separate edge

SOURCE ATTRIBUTION:
- When the article says "according to CBSL" or "the opposition claims",
  make the cited source the edge's source node
- The news outlet should only be the source node when it's making
  its own editorial claim
"""

# Use bulk ingestion — sort articles chronologically first
articles_sorted = sorted(articles, key=lambda a: a['published_date'])

raw_episodes = [
    RawEpisode(
        name=f"{a['outlet']}_{a['id']}",
        content=a['body'],
        source_description=f"News article: '{a['title']}' from {a['outlet']}",
        reference_time=a['published_date'],
        source=EpisodeType.text,
    )
    for a in articles_sorted
]

await graphiti.add_episode_bulk(
    bulk_episodes=raw_episodes,
    group_id="sri-lanka-news",
    entity_types=PHASE_2_ENTITY_TYPES,
    edge_types=PHASE_2_EDGE_TYPES,
    custom_extraction_instructions=PHASE_2_INSTRUCTIONS,
)
```

---

## Query Layer

### 4.1 Entity Timeline

Returns all edges (current + invalidated) for an entity, sorted by `valid_at`.

```python
async def get_entity_timeline(
    driver: GraphDriver,
    entity_name: str,
    group_id: str = "sri-lanka-news",
    edge_types: list[str] | None = None,
) -> list[dict]:
    edge_type_filter = ""
    if edge_types:
        edge_type_filter = "AND e.name IN $edge_types"

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[e:RELATES_TO]-(m:Entity)
        WHERE n.name = $entity_name {edge_type_filter}
        RETURN e.uuid AS uuid,
               e.name AS relation,
               e.fact AS fact,
               e.valid_at AS valid_at,
               e.invalid_at AS invalid_at,
               e.expired_at AS expired_at,
               e.episodes AS episodes,
               n.name AS source,
               m.name AS target,
               e.attributes AS attributes
        ORDER BY e.valid_at ASC
    """

    results = await driver.execute_query(query,
        entity_name=entity_name,
        group_id=group_id,
        edge_types=edge_types or []
    )
    return results
```

### 4.2 Contradiction Finder

Finds pairs of edges where a newer fact invalidated an older one.

```python
async def find_contradictions(
    driver: GraphDriver,
    group_id: str = "sri-lanka-news",
    entity_name: str | None = None,
    since: datetime | None = None,
) -> list[dict]:
    entity_filter = "AND n.name = $entity_name" if entity_name else ""
    time_filter = "AND old_edge.expired_at >= $since" if since else ""

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[old_edge:RELATES_TO]->(m:Entity)
        WHERE old_edge.expired_at IS NOT NULL {entity_filter} {time_filter}

        MATCH (n)-[new_edge:RELATES_TO]->(m)
        WHERE new_edge.created_at >= old_edge.expired_at
          AND new_edge.expired_at IS NULL
          AND new_edge.name = old_edge.name

        RETURN n.name AS entity,
               m.name AS target,
               old_edge.name AS relation,
               old_edge.fact AS old_fact,
               old_edge.valid_at AS old_valid_at,
               old_edge.expired_at AS expired_at,
               old_edge.attributes AS old_attributes,
               new_edge.fact AS new_fact,
               new_edge.valid_at AS new_valid_at,
               new_edge.attributes AS new_attributes,
               old_edge.episodes AS old_sources,
               new_edge.episodes AS new_sources
        ORDER BY old_edge.expired_at DESC
    """

    results = await driver.execute_query(query,
        group_id=group_id,
        entity_name=entity_name,
        since=since
    )
    return results
```

### 4.3 Recurring Pattern Detector

Finds the same relationship repeated across different years.

```python
async def find_recurring_patterns(
    driver: GraphDriver,
    group_id: str = "sri-lanka-news",
    min_occurrences: int = 2,
    entity_name: str | None = None,
) -> list[dict]:
    entity_filter = "WHERE n.name = $entity_name" if entity_name else ""

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[e:RELATES_TO]->(m:Entity)
        {entity_filter}
        WITH n.name AS entity,
             m.name AS target,
             e.name AS relation,
             collect({{
                 fact: e.fact,
                 valid_at: e.valid_at,
                 attributes: e.attributes,
                 episodes: e.episodes,
                 year: date(e.valid_at).year
             }}) AS occurrences
        WHERE size(occurrences) >= $min_occurrences

        WITH entity, target, relation, occurrences,
             [o IN occurrences | o.year] AS years
        WHERE size(apoc.coll.toSet(years)) >= $min_occurrences

        RETURN entity, target, relation, occurrences
        ORDER BY size(occurrences) DESC
    """

    results = await driver.execute_query(query,
        group_id=group_id,
        min_occurrences=min_occurrences,
        entity_name=entity_name
    )
    return results
```

### 4.4 Source Agreement/Disagreement

Finds cases where different sources report different values for the same indicator within the same time period.

```python
async def find_source_disagreements(
    driver: GraphDriver,
    group_id: str = "sri-lanka-news",
    target_name: str | None = None,
) -> list[dict]:
    target_filter = "AND target.name = $target_name" if target_name else ""

    query = f"""
        MATCH (source1:Entity {{group_id: $group_id}})-[e1:RELATES_TO {{name: 'REPORTS_VALUE'}}]->(target:Entity)
        MATCH (source2:Entity {{group_id: $group_id}})-[e2:RELATES_TO {{name: 'REPORTS_VALUE'}}]->(target)
        WHERE source1.uuid <> source2.uuid
          AND e1.expired_at IS NULL AND e2.expired_at IS NULL
          AND abs(duration.between(date(e1.valid_at), date(e2.valid_at)).months) <= 1
          {target_filter}

        RETURN target.name AS indicator,
               source1.name AS source_a,
               e1.fact AS claim_a,
               e1.attributes AS attrs_a,
               source2.name AS source_b,
               e2.fact AS claim_b,
               e2.attributes AS attrs_b,
               e1.valid_at AS date_a,
               e2.valid_at AS date_b
    """

    results = await driver.execute_query(query,
        group_id=group_id,
        target_name=target_name
    )
    return results
```

---

## How Contradictions Get Captured

### Political Flip-Flop

```
2023-03: (Politician X) --[SUPPORTS_POLICY]--> (IMF Program)
         valid_at=2023-03, strength="strong", context="parliament"

2024-06: (Politician X) --[OPPOSES_POLICY]--> (IMF Program)
         valid_at=2024-06, strength="strong", context="rally"
         -> The 2023 SUPPORTS_POLICY edge gets expired_at=2024-06
```

### Economic Data Contradictions (Source-Aware)

```
(Central Bank) --[REPORTS_VALUE]--> (Inflation Rate) reported_value="4.2%"
(Opposition)   --[REPORTS_VALUE]--> (Inflation Rate) reported_value="11.3%"
-> Both coexist — different source nodes prevent false dedup
```

### Position Changes

```
2022: (Politician Y) --[HOLDS_POSITION]--> (Minister of Finance)
      valid_at=2022-01, invalid_at=2023-08

2023: (Politician Y) --[HOLDS_POSITION]--> (Opposition Leader)
      valid_at=2023-08
      -> Both edges preserved, full career timeline
```

### Recurring Annual Story

```
2023: (Govt) --[REPORTS_VALUE]--> (Flood Damage) reported_value="Rs 5B", valid_at=2023-05
2024: (Govt) --[REPORTS_VALUE]--> (Flood Damage) reported_value="Rs 8B", valid_at=2024-05
2025: (Govt) --[REPORTS_VALUE]--> (Flood Damage) reported_value="Rs 12B", valid_at=2025-05
-> Three edges, year-over-year comparison
```

---

## Two-Pass Strategy Decisions

| Decision | Choice | Reason |
|---|---|---|
| Separate group_id per phase | `sri-lanka-news-discovery` vs `sri-lanka-news` | Keep Phase 1 graph for comparison, don't pollute production |
| Wipe before Phase 2? | No — use different group_id | Can delete discovery group later; keeping it enables quality comparison |
| Bulk vs single in Phase 2 | `add_episode_bulk` | Faster — single transaction, cross-episode dedup, efficient embeddings |
| Chronological order | Sort articles by `published_date` before ingesting | Ensures temporal invalidation chain is correct — older facts get invalidated by newer ones in the right order |

---

## Output Layers (Future)

1. **Graph layer** (this spec) — Graphiti models + query functions
2. **API layer** (future) — FastAPI endpoints wrapping the query functions
3. **Web dashboard** (future) — Timeline views, contradiction highlights, source comparison UI
