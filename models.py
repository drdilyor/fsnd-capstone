import os
from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

db = SQLAlchemy()
default_db_path = 'sqlite:///db.sqlite3'

def setup_db(app, database_path=os.environ.get('DATABASE', default_db_path)):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.create_all()

class DbMethods:
    def insert(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):  # noqa
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


class Movie(DbMethods, db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    release_date = Column(Date)

    actors = relationship('Actor', backref='movie', lazy=True)

    def __init__(self, title: str, release_date: date): # noqa
        self.title = title
        self.release_date = release_date

    def __str__(self):
        return f"{self.__class__.__name__} {self.id} {self.title}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id!r}, {self.title!r}, {self.release_date!r})"

    def format(self):
        return dict(
            id=self.id,
            title=self.title,
            release_date=self.release_date.isoformat(),
        )

    def format_long(self):
        return {**self.format(), **dict(
            actors=[a.format() for a in self.actors]
        )}


class Actor(DbMethods, db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(Integer)
    movie_id = Column(Integer, ForeignKey('movie.id'), nullable=True)

    def __init__(self, name: str, age: int, gender: int, movie_id: int): # noqa
        self.name = name
        self.age = age
        self.gender = gender
        self.movie_id = movie_id

    def __str__(self):
        return f"{self.__class__.__name__} {self.id} {self.name}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id!r}, {self.name!r}, {self.age!r}, {self.gender_str})"

    @property
    def gender_str(self):
        return ['Man', 'Woman'][self.gender]

    def format(self):
        return dict(
            id=self.id,
            name=self.name,
            age=self.age,
            gender=self.gender,
            movie_id=self.movie_id,
        )
