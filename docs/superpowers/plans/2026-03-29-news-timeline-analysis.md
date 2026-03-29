# News Timeline Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a news timeline analysis system on Graphiti that tracks political contradictions, economic data shifts, recurring patterns, and source disagreements in Sri Lankan news articles.

**Architecture:** A `news_analysis/` package at the project root containing: Pydantic entity/edge type definitions, two-phase ingestion scripts (discovery + production), a query layer for timelines/contradictions/patterns, and a gap analysis tool to bridge the phases. All code uses Graphiti's existing `add_episode`/`add_episode_bulk` APIs with custom entity types and edge types.

**Tech Stack:** Python 3.11+, Graphiti (graphiti_core), Pydantic v2, Neo4j 5.26+, pytest + pytest-asyncio

---

## File Structure

```
news_analysis/
    __init__.py
    entity_types.py          # Phase 1 + Phase 2 Pydantic entity models
    edge_types.py            # Phase 2 Pydantic edge models + edge type map
    ingest.py                # Phase 1 + Phase 2 ingestion functions
    gap_analysis.py          # Cypher queries to analyze Phase 1 results
    queries.py               # Timeline, contradiction, recurring, source disagreement queries

tests/
    news_analysis/
        __init__.py
        test_entity_types.py
        test_edge_types.py
        test_queries.py
        test_ingest.py
        test_gap_analysis.py
```

---

### Task 1: Phase 1 Entity Types

**Files:**
- Create: `news_analysis/__init__.py`
- Create: `news_analysis/entity_types.py`
- Create: `tests/news_analysis/__init__.py`
- Create: `tests/news_analysis/test_entity_types.py`

- [ ] **Step 1: Write tests for Phase 1 entity types**

```python
# tests/news_analysis/test_entity_types.py
from pydantic import BaseModel

from news_analysis.entity_types import (
    Event,
    Location,
    Organization,
    Person,
    Policy,
)


class TestPhase1EntityTypes:
    def test_person_defaults(self):
        p = Person()
        assert p.role is None

    def test_person_with_role(self):
        p = Person(role='politician')
        assert p.role == 'politician'

    def test_organization_defaults(self):
        o = Organization()
        assert o.org_type is None

    def test_organization_with_type(self):
        o = Organization(org_type='political_party')
        assert o.org_type == 'political_party'

    def test_location_defaults(self):
        loc = Location()
        assert loc.location_type is None

    def test_location_with_type(self):
        loc = Location(location_type='district')
        assert loc.location_type == 'district'

    def test_policy_defaults(self):
        p = Policy()
        assert p.domain is None

    def test_policy_with_domain(self):
        p = Policy(domain='economic')
        assert p.domain == 'economic'

    def test_event_defaults(self):
        e = Event()
        assert e.event_type is None

    def test_event_with_type(self):
        e = Event(event_type='election')
        assert e.event_type == 'election'

    def test_all_are_pydantic_models(self):
        """Graphiti requires entity types to be Pydantic BaseModel subclasses"""
        for model_cls in [Person, Organization, Location, Policy, Event]:
            assert issubclass(model_cls, BaseModel)

    def test_all_fields_optional(self):
        """All fields must be optional (None default) for Graphiti extraction"""
        for model_cls in [Person, Organization, Location, Policy, Event]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None, (
                    f'{model_cls.__name__}.{field_name} is not optional'
                )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_entity_types.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'news_analysis'`

- [ ] **Step 3: Create the package and implement Phase 1 entity types**

```python
# news_analysis/__init__.py
```

```python
# news_analysis/entity_types.py
from pydantic import BaseModel, Field

# === Phase 1: Discovery Entity Types ===


class Person(BaseModel):
    """Any named individual mentioned in news articles"""

    role: str | None = Field(
        default=None,
        description='Role if mentioned (politician, official, activist, etc.)',
    )


class Organization(BaseModel):
    """Political parties, government bodies, companies, NGOs, international orgs"""

    org_type: str | None = Field(
        default=None,
        description='Type: political_party, government, military, ngo, company, international',
    )


class Location(BaseModel):
    """Districts, provinces, cities, countries referenced in articles"""

    location_type: str | None = Field(
        default=None,
        description='Type: country, province, district, city, area',
    )


class Policy(BaseModel):
    """Laws, bills, agreements, economic policies, reforms"""

    domain: str | None = Field(
        default=None,
        description='Domain: economic, social, constitutional, foreign, environmental',
    )


class Event(BaseModel):
    """Protests, elections, disasters, diplomatic events, incidents"""

    event_type: str | None = Field(
        default=None,
        description='Type: election, protest, disaster, diplomatic, legislative, scandal',
    )
```

