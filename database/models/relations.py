from sqlalchemy import Column, Table, Integer, ForeignKey
from database.db import Base

film_actors = Table(
    "film_actors",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
)

tvseries_actors = Table(
    "tvseries_actors",
    Base.metadata,
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
)

film_directors = Table(
    "film_directors",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
)

tvseries_directors = Table(
    "tvseries_directors",
    Base.metadata,
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
)

film_voice_over = Table(
    "film_voice_over",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
)

tvseries_voice_over = Table(
    "tvseries_voice_over",
    Base.metadata,
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
)

genre_films = Table(
    "genre_films",
    Base.metadata,
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
)

genre_tvseries = Table(
    "genre_tvseries",
    Base.metadata,
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
)

film_countries = Table(
    "film_countries",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
)

tvseries_countries = Table(
    "tvseries_countries",
    Base.metadata,
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
)

tvseries_sequels = Table(
    "tvseries_sequels",
    Base.metadata,
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
    Column("sequel_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
)

person_roles = Table(
    "person_roles",
    Base.metadata,
    Column("person_id", Integer, ForeignKey("persons.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

film_trivias = Table(
    "film_trivias",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("trivia_id", Integer, ForeignKey("trivia.id"), primary_key=True),
)

tvseries_trivias = Table(
    "tvseries_trivias",
    Base.metadata,
    Column("tvseries_id", Integer, ForeignKey("tvseries.id"), primary_key=True),
    Column("trivia_id", Integer, ForeignKey("trivia.id"), primary_key=True),
)
