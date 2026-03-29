"""Tests for podcast_vault.edge_types module."""

from pydantic import BaseModel

from podcast_vault.edge_types import (
    EDGE_TYPE_MAP,
    EDGE_TYPES,
    AppearsOn,
    DescribesProtocol,
    MakesClaim,
    RecommendsBook,
    RecommendsProduct,
    ReferencesStudy,
    RelatesTo,
    SupportsProtocol,
)

# ── Defaults ──────────────────────────────────────────────────────────────────


def test_makes_claim_defaults():
    mc = MakesClaim()
    assert mc.insight_type is None
    assert mc.confidence is None
    assert mc.start_time is None
    assert mc.end_time is None
    assert mc.youtube_url is None


def test_describes_protocol_defaults():
    dp = DescribesProtocol()
    assert dp.start_time is None
    assert dp.end_time is None
    assert dp.youtube_url is None


def test_references_study_defaults():
    rs = ReferencesStudy()
    assert rs.context is None


def test_recommends_book_defaults():
    rb = RecommendsBook()
    assert rb.strength is None


def test_recommends_product_defaults():
    rp = RecommendsProduct()
    assert rp.usage is None


def test_relates_to_defaults():
    rt = RelatesTo()
    assert rt.relationship is None


def test_appears_on_defaults():
    ao = AppearsOn()
    assert ao.episode_title is None
    assert ao.episode_number is None
    assert ao.episode_date is None
    assert ao.youtube_id is None


def test_supports_protocol_defaults():
    sp = SupportsProtocol()
    assert sp.strength is None


# ── With values ───────────────────────────────────────────────────────────────


def test_makes_claim_with_values():
    mc = MakesClaim(
        insight_type='claim',
        confidence='high',
        start_time='14:23',
        end_time='16:05',
        youtube_url='https://youtube.com/watch?v=abc&t=863',
    )
    assert mc.insight_type == 'claim'
    assert mc.confidence == 'high'
    assert mc.start_time == '14:23'
    assert mc.end_time == '16:05'
    assert mc.youtube_url == 'https://youtube.com/watch?v=abc&t=863'


def test_describes_protocol_with_values():
    dp = DescribesProtocol(
        start_time='5:00',
        end_time='10:30',
        youtube_url='https://youtube.com/watch?v=xyz&t=300',
    )
    assert dp.start_time == '5:00'
    assert dp.end_time == '10:30'
    assert dp.youtube_url == 'https://youtube.com/watch?v=xyz&t=300'


def test_references_study_with_values():
    rs = ReferencesStudy(context='supports_claim')
    assert rs.context == 'supports_claim'


def test_recommends_book_with_values():
    rb = RecommendsBook(strength='strong')
    assert rb.strength == 'strong'


def test_recommends_product_with_values():
    rp = RecommendsProduct(usage='daily')
    assert rp.usage == 'daily'


def test_relates_to_with_values():
    rt = RelatesTo(relationship='causes')
    assert rt.relationship == 'causes'


def test_appears_on_with_values():
    ao = AppearsOn(
        episode_title='Sleep Science',
        episode_number='42',
        episode_date='2023-01-15',
        youtube_id='dQw4w9WgXcQ',
    )
    assert ao.episode_title == 'Sleep Science'
    assert ao.episode_number == '42'
    assert ao.episode_date == '2023-01-15'
    assert ao.youtube_id == 'dQw4w9WgXcQ'


def test_supports_protocol_with_values():
    sp = SupportsProtocol(strength='strong')
    assert sp.strength == 'strong'


# ── BaseModel subclass checks ─────────────────────────────────────────────────


def test_all_edge_types_are_basemodel_subclasses():
    edge_classes = [
        MakesClaim,
        DescribesProtocol,
        ReferencesStudy,
        RecommendsBook,
        RecommendsProduct,
        RelatesTo,
        AppearsOn,
        SupportsProtocol,
    ]
    for cls in edge_classes:
        assert issubclass(cls, BaseModel), f'{cls.__name__} must be a BaseModel subclass'


# ── All fields optional ───────────────────────────────────────────────────────