```python
# tests/news_analysis/__init__.py
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_entity_types.py -v`
Expected: All 12 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/__init__.py news_analysis/entity_types.py tests/news_analysis/__init__.py tests/news_analysis/test_entity_types.py
git commit -m "feat: add Phase 1 discovery entity types for news analysis"
```

---

### Task 2: Phase 2 Entity Types

**Files:**
- Modify: `news_analysis/entity_types.py`
- Modify: `tests/news_analysis/test_entity_types.py`

- [ ] **Step 1: Write tests for Phase 2 entity types**

Append to `tests/news_analysis/test_entity_types.py`:

```python
from news_analysis.entity_types import (
    EconomicIndicator,
    GovernmentBody,
    InternationalEntity,
    NewsOutlet,
    Politician,
    PoliticalParty,
)


class TestPhase2EntityTypes:
    def test_politician_defaults(self):
        p = Politician()
        assert p.party is None
        assert p.title is None

    def test_politician_with_values(self):
        p = Politician(party='UNP', title='Hon.')
        assert p.party == 'UNP'
        assert p.title == 'Hon.'

    def test_government_body_defaults(self):
        g = GovernmentBody()
        assert g.body_type is None
        assert g.jurisdiction is None

    def test_government_body_with_values(self):
        g = GovernmentBody(body_type='ministry', jurisdiction='national')
        assert g.body_type == 'ministry'
        assert g.jurisdiction == 'national'

    def test_political_party_defaults(self):
        p = PoliticalParty()
        assert p.coalition is None

    def test_political_party_with_values(self):
        p = PoliticalParty(coalition='SLPP-led alliance')
        assert p.coalition == 'SLPP-led alliance'

    def test_economic_indicator_defaults(self):
        e = EconomicIndicator()
        assert e.indicator_type is None
        assert e.unit is None

    def test_economic_indicator_with_values(self):
        e = EconomicIndicator(indicator_type='inflation', unit='percentage')
        assert e.indicator_type == 'inflation'
        assert e.unit == 'percentage'

    def test_international_entity_defaults(self):
        ie = InternationalEntity()
        assert ie.entity_type is None

    def test_international_entity_with_values(self):
        ie = InternationalEntity(entity_type='multilateral')
        assert ie.entity_type == 'multilateral'

    def test_news_outlet_defaults(self):
        n = NewsOutlet()
        assert n.outlet_type is None
        assert n.language is None

    def test_news_outlet_with_values(self):
        n = NewsOutlet(outlet_type='newspaper', language='english')
        assert n.outlet_type == 'newspaper'
        assert n.language == 'english'

    def test_all_phase2_are_pydantic_models(self):
        for model_cls in [
            Politician, GovernmentBody, PoliticalParty,
            EconomicIndicator, InternationalEntity, NewsOutlet,
        ]:
            assert issubclass(model_cls, BaseModel)

    def test_all_phase2_fields_optional(self):
        for model_cls in [
            Politician, GovernmentBody, PoliticalParty,
            EconomicIndicator, InternationalEntity, NewsOutlet,
        ]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None, (
                    f'{model_cls.__name__}.{field_name} is not optional'
                )
```

- [ ] **Step 2: Run tests to verify new tests fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_entity_types.py::TestPhase2EntityTypes -v`
Expected: FAIL — `ImportError: cannot import name 'Politician'`

- [ ] **Step 3: Add Phase 2 entity types to entity_types.py**

Append to `news_analysis/entity_types.py`:

