from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    Date,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.orm import relationship

from database.db import Base
from database.models.relations import (
    film_actors,
    tvseries_actors,
    film_directors,
    tvseries_directors,
    film_voice_over,
    tvseries_voice_over,
    genre_films,
    genre_tvseries,
    film_countries,
    tvseries_countries,
    tvseries_sequels,
    person_roles,
)


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, nullable=False)
    kinopoisk_id = Column(Integer, nullable=False, index=True, unique=True)
    title_russian = Column(String, index=True)
    title_original = Column(String, index=True)
    production_year = Column(Integer, index=True)
    short_description = Column(String)
    synopsis = Column(String)
    trailer_ya_stream_url = Column(String)
    trailer_youtube = Column(String)
    cover_url = Column(String)
    tagline = Column(String)
    kinopoisk_poster_url = Column(String)
    rating_imdb = Column(Float)
    rating_kinopoisk = Column(Float)
    rating_kinopoisk_top10_pos = Column(Integer)
    rating_kinopoisk_top250_pos = Column(Integer)
    rating_russian_critics = Column(Float)
    rating_world_wide_critics = Column(Float)
    duration = Column(Integer)
    kinopoisk_url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    genres = relationship("Genre", secondary=genre_films, back_populates="films")
    countries = relationship(
        "Country", secondary=film_countries, back_populates="films"
    )
    actors = relationship("Person", secondary=film_actors, back_populates="films")
    directors = relationship(
        "Person", secondary=film_directors, back_populates="directed_films"
    )
    voice_over_actors = relationship(
        "Person", secondary=film_voice_over, back_populates="voice_over_films"
    )
    trivias = relationship(
        "Trivia",
        secondary="film_trivias",
        back_populates="films",
    )

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "title_russian": self.title_russian,
                "title_original": self.title_original,
                "production_year": self.production_year,
                "short_description": self.short_description,
                "synopsis": self.synopsis,
                "cover_url": self.cover_url,
                "tagline": self.tagline,
                "kinopoisk_poster_url": self.kinopoisk_poster_url,
                "rating_imdb": self.rating_imdb,
                "rating_kinopoisk": self.rating_kinopoisk,
                "rating_kinopoisk_top10_pos": self.rating_kinopoisk_top10_pos,
                "rating_kinopoisk_top250_pos": self.rating_kinopoisk_top250_pos,
                "rating_russian_critics": self.rating_russian_critics,
                "rating_world_wide_critics": self.rating_world_wide_critics,
                "duration": self.duration,
                "typename": self.__qualname__.lower(),
            }
        )