def test_all_edge_types_instantiate_with_no_args():
    """All fields must be optional — instantiation with no args must succeed."""
    edge_classes = [
        MakesClaim,
        DescribesProtocol,
        ReferencesStudy,
        RecommendsBook,
        RecommendsProduct,
        RelatesTo,
        AppearsOn,
        SupportsProtocol,
    ]
    for cls in edge_classes:
        instance = cls()
        assert instance is not None, f'{cls.__name__} must instantiate with no args'


# ── EDGE_TYPES dict ───────────────────────────────────────────────────────────


def test_edge_types_dict_has_expected_keys():
    expected_keys = {
        'MakesClaim',
        'DescribesProtocol',
        'ReferencesStudy',
        'RecommendsBook',
        'RecommendsProduct',
        'RelatesTo',
        'AppearsOn',
        'SupportsProtocol',
    }
    assert set(EDGE_TYPES.keys()) == expected_keys


def test_edge_types_dict_values_match_classes():
    assert EDGE_TYPES['MakesClaim'] is MakesClaim
    assert EDGE_TYPES['DescribesProtocol'] is DescribesProtocol
    assert EDGE_TYPES['ReferencesStudy'] is ReferencesStudy
    assert EDGE_TYPES['RecommendsBook'] is RecommendsBook
    assert EDGE_TYPES['RecommendsProduct'] is RecommendsProduct
    assert EDGE_TYPES['RelatesTo'] is RelatesTo
    assert EDGE_TYPES['AppearsOn'] is AppearsOn
    assert EDGE_TYPES['SupportsProtocol'] is SupportsProtocol


def test_edge_types_dict_values_are_basemodel_subclasses():
    for name, cls in EDGE_TYPES.items():
        assert issubclass(cls, BaseModel), f'EDGE_TYPES[{name!r}] must be a BaseModel subclass'


# ── EDGE_TYPE_MAP ─────────────────────────────────────────────────────────────


def test_edge_type_map_has_expected_entity_pairs():
    expected_pairs = {
        ('Guest', 'Topic'),
        ('Guest', 'Protocol'),
        ('Guest', 'Study'),
        ('Guest', 'Book'),
        ('Guest', 'Product'),
        ('Guest', 'Podcast'),
        ('Topic', 'Topic'),
        ('Protocol', 'Topic'),
        ('Study', 'Protocol'),
        ('Study', 'Topic'),
    }
    assert set(EDGE_TYPE_MAP.keys()) == expected_pairs


def test_edge_type_map_values_are_lists_of_strings():
    for pair, edge_names in EDGE_TYPE_MAP.items():
        assert isinstance(edge_names, list), f'EDGE_TYPE_MAP[{pair}] must be a list'
        for name in edge_names:
            assert isinstance(name, str), f'Edge name {name!r} in {pair} must be a string'


def test_edge_type_map_names_exist_in_edge_types():
    for pair, edge_names in EDGE_TYPE_MAP.items():
        for name in edge_names:
            assert name in EDGE_TYPES, f'{name!r} from EDGE_TYPE_MAP[{pair}] not in EDGE_TYPES'


def test_edge_type_map_specific_mappings():
    assert EDGE_TYPE_MAP[('Guest', 'Topic')] == ['MakesClaim']
    assert EDGE_TYPE_MAP[('Guest', 'Protocol')] == ['DescribesProtocol']
    assert EDGE_TYPE_MAP[('Guest', 'Study')] == ['ReferencesStudy']
    assert EDGE_TYPE_MAP[('Guest', 'Book')] == ['RecommendsBook']
    assert EDGE_TYPE_MAP[('Guest', 'Product')] == ['RecommendsProduct']
    assert EDGE_TYPE_MAP[('Guest', 'Podcast')] == ['AppearsOn']
    assert EDGE_TYPE_MAP[('Topic', 'Topic')] == ['RelatesTo']
    assert EDGE_TYPE_MAP[('Protocol', 'Topic')] == ['RelatesTo']
    assert EDGE_TYPE_MAP[('Study', 'Protocol')] == ['SupportsProtocol']
    assert EDGE_TYPE_MAP[('Study', 'Topic')] == ['RelatesTo']
