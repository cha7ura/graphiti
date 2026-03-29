from pydantic import BaseModel

from news_analysis.edge_types import (
    EDGE_TYPE_MAP,
    PHASE_2_EDGE_TYPES,
    BelongsToParty,
    EnforcesPolicy,
    HoldsPosition,
    InvolvedInEvent,
    MakesStatement,
    OpposesPolicy,
    ReportsValue,
    SupportsPolicy,
)


class TestEdgeTypes:
    def test_holds_position_defaults(self):
        e = HoldsPosition()
        assert e.position_title is None

    def test_holds_position_with_values(self):
        e = HoldsPosition(position_title='Minister of Finance')
        assert e.position_title == 'Minister of Finance'

    def test_makes_statement_defaults(self):
        e = MakesStatement()
        assert e.context is None
        assert e.topic is None

    def test_makes_statement_with_values(self):
        e = MakesStatement(context='parliament', topic='economy')
        assert e.context == 'parliament'
        assert e.topic == 'economy'

    def test_supports_policy_defaults(self):
        e = SupportsPolicy()
        assert e.strength is None

    def test_opposes_policy_defaults(self):
        e = OpposesPolicy()
        assert e.strength is None

    def test_reports_value_defaults(self):
        e = ReportsValue()
        assert e.reported_value is None
        assert e.reporting_source is None

    def test_reports_value_with_values(self):
        e = ReportsValue(reported_value='4.2%', reporting_source='CBSL')
        assert e.reported_value == '4.2%'
        assert e.reporting_source == 'CBSL'

    def test_belongs_to_party_defaults(self):
        e = BelongsToParty()
        assert e.role_in_party is None

    def test_involved_in_event_defaults(self):
        e = InvolvedInEvent()
        assert e.role is None

    def test_enforces_policy_defaults(self):
        e = EnforcesPolicy()
        assert e.enforcement_status is None

    def test_all_are_pydantic_models(self):
        for model_cls in [
            HoldsPosition, MakesStatement, SupportsPolicy, OpposesPolicy,
            ReportsValue, BelongsToParty, InvolvedInEvent, EnforcesPolicy,
        ]:
            assert issubclass(model_cls, BaseModel)

    def test_all_fields_optional(self):
        for model_cls in [
            HoldsPosition, MakesStatement, SupportsPolicy, OpposesPolicy,
            ReportsValue, BelongsToParty, InvolvedInEvent, EnforcesPolicy,
        ]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None


class TestEdgeTypeMap:
    def test_edge_type_map_has_expected_keys(self):
        expected_keys = [
            ('Politician', 'GovernmentBody'),
            ('Politician', 'Policy'),
            ('Politician', 'PoliticalParty'),
            ('Politician', 'Event'),
            ('Politician', 'EconomicIndicator'),
            ('PoliticalParty', 'Policy'),
            ('PoliticalParty', 'Event'),
            ('GovernmentBody', 'EconomicIndicator'),
            ('GovernmentBody', 'Policy'),
            ('GovernmentBody', 'Event'),
            ('InternationalEntity', 'EconomicIndicator'),
            ('InternationalEntity', 'Policy'),
            ('NewsOutlet', 'EconomicIndicator'),
            ('NewsOutlet', 'Event'),
            ('NewsOutlet', 'Politician'),
        ]
        for key in expected_keys:
            assert key in EDGE_TYPE_MAP, f'Missing edge type map key: {key}'

    def test_politician_government_body_edges(self):
        assert EDGE_TYPE_MAP[('Politician', 'GovernmentBody')] == ['HoldsPosition']

    def test_politician_policy_edges(self):
        assert EDGE_TYPE_MAP[('Politician', 'Policy')] == ['SupportsPolicy', 'OpposesPolicy']

    def test_government_body_economic_indicator_edges(self):
        assert EDGE_TYPE_MAP[('GovernmentBody', 'EconomicIndicator')] == ['ReportsValue']

    def test_phase_2_edge_types_dict(self):
        """PHASE_2_EDGE_TYPES should map string names to model classes"""
        assert PHASE_2_EDGE_TYPES['HoldsPosition'] is HoldsPosition
        assert PHASE_2_EDGE_TYPES['MakesStatement'] is MakesStatement
        assert PHASE_2_EDGE_TYPES['ReportsValue'] is ReportsValue
        assert len(PHASE_2_EDGE_TYPES) == 8
