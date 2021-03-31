from flask import Flask, request, abort
from flask_cors import CORS

from auth import requires_auth, AuthError


def create_app():
    # create and configure the app
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    def index():
        return {'message': 'hello world'}

    @app.route('/headers')
    @requires_auth()
    def test_auth(payload):
        return {'message': 'granted', 'content': payload}

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
