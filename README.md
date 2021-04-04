> **Warning**: auto generated, do NOT edit it by hand! Instead make changes to docs-pre.md and docs-post.md files

# Casting Agency 😃
A simple application written in flask to manage actors and movies. You may also
be interested in [frontend](https://github.com/drdilyor/fsnd-frontend)

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

## Tests
> Auth0 credentials <br>
> email: **assistant@drdilyor-fsnd.com** <br>
> email: **director@drdilyor-fsnd.com** <br>
> email: **producer@drdilyor-fsnd.com** <br>
> password: **26D6udjbvWK5fXT**

I've written a handful of unittests. To execute all of them:
```shell script
python src/test_app.py
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

## API Docs
API is deployed to http://localhost:8000

### Index
#### Endpoint
`GET /`

#### Sample request
```shell script
curl http://localhost:8000/
```

The above command returns json structured like this:
```json
"No example response available"
```

#### Permission
`This endpoint is publicly available`
#### Raises
This endpoint doesn't raise any errors

### Get Jwt Contents
#### Endpoint
`GET /headers`

#### Sample request
```shell script
curl http://localhost:8000/headers
```

The above command returns json structured like this:
```json
"No example response available"
```

#### Permission
`This endpoint is publicly available`
#### Raises
This endpoint doesn't raise any errors

### Get Actors
#### Endpoint
`GET /actors`

#### Sample request
```shell script
curl http://localhost:8000/actors \
-H "Authorization: Bearer $token"
```

The above command returns json structured like this:
```json
{
  "success": true,
  "actors": [
    {
      "id": 1,
      "name": "Axad Qayyum",
      "age": 42,
      "gender": 0
    }
  ]
}
```

#### Permission
`read:actor`
#### Raises
This endpoint doesn't raise any errors

### Get Actor
#### Endpoint
`GET /actors/<int:pk>`

#### Sample request
```shell script
curl http://localhost:8000/actors/1 \
-H "Authorization: Bearer $token"
```

The above command returns json structured like this:
```json
{
  "success": true,
  "actor": {
    "id": 1,
    "name": "Axad Qayyum",
    "age": 42,
    "gender": 0
  }
}
```

#### Permission
`read:actor`
#### Raises
- **[404](#404)**
### Add Actor
#### Endpoint
`POST /actors`

#### Sample request
```shell script
curl http://localhost:8000/actors \
-X POST \
-H "Authorization: Bearer $token" \
-H 'Content-Type: application/json' \
-d '{"name": "Axad Qayyum", "age": 42, "gender": 0}'
```

The above command returns json structured like this:
```json
{
  "success": true,
  "actor": {
    "id": 1,
    "name": "Axad Qayyum",
    "age": 42,
    "gender": 0
  }
}
```

#### Permission
`add:actor`
#### Raises
- **[422](#422)**
- **[400](#400)**
### Update Actor
#### Endpoint
`PATCH /actors/<int:pk>`

#### Sample request
```shell script
curl http://localhost:8000/actors/1 \
-X PATCH \
-H "Authorization: Bearer $token" \
-H 'Content-Type: application/json' \
-d '{"name": "Axad Qayyum", "age": 42, "gender": 0}'
```

The above command returns json structured like this:
```json
{
  "success": true,
  "actor": {
    "id": 1,
    "name": "Axad Qayyum",
    "age": 42,
    "gender": 0
  }
}
```

#### Permission
`update:actor`
#### Raises
- **[404](#404)**
- **[422](#422)**
### Delete Actor
#### Endpoint
`DELETE /actors/<int:pk>`

#### Sample request
```shell script
curl http://localhost:8000/actors/1 \
-X DELETE \
-H "Authorization: Bearer $token"
```

The above command returns json structured like this:
```json
{
  "success": true,
  "actor": {
    "id": 1,
    "name": "Axad Qayyum",
    "age": 42,
    "gender": 0
  }
}
```

#### Permission
`delete:actor`
#### Raises
- **[404](#404)**
- **[422](#422)**
### Get Movies
#### Endpoint
`GET /movies`

#### Sample request
```shell script
curl http://localhost:8000/movies \
-H "Authorization: Bearer $token"
```

The above command returns json structured like this:
```json
{
  "success": true,
  "movies": [
    {
      "id": 1,
      "title": "My example movie",
      "release_date": "2022-05-01"
    }
  ]
}
```

#### Permission
`read:movie`
#### Raises
This endpoint doesn't raise any errors

### Get Movie
#### Endpoint
`GET /movies/<int:pk>`

#### Sample request
```shell script
curl http://localhost:8000/movies/1 \
-H "Authorization: Bearer $token"
```

The above command returns json structured like this:
```json
{
  "success": true,
  "movie": {
    "id": 1,
    "title": "My example movie",
    "release_date": "2022-05-01"
  }
}
```

#### Permission
`read:movie`
#### Raises
- **[404](#404)**
### Add Movie
#### Endpoint
`POST /movies`

#### Sample request
```shell script
curl http://localhost:8000/movies \
-X POST \
-H "Authorization: Bearer $token" \
-H 'Content-Type: application/json' \
-d '{"title": "Here goes rainbow...", "release_date": "2022-05-01"}'
```

The above command returns json structured like this:
```json
{
  "success": true,
  "movie": {
    "id": 1,
    "title": "My example movie",
    "release_date": "2022-05-01"
  }
}
```

#### Permission
`add:movie`
#### Raises
- **[422](#422)**
- **[400](#400)**
### Update Movie
#### Endpoint
`PATCH /movies/<int:pk>`

#### Sample request
```shell script
curl http://localhost:8000/movies/1 \
-X PATCH \
-H "Authorization: Bearer $token" \
-H 'Content-Type: application/json' \
-d '{"title": "Here goes rainbow...", "release_date": "2022-05-01"}'
```

The above command returns json structured like this:
```json
{
  "success": true,
  "movie": {
    "id": 1,
    "title": "My example movie",
    "release_date": "2022-05-01"
  }
}
```

#### Permission
`update:movie`
#### Raises
- **[404](#404)**
- **[422](#422)**
### Delete Movie
#### Endpoint
`DELETE /movies/<int:pk>`

#### Sample request
```shell script
curl http://localhost:8000/movies/1 \
-X DELETE \
-H "Authorization: Bearer $token"
```

The above command returns json structured like this:
```json
{
  "success": true,
  "movie": {
    "id": 1,
    "title": "My example movie",
    "release_date": "2022-05-01"
  }
}
```

#### Permission
`delete:movie`
#### Raises
- **[404](#404)**
- **[422](#422)**

## API Errors

### 400
Bad Request: Raised if some fields are missing in POST or PATCH requests or if they of invalid type

#### Response be like
```json
{
  "success": false,
  "error": 400,
  "message": "bad request"
}
```

### 403
Forbidden: Raised if you don't have enough permissions

#### Response be like
```json
{
  "success": false,
  "error": 403,
  "message": "forbidden"
}
```

### 404
Not Found: Raised if the given resource cannot be found

#### Response be like
```json
{
  "success": false,
  "error": 404,
  "message": "not found"
}
```

### 422
Unprocessable: Raised if database error occurred, e.g. foreign key constraint failed

#### Response be like
```json
{
  "success": false,
  "error": 422,
  "message": "unprocessable"
}
```

### 500
Internal Server Error: Raised if the server failed to fulfill the request

#### Response be like
```json
{
  "success": false,
  "error": 500,
  "message": "internal server error"
}
```

