#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movie'
    id          = Column(Integer, primary_key=True)
    name        = Column(String(250))
    size        = Column(Integer, nullable=True)
    tags        = Column(String(500), nullable=True)
    comment     = Column(String(1500), nullable=True)
    rating      = Column('rating', Integer, CheckConstraint('rating>0'), CheckConstraint('rating<101'), nullable=True)
    screenshot  = Column(String(500), nullable=True)


class File(Base):
    __tablename__ = 'file'
    id          = Column(Integer, primary_key=True)
    location    = Column(String(500), nullable=False)
    size        = Column(Integer, nullable=True)
    movie_id    = Column(Integer, ForeignKey('movie.id'))
    movie       = relationship(Movie)


engine = create_engine('sqlite:///movie.db')
Base.metadata.create_all(engine)
