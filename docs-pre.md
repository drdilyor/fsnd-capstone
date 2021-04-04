# Casting Agency 😃
A simple application written in flask to manage actors and movies. You may also
be interested in [frontend](https://github.com/drdilyor/fsnd-frontend)
My last Project for Full Stack Nanodegree on Udacity :)

## Local setup
> **Note**: These instructions are unix-oriented

Python version required: **python 3.8**.
It might work in other versions as well, but I haven't tested yet

### Clone the repo:
```shell script
git clone https://github.com/drdilyor/fsnd-capstone
cd fsnd-capstone
```

### Create a virtual environment:
```shell script
python3 -m venv venv --prompt "Capstone by an UZBEK CODER"
source venv/bin/activate
```

### Install required packages:
```shell script
pip install -r requirements.txt
```

#### Key dependencies:
- **Flask** - a minimalistic web framework
- **SQLAlchemy** - a Relational Database ORM
- **psycopg2** - DB API for PostgreSQL
- **Flask-Migrate** - Migration tool for SQLAlchemy
- **Flask-CORS** - CORS toolkit for flask

### Configure the environment
Shell file `setup.sh` includes a sample configuration. You should be fine by just sourcing it:
```shell script
source setup.sh
```

- `AUTH0_DOMAIN` - Auth0 domain to use for authentication, you can obtain a one from auth0.com
- `API_AUDIENCE` - Identification of the Auth0 API, you can obtain a one from Auth0 dashboard
- `DATABASE` - (optional) Database URI to use. Defaults to: `sqlite:///db.sqlite3`

### Initialize database
Create a PostgreSQL database:
```shell script
createdb fsnd-capstone
```
...next, create schemas:
```shell script
./manage.py db upgrade
```

### Finally, *Start the server*
...using either gunicorn:
```shell script
gunicorn src:APP -b :8000
```
...or flask's development server:
```shell script
cd src
flask run -p 8000
```

## Role based access control (RBAC)
This project defines 3 roles:
- **Casting Assistant**:
  - `read:actor`
  - `read:movie`
- **Casting Director**:
  - All permissions of Casting Assistant
  - `add:actor`
  - `update:actor`
  - `delete:actor`
  - `update:movie`
- **Executive Producer**:
  - All permissions of Casting Director
  - `add:movie`
  - `delete:movie`

> Auth0 credentials <br>
> email: **assistant@drdilyor-fsnd.com** <br>
> email: **director@drdilyor-fsnd.com** <br>
> email: **producer@drdilyor-fsnd.com** <br>
> password: **26D6udjbvWK5fXT**

## Tests

I've written a handful of unittests. To execute all of them:
```shell script
python test_app.py
```
If you are getting 401 errors, please update the jwt tokens in `test_app.py`
using the above credentials.

### Hand-testing
You can use curl or postman (get it from [here](https://getposman.com)).

#### cURL
I recommend setting host and JWT as a variable so that you don't have to pass it to
every request manually:
```shell script
host=http://localhost:8000
token=JWT_TOKEN_HERE
```

Then make requests like this:
```shell script
curl $host/headers \
-H "Authorization: Bearer $token"
```
> **Note**: make sure to use double quotes (`"`) around authorization header
> so that shell expands `$token` to its contents. Otherwise authorization header
> will be literally `Authorization: Bearer $token`

The above command outputs like this:
```json
{
  "message": "granted",
  "content": {
    "here goes": "jwt contents..."
  }
}
```

## Models
### Actor
- **name** - full name
- **age** - actor's age in years
- **gender** - either 0 for man, and 1 for woman

### Movie
- **title** - title of the movie
- **release_date** - when the movie is scheduled to a release
