from pydantic import BaseModel

from news_analysis.entity_types import (
    Event,
    Location,
    Organization,
    Person,
    Policy,
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
