"""Tests for podcast_vault.extract module."""
from datetime import datetime

from podcast_vault.extract import (
    INSIGHT_EXTRACTION_PROMPT,
    VALID_INSIGHT_TYPES,
    EpisodeTranscript,
    ExtractedInsight,
    TranscriptSegment,
    chunk_transcript,
    format_chunk_for_prompt,
)

# ---------------------------------------------------------------------------
# TranscriptSegment
# ---------------------------------------------------------------------------


def test_transcript_segment_creation():
    seg = TranscriptSegment(text='Hello world', start_time=0.0, end_time=5.5)
    assert seg.text == 'Hello world'
    assert seg.start_time == 0.0
    assert seg.end_time == 5.5


# ---------------------------------------------------------------------------
# EpisodeTranscript
# ---------------------------------------------------------------------------


def test_episode_transcript_required_fields():
    seg = TranscriptSegment(text='Intro', start_time=0.0, end_time=3.0)
    ep = EpisodeTranscript(
        podcast_name='HealthCast',
        episode_title='Sleep Science',
        youtube_id='abc123',
        published_date=datetime(2025, 1, 15),
        guests=['Dr. Smith'],
        host='Jane Doe',
        segments=[seg],
    )
    assert ep.podcast_name == 'HealthCast'
    assert ep.episode_title == 'Sleep Science'
    assert ep.youtube_id == 'abc123'
    assert ep.published_date == datetime(2025, 1, 15)
    assert ep.guests == ['Dr. Smith']
    assert ep.host == 'Jane Doe'
    assert ep.segments == [seg]
    # Optional fields default to None
    assert ep.episode_number is None
    assert ep.description is None


def test_episode_transcript_optional_fields():
    ep = EpisodeTranscript(
        podcast_name='HealthCast',
        episode_title='Sleep Science',
        youtube_id='abc123',
        published_date=datetime(2025, 1, 15),
        guests=['Dr. Smith'],
        host='Jane Doe',
        segments=[],
        episode_number='42',
        description='Show notes here',
    )
    assert ep.episode_number == '42'
    assert ep.description == 'Show notes here'


# ---------------------------------------------------------------------------
# ExtractedInsight
# ---------------------------------------------------------------------------


def test_extracted_insight_defaults():
    insight = ExtractedInsight(
        insight_type='claim',
        text='Sleep deprivation impairs cognition.',
        guest='Dr. Smith',
        topics=['sleep', 'cognition'],
        start_time=120.0,
        end_time=145.0,
    )
    assert insight.referenced_studies == []
    assert insight.referenced_books == []
    assert insight.referenced_products == []
    assert insight.protocol_name is None


def test_extracted_insight_all_fields():
    insight = ExtractedInsight(
        insight_type='protocol',
        text='Morning sunlight exposure protocol.',
        guest='Dr. Jones',
        topics=['sleep', 'circadian'],
        start_time=600.0,
        end_time=720.0,
        referenced_studies=['Walker 2017', 'a Harvard study on sleep'],
        referenced_books=['Why We Sleep - Matthew Walker'],
        referenced_products=['blue-light glasses'],
        protocol_name='Morning Light Protocol',
    )
    assert insight.insight_type == 'protocol'
    assert insight.guest == 'Dr. Jones'
    assert insight.topics == ['sleep', 'circadian']
    assert insight.start_time == 600.0
    assert insight.end_time == 720.0
    assert insight.referenced_studies == ['Walker 2017', 'a Harvard study on sleep']
    assert insight.referenced_books == ['Why We Sleep - Matthew Walker']
    assert insight.referenced_products == ['blue-light glasses']
    assert insight.protocol_name == 'Morning Light Protocol'


def test_extracted_insight_mutable_defaults_are_independent():
    """Each instance should get its own list, not share a default."""
    a = ExtractedInsight(
        insight_type='opinion',
        text='Opinion A',
        guest='Host',
        topics=['misc'],
        start_time=0.0,
        end_time=10.0,
    )
    b = ExtractedInsight(
        insight_type='opinion',
        text='Opinion B',
        guest='Host',
        topics=['misc'],
        start_time=10.0,
        end_time=20.0,
    )
    a.referenced_studies.append('study1')
    assert b.referenced_studies == [], 'Mutable default was shared between instances'


# ---------------------------------------------------------------------------
# VALID_INSIGHT_TYPES
# ---------------------------------------------------------------------------


def test_valid_insight_types_count():
    assert len(VALID_INSIGHT_TYPES) == 6


def test_valid_insight_types_contains_expected():
    expected = {'claim', 'framework', 'protocol', 'story', 'opinion', 'recommendation'}
    assert set(VALID_INSIGHT_TYPES) == expected


