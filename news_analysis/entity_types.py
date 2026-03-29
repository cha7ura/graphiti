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


# === Phase 2: Refined Entity Types ===


class Politician(BaseModel):
    """Elected officials, ministers, party leaders, presidential candidates"""

    party: str | None = Field(
        default=None,
        description='Current political party name',
    )
    title: str | None = Field(
        default=None,
        description='Honorific: Hon., Dr., etc.',
    )


class GovernmentBody(BaseModel):
    """Ministries, departments, commissions, courts, parliament"""

    body_type: str | None = Field(
        default=None,
        description='ministry, department, commission, court, parliament, central_bank',
    )
    jurisdiction: str | None = Field(
        default=None,
        description='national, provincial, or district level',
    )


class PoliticalParty(BaseModel):
    """SLPP, SJB, UNP, JVP/NPP, SLFP, TNA, etc."""

    coalition: str | None = Field(
        default=None,
        description='Coalition or alliance name if part of one',
    )


class EconomicIndicator(BaseModel):
    """Inflation rate, GDP, debt-to-GDP ratio, forex reserves, etc."""

    indicator_type: str | None = Field(
        default=None,
        description='inflation, gdp, debt_ratio, reserves, unemployment, interest_rate, exchange_rate',
    )
    unit: str | None = Field(
        default=None,
        description='percentage, USD, LKR, billions, etc.',
    )


class InternationalEntity(BaseModel):
    """IMF, World Bank, UN, foreign governments involved in SL affairs"""

    entity_type: str | None = Field(
        default=None,
        description='multilateral, foreign_government, ngo, donor_agency',
    )


class NewsOutlet(BaseModel):
    """News publication or media organization"""

    outlet_type: str | None = Field(
        default=None,
        description='newspaper, tv, online, wire_service, state_media',
    )
    language: str | None = Field(
        default=None,
        description='Primary language: sinhala, tamil, english',
    )
