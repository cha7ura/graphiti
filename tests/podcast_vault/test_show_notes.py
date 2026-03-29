"""Tests for podcast_vault.show_notes module."""

from podcast_vault.show_notes import (
    ShowNoteLink,
    classify_url,
    extract_context,
    extract_show_note_links,
    get_product_links,
    get_study_links,
)

# ---------------------------------------------------------------------------
# classify_url
# ---------------------------------------------------------------------------


def test_classify_url_pubmed_is_study():
    url = 'https://pubmed.ncbi.nlm.nih.gov/12345678/'
    assert classify_url(url) == 'study'


def test_classify_url_doi_is_study():
    url = 'https://doi.org/10.1038/s41586-021-03819-2'
    assert classify_url(url) == 'study'


def test_classify_url_nature_is_study():
    url = 'https://www.nature.com/articles/s41586-021-03819-2'
    assert classify_url(url) == 'study'


def test_classify_url_amazon_is_product():
    url = 'https://www.amazon.com/dp/B08XYZ1234'
    assert classify_url(url) == 'product'


def test_classify_url_iherb_is_product():
    url = 'https://www.iherb.com/pr/magnesium-glycinate/12345'
    assert classify_url(url) == 'product'


def test_classify_url_wikipedia_is_guest_bio():
    url = 'https://en.wikipedia.org/wiki/Andrew_Huberman'
    assert classify_url(url) == 'guest_bio'


def test_classify_url_twitter_is_guest_bio():
    url = 'https://twitter.com/hubermanlab'
    assert classify_url(url) == 'guest_bio'


def test_classify_url_x_com_is_guest_bio():
    url = 'https://x.com/hubermanlab'
    assert classify_url(url) == 'guest_bio'


def test_classify_url_unknown_is_other():
    url = 'https://www.somerandomblog.com/post/123'
    assert classify_url(url) == 'other'


def test_classify_url_case_insensitive():
    url = 'HTTPS://PUBMED.NCBI.NLM.NIH.GOV/12345678/'
    assert classify_url(url) == 'study'


# ---------------------------------------------------------------------------
# extract_context
# ---------------------------------------------------------------------------


def test_extract_context_returns_surrounding_text():
    text = 'For more information see https://pubmed.ncbi.nlm.nih.gov/123/ for details.'
    url = 'https://pubmed.ncbi.nlm.nih.gov/123/'
    context = extract_context(text, url, context_chars=20)
    assert url in context
    assert 'see' in context or 'details' in context


def test_extract_context_url_not_found_returns_empty():
    text = 'Some text without the url'
    context = extract_context(text, 'https://nothere.com', context_chars=50)
    assert context == ''


def test_extract_context_at_start_of_text():
    url = 'https://example.com'
    text = f'{url} is a great resource'
    context = extract_context(text, url, context_chars=50)
    assert url in context


def test_extract_context_at_end_of_text():
    url = 'https://example.com'
    text = f'A great resource: {url}'
    context = extract_context(text, url, context_chars=50)
    assert url in context


# ---------------------------------------------------------------------------
# extract_show_note_links
# ---------------------------------------------------------------------------


def test_extract_show_note_links_empty_string():
    result = extract_show_note_links('')
    assert result == []


def test_extract_show_note_links_no_urls():
    result = extract_show_note_links('No links here, just plain text.')
    assert result == []


def test_extract_show_note_links_extracts_and_classifies():
    description = (
        'Check the study: https://pubmed.ncbi.nlm.nih.gov/99999999/ '
        'Buy the supplement: https://www.amazon.com/dp/B001234 '
        'Follow the guest: https://twitter.com/drsmith'
    )
    links = extract_show_note_links(description)
    assert len(links) == 3
    types = {link.link_type for link in links}
    assert 'study' in types
    assert 'product' in types
    assert 'guest_bio' in types


def test_extract_show_note_links_handles_multiple_urls():
    description = (
        'Study 1: https://doi.org/10.1000/xyz123\n'
        'Study 2: https://pubmed.ncbi.nlm.nih.gov/11111111/\n'
        'Product: https://www.iherb.com/pr/omega3/9999\n'
    )
    links = extract_show_note_links(description)
    assert len(links) == 3


def test_extract_show_note_links_context_is_populated():
    url = 'https://pubmed.ncbi.nlm.nih.gov/55555/'
    description = f'See this research paper: {url} for sleep insights'
    links = extract_show_note_links(description)
    assert len(links) == 1
    assert links[0].context != ''
    assert url in links[0].url


def test_extract_show_note_links_strips_trailing_punctuation():
    description = 'See https://pubmed.ncbi.nlm.nih.gov/99999/, for more.'
    links = extract_show_note_links(description)
    assert len(links) == 1
    # Trailing comma should be stripped
    assert not links[0].url.endswith(',')


def test_extract_show_note_links_returns_show_note_link_objects():
    description = 'Check https://www.amazon.com/dp/B001'
    links = extract_show_note_links(description)
    assert len(links) == 1
    assert isinstance(links[0], ShowNoteLink)
    assert links[0].url == 'https://www.amazon.com/dp/B001'
    assert links[0].link_type == 'product'


# ---------------------------------------------------------------------------
# get_study_links / get_product_links
# ---------------------------------------------------------------------------


def test_get_study_links_filters_correctly():
    all_links = [
        ShowNoteLink(url='https://pubmed.ncbi.nlm.nih.gov/1/', link_type='study', context=''),
        ShowNoteLink(url='https://www.amazon.com/dp/B001', link_type='product', context=''),
        ShowNoteLink(url='https://doi.org/10.1/xyz', link_type='study', context=''),
    ]
    studies = get_study_links(all_links)
    assert len(studies) == 2
    assert all(link.link_type == 'study' for link in studies)


def test_get_product_links_filters_correctly():
    all_links = [
        ShowNoteLink(url='https://pubmed.ncbi.nlm.nih.gov/1/', link_type='study', context=''),
        ShowNoteLink(url='https://www.amazon.com/dp/B001', link_type='product', context=''),
        ShowNoteLink(url='https://www.iherb.com/pr/omega/1', link_type='product', context=''),
    ]
    products = get_product_links(all_links)
    assert len(products) == 2
    assert all(link.link_type == 'product' for link in products)


def test_get_study_links_empty_input():
    assert get_study_links([]) == []


def test_get_product_links_empty_input():
    assert get_product_links([]) == []


def test_get_study_links_no_studies():
    all_links = [
        ShowNoteLink(url='https://twitter.com/someone', link_type='guest_bio', context=''),
    ]
    assert get_study_links(all_links) == []