```python
# === Phase 2: Refined Entity Types ===


class Politician(BaseModel):
    """Elected officials, ministers, party leaders, presidential candidates"""

    party: str | None = Field(
        default=None,
        description='Current political party name',
    )
    title: str | None = Field(
        default=None,
        description='Honorific: Hon., Dr., etc.',
    )


class GovernmentBody(BaseModel):
    """Ministries, departments, commissions, courts, parliament"""

    body_type: str | None = Field(
        default=None,
        description='ministry, department, commission, court, parliament, central_bank',
    )
    jurisdiction: str | None = Field(
        default=None,
        description='national, provincial, or district level',
    )


class PoliticalParty(BaseModel):
    """SLPP, SJB, UNP, JVP/NPP, SLFP, TNA, etc."""

    coalition: str | None = Field(
        default=None,
        description='Coalition or alliance name if part of one',
    )


class EconomicIndicator(BaseModel):
    """Inflation rate, GDP, debt-to-GDP ratio, forex reserves, etc."""

    indicator_type: str | None = Field(
        default=None,
        description='inflation, gdp, debt_ratio, reserves, unemployment, interest_rate, exchange_rate',
    )
    unit: str | None = Field(
        default=None,
        description='percentage, USD, LKR, billions, etc.',
    )


class InternationalEntity(BaseModel):
    """IMF, World Bank, UN, foreign governments involved in SL affairs"""

    entity_type: str | None = Field(
        default=None,
        description='multilateral, foreign_government, ngo, donor_agency',
    )


class NewsOutlet(BaseModel):
    """News publication or media organization"""

    outlet_type: str | None = Field(
        default=None,
        description='newspaper, tv, online, wire_service, state_media',
    )
    language: str | None = Field(
        default=None,
        description='Primary language: sinhala, tamil, english',
    )
```

- [ ] **Step 4: Run all entity type tests**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_entity_types.py -v`
Expected: All 26 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/entity_types.py tests/news_analysis/test_entity_types.py
git commit -m "feat: add Phase 2 refined entity types (Politician, GovernmentBody, etc.)"
```

---

### Task 3: Edge Types and Edge Type Map

**Files:**
- Create: `news_analysis/edge_types.py`
- Create: `tests/news_analysis/test_edge_types.py`

- [ ] **Step 1: Write tests for edge types and edge type map**

```python
# tests/news_analysis/test_edge_types.py
from pydantic import BaseModel

from news_analysis.edge_types import (
    EDGE_TYPE_MAP,
    PHASE_2_EDGE_TYPES,
    BelongsToParty,
    EnforcesPolicy,
    HoldsPosition,
    InvolvedInEvent,
    MakesStatement,
    OpposesPolicy,
    ReportsValue,
    SupportsPolicy,
)


class TestEdgeTypes:
    def test_holds_position_defaults(self):
        e = HoldsPosition()
        assert e.position_title is None

    def test_holds_position_with_values(self):
        e = HoldsPosition(position_title='Minister of Finance')
        assert e.position_title == 'Minister of Finance'

    def test_makes_statement_defaults(self):
        e = MakesStatement()
        assert e.context is None
        assert e.topic is None

    def test_makes_statement_with_values(self):
        e = MakesStatement(context='parliament', topic='economy')
        assert e.context == 'parliament'
        assert e.topic == 'economy'

    def test_supports_policy_defaults(self):
        e = SupportsPolicy()
        assert e.strength is None

    def test_opposes_policy_defaults(self):
        e = OpposesPolicy()
        assert e.strength is None

    def test_reports_value_defaults(self):
        e = ReportsValue()
        assert e.reported_value is None
        assert e.reporting_source is None

    def test_reports_value_with_values(self):
        e = ReportsValue(reported_value='4.2%', reporting_source='CBSL')
        assert e.reported_value == '4.2%'
        assert e.reporting_source == 'CBSL'

    def test_belongs_to_party_defaults(self):
        e = BelongsToParty()
        assert e.role_in_party is None

    def test_involved_in_event_defaults(self):
        e = InvolvedInEvent()
        assert e.role is None

    def test_enforces_policy_defaults(self):
        e = EnforcesPolicy()
        assert e.enforcement_status is None

    def test_all_are_pydantic_models(self):
        for model_cls in [
            HoldsPosition, MakesStatement, SupportsPolicy, OpposesPolicy,
            ReportsValue, BelongsToParty, InvolvedInEvent, EnforcesPolicy,
        ]:
            assert issubclass(model_cls, BaseModel)

    def test_all_fields_optional(self):
        for model_cls in [
            HoldsPosition, MakesStatement, SupportsPolicy, OpposesPolicy,
            ReportsValue, BelongsToParty, InvolvedInEvent, EnforcesPolicy,
        ]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None


class TestEdgeTypeMap:
    def test_edge_type_map_has_expected_keys(self):
        expected_keys = [
            ('Politician', 'GovernmentBody'),
            ('Politician', 'Policy'),
            ('Politician', 'PoliticalParty'),
            ('Politician', 'Event'),
            ('Politician', 'EconomicIndicator'),
            ('PoliticalParty', 'Policy'),
            ('PoliticalParty', 'Event'),
            ('GovernmentBody', 'EconomicIndicator'),
            ('GovernmentBody', 'Policy'),
            ('GovernmentBody', 'Event'),
            ('InternationalEntity', 'EconomicIndicator'),
            ('InternationalEntity', 'Policy'),
            ('NewsOutlet', 'EconomicIndicator'),
            ('NewsOutlet', 'Event'),
            ('NewsOutlet', 'Politician'),
        ]
        for key in expected_keys:
            assert key in EDGE_TYPE_MAP, f'Missing edge type map key: {key}'

    def test_politician_government_body_edges(self):
        assert EDGE_TYPE_MAP[('Politician', 'GovernmentBody')] == ['HoldsPosition']

    def test_politician_policy_edges(self):
        assert EDGE_TYPE_MAP[('Politician', 'Policy')] == ['SupportsPolicy', 'OpposesPolicy']

    def test_government_body_economic_indicator_edges(self):
        assert EDGE_TYPE_MAP[('GovernmentBody', 'EconomicIndicator')] == ['ReportsValue']

    def test_phase_2_edge_types_dict(self):
        """PHASE_2_EDGE_TYPES should map string names to model classes"""
        assert PHASE_2_EDGE_TYPES['HoldsPosition'] is HoldsPosition
        assert PHASE_2_EDGE_TYPES['MakesStatement'] is MakesStatement
        assert PHASE_2_EDGE_TYPES['ReportsValue'] is ReportsValue
        assert len(PHASE_2_EDGE_TYPES) == 8
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_edge_types.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'news_analysis.edge_types'`

