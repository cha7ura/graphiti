from pydantic import BaseModel, Field


class HoldsPosition(BaseModel):
    """Politician holds a government position (Minister, MP, President, etc.)"""

    position_title: str | None = Field(
        default=None,
        description='The specific position: President, Minister of Finance, MP for Colombo, etc.',
    )


class MakesStatement(BaseModel):
    """A person or org makes a public claim, promise, or assertion"""

    context: str | None = Field(
        default=None,
        description='Context: interview, parliament, press_conference, rally, social_media',
    )
    topic: str | None = Field(
        default=None,
        description='What the statement is about: economy, policy, opposition, etc.',
    )


class SupportsPolicy(BaseModel):
    """Person or party publicly supports a policy or position"""

    strength: str | None = Field(
        default=None,
        description='strong, conditional, lukewarm',
    )


class OpposesPolicy(BaseModel):
    """Person or party publicly opposes a policy or position"""

    strength: str | None = Field(
        default=None,
        description='strong, conditional, lukewarm',
    )


class ReportsValue(BaseModel):
    """A source reports a specific value for an economic indicator"""

    reported_value: str | None = Field(
        default=None,
        description="The actual value reported: '12.5%', 'USD 3.2 billion', etc.",
    )
    reporting_source: str | None = Field(
        default=None,
        description='Who reported it: CBSL, IMF, Ministry of Finance, opposition claim',
    )


class BelongsToParty(BaseModel):
    """Politician is a member of a political party"""

    role_in_party: str | None = Field(
        default=None,
        description='leader, deputy_leader, member, spokesperson',
    )


class InvolvedInEvent(BaseModel):
    """Person, org, or party is involved in an event"""

    role: str | None = Field(
        default=None,
        description='organizer, participant, target, responder, critic',
    )


class EnforcesPolicy(BaseModel):
    """Government body implements or enforces a policy"""

    enforcement_status: str | None = Field(
        default=None,
        description='implementing, partially_implementing, blocking, reviewing',
    )


# Dict for passing to Graphiti's edge_types parameter
PHASE_2_EDGE_TYPES: dict[str, type[BaseModel]] = {
    'HoldsPosition': HoldsPosition,
    'MakesStatement': MakesStatement,
    'SupportsPolicy': SupportsPolicy,
    'OpposesPolicy': OpposesPolicy,
    'ReportsValue': ReportsValue,
    'BelongsToParty': BelongsToParty,
    'InvolvedInEvent': InvolvedInEvent,
    'EnforcesPolicy': EnforcesPolicy,
}

# Constrains which edge types can connect which entity types
EDGE_TYPE_MAP: dict[tuple[str, str], list[str]] = {
    ('Politician', 'GovernmentBody'): ['HoldsPosition'],
    ('Politician', 'Policy'): ['SupportsPolicy', 'OpposesPolicy'],
    ('Politician', 'PoliticalParty'): ['BelongsToParty'],
    ('Politician', 'Event'): ['InvolvedInEvent', 'MakesStatement'],
    ('Politician', 'EconomicIndicator'): ['MakesStatement', 'ReportsValue'],
    ('PoliticalParty', 'Policy'): ['SupportsPolicy', 'OpposesPolicy'],
    ('PoliticalParty', 'Event'): ['InvolvedInEvent'],
    ('GovernmentBody', 'EconomicIndicator'): ['ReportsValue'],
    ('GovernmentBody', 'Policy'): ['EnforcesPolicy'],
    ('GovernmentBody', 'Event'): ['InvolvedInEvent'],
    ('InternationalEntity', 'EconomicIndicator'): ['ReportsValue'],
    ('InternationalEntity', 'Policy'): ['SupportsPolicy', 'OpposesPolicy'],
    ('NewsOutlet', 'EconomicIndicator'): ['ReportsValue'],
    ('NewsOutlet', 'Event'): ['InvolvedInEvent'],
    ('NewsOutlet', 'Politician'): ['MakesStatement'],
}
