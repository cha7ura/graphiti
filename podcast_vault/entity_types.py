from pydantic import BaseModel, Field


class Guest(BaseModel):
    """Podcast guest or host who makes claims and shares insights"""

    expertise: str | None = Field(
        default=None,
        description='Primary field: neuroscience, psychology, fitness, business, medicine',
    )
    credentials: str | None = Field(
        default=None,
        description='PhD, MD, Professor at Stanford, CEO of X, etc.',
    )


class Podcast(BaseModel):
    """A podcast show (not an episode — the show itself)"""

    host: str | None = Field(
        default=None,
        description='Primary host name: Andrew Huberman, Steven Bartlett, Lex Fridman',
    )


class Topic(BaseModel):
    """A subject area discussed — brain health, dopamine, sleep, weight loss, fasting"""

    domain: str | None = Field(
        default=None,
        description='health, neuroscience, psychology, fitness, nutrition, business, relationships, productivity',
    )


class Study(BaseModel):
    """A scientific study or research paper referenced by a guest"""

    authors: str | None = Field(
        default=None,
        description='Lead author or author list: "Sramek et al.", "Walker & Stickgold"',
    )
    year: str | None = Field(
        default=None,
        description='Publication year if mentioned',
    )
    journal: str | None = Field(
        default=None,
        description='Journal name if mentioned',
    )
    doi: str | None = Field(
        default=None,
        description='DOI if found by research enrichment agent',
    )


class Book(BaseModel):
    """A book recommended or referenced by a guest"""

    author: str | None = Field(
        default=None,
        description='Book author',
    )


class Product(BaseModel):
    """A supplement, tool, device, or product mentioned by a guest"""

    product_type: str | None = Field(
        default=None,
        description='supplement, device, app, tool, food, protocol',
    )


class Protocol(BaseModel):
    """A specific actionable routine or method"""

    category: str | None = Field(
        default=None,
        description='sleep, exercise, nutrition, cold_exposure, breathing, meditation, supplement_stack',
    )
    difficulty: str | None = Field(
        default=None,
        description='beginner, intermediate, advanced',
    )


ENTITY_TYPES: dict[str, type[BaseModel]] = {
    'Guest': Guest,
    'Podcast': Podcast,
    'Topic': Topic,
    'Study': Study,
    'Book': Book,
    'Product': Product,
    'Protocol': Protocol,
}