- [ ] **Step 3: Implement edge types**

```python
# news_analysis/edge_types.py
from pydantic import BaseModel, Field


class HoldsPosition(BaseModel):
    """Politician holds a government position (Minister, MP, President, etc.)"""

    position_title: str | None = Field(
        default=None,
        description='The specific position: President, Minister of Finance, MP for Colombo, etc.',
    )


class MakesStatement(BaseModel):
    """A person or org makes a public claim, promise, or assertion"""

    context: str | None = Field(
        default=None,
        description='Context: interview, parliament, press_conference, rally, social_media',
    )
    topic: str | None = Field(
        default=None,
        description='What the statement is about: economy, policy, opposition, etc.',
    )


class SupportsPolicy(BaseModel):
    """Person or party publicly supports a policy or position"""

    strength: str | None = Field(
        default=None,
        description='strong, conditional, lukewarm',
    )


class OpposesPolicy(BaseModel):
    """Person or party publicly opposes a policy or position"""

    strength: str | None = Field(
        default=None,
        description='strong, conditional, lukewarm',
    )


class ReportsValue(BaseModel):
    """A source reports a specific value for an economic indicator"""

    reported_value: str | None = Field(
        default=None,
        description="The actual value reported: '12.5%', 'USD 3.2 billion', etc.",
    )
    reporting_source: str | None = Field(
        default=None,
        description='Who reported it: CBSL, IMF, Ministry of Finance, opposition claim',
    )


class BelongsToParty(BaseModel):
    """Politician is a member of a political party"""

    role_in_party: str | None = Field(
        default=None,
        description='leader, deputy_leader, member, spokesperson',
    )


class InvolvedInEvent(BaseModel):
    """Person, org, or party is involved in an event"""

    role: str | None = Field(
        default=None,
        description='organizer, participant, target, responder, critic',
    )


class EnforcesPolicy(BaseModel):
    """Government body implements or enforces a policy"""

    enforcement_status: str | None = Field(
        default=None,
        description='implementing, partially_implementing, blocking, reviewing',
    )


# Dict for passing to Graphiti's edge_types parameter
PHASE_2_EDGE_TYPES: dict[str, type[BaseModel]] = {
    'HoldsPosition': HoldsPosition,
    'MakesStatement': MakesStatement,
    'SupportsPolicy': SupportsPolicy,
    'OpposesPolicy': OpposesPolicy,
    'ReportsValue': ReportsValue,
    'BelongsToParty': BelongsToParty,
    'InvolvedInEvent': InvolvedInEvent,
    'EnforcesPolicy': EnforcesPolicy,
}

# Constrains which edge types can connect which entity types
EDGE_TYPE_MAP: dict[tuple[str, str], list[str]] = {
    ('Politician', 'GovernmentBody'): ['HoldsPosition'],
    ('Politician', 'Policy'): ['SupportsPolicy', 'OpposesPolicy'],
    ('Politician', 'PoliticalParty'): ['BelongsToParty'],
    ('Politician', 'Event'): ['InvolvedInEvent', 'MakesStatement'],
    ('Politician', 'EconomicIndicator'): ['MakesStatement', 'ReportsValue'],
    ('PoliticalParty', 'Policy'): ['SupportsPolicy', 'OpposesPolicy'],
    ('PoliticalParty', 'Event'): ['InvolvedInEvent'],
    ('GovernmentBody', 'EconomicIndicator'): ['ReportsValue'],
    ('GovernmentBody', 'Policy'): ['EnforcesPolicy'],
    ('GovernmentBody', 'Event'): ['InvolvedInEvent'],
    ('InternationalEntity', 'EconomicIndicator'): ['ReportsValue'],
    ('InternationalEntity', 'Policy'): ['SupportsPolicy', 'OpposesPolicy'],
    ('NewsOutlet', 'EconomicIndicator'): ['ReportsValue'],
    ('NewsOutlet', 'Event'): ['InvolvedInEvent'],
    ('NewsOutlet', 'Politician'): ['MakesStatement'],
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_edge_types.py -v`
Expected: All 17 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/edge_types.py tests/news_analysis/test_edge_types.py
git commit -m "feat: add edge types and edge type map for news analysis"
```

---

### Task 4: Ingestion Config (Phase 1 + Phase 2)

**Files:**
- Create: `news_analysis/ingest.py`
- Create: `tests/news_analysis/test_ingest.py`

- [ ] **Step 1: Write tests for ingestion config and functions**

```python
# tests/news_analysis/test_ingest.py
from datetime import datetime, timezone

