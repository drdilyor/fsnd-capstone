import json
import unittest
from datetime import date

from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, db, Actor, Movie


class MyTestCase(unittest.TestCase):
    jwt: str
    app: Flask = None
    client: FlaskClient
    database_name = "fsnd_capstone_test"
    database_path = "postgresql://postgres:postgres@localhost:5432/{}".format(database_name)
    db: SQLAlchemy = None

    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(*args, **kwargs)

        if MyTestCase.app is None:
            MyTestCase.app = create_app()
        MyTestCase.client = self.app.test_client()
        if MyTestCase.db is None:
            setup_db(self.app, self.database_path)
            MyTestCase.db = db

        self.db.drop_all()
        self.db.create_all()

        self.sample_actor = dict(
            name='My actor',
            age=42,
            gender=0,
        )
        self.bad_actor = dict(
            name='',  # oops, empty name
            age=42,
            gender=0,
        )
        self.sample_movie = dict(
            title='My movie',
            release_date=date(2021, 3, 30).isoformat(),
        )
        self.bad_movie = dict(
            title='',
            release_date=date(2021, 3, 30).isoformat(),
        )

    def setUp(self):
        """Define test variables and initialize app.
        Don't call db.drop_all() here, as it is causing hang on my machine
        """

    def error_forbidden(self, method, url, json_data=None):
        res = getattr(self.client, method)(
            url, json=json_data,
            headers={'Authorization': f'Bearer {self.jwt}'},
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)


class CastingAssistantTest(MyTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt = ''  # TODO

    def test_get_actors(self):
        res = self.client.get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['actors'], list)

    def test_get_movies(self):
        res = self.client.get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['movies'], list)

    def test_get_an_actor(self):
        a = Actor(**self.sample_actor).insert()
        aid = a.id
        res = self.client.get(f'/actors/{aid}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor']['title'], a.title)

    def test_get_actor_404(self):
        aid = 999
        res = self.client.get(f'/actors/{aid}')
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_get_an_movie(self):
        m = Movie(**self.sample_movie).insert()
        mid = m.id
        res = self.client.get(f'/movies/{mid}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['title'], m.title)

    def test_get_movie_404(self):
        mid = 999
        res = self.client.get(f'/movies/{mid}')
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_delete_actor(self):
        self.error_forbidden('delete', '/movies/1')

    def test_delete_movie(self):
        self.error_forbidden('delete', '/actors/1')

    def test_post_actor(self):
        self.error_forbidden('post', '/actors', self.sample_actor)

    def test_post_movie(self):
        self.error_forbidden('post', '/movies', self.sample_movie)

    def test_patch_actor(self):
        self.error_forbidden('patch', '/actors/1', {})

    def test_patch_movie(self):
        self.error_forbidden('patch', '/movies/1', {})


class CastingDirectorTest(MyTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt = ''

    def test_get_actors(self):
        CastingAssistantTest.test_get_actors(self)  # noqa

    def test_get_movies(self):
        CastingAssistantTest.test_get_movies(self)  # noqa

    def test_get_an_actor(self):
        CastingAssistantTest.test_get_an_actor(self)  # noqa

    def test_get_actor_404(self):
        CastingAssistantTest.test_get_actor_404(self)  # noqa

    def test_get_an_movie(self):
        CastingAssistantTest.test_get_an_movie(self)  # noqa

    def test_get_movie_404(self):
        CastingAssistantTest.test_get_movie_404(self)  # noqa

    def test_delete_actor(self):
        aid = Actor(**self.sample_actor).insert().id
        res = self.client.delete(f'/actors/{aid}')
        _data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNone(Actor.query.get(aid))

    def test_delete_actor_404(self):
        aid = 999
        res = self.client.delete(f'/actors/{aid}')
        _data = json.loads(res.data)

        self.assertIsNone(Actor.query.get(aid))
        self.assertEqual(res.status_code, 404)

    def test_delete_movie(self):
        CastingAssistantTest.test_delete_movie(self)  # noqa

    def test_post_actor(self):
        res = self.client.post('/actors', json=self.sample_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data.get('actor'))

    def test_post_actor_400(self):
        res = self.client.post('/actors', json=self.bad_actor)
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)

    def test_post_movie(self):
        CastingAssistantTest.test_post_movie(self)  # noqa

    def test_patch_actor(self):
        a = Actor(**self.sample_actor).insert()
        res = self.client.patch(f'/actors/{a.id}', json=dict(
            name='My new name'
        ))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor']['name'], a.name)

    def test_patch_actor_404(self):
        aid = 999
        res = self.client.patch(f'/actors/{aid}', json=dict(
            name='My new name'
        ))
        _data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_patch_movie(self):
        a = Movie(**self.sample_movie).insert()
        res = self.client.patch(f'/movies/{a.id}', json=dict(
            title='My new title'
        ))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['name'], a.name)

    def test_patch_movie_404(self):
        mid = 999
        res = self.client.patch(f'/movies/{mid}', json=dict(
            title='My new title'
        ))
        _data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)


class ExecutiveProducerTest(MyTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt = ''

    def test_get_actors(self):
        CastingDirectorTest.test_get_actors(self)  # noqa

    def test_get_movies(self):
        CastingDirectorTest.test_get_movies(self)  # noqa

    def test_get_an_actor(self):
        CastingDirectorTest.test_get_an_actor(self)  # noqa

    def test_get_actor_404(self):
        CastingDirectorTest.test_get_actor_404(self)  # noqa

    def test_get_an_movie(self):
        CastingDirectorTest.test_get_an_movie(self)  # noqa

    def test_get_movie_404(self):
        CastingDirectorTest.test_get_movie_404(self)  # noqa

    def test_delete_actor(self):
        CastingDirectorTest.test_delete_actor(self)  # noqa

    def test_delete_actor_404(self):
        CastingDirectorTest.test_delete_actor_404(self)  # noqa

    def test_delete_movie(self):
        CastingDirectorTest.test_delete_movie(self)  # noqa

    def test_post_actor(self):
        CastingDirectorTest.test_post_actor(self)  # noqa

    def test_post_actor_400(self):
        CastingDirectorTest.test_post_actor_400(self)  # noqa

    def test_post_movie(self):
        CastingDirectorTest.test_post_movie(self)  # noqa

    def test_patch_actor(self):
        CastingDirectorTest.test_patch_actor(self)  # noqa

    def test_patch_actor_404(self):
        CastingDirectorTest.test_patch_actor_404(self)  # noqa

    def test_patch_movie(self):
        CastingDirectorTest.test_patch_movie(self)  # noqa

    def test_patch_movie_404(self):
        CastingDirectorTest.test_patch_movie_404(self)  # noqa


if __name__ == '__main__':
    unittest.main()
