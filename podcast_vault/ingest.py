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
