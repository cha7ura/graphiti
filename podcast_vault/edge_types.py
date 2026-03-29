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
