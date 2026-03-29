from pydantic import BaseModel, Field

# === Phase 1: Discovery Entity Types ===


class Person(BaseModel):
    """Any named individual mentioned in news articles"""

    role: str | None = Field(
        default=None,
        description='Role if mentioned (politician, official, activist, etc.)',
    )


class Organization(BaseModel):
    """Political parties, government bodies, companies, NGOs, international orgs"""

    org_type: str | None = Field(
        default=None,
        description='Type: political_party, government, military, ngo, company, international',
    )


class Location(BaseModel):
    """Districts, provinces, cities, countries referenced in articles"""

    location_type: str | None = Field(
        default=None,
        description='Type: country, province, district, city, area',
    )


class Policy(BaseModel):
    """Laws, bills, agreements, economic policies, reforms"""

    domain: str | None = Field(
        default=None,
        description='Domain: economic, social, constitutional, foreign, environmental',
    )


class Event(BaseModel):
    """Protests, elections, disasters, diplomatic events, incidents"""

    event_type: str | None = Field(
        default=None,
        description='Type: election, protest, disaster, diplomatic, legislative, scandal',
    )