import pytest

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_ingest.py -v`
Expected: FAIL — `ImportError: cannot import name 'PHASE_1_ENTITY_TYPES'`

- [ ] **Step 3: Implement ingestion module**

```python
# news_analysis/ingest.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from news_analysis.edge_types import EDGE_TYPE_MAP, PHASE_2_EDGE_TYPES
from news_analysis.entity_types import (
    EconomicIndicator,
    Event,
    GovernmentBody,
    InternationalEntity,
    Location,
    NewsOutlet,
    Organization,
    Person,
    Policy,
    Politician,
    PoliticalParty,
)

PHASE_1_GROUP_ID = 'sri-lanka-news-discovery'
PHASE_2_GROUP_ID = 'sri-lanka-news'

# Re-export for convenience
PHASE_2_EDGE_TYPES = PHASE_2_EDGE_TYPES

PHASE_1_ENTITY_TYPES: dict[str, type[BaseModel]] = {
    'Person': Person,
    'Organization': Organization,
    'Location': Location,
    'Policy': Policy,
    'Event': Event,
}

PHASE_2_ENTITY_TYPES: dict[str, type[BaseModel]] = {
    'Politician': Politician,
    'GovernmentBody': GovernmentBody,
    'PoliticalParty': PoliticalParty,
    'EconomicIndicator': EconomicIndicator,
    'Policy': Policy,
    'Event': Event,
    'Location': Location,
    'InternationalEntity': InternationalEntity,
    'NewsOutlet': NewsOutlet,
}

PHASE_1_INSTRUCTIONS = """\
You are analyzing Sri Lankan news articles. Extract all named entities
and relationships. Pay special attention to:
- Politicians and their stated positions/opinions
- Economic figures and who is reporting them
- Government decisions and policy changes
- References to past events or previous statements\
"""

PHASE_2_INSTRUCTIONS = """\
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
  its own editorial claim\
"""


def build_episode_name(outlet: str, article_id: str) -> str:
    """Build a Graphiti episode name from outlet and article ID."""
    sanitized_outlet = outlet.replace(' ', '-')
    return f'{sanitized_outlet}_{article_id}'


