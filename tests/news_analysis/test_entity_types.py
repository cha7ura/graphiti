from pydantic import BaseModel

from news_analysis.entity_types import (
    EconomicIndicator,
    Event,
    GovernmentBody,
    InternationalEntity,
    Location,
    NewsOutlet,
    Organization,
    Person,
    Policy,
    PoliticalParty,
    Politician,
)


class TestPhase1EntityTypes:
    def test_person_defaults(self):
        p = Person()
        assert p.role is None

    def test_person_with_role(self):
        p = Person(role='politician')
        assert p.role == 'politician'

    def test_organization_defaults(self):
        o = Organization()
        assert o.org_type is None

    def test_organization_with_type(self):
        o = Organization(org_type='political_party')
        assert o.org_type == 'political_party'

    def test_location_defaults(self):
        loc = Location()
        assert loc.location_type is None

    def test_location_with_type(self):
        loc = Location(location_type='district')
        assert loc.location_type == 'district'

    def test_policy_defaults(self):
        p = Policy()
        assert p.domain is None

    def test_policy_with_domain(self):
        p = Policy(domain='economic')
        assert p.domain == 'economic'

    def test_event_defaults(self):
        e = Event()
        assert e.event_type is None

    def test_event_with_type(self):
        e = Event(event_type='election')
        assert e.event_type == 'election'

    def test_all_are_pydantic_models(self):
        """Graphiti requires entity types to be Pydantic BaseModel subclasses"""
        for model_cls in [Person, Organization, Location, Policy, Event]:
            assert issubclass(model_cls, BaseModel)

    def test_all_fields_optional(self):
        """All fields must be optional (None default) for Graphiti extraction"""
        for model_cls in [Person, Organization, Location, Policy, Event]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None, (
                    f'{model_cls.__name__}.{field_name} is not optional'
                )


class TestPhase2EntityTypes:
    def test_politician_defaults(self):
        p = Politician()
        assert p.party is None
        assert p.title is None

    def test_politician_with_values(self):
        p = Politician(party='UNP', title='Hon.')
        assert p.party == 'UNP'
        assert p.title == 'Hon.'

    def test_government_body_defaults(self):
        g = GovernmentBody()
        assert g.body_type is None
        assert g.jurisdiction is None

    def test_government_body_with_values(self):
        g = GovernmentBody(body_type='ministry', jurisdiction='national')
        assert g.body_type == 'ministry'
        assert g.jurisdiction == 'national'

    def test_political_party_defaults(self):
        p = PoliticalParty()
        assert p.coalition is None

    def test_political_party_with_values(self):
        p = PoliticalParty(coalition='SLPP-led alliance')
        assert p.coalition == 'SLPP-led alliance'

    def test_economic_indicator_defaults(self):
        e = EconomicIndicator()
        assert e.indicator_type is None
        assert e.unit is None

    def test_economic_indicator_with_values(self):
        e = EconomicIndicator(indicator_type='inflation', unit='percentage')
        assert e.indicator_type == 'inflation'
        assert e.unit == 'percentage'

    def test_international_entity_defaults(self):
        ie = InternationalEntity()
        assert ie.entity_type is None

    def test_international_entity_with_values(self):
        ie = InternationalEntity(entity_type='multilateral')
        assert ie.entity_type == 'multilateral'

    def test_news_outlet_defaults(self):
        n = NewsOutlet()
        assert n.outlet_type is None
        assert n.language is None

    def test_news_outlet_with_values(self):
        n = NewsOutlet(outlet_type='newspaper', language='english')
        assert n.outlet_type == 'newspaper'
        assert n.language == 'english'

    def test_all_phase2_are_pydantic_models(self):
        for model_cls in [
            Politician, GovernmentBody, PoliticalParty,
            EconomicIndicator, InternationalEntity, NewsOutlet,
        ]:
            assert issubclass(model_cls, BaseModel)

    def test_all_phase2_fields_optional(self):
        for model_cls in [
            Politician, GovernmentBody, PoliticalParty,
            EconomicIndicator, InternationalEntity, NewsOutlet,
        ]:
            instance = model_cls()
            for field_name in model_cls.model_fields:
                assert getattr(instance, field_name) is None, (
                    f'{model_cls.__name__}.{field_name} is not optional'
                )
