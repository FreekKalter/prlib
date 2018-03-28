#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer, String, CheckConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
from . import app
import re

Base = declarative_base()


class Serie(Base):
    __tablename__ = 'serie'
    id          = Column(Integer, primary_key=True)
    name        = Column(String(250), nullable=False)
    tags        = Column(String(500), nullable=True)
    rating      = Column('rating', Integer, CheckConstraint('rating>=0'), CheckConstraint('rating<=100'), nullable=True)
    comment     = Column(String(1500), nullable=True)


class Movie(Base):
    __tablename__ = 'movie'
    id                      = Column(Integer, primary_key=True)
    name                    = Column(String(250))
    # size                  = Column(Integer, nullable=True)
    location                = Column(String(500), nullable=False, unique=True)
    added                   = Column(DateTime, nullable=False)
    last_played             = Column(DateTime, nullable=True)
    tags                    = Column(String(500), nullable=True)
    comment                 = Column(String(1500), nullable=True)
    rating                  = Column('rating', Integer, CheckConstraint('rating>=0'),
                                     CheckConstraint('rating<=100'), nullable=True)
    screenshot              = Column(String(500), nullable=True)
    thumbnail               = Column(String(500), nullable=True)
    serie_id                = Column(Integer, ForeignKey('serie.id'))
    serie                   = relationship(Serie)
    files                   = relationship("File", back_populates="movie", cascade="all, delete-orphan")
    __compressed_regex__    = re.compile("-compressed.mp4$")

    @property
    def size(self):
        return sum([f.size for f in self.files])

    @property
    def compressed(self):
        return all([self.__compressed_regex__.search(f.location) for f in self.files])

    @property
    def days(self):
        days = 365
        if self.last_played:
            days = (datetime.now() - self.last_played).days
        if days > 365:
            return 365
        return days

    @property
    def change(self):
        lp, added = (365, 365)
        if self.last_played:
            lp = (datetime.now() - self.last_played).days
        if self.added:
            added = (datetime.now() - self.added).days
        change = lp + added
        if change > 2 * 365:
            return 2 * 365
        else:
            return change


class File(Base):
    __tablename__ = 'file'
    id          = Column(Integer, primary_key=True)
    location    = Column(String(500), nullable=False)
    size        = Column(Integer, nullable=True)
    preview     = Column(String(500), nullable=True)
    thumbnail   = Column(String(500), nullable=True)
    movie_id    = Column(Integer, ForeignKey('movie.id'))
    movie       = relationship(Movie, back_populates="files")

    def __str__(self):
        return self.location


def create():
    engine = create_engine('sqlite:///' + app.config['DB_FILE'])
    Base.metadata.create_all(engine)
