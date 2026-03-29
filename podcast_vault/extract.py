from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TranscriptSegment:
    """A single segment from Whisper transcription."""

    text: str
    start_time: float  # seconds
    end_time: float  # seconds


@dataclass
class EpisodeTranscript:
    """Full transcript and metadata for a podcast episode."""

    podcast_name: str
    episode_title: str
    youtube_id: str
    published_date: datetime
    guests: list[str]
    host: str
    segments: list[TranscriptSegment]
    episode_number: str | None = None
    description: str | None = None  # YouTube description / show notes


@dataclass
class ExtractedInsight:
    """A single structured insight extracted from a transcript chunk."""

    insight_type: str  # claim, framework, protocol, story, opinion, recommendation
    text: str  # The insight in clean prose
    guest: str  # Who said it
    topics: list[str]  # Topics covered
    start_time: float  # Timestamp in seconds
    end_time: float  # Timestamp in seconds
    referenced_studies: list[str] = field(default_factory=list)
    referenced_books: list[str] = field(default_factory=list)
    referenced_products: list[str] = field(default_factory=list)
    protocol_name: str | None = None


VALID_INSIGHT_TYPES = [
    'claim',
    'framework',
    'protocol',
    'story',
    'opinion',
    'recommendation',
]


INSIGHT_EXTRACTION_PROMPT = """\
You are extracting structured insights from a podcast transcript chunk.

SPEAKERS:
{speakers}

TRANSCRIPT CHUNK (timestamps in seconds):
{chunk_text}

Extract every distinct insight. An insight is one of:
- **claim**: A factual assertion ("X causes Y", "doing X increases Y by Z%")
- **framework**: A mental model or structured thinking pattern ("The 80/20 rule for...")
- **protocol**: A specific actionable routine with steps ("Every morning I do X then Y then Z")
- **story**: A personal anecdote or experience ("When I was at Stanford...")
- **opinion**: A subjective viewpoint ("I think X is the biggest...")
- **recommendation**: Explicitly recommending a book, product, tool, or practice

For each insight extract:
1. insight_type: one of the types above
2. text: the insight as a clean, self-contained statement (not a quote — rewrite for clarity)
3. guest: who said it (use the speaker name from SPEAKERS)
4. topics: 1-3 topic labels (use consistent naming: "sleep", "dopamine", not "sleeping" or "dopaminergic pathways")
5. start_time: timestamp in seconds where the insight begins
6. end_time: timestamp in seconds where it ends
7. referenced_studies: any papers/studies mentioned (author + year if available)
8. referenced_books: any books mentioned (title + author)
9. referenced_products: any supplements, tools, devices, apps mentioned
10. protocol_name: if this is a protocol, give it a clear name

RULES:
- Only extract what was explicitly said — do not infer or add information
- Merge multi-sentence insights into one clean statement
- Use the exact timestamp range where the insight was discussed
- If a study is mentioned without full details, include what was said ("a Harvard study on sleep")
- One insight per distinct claim/idea — don't bundle multiple claims\
"""


def chunk_transcript(
    segments: list[TranscriptSegment],
    chunk_duration: float = 300.0,  # 5 minutes in seconds
    overlap_duration: float = 30.0,  # 30 second overlap
) -> list[list[TranscriptSegment]]:
    """Split transcript segments into overlapping time-based chunks.

    Each chunk covers approximately chunk_duration seconds with
    overlap_duration seconds of overlap between consecutive chunks.
    Does not mutate the input.
    """
    if not segments:
        return []

    chunks: list[list[TranscriptSegment]] = []
    chunk_start = segments[0].start_time

    while True:
        chunk_end = chunk_start + chunk_duration

        # Collect segments that fall within this chunk window
        chunk_segments = [
            seg for seg in segments if seg.start_time < chunk_end and seg.end_time > chunk_start
        ]

        if not chunk_segments:
            break

        chunks.append(chunk_segments)

        # Advance by (chunk_duration - overlap_duration)
        chunk_start += chunk_duration - overlap_duration

        # Stop if we've passed all segments
        if chunk_start >= segments[-1].end_time:
            break

    return chunks


def format_chunk_for_prompt(
    chunk: list[TranscriptSegment],
    speakers: list[str],
) -> str:
    """Format a chunk of transcript segments for the extraction prompt."""
    speakers_str = ', '.join(speakers)
    chunk_lines = [
        f'[{seg.start_time:.0f}s - {seg.end_time:.0f}s] {seg.text}' for seg in chunk
    ]
    chunk_text = '\n'.join(chunk_lines)
    return INSIGHT_EXTRACTION_PROMPT.format(
        speakers=speakers_str,
        chunk_text=chunk_text,
    )