def build_source_description(
    title: str, outlet: str, category: str | None
) -> str:
    """Build a source description string for Graphiti episode ingestion."""
    base = f"News article: '{title}' from {outlet}"
    if category:
        return f'{base}, category: {category}'
    return base


def sort_articles_chronologically(
    articles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Sort articles by published_date ascending. Does not mutate the input."""
    return sorted(articles, key=lambda a: a['published_date'])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_ingest.py -v`
Expected: All 13 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/ingest.py tests/news_analysis/test_ingest.py
git commit -m "feat: add ingestion config for Phase 1 and Phase 2"
```

---

### Task 5: Gap Analysis Queries

**Files:**
- Create: `news_analysis/gap_analysis.py`
- Create: `tests/news_analysis/test_gap_analysis.py`

- [ ] **Step 1: Write tests for gap analysis**

The gap analysis runs Cypher queries against Neo4j. We test that the functions produce correct query strings and accept the right parameters. Integration testing with a real DB is out of scope here (marked `_int`).

```python
# tests/news_analysis/test_gap_analysis.py
import pytest

from news_analysis.gap_analysis import (
    ANALYSIS_QUERIES,
    GapAnalysisResult,
)


class TestGapAnalysisQueries:
    def test_analysis_queries_has_all_keys(self):
        expected_keys = [
            'edge_types',
            'entity_distribution',
            'key_entities',
            'contradictions',
            'temporal_coverage',
            'person_roles',
        ]
        for key in expected_keys:
            assert key in ANALYSIS_QUERIES, f'Missing analysis query: {key}'

    def test_each_query_has_cypher_and_description(self):
        for name, query_def in ANALYSIS_QUERIES.items():
            assert 'cypher' in query_def, f'{name} missing cypher'
            assert 'description' in query_def, f'{name} missing description'
            assert len(query_def['cypher']) > 0, f'{name} has empty cypher'
            assert len(query_def['description']) > 0, f'{name} has empty description'

    def test_edge_types_query_contains_relates_to(self):
        assert 'RELATES_TO' in ANALYSIS_QUERIES['edge_types']['cypher']

    def test_contradictions_query_filters_expired(self):
        assert 'expired_at IS NOT NULL' in ANALYSIS_QUERIES['contradictions']['cypher']

    def test_entity_distribution_query_filters_group(self):
        assert 'group_id' in ANALYSIS_QUERIES['entity_distribution']['cypher']

    def test_gap_analysis_result_structure(self):
        result = GapAnalysisResult(
            edge_types=[{'edge_type': 'SUPPORTS', 'freq': 10}],
            entity_distribution=[{'label': 'Person', 'count': 50}],
            key_entities=[],
            contradictions=[],
            temporal_coverage=[],
            person_roles=[],
        )
        assert result.edge_types[0]['freq'] == 10
        assert result.entity_distribution[0]['label'] == 'Person'
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_gap_analysis.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'news_analysis.gap_analysis'`

- [ ] **Step 3: Implement gap analysis module**

```python
# news_analysis/gap_analysis.py
from dataclasses import dataclass, field
from typing import Any

from graphiti_core.driver.driver import GraphDriver

from news_analysis.ingest import PHASE_1_GROUP_ID


@dataclass
class GapAnalysisResult:
    """Container for gap analysis query results."""

    edge_types: list[dict[str, Any]] = field(default_factory=list)
    entity_distribution: list[dict[str, Any]] = field(default_factory=list)
    key_entities: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    temporal_coverage: list[dict[str, Any]] = field(default_factory=list)
    person_roles: list[dict[str, Any]] = field(default_factory=list)


ANALYSIS_QUERIES: dict[str, dict[str, str]] = {
    'edge_types': {
        'description': 'Edge types extracted organically — what relationships dominate?',
        'cypher': """
            MATCH ()-[e:RELATES_TO]->()
            WHERE e.group_id = $group_id
            RETURN e.name AS edge_type, count(e) AS freq
            ORDER BY freq DESC LIMIT 30
        """,
    },
    'entity_distribution': {
        'description': 'Entity label distribution',
        'cypher': """
            MATCH (n:Entity {group_id: $group_id})
            UNWIND labels(n) AS label
            WITH label WHERE label <> 'Entity'
            RETURN label, count(*) AS count
            ORDER BY count DESC
        """,
    },
    'key_entities': {
        'description': 'Most connected entities (key players)',
        'cypher': """
            MATCH (n:Entity {group_id: $group_id})-[e:RELATES_TO]-()
            RETURN n.name AS name, labels(n) AS labels, count(e) AS connections
            ORDER BY connections DESC LIMIT 30
        """,
    },
    'contradictions': {
        'description': 'Contradictions already detected (edges with expired_at)',
        'cypher': """
            MATCH ()-[e:RELATES_TO]->()
            WHERE e.group_id = $group_id AND e.expired_at IS NOT NULL
            RETURN e.name AS edge_type, e.fact AS fact,
                   e.valid_at AS valid_at, e.expired_at AS expired_at
            ORDER BY e.expired_at DESC LIMIT 30
        """,
    },
    'temporal_coverage': {
        'description': 'Temporal coverage per edge type',
        'cypher': """
            MATCH ()-[e:RELATES_TO]->()
            WHERE e.group_id = $group_id
            RETURN e.name AS edge_type,
                   count(e) AS total,
                   count(e.valid_at) AS has_valid_at,
                   count(e.invalid_at) AS has_invalid_at,
                   count(e.expired_at) AS has_expired_at
            ORDER BY total DESC LIMIT 20
        """,
    },
    'person_roles': {
        'description': 'Person entities — which should be reclassified as Politician?',
        'cypher': """
            MATCH (p:Person {group_id: $group_id})
            RETURN p.name AS name, p.summary AS summary, p.attributes AS attributes
            ORDER BY p.name LIMIT 50
        """,
    },
}


async def run_gap_analysis(
    driver: GraphDriver,
    group_id: str = PHASE_1_GROUP_ID,
) -> GapAnalysisResult:
    """Run all gap analysis queries against the graph and return results."""
    result = GapAnalysisResult()

    for query_name, query_def in ANALYSIS_QUERIES.items():
        records = await driver.execute_query(
            query_def['cypher'],
            group_id=group_id,
        )
        setattr(result, query_name, records)

    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_gap_analysis.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/gap_analysis.py tests/news_analysis/test_gap_analysis.py
git commit -m "feat: add gap analysis queries for Phase 1 discovery"
```

---

### Task 6: Query Layer — Entity Timeline

**Files:**
- Create: `news_analysis/queries.py`
- Create: `tests/news_analysis/test_queries.py`

- [ ] **Step 1: Write tests for entity timeline query**

```python
# tests/news_analysis/test_queries.py
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from news_analysis.queries import get_entity_timeline


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestGetEntityTimeline -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'news_analysis.queries'`

- [ ] **Step 3: Implement entity timeline query**

```python
# news_analysis/queries.py
from datetime import datetime
from typing import Any

from graphiti_core.driver.driver import GraphDriver

from news_analysis.ingest import PHASE_2_GROUP_ID


async def get_entity_timeline(
    driver: GraphDriver,
    entity_name: str,
    group_id: str = PHASE_2_GROUP_ID,
    edge_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return all edges (current + invalidated) for an entity, sorted by valid_at."""
    edge_type_filter = ''
    params: dict[str, Any] = {
        'entity_name': entity_name,
        'group_id': group_id,
    }

    if edge_types:
        edge_type_filter = 'AND e.name IN $edge_types'
        params['edge_types'] = edge_types

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

    return await driver.execute_query(query, **params)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestGetEntityTimeline -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/queries.py tests/news_analysis/test_queries.py
git commit -m "feat: add entity timeline query"
```

---

### Task 7: Query Layer — Contradiction Finder

**Files:**
- Modify: `news_analysis/queries.py`
- Modify: `tests/news_analysis/test_queries.py`

- [ ] **Step 1: Write tests for contradiction finder**

Append to `tests/news_analysis/test_queries.py`:

```python
from news_analysis.queries import find_contradictions


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
```

- [ ] **Step 2: Run tests to verify new tests fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestFindContradictions -v`
Expected: FAIL — `ImportError: cannot import name 'find_contradictions'`

- [ ] **Step 3: Implement find_contradictions**

Append to `news_analysis/queries.py`:

```python
async def find_contradictions(
    driver: GraphDriver,
    group_id: str = PHASE_2_GROUP_ID,
    entity_name: str | None = None,
    since: datetime | None = None,
) -> list[dict[str, Any]]:
    """Find pairs of edges where a newer fact invalidated an older one."""
    entity_filter = 'AND n.name = $entity_name' if entity_name else ''
    time_filter = 'AND old_edge.expired_at >= $since' if since else ''

    params: dict[str, Any] = {'group_id': group_id}
    if entity_name:
        params['entity_name'] = entity_name
    if since:
        params['since'] = since

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

    return await driver.execute_query(query, **params)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestFindContradictions -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/queries.py tests/news_analysis/test_queries.py
git commit -m "feat: add contradiction finder query"
```

---

### Task 8: Query Layer — Recurring Pattern Detector

**Files:**
- Modify: `news_analysis/queries.py`
- Modify: `tests/news_analysis/test_queries.py`

- [ ] **Step 1: Write tests for recurring pattern detector**

Append to `tests/news_analysis/test_queries.py`:

```python
from news_analysis.queries import find_recurring_patterns


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
```

- [ ] **Step 2: Run tests to verify new tests fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestFindRecurringPatterns -v`
Expected: FAIL — `ImportError: cannot import name 'find_recurring_patterns'`

- [ ] **Step 3: Implement find_recurring_patterns**

Append to `news_analysis/queries.py`:

```python
async def find_recurring_patterns(
    driver: GraphDriver,
    group_id: str = PHASE_2_GROUP_ID,
    min_occurrences: int = 2,
    entity_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find relationships that recur across different years."""
    entity_filter = 'AND n.name = $entity_name' if entity_name else ''

    params: dict[str, Any] = {
        'group_id': group_id,
        'min_occurrences': min_occurrences,
    }
    if entity_name:
        params['entity_name'] = entity_name

    query = f"""
        MATCH (n:Entity {{group_id: $group_id}})-[e:RELATES_TO]->(m:Entity)
        WHERE e.valid_at IS NOT NULL {entity_filter}
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

    return await driver.execute_query(query, **params)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestFindRecurringPatterns -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/queries.py tests/news_analysis/test_queries.py
git commit -m "feat: add recurring pattern detector query"
```

---

### Task 9: Query Layer — Source Disagreement Finder

**Files:**
- Modify: `news_analysis/queries.py`
- Modify: `tests/news_analysis/test_queries.py`

- [ ] **Step 1: Write tests for source disagreement finder**

Append to `tests/news_analysis/test_queries.py`:

```python
from news_analysis.queries import find_source_disagreements


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
```

- [ ] **Step 2: Run tests to verify new tests fail**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py::TestFindSourceDisagreements -v`
Expected: FAIL — `ImportError: cannot import name 'find_source_disagreements'`

- [ ] **Step 3: Implement find_source_disagreements**

Append to `news_analysis/queries.py`:

```python
async def find_source_disagreements(
    driver: GraphDriver,
    group_id: str = PHASE_2_GROUP_ID,
    target_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find cases where different sources report different values for the same indicator."""
    target_filter = 'AND target.name = $target_name' if target_name else ''

    params: dict[str, Any] = {'group_id': group_id}
    if target_name:
        params['target_name'] = target_name

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

    return await driver.execute_query(query, **params)
```

- [ ] **Step 4: Run all query tests**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/test_queries.py -v`
Expected: All 29 tests PASS

- [ ] **Step 5: Commit**

```bash
git add news_analysis/queries.py tests/news_analysis/test_queries.py
git commit -m "feat: add source disagreement finder query"
```

---

### Task 10: Final Integration — Push to Remote

**Files:** None (git operations only)

- [ ] **Step 1: Run all news_analysis tests**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/news_analysis/ -v`
Expected: All tests PASS

- [ ] **Step 2: Run existing project tests to verify no regressions**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && python -m pytest tests/ -k "not _int" --ignore=tests/news_analysis/ -x -q`
Expected: All existing tests PASS (no regressions)

- [ ] **Step 3: Run linter**

Run: `cd /Users/chaturaattidiya/Documents/Github/project-ref/graphiti && ruff check news_analysis/ tests/news_analysis/`
Expected: No lint errors

- [ ] **Step 4: Push branch to fork**

```bash
git push -u origin feature/news-timeline-analysis
```
