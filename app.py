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

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
