from datetime import date

from flask import Flask, request, abort
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from auth import requires_auth, AuthError
from models import setup_db, Actor, Movie, db

# !!WARN: NEVER PUT BLANK LINES INSIDE FUNCTIONS
# ..INFO: YOU CAN PUT A HASH (#) INSTEAD
# !!WARN: ALWAYS PUT AT LEAST A SINGLE BLANK LINE BETWEEN FUNCTIONS
# ..INFO: THIS IS DUE TO HOW DOCS GENERATOR WORKS


def create_app():
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)
    @app.after_request
    def after_request(response):
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        header['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        header['Access-Control-Allow-Methods'] = '*'
        return response

    @app.route('/')
    def index():
        return {'message': 'hello world'}

    @app.route('/headers')
    @requires_auth()
    def get_jwt_contents(payload):
        return {'message': 'granted', 'content': payload}

    @app.route('/actors')
    @requires_auth('read:actor')
    def get_actors(_p):
        """No pagination"""
        return {
            'success': True,
            'actors': [a.format() for a in Actor.query.order_by(Actor.id).all()]
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
        data = request.get_json()
        try:
            # sorry, broken validation for `gender`
            a = Actor(
                name=data.get('name') or abort(400),
                age=data.get('age') or abort(400),
                gender=data.get('gender'),
            ).insert()
            return {
                'success': True,
                'actor': a.format(),
            }
        except SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    @app.route('/actors/<int:pk>', methods=['PATCH'])
    @requires_auth('update:actor')
    def update_actor(_p, pk: int):
        data = request.get_json()
        a = Actor.query.get(pk) or abort(404)
        try:
            for field in ('name', 'age', 'gender'):
                if field in data:
                    setattr(a, field, data[field])
            a.update()
            return {
                'success': True,
                'actor': a.format(),
            }
        except SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    @app.route('/actors/<int:pk>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(_p, pk: int):
        a = Actor.query.get(pk) or abort(404)
        try:
            a.delete()
            return {'success': True}
        except SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    @app.route('/movies')
    @requires_auth('read:movie')
    def get_movies(_p):
        """No pagination"""
        return {
            'success': True,
            'movies': [m.format() for m in Movie.query.all()]
        }

    @app.route('/movies/<int:pk>')
    @requires_auth('read:movie')
    def get_movie(_p, pk: int):
        return {
            'success': True,
            'movie': (Movie.query.get(pk) or abort(404)).format(),
        }

    @app.route('/movies', methods=['POST'])
    @requires_auth('add:movie')
    def add_movie(_p):
        data = request.get_json()
        try:
            # sorry, broken validation for `gender`
            a = Movie(
                title=data.get('title') or abort(400),
                release_date=date.fromisoformat(
                    data.get('release_date') or abort(400)
                ),
            ).insert()
            return {
                'success': True,
                'movie': a.format(),
            }
        except SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    @app.route('/movies/<int:pk>', methods=['PATCH'])
    @requires_auth('update:movie')
    def update_movie(_p, pk: int):
        data = request.get_json()
        m = Movie.query.get(pk) or abort(404)
        try:
            for field in ('title', 'release_date'):
                if field in data:
                    setattr(m, field, data[field])
            m.update()
            return {
                'success': True,
                'movie': m.format(),
            }
        except SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    @app.route('/movies/<int:pk>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(_p, pk: int):
        m = Movie.query.get(pk) or abort(404)
        try:
            m.delete()
            return {'success': True}
        except SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    @app.errorhandler(AuthError)
    def auth_error(e: AuthError):
        return {
                   'success': False,
                   'error': e.error,
               }, e.status_code

    @app.errorhandler(400)
    def bad_request(_error):
        """Raised if some fields are missing in POST or PATCH requests or if they of invalid type"""
        return {
                   'success': False,
                   'error': 400,
                   'message': 'bad request',
               }, 400

    @app.errorhandler(403)
    def forbidden(_error):
        """Raised if you don't have enough permissions"""
        return {
                   'success': False,
                   'error': 403,
                   'message': 'forbidden',
               }, 403

    @app.errorhandler(404)
    def not_found(_error):
        """Raised if the given resource cannot be found"""
        return {
                   'success': False,
                   'error': 404,
                   'message': 'not found',
               }, 404

    @app.errorhandler(422)
    def unprocessable(_error):
        """Raised if database error occurred, e.g. foreign key constraint failed"""
        return {
                   'success': False,
                   'error': 422,
                   'message': 'unprocessable',
               }, 422

    @app.errorhandler(500)
    def internal_server_error(_error):
        """Raised if the server failed to fulfill the request"""
        return {
                   'success': False,
                   'error': 500,
                   'message': 'internal server error',
               }, 500

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
