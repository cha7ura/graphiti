import re
from dataclasses import dataclass


@dataclass
class ShowNoteLink:
    """A URL extracted from podcast show notes / YouTube description."""

    url: str
    link_type: str  # study, product, guest_bio, other
    context: str  # Surrounding text from show notes


# URL patterns for classifying links
LINK_TYPE_PATTERNS: dict[str, list[str]] = {
    'study': [
        r'pubmed\.ncbi\.nlm\.nih\.gov',
        r'doi\.org',
        r'nature\.com',
        r'sciencedirect\.com',
        r'ncbi\.nlm\.nih\.gov',
        r'scholar\.google\.com',
        r'cell\.com',
        r'thelancet\.com',
        r'bmj\.com',
        r'jamanetwork\.com',
        r'arxiv\.org',
    ],
    'product': [
        r'amazon\.com',
        r'iherb\.com',
        r'thorne\.com',
        r'momentous\.com',
        r'athleticgreens\.com',
        r'drinkag1\.com',
    ],
    'guest_bio': [
        r'wikipedia\.org',
        r'twitter\.com',
        r'x\.com',
        r'linkedin\.com',
        r'instagram\.com',
    ],
}

# Regex for extracting URLs from text
URL_REGEX = re.compile(
    r'https?://[^\s<>\"\'\)\]]+',
    re.IGNORECASE,
)


def classify_url(url: str) -> str:
    """Classify a URL into a link type based on domain patterns."""
    for link_type, patterns in LINK_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return link_type
    return 'other'


def extract_context(text: str, url: str, context_chars: int = 100) -> str:
    """Extract surrounding text around a URL for context."""
    idx = text.find(url)
    if idx == -1:
        return ''
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(url) + context_chars)
    return text[start:end].strip()


def extract_show_note_links(description: str) -> list[ShowNoteLink]:
    """Parse URLs from YouTube description and classify them."""
    if not description:
        return []

    urls = URL_REGEX.findall(description)
    links: list[ShowNoteLink] = []

    for url in urls:
        # Clean trailing punctuation that might have been captured
        url = url.rstrip('.,;:!?)')
        link_type = classify_url(url)
        context = extract_context(description, url)
        links.append(ShowNoteLink(url=url, link_type=link_type, context=context))

    return links


def get_study_links(links: list[ShowNoteLink]) -> list[ShowNoteLink]:
    """Filter to only study/research links."""
    return [link for link in links if link.link_type == 'study']


def get_product_links(links: list[ShowNoteLink]) -> list[ShowNoteLink]:
    """Filter to only product links."""
    return [link for link in links if link.link_type == 'product']
