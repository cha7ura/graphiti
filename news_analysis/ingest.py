from datetime import datetime
from typing import Any

from pydantic import BaseModel

from news_analysis.edge_types import PHASE_2_EDGE_TYPES as _PHASE_2_EDGE_TYPES
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
PHASE_2_EDGE_TYPES = _PHASE_2_EDGE_TYPES

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
