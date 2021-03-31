from flask import Flask, request, abort
from flask_cors import CORS

from auth import requires_auth, AuthError
from models import setup_db, Actor, Movie


def create_app():
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)

    @app.route('/')
    def index():
        return {'message': 'hello world'}

    @app.route('/headers')
    @requires_auth()
    def test_auth(payload):
        return {'message': 'granted', 'content': payload}

    @app.route('/actors')
    @requires_auth('read:actor')
    def get_actors(_p):
        """No pagination"""
        return {
            'success': True,
            'actors': [a.format() for a in Actor.query.all()]
        }

    @app.route('/actors/<int:pk>')
    @requires_auth('read:actor')
    def get_actor(_p, pk: int):
        return {
            'success': True,
            'actor': (Actor.query.get(pk) or abort(404)).format(),
        }

    @app.route('/actors', methods=['POST'])
    @requires_auth('add:actor')
    def add_actor(_p):
        return {'message': 'not implemented'}, 500

    @app.route('/actors/<int:pk>', methods=['PATCH'])
    @requires_auth('update:actor')
    def update_actor(_p, pk: int):
        return {'message': 'not implemented'}, 500

    @app.route('/actors/<int:pk>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(_p, pk: int):
        return {'message': 'not implemented'}, 500

    @app.route('/movies')
    @requires_auth('read:movie')
    def get_movies(_p):
        return {'message': 'not implemented'}, 500

    @app.route('/movies/<int:pk>')
    @requires_auth('read:movie')
    def get_movie(_p, pk: int):
        return {'message': 'not implemented'}, 500

    @app.route('/movies', methods=['POST'])
    @requires_auth('add:movie')
    def add_movie(_p):
        return {'message': 'not implemented'}, 500

    @app.route('/movies/<int:pk>', methods=['PATCH'])
    @requires_auth('update:movie')
    def update_movie(_p, pk: int):
        return {'message': 'not implemented'}, 500

    @app.route('/movies/<int:pk>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(_p, pk: int):
        return {'message': 'not implemented'}, 500

    @app.errorhandler(AuthError)
    def auth_error(e: AuthError):
        return {
                   'success': False,
                   'error': e.error,
               }, e.status_code

    @app.errorhandler(400)
    def bad_request(_error):
        return {
                   'success': False,
                   'error': 400,
                   'message': 'bad request',
               }, 400

    @app.errorhandler(403)
    def not_found(_error):
        return {
                   'success': False,
                   'error': 403,
                   'message': 'forbidden',
               }, 403

    @app.errorhandler(404)
    def not_found(_error):
        return {
                   'success': False,
                   'error': 404,
                   'message': 'not found',
               }, 404

    @app.errorhandler(422)
    def unprocessable(_error):
        return {
                   'success': False,
                   'error': 422,
                   'message': 'unprocessable',
               }, 422

    @app.errorhandler(500)
    def internal_server_error(_error):
        return {
                   'success': False,
                   'error': 500,
                   'message': 'internal server error',
               }, 500

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
