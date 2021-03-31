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
            movie_id=499,
            age=4,
            gender=0,
        )
        self.bad_actor = dict(
            name='',  # oops, empty name
            movie_id=499,
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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTdhYzk4OWMwNTAwNjkxNWU2NGQiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3MTY5ODc5LCJleHAiOjE2MTcxNzcwNzksImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSJdfQ.mGIOAZ12d41eQZJxSMsdgxCqcwQ94qsiL2zzrlFjogu8BNmHsxGXIa972QK7SlTVuF3vG5U37UIOD7t_dhR8Rm9TFT3Egzy8KLbC4z4OUxjNx9ynzj9VBQeBcQggQIaHTsld-RcdUFoHnV-AHnDZUP_tL9WGY50e_J60ReW269aN8It8n4jPeJbWY36wq9h9zm4xI9mkp6IT-yWFUWIiITuCK2l5GAvEa6RNAq1J9Or0o71UlI92MuI3cd0ZCgj5TrSoTawLXKJgXLpvi-CRbPa4bXZjaLH6SbQQRA2xpZUG14YW3STr-WQTrD1BwXKe7jdAVvov9MAwmUk229Oh2g'  # noqa

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
        self.assertEqual(data['actor']['title'], a.title)

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
        self.assertIsInstance(data['movie']['actors'], list)

    def test_get_movie_404(self):
        mid = 999
        res = self.get(f'/movies/{mid}')
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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTg4ZGNiZjUzOTAwNjlkNjQ2MTAiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3MTcwMDQ4LCJleHAiOjE2MTcxNzcyNDgsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJkZWxldGU6YWN0b3IiLCJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.WJghz_t5PwlFgnmOvt9vTudKoMYT_6DHaBoTbXNJ1mPesqCXWwQP9Qe9pby3PeMb7DQTP8I101tiEQURxiG08PaWRw-2vpJAEExwcYmzRKaCbNnhDUScUBnz35jSjB-P-CCYPJDqSE6dpy6m6p8X2-db_NqQJS-1Ij1BMwlpnzjg4jPkmZiTjcfak4NSK50EdIMdRCwgVomusCSwEksP13ErUPhIIWkxZEFbyAx5GIUpu-vi2jJd_9HGIuZMVkb0WtqAEcRPwZY75o4TcSYTT8EB-3ESqM_LenxkFuvnZ1ylskMrbftB16JweH15oIEb2e-5O7c-4f_BZl3Ebej83g'  # noqa

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
        a = Movie(**self.sample_movie).insert()
        res = self.patch(f'/movies/{a.id}', json=dict(
            title='My new title'
        ))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['name'], a.name)

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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTkxNDdmNzU0MzAwNzBiOGFmNTEiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3MTcwODcwLCJleHAiOjE2MTcxNzgwNzAsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJhZGQ6bW92aWUiLCJkZWxldGU6YWN0b3IiLCJkZWxldGU6bW92aWUiLCJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.ifQqq9fax4lUt1qQj0D9OEx3VcCmTbx92eE3Gbqa63hQFRl0UA3brmvq3_nIoIMBx1BrmGaAM-jbb-T9I0BnCy-49F0jQzB1hLIR5SOR7_-l4OI48dUJmGQPr5cEufE1oJM7BCenW16-03LO2vtGH0MH0PK5xSM3V_fqDDS52AHTxfRXlUGMkjTvmlW3itR7M_CIvhSLX6p_Eq21fvxMyGE9vby_AkrlYCgAGgQLEeCZEGb_IrVqPEmvtXOcTEr3X9fMeyk8D7OIaPIDNw3c1pk5osY2cGOq1J1hG9PJH_vlnp0MHVV6HwNH2prr5mWCqQ7V7v3rgKFa0CR0GjCKZQ'  # noqa

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
        self.assertIsNone(Movie.get(mid))

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
