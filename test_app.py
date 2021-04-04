import json
import unittest
from datetime import date

from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from src.app import create_app
from src.models import setup_db, db, Actor, Movie


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
            age=4,
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
        m = Movie(**self.sample_movie)
        m.id = 499
        m.insert()

    def setUp(self):
        """Define test variables and initialize app.
        Don't call db.drop_all() here, as it is causing hang on my machine
        """

    def tearDown(self):
        self.db.session.close()

    def error_forbidden(self, method, url, json_data=None):
        res = getattr(self.client, method)(
            url, json=json_data,
            headers={'Authorization': f'Bearer {self.jwt}'},
        )
        data = json.loads(res.data)
        if res.status_code == 401:
            print(data['error'])
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs, headers={
            'Authorization': f'Bearer {self.jwt}',
        })

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs, headers={
            'Authorization': f'Bearer {self.jwt}',
        })

    def patch(self, *args, **kwargs):
        return self.client.patch(*args, **kwargs, headers={
            'Authorization': f'Bearer {self.jwt}',
        })

    def delete(self, *args, **kwargs):
        return self.client.delete(*args, **kwargs, headers={
            'Authorization': f'Bearer {self.jwt}',
        })


class CastingAssistantTest(MyTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTdhYzk4OWMwNTAwNjkxNWU2NGQiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3NTM3NjQxLCJleHAiOjE2MTc2MjQwNDEsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSJdfQ.yeG6u1S7OGqPKL2mQJF2p2f1sbjHvGY_kUjH2Xm6B0zjoNGta7mAERA03dG2bQBfSBFR8EDIv6e0VobIu_wnR7UshCxYZaiFaNa_mbZII8Is30SzFhXkpdltFPVL-DDT-1lvGc8FJp7RjsMCIcHr33Szb859NOXa9z4-7O_pwd3CAf9-Idw_RLChB4Uv88d9rM3XDiNqG9Usn5o8l_faJ1P6rtMjcyM2u2u8WWDTXPTbogPvm0jR7vcKVcRnjw7xrxYy_HEcBOVUabFE5HcbnWttoM92yjKngvejQj2C7RvX6Yx8lFZbgaw6-DGxv-9OPvmdZ3fHj17jkKHmwKcGlg'  # noqa

    def test_get_actors(self):
        res = self.get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['actors'], list)

    def test_get_movies(self):
        res = self.get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['movies'], list)

    def test_get_an_actor(self):
        a = Actor(**self.sample_actor).insert()
        aid = a.id
        res = self.get(f'/actors/{aid}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor']['name'], a.name)

    def test_get_actor_404(self):
        aid = 999
        res = self.get(f'/actors/{aid}')
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_get_an_movie(self):
        m = Movie(**self.sample_movie).insert()
        mid = m.id
        res = self.get(f'/movies/{mid}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['title'], m.title)

    def test_get_movie_404(self):
        mid = 999
        res = self.get(f'/movies/{mid}')
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_delete_actor(self):
        self.error_forbidden('delete', '/actors/1')

    def test_delete_movie(self):
        self.error_forbidden('delete', '/movies/1')

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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTg4ZGNiZjUzOTAwNjlkNjQ2MTAiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3NTM3Njk2LCJleHAiOjE2MTc2MjQwOTYsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJkZWxldGU6YWN0b3IiLCJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.iMZTG9AQpZmZIymHsfsqKXblK9Cy4ehGgwGK0oadciLVT5AgY-6VNU_P9sTeJfnVF7YiRGs33bWNVAMviHRNL2NVxgJawWDZnmetqUr6-gHk5PDFBfo3tMyHv2n7mEmjoaPn5cheNjtVd9kUUciHSxhCP0kfn2b9HLosDUDoPc9fs5tmB_ihZo7waqf2_PGcbQIzAA3vwMNBSD-NiHzidZm08XNUJPgU3b5XPNM_4hEgNM5ovFal1Tj-HIz0jtOhGOSGuzrBd_aIgjTr66icz36IdOrbKdUkx-HyGazPCI8_Lrno1CbSv-YDxIp41cVXqDsbWcMlZaU6gZWhIwkHxw'  # noqa

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
        res = self.delete(f'/actors/{aid}')
        _data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNone(Actor.query.get(aid))

    def test_delete_actor_404(self):
        aid = 999
        res = self.delete(f'/actors/{aid}')
        _data = json.loads(res.data)

        self.assertIsNone(Actor.query.get(aid))
        self.assertEqual(res.status_code, 404)

    def test_delete_movie(self):
        CastingAssistantTest.test_delete_movie(self)  # noqa

    def test_post_actor(self):
        res = self.post('/actors', json=self.sample_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data.get('actor'))

    def test_post_actor_400(self):
        res = self.post('/actors', json=self.bad_actor)
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)

    def test_post_movie(self):
        CastingAssistantTest.test_post_movie(self)  # noqa

    def test_patch_actor(self):
        a = Actor(**self.sample_actor).insert()
        res = self.patch(f'/actors/{a.id}', json=dict(
            name='My new name'
        ))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor']['name'], a.name)

    def test_patch_actor_404(self):
        aid = 999
        res = self.patch(f'/actors/{aid}', json=dict(
            name='My new name'
        ))
        _data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_patch_movie(self):
        m = Movie(**self.sample_movie).insert()
        res = self.patch(f'/movies/{m.id}', json=dict(
            title='My new title'
        ))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['title'], m.title)

    def test_patch_movie_404(self):
        mid = 999
        res = self.patch(f'/movies/{mid}', json=dict(
            title='My new title'
        ))
        _data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)


class ExecutiveProducerTest(MyTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTkxNDdmNzU0MzAwNzBiOGFmNTEiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3NTM3NzI5LCJleHAiOjE2MTc2MjQxMjksImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJhZGQ6bW92aWUiLCJkZWxldGU6YWN0b3IiLCJkZWxldGU6bW92aWUiLCJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.LJWO5OFWqDNwrChvP6v-zPW3hqtRTDXgb-hkqHeXv-jUxFtbFU2fOj8xK4jVlSlgrd5drgvRLY1YcoudxnHDjxKZML3k5Dzc4Rb9bqhHWCUa92UIH_1pzkoNCJjJGQOWcYM0viUy610nurx1Gpy9ygm8x1Wr-aAhI7_acGH3SMlUQmG661zhfs7OIpcxEVseQgAnuH4H7D7dKD1oqxEs3bq6HqJyhwdYYAz6KMPk3uC5U9sVJQ7x84eY47uHYmtOQs3eaEqXGCkYRknFF-kG8uM4ppbE7O7sDk-WVJQB1uJ7Zfh45kyMDrDejtIMtGnYFlMwTLxupkS_SInziIZb0Q'  # noqa

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
        mid = Movie(**self.sample_movie).insert().id
        res = self.delete(f'/movies/{mid}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNone(Movie.query.get(mid))

    def test_delete_movie_404(self):
        mid = 999
        res = self.delete(f'/actors/{mid}')
        _data = json.loads(res.data)

        self.assertIsNone(Movie.query.get(mid))
        self.assertEqual(res.status_code, 404)

    def test_post_actor(self):
        CastingDirectorTest.test_post_actor(self)  # noqa

    def test_post_actor_400(self):
        CastingDirectorTest.test_post_actor_400(self)  # noqa

    def test_post_movie(self):
        res = self.post('/movies', json=self.sample_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data.get('movie'))

    def test_post_movie_400(self):
        res = self.post('/movies', json=self.bad_movie)
        _data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)

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