class TvSeries(Base):
    __tablename__ = "tvseries"

    id = Column(Integer, primary_key=True, nullable=False)
    kinopoisk_id = Column(Integer, nullable=False, index=True, unique=True)
    toramp_id = Column(Integer, index=True, unique=True)
    title_russian = Column(String, index=True)
    title_original = Column(String, index=True)
    production_year = Column(Integer, index=True)
    short_description = Column(String)
    synopsis = Column(String)
    release_start = Column(Integer)
    release_end = Column(Integer)
    seasons_count = Column(Integer)
    is_next_season_in_production = Column(Boolean)
    new_seria_date = Column(Date)
    cover_url = Column(String)
    trailer_ya_stream_url = Column(String)
    trailer_youtube = Column(String)
    tagline = Column(String)
    kinopoisk_poster_url = Column(String)
    toramp_poster_url = Column(String)
    rating_imdb = Column(Float)
    rating_kinopoisk = Column(Float)
    rating_kinopoisk_top10_pos = Column(Integer)
    rating_kinopoisk_top250_pos = Column(Integer)
    rating_russian_critics = Column(Float)
    rating_world_wide_critics = Column(Float)
    episodes_count = Column(Integer)
    duration_total = Column(Integer)
    duration_series = Column(Integer)
    kinopoisk_url = Column(String)
    toramp_url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    genres = relationship("Genre", secondary=genre_tvseries, back_populates="tvseries")
    countries = relationship(
        "Country", secondary=tvseries_countries, back_populates="tvseries"
    )
    actors = relationship(
        "Person", secondary=tvseries_actors, back_populates="tvseries"
    )
    directors = relationship(
        "Person", secondary=tvseries_directors, back_populates="directed_tvseries"
    )
    voice_over_actors = relationship(
        "Person", secondary=tvseries_voice_over, back_populates="voice_over_tvseries"
    )
    seasons = relationship(
        "Season", back_populates="tvseries", cascade="all, delete-orphan"
    )
    sequels = relationship(
        "TvSeries",
        secondary=tvseries_sequels,
        primaryjoin=id == tvseries_sequels.c.tvseries_id,
        secondaryjoin=id == tvseries_sequels.c.sequel_id,
        backref="prequels",
    )
    trivias = relationship(
        "Trivia",
        secondary="tvseries_trivias",
        back_populates="tvseries",
    )

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "title_russian": self.title_russian,
                "title_original": self.title_original,
                "production_year": self.production_year,
                "short_description": self.short_description,
                "synopsis": self.synopsis,
                "release_start": self.release_start,
                "release_end": self.release_end,
                "seasons_count": self.seasons_count,
                "is_next_season_in_production": self.is_next_season_in_production,
                "new_seria_date": self.new_seria_date,
                "cover_url": self.cover_url,
                "tagline": self.tagline,
                "poster_url": self.kinopoisk_poster_url,
                "rating_imdb": self.rating_imdb,
                "rating_kinopoisk": self.rating_kinopoisk,
                "rating_kinopoisk_top10_pos": self.rating_kinopoisk_top10_pos,
                "rating_kinopoisk_top250_pos": self.rating_kinopoisk_top250_pos,
                "rating_russian_critics": self.rating_russian_critics,
                "rating_world_wide_critics": self.rating_world_wide_critics,
                "episodes_count": self.episodes_count,
                "duration_total": self.duration_total,
                "duration_series": self.duration_series,
                "typename": self.__qualname__.lower(),
            }
        )


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint("tvseries_id", "season_number", name="uq_season"),
    )

    id = Column(Integer, primary_key=True)
    tvseries_id = Column(Integer, ForeignKey("tvseries.id"), nullable=False)
    season_number = Column(Integer, nullable=False)
    release_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    episodes = relationship(
        "Episode", back_populates="season", cascade="all, delete-orphan"
    )
    tvseries = relationship("TvSeries", back_populates="seasons")

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "tvseries_id": self.tvseries_id,
                "season_number": self.season_number,
                "release_year": self.release_year,
                "typename": self.__qualname__.lower(),
            }
        )


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title_russian = Column(String)
    title_original = Column(String)
    release_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    season = relationship("Season", back_populates="episodes")

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "season_id": self.season_id,
                "episode_number": self.episode_number,
                "title_russian": self.title_russian,
                "title_original": self.title_original,
                "release_date": self.release_date,
                "typename": self.__qualname__.lower(),
            }
        )


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, nullable=False)
    kinopoisk_id = Column(Integer, nullable=False, index=True, unique=True)
    name = Column(String, index=True)
    original_name = Column(String, index=True)
    birth_date = Column(Date)
    kinopoisk_avatars_url = Column(String)
    kinopoisk_person_url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    films = relationship("Film", secondary=film_actors, back_populates="actors")
    tvseries = relationship(
        "TvSeries", secondary=tvseries_actors, back_populates="actors"
    )
    directed_films = relationship(
        "Film", secondary=film_directors, back_populates="directors"
    )
    directed_tvseries = relationship(
        "TvSeries", secondary=tvseries_directors, back_populates="directors"
    )
    voice_over_films = relationship(
        "Film", secondary=film_voice_over, back_populates="voice_over_actors"
    )
    voice_over_tvseries = relationship(
        "TvSeries", secondary=tvseries_voice_over, back_populates="voice_over_actors"
    )
    roles = relationship("Role", secondary=person_roles, back_populates="persons")

    def __repr__(self):
        person_name = self.name if self.name else self.original_name
        return str(
            {
                "id": self.id,
                "name": person_name,
                "birth_date": self.birth_date,
                "avatars_url": self.kinopoisk_avatars_url,
                "typename": self.__qualname__.lower(),
            }
        )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    persons = relationship("Person", secondary=person_roles, back_populates="roles")

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "name": self.name,
                "typename": self.__qualname__.lower(),
            }
        )


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    kinopoisk_id = Column(Integer, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False, index=True, unique=True)
    slug = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    films = relationship("Film", secondary=genre_films, back_populates="genres")
    tvseries = relationship(
        "TvSeries", secondary=genre_tvseries, back_populates="genres"
    )

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "name": self.name,
                "typename": self.__qualname__.lower(),
            }
        )


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    kinopoisk_id = Column(Integer, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    films = relationship("Film", secondary=film_countries, back_populates="countries")
    tvseries = relationship(
        "TvSeries", secondary=tvseries_countries, back_populates="countries"
    )

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "name": self.name,
                "typename": self.__qualname__.lower(),
            }
        )


class Trivia(Base):
    __tablename__ = "trivia"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    kinopoisk_id = Column(Integer, index=True, nullable=False, unique=True)
    text = Column(String, nullable=False)
    trivia_type = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    films = relationship("Film", secondary="film_trivias", back_populates="trivias")
    tvseries = relationship(
        "TvSeries", secondary="tvseries_trivias", back_populates="trivias"
    )

    def __repr__(self):
        return str(
            {
                "id": self.id,
                "text": self.text,
                "trivia_type": self.trivia_type,
                "typename": self.__qualname__.lower(),
            }
        )
