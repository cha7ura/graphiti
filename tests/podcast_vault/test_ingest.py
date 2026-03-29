"""Tests for podcast_vault.ingest module."""

from podcast_vault.ingest import (
    GRAPHITI_EXTRACTION_INSTRUCTIONS,
    GROUP_ID_PREFIX,
    build_episode_name,
    build_group_id,
    build_source_description,
    build_youtube_url,
    format_timestamp,
)

# ── Constants ─────────────────────────────────────────────────────────────────


def test_group_id_prefix_is_podcast():
    assert GROUP_ID_PREFIX == 'podcast'


def test_graphiti_extraction_instructions_is_non_empty_string():
    assert isinstance(GRAPHITI_EXTRACTION_INSTRUCTIONS, str)
    assert len(GRAPHITI_EXTRACTION_INSTRUCTIONS) > 0


def test_graphiti_extraction_instructions_contains_entity_section():
    assert 'ENTITY EXTRACTION' in GRAPHITI_EXTRACTION_INSTRUCTIONS


def test_graphiti_extraction_instructions_contains_relationship_section():
    assert 'RELATIONSHIP RULES' in GRAPHITI_EXTRACTION_INSTRUCTIONS


def test_graphiti_extraction_instructions_contains_temporal_section():
    assert 'TEMPORAL RULES' in GRAPHITI_EXTRACTION_INSTRUCTIONS


# ── build_episode_name ────────────────────────────────────────────────────────


def test_build_episode_name_basic():
    result = build_episode_name('Huberman Lab', 'dQw4w9WgXcQ', 863)
    assert result == 'Huberman-Lab_dQw4w9WgXcQ_863'


def test_build_episode_name_spaces_replaced_with_dashes():
    result = build_episode_name('The Joe Rogan Experience', 'abc123', 0)
    assert ' ' not in result
    assert 'The-Joe-Rogan-Experience' in result


def test_build_episode_name_includes_youtube_id():
    youtube_id = 'aBcDeFgHiJk'
    result = build_episode_name('Some Podcast', youtube_id, 100)
    assert youtube_id in result


def test_build_episode_name_includes_start_time():
    result = build_episode_name('Some Podcast', 'xyz', 3661)
    assert '3661' in result


def test_build_episode_name_zero_start_time():
    result = build_episode_name('My Show', 'vid1', 0)
    assert result == 'My-Show_vid1_0'


# ── build_source_description ─────────────────────────────────────────────────


def test_build_source_description_contains_all_parts():
    result = build_source_description(
        episode_title='Sleep & Memory',
        podcast_name='Huberman Lab',
        guest='Matthew Walker',
        start_time='14:23',
        end_time='16:05',
        youtube_url='https://youtube.com/watch?v=abc&t=863',
    )
    assert 'Sleep & Memory' in result
    assert 'Huberman Lab' in result
    assert 'Matthew Walker' in result
    assert '14:23' in result
    assert '16:05' in result
    assert 'https://youtube.com/watch?v=abc&t=863' in result


def test_build_source_description_returns_string():
    result = build_source_description(
        episode_title='Ep1',
        podcast_name='Show',
        guest='Guest',
        start_time='0:00',
        end_time='1:00',
        youtube_url='https://youtube.com/watch?v=x',
    )
    assert isinstance(result, str)


# ── build_youtube_url ─────────────────────────────────────────────────────────


def test_build_youtube_url_basic():
    result = build_youtube_url('dQw4w9WgXcQ', 863)
    assert result == 'https://youtube.com/watch?v=dQw4w9WgXcQ&t=863'


def test_build_youtube_url_zero_seconds():
    result = build_youtube_url('abc123', 0)
    assert result == 'https://youtube.com/watch?v=abc123&t=0'


def test_build_youtube_url_contains_video_id():
    video_id = 'testVideoId'
    result = build_youtube_url(video_id, 100)
    assert video_id in result


def test_build_youtube_url_contains_timestamp():
    result = build_youtube_url('vid', 3600)
    assert 't=3600' in result


def test_build_youtube_url_format():
    result = build_youtube_url('XYZ', 42)
    assert result.startswith('https://youtube.com/watch?v=')
    assert '&t=' in result


# ── format_timestamp ──────────────────────────────────────────────────────────


def test_format_timestamp_minutes_and_seconds():
    assert format_timestamp(90) == '1:30'


def test_format_timestamp_zero():
    assert format_timestamp(0) == '0:00'


def test_format_timestamp_exactly_one_minute():
    assert format_timestamp(60) == '1:00'


def test_format_timestamp_hours_minutes_seconds():
    assert format_timestamp(3661) == '1:01:01'


def test_format_timestamp_exactly_one_hour():
    assert format_timestamp(3600) == '1:00:00'


def test_format_timestamp_seconds_only():
    assert format_timestamp(45) == '0:45'


def test_format_timestamp_large_value():
    # 2 hours 30 minutes 15 seconds = 9015 seconds
    assert format_timestamp(9015) == '2:30:15'


def test_format_timestamp_float_input():
    # Should truncate fractional seconds
    assert format_timestamp(90.9) == '1:30'


def test_format_timestamp_two_digit_minutes_and_seconds():
    # 10 minutes 10 seconds = 610 seconds
    assert format_timestamp(610) == '10:10'


# ── build_group_id ────────────────────────────────────────────────────────────


def test_build_group_id_basic():
    result = build_group_id('Huberman Lab')
    assert result == 'podcast-huberman-lab'


def test_build_group_id_prefix():
    result = build_group_id('Any Show')
    assert result.startswith('podcast-')


def test_build_group_id_lowercase():
    result = build_group_id('UPPER CASE SHOW')
    assert result == result.lower()


def test_build_group_id_spaces_replaced():
    result = build_group_id('My Podcast Show')
    assert ' ' not in result
    assert result == 'podcast-my-podcast-show'


def test_build_group_id_apostrophe_removed():
    result = build_group_id("Lex Fridman's Podcast")
    assert "'" not in result
    assert result == "podcast-lex-fridmans-podcast"


def test_build_group_id_returns_string():
    result = build_group_id('Test Show')
    assert isinstance(result, str)
