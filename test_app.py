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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTdhYzk4OWMwNTAwNjkxNWU2NGQiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3MjQ5NDcyLCJleHAiOjE2MTczMzU4NzIsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSJdfQ.ARUfDKm2gV3BMwX9AZHwXL7roE8AvEqthzQxyTDuJL4xSN7JomfFx6O6wzYF5wrviXuPFQIQmD-VucPZvvEMqrqD5naKbDLB4dOZyPH-SMQAb5HI_NT983riUra8n95E_hv2JW04PIZKdBtAJJwhgX_aKGpCB-XtoQSPpTybqLC72ofv0QSFa5ZY6lxIF5Yq5w9EksR3PN2ifanKcPUauKCDKsfo1PkCxNbxZvIMUbACn5ZSDZM5jEwdsFZ-YG8yX2M0G5z-fBxxu2UjB8LR_I5fwAREBUEac2kdJ3AMG2G92K7-V9JUEgX7NcBL0ClBWWjGFPxiWRmuxf2xklWIbA'  # noqa

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
        self.assertIsInstance(data['movie']['actors'], list)

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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTg4ZGNiZjUzOTAwNjlkNjQ2MTAiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3MjQ5NDY3LCJleHAiOjE2MTczMzU4NjcsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJkZWxldGU6YWN0b3IiLCJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.0inYQRqOpBlL0Q8vSo9Vn3JpftFzBCwhtdcFcewV79yalxr6pRpnlQT_f6rEh2jJF3tOqeHkoZRo5RtL9sv9UBVFS_BBGyfOyIoDR-FVRV2l-A6fCR0xXS_TlJsT0L5ijqBVbpkEhMs7yklT-XdhGMSnc2kN9kVhB4xqvyaP9xtqpK_qjLBnmjXQNSYP3KKdf1q6kBDmCB1VUwSzNqw95Axu0lV77n5fuTXYvKr1LqcXQRlVmXW1xmyW7sbaTm5cyjt0iyfnzYA8115oq0opFuIVXuMlnHx8Nx2_X5P90-JK2A3Qy7AGvo0Y0i1GOjwOc4d0YHfon22lGPEfpRoDWg'  # noqa

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
        self.jwt = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZKeTlHd3BuTE5NUzRkS2pqR3FZeiJ9.eyJpc3MiOiJodHRwczovL2RyZGlseW9yLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDYzZTkxNDdmNzU0MzAwNzBiOGFmNTEiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjE3MjQ5NDcwLCJleHAiOjE2MTczMzU4NzAsImF6cCI6IkFtN1ZKSHcyNnZOZUdvbmtnRDNYYnhNQnZjcWJzeEJVIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJhZGQ6bW92aWUiLCJkZWxldGU6YWN0b3IiLCJkZWxldGU6bW92aWUiLCJyZWFkOmFjdG9yIiwicmVhZDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.EMksRjrJfjXZZwXtO3PcWojlgnRnVcxIfyB6TB1YfdbJ5pv9gNNV1dlsRN7_AL3ZyJbVgvnJiKudxXHugC-QFA4Mg9j1_IkW-f1pXuCvpidG7095KqRrtiWWn8st3TBuai9g3gD4MdOCV-IAjjEGOSlM_TqVCsugJOU491StSverckP0yp4LSkTzZjk8WH7aXKfYQtLGkovbtVBw4_2AgiDaxLeeQXFLo0N14gTEymcZQFNB2zBJrF_6wOQR2J7gl_IdZmkmldIS6bUvO1wgVhO6CNvGDuqWVAX5ajFVjQYzB5ZkePnksRdod_PLz7o47ruPBkUo8RFHEDtPyLzIrw'  # noqa

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
