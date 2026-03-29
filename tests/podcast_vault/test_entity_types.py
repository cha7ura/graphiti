"""Tests for podcast_vault.entity_types module."""

from pydantic import BaseModel

from podcast_vault.entity_types import (
    ENTITY_TYPES,
    Book,
    Guest,
    Podcast,
    Product,
    Protocol,
    Study,
    Topic,
)

# ── Defaults ──────────────────────────────────────────────────────────────────


def test_guest_defaults():
    g = Guest()
    assert g.expertise is None
    assert g.credentials is None


def test_podcast_defaults():
    p = Podcast()
    assert p.host is None


def test_topic_defaults():
    t = Topic()
    assert t.domain is None


def test_study_defaults():
    s = Study()
    assert s.authors is None
    assert s.year is None
    assert s.journal is None
    assert s.doi is None


def test_book_defaults():
    b = Book()
    assert b.author is None


def test_product_defaults():
    p = Product()
    assert p.product_type is None


def test_protocol_defaults():
    p = Protocol()
    assert p.category is None
    assert p.difficulty is None


# ── With values ───────────────────────────────────────────────────────────────


def test_guest_with_values():
    g = Guest(expertise='neuroscience', credentials='PhD, Stanford')
    assert g.expertise == 'neuroscience'
    assert g.credentials == 'PhD, Stanford'


def test_podcast_with_values():
    p = Podcast(host='Andrew Huberman')
    assert p.host == 'Andrew Huberman'


def test_topic_with_values():
    t = Topic(domain='health')
    assert t.domain == 'health'


def test_study_with_values():
    s = Study(authors='Walker & Stickgold', year='2019', journal='Nature', doi='10.1000/xyz')
    assert s.authors == 'Walker & Stickgold'
    assert s.year == '2019'
    assert s.journal == 'Nature'
    assert s.doi == '10.1000/xyz'


def test_book_with_values():
    b = Book(author='Matthew Walker')
    assert b.author == 'Matthew Walker'


def test_product_with_values():
    p = Product(product_type='supplement')
    assert p.product_type == 'supplement'


def test_protocol_with_values():
    p = Protocol(category='sleep', difficulty='beginner')
    assert p.category == 'sleep'
    assert p.difficulty == 'beginner'


# ── BaseModel subclass checks ─────────────────────────────────────────────────


def test_all_entity_types_are_basemodel_subclasses():
    entity_classes = [Guest, Podcast, Topic, Study, Book, Product, Protocol]
    for cls in entity_classes:
        assert issubclass(cls, BaseModel), f'{cls.__name__} must be a BaseModel subclass'


# ── All fields optional ───────────────────────────────────────────────────────


def test_all_entity_types_instantiate_with_no_args():
    """All fields must be optional — instantiation with no args must succeed."""
    entity_classes = [Guest, Podcast, Topic, Study, Book, Product, Protocol]
    for cls in entity_classes:
        instance = cls()
        assert instance is not None, f'{cls.__name__} must instantiate with no args'


# ── ENTITY_TYPES dict ─────────────────────────────────────────────────────────


def test_entity_types_dict_has_expected_keys():
    expected_keys = {'Guest', 'Podcast', 'Topic', 'Study', 'Book', 'Product', 'Protocol'}
    assert set(ENTITY_TYPES.keys()) == expected_keys


def test_entity_types_dict_values_match_classes():
    assert ENTITY_TYPES['Guest'] is Guest
    assert ENTITY_TYPES['Podcast'] is Podcast
    assert ENTITY_TYPES['Topic'] is Topic
    assert ENTITY_TYPES['Study'] is Study
    assert ENTITY_TYPES['Book'] is Book
    assert ENTITY_TYPES['Product'] is Product
    assert ENTITY_TYPES['Protocol'] is Protocol


def test_entity_types_dict_values_are_basemodel_subclasses():
    for name, cls in ENTITY_TYPES.items():
        assert issubclass(cls, BaseModel), f'ENTITY_TYPES[{name!r}] must be a BaseModel subclass'