# ---------------------------------------------------------------------------
# INSIGHT_EXTRACTION_PROMPT
# ---------------------------------------------------------------------------


def test_prompt_not_empty():
    assert INSIGHT_EXTRACTION_PROMPT.strip() != ''


def test_prompt_contains_speakers_placeholder():
    assert '{speakers}' in INSIGHT_EXTRACTION_PROMPT


def test_prompt_contains_chunk_text_placeholder():
    assert '{chunk_text}' in INSIGHT_EXTRACTION_PROMPT


def test_prompt_contains_key_terms():
    for term in ('SPEAKERS', 'TRANSCRIPT CHUNK', 'claim', 'framework', 'protocol'):
        assert term in INSIGHT_EXTRACTION_PROMPT, f'Expected "{term}" in prompt'


# ---------------------------------------------------------------------------
# chunk_transcript
# ---------------------------------------------------------------------------


def test_chunk_transcript_empty_returns_empty():
    result = chunk_transcript([])
    assert result == []


def test_chunk_transcript_short_segments_returns_one_chunk():
    """Segments that fit within one chunk_duration should return a single chunk."""
    segments = [
        TranscriptSegment(text='A', start_time=0.0, end_time=60.0),
        TranscriptSegment(text='B', start_time=60.0, end_time=120.0),
        TranscriptSegment(text='C', start_time=120.0, end_time=180.0),
    ]
    chunks = chunk_transcript(segments, chunk_duration=300.0, overlap_duration=30.0)
    assert len(chunks) == 1
    assert chunks[0] == segments


def test_chunk_transcript_10_minutes_returns_multiple_chunks():
    """Segments spanning 10 min with 5-min chunks + 30s overlap gives 3 chunks."""
    # Create segments: one per minute, from 0 to 600s
    segments = [
        TranscriptSegment(text=f'seg{i}', start_time=float(i * 60), end_time=float((i + 1) * 60))
        for i in range(10)
    ]
    chunks = chunk_transcript(segments, chunk_duration=300.0, overlap_duration=30.0)
    # With 5-min chunks and 30s overlap, step is 270s
    # chunk 0: [0, 300), chunk 1: [270, 570), chunk 2: [540, 840)
    assert len(chunks) >= 2, f'Expected at least 2 chunks, got {len(chunks)}'
    # Verify overlap: the last segment of chunk[0] should also appear in chunk[1]
    last_of_first = chunks[0][-1]
    assert last_of_first in chunks[1], 'Expected overlap between chunk 0 and chunk 1'


def test_chunk_transcript_does_not_mutate_input():
    segments = [
        TranscriptSegment(text='A', start_time=0.0, end_time=100.0),
        TranscriptSegment(text='B', start_time=100.0, end_time=200.0),
        TranscriptSegment(text='C', start_time=200.0, end_time=300.0),
        TranscriptSegment(text='D', start_time=300.0, end_time=400.0),
        TranscriptSegment(text='E', start_time=400.0, end_time=500.0),
    ]
    original_ids = [id(s) for s in segments]
    original_len = len(segments)
    chunk_transcript(segments, chunk_duration=200.0, overlap_duration=50.0)
    assert len(segments) == original_len
    assert [id(s) for s in segments] == original_ids


def test_chunk_transcript_all_segments_covered():
    """Every segment should appear in at least one chunk."""
    segments = [
        TranscriptSegment(text=f'seg{i}', start_time=float(i * 60), end_time=float((i + 1) * 60))
        for i in range(10)
    ]
    chunks = chunk_transcript(segments, chunk_duration=300.0, overlap_duration=30.0)
    covered = {id(seg) for chunk in chunks for seg in chunk}
    for seg in segments:
        assert id(seg) in covered, f'Segment {seg.text} not covered by any chunk'


# ---------------------------------------------------------------------------
# format_chunk_for_prompt
# ---------------------------------------------------------------------------


def test_format_chunk_for_prompt_contains_speaker_names():
    segs = [TranscriptSegment(text='Hello', start_time=0.0, end_time=5.0)]
    result = format_chunk_for_prompt(segs, speakers=['Dr. Smith', 'Jane Doe'])
    assert 'Dr. Smith' in result
    assert 'Jane Doe' in result


def test_format_chunk_for_prompt_contains_timestamps():
    segs = [TranscriptSegment(text='Sleep matters', start_time=120.0, end_time=135.0)]
    result = format_chunk_for_prompt(segs, speakers=['Host'])
    assert '120s' in result
    assert '135s' in result


def test_format_chunk_for_prompt_contains_segment_text():
    segs = [TranscriptSegment(text='Unique marker text XYZ', start_time=0.0, end_time=10.0)]
    result = format_chunk_for_prompt(segs, speakers=['Host'])
    assert 'Unique marker text XYZ' in result
