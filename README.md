# Registered Trademarks in Hong Kong

The Intellecutal Property Department of Hong Kong Government has a website for the public to query its database with its GUI. However, its website does not have API that allows developers to obtain the data programmatically. Due to this lack of API, this web app is built with API that thus far has has the following functionalities:

1) Display trademarks
2) Display a specific trademark given its application number
3) Search for trademarks given a search term
4) Search for class specifications given a search term
5) Update a trademark given its application number
6) Update a class specification given its internal index in database
7) Add a trademark
8) Add a class specification
9) Delete a trademak given its application number
10) Delete a class specification given its internal index in database

## Data

As the file size exceeds 100MB limit of GitHub, the data is not available here.

## Tokens

The credentials are stored in the setup.sh file. Please run the following to save the credentials as environment variables:

```bash
source setup.sh
```

## Local Hosting

### Frontend

Current, this web app is built without a frondend.

### Backend

#### Key Dependencies

- [Flask](https://flask.palletsprojects.com/en/2.0.x/) is a lightweight backend microservices framework. Flask is required for handling requests and responses.
- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and Object Relational Mapper (ORM) for data modeling along with PostgreSQL.
- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/) is a Flask extension for handling cross origin requests.
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) is a Flask extension for handling SQLAlchemy database migrations for Flask applications using Alembic.
- [Flask-Moment](https://pypi.org/project/Flask-Moment/) is a Flask extension for enhancing Jinja2 templates with formatting of dates and times using moment.js.
- [Flask-Script](https://flask-script.readthedocs.io/en/latest/) is a Flask extension for supporting in writing extenal scripts in Flask applications.

#### Installing Dependencies

1. install dependencies by navigating to the `/backend` directory and running:

```bash
pip3 install -r requirements.txt
```

This will install all of the required packages selected within the `requirements.txt` file.

2. restore a database using the hktm.psql file downloaded. With Postgres running, run the following in terminal:

```bash
psql hktm < hktm.psql
```

3. save the credentials as environment variables:

```bash
source setup.sh
```

4. To run the server, execute:

On Linux:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

On Windows:
```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

Setting the `FLASK_APP` variable to `flask` directs flask to find the application `app.py`. 

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

## Hosting on Heroku

This app is hosted live on Heroku. The URL is https://hktm.herokuapp.com. Since there is no home page, please go to different endpoints instead. Here are the steps for deploying the app on Heroku:

1. modify the database path in models.py: comment out the code for connecting local database and use the code for connecting postgres database on Heroku

```bash
# Connect the local postgres database
# database_name = "hktm"
# database_path = "postgresql://{}/{}".format(
    "postgres@localhost:5432", database_name)

# Connect the postgres database on Heroku
database_path = "postgresql" + os.environ['DATABASE_URL'][8:]
```

2. create Heroku app

```bash
heroku create <app_name>
```

3. add git remote for Heroku to local repository

```bash
git remote add  heroku <heroku_git_url>
```

4. add postgresql add on for our database

```bash
heroku addons:create heroku-postgresql:hobby-dev --app <app_name>
```

5. check configuration variables in Heroku

```bash
heroku config --app <app_name>
```

6. push the code on Heroku

```bash
git push heroku master
```

7. run database migration script

```bash
heroku run python manage.py db upgrade --app <app_name>
```

You will then have the live application on Heroku!

## Third-Party Authentication

Auth0 is set up and running. The configurations are set in setup.sh file which exports the following:
1. Auth0 domain name
2. The JWT code signing secret
3. Auth0 client ID

## API Reference

### Introduction
* Base URL: This app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `localhost:5000` or `127.0.0.1:5000`, which is set as a proxy in the frontend configuration. The frondend is hosted at the port `3000`.
* Authentication: This version of the application requires authentication with the appropriate JWT Token.

### Roles and Permissions

|    Roles    |                       Permissions                         |
| ----------- | --------------------------------------------------------- |
| Public User |             [GET /trademarks](#get-trademarks)            |
|             |      [GET /trademarks/app_no](#get-trademarksapp_no)      |
|             |     [POST /trademarks/search](#post-trademarkssearch)     |
|             |[POST /trademark_specs/search](#post-trademark_specssearch)|
|    Editor   |    [PATCH /trademarks/app_no](#patch-trademarksapp_no)    |
|             |   [PATCH /trademark_specs/id](#patch-trademark_specsid)   |
|    Admin    |            [POST /trademarks](#post-trademarks)           |
|             |       [POST /trademark_specs](#post-trademark_specs)      |
|             |   [DELETE /trademarks/app_no](#delete-trademarksapp_no)   |
|             |  [DELETE /trademark_specs/id](#delete-trademark_specsid)  |

### Error Handling

Errors are returned as JSON objects in the following format

```bash
{
    "sucess": False,
    "error": 400,
    "message": "Bad Request"
}
```

The API will return four error types when requests fail:

* 400: Bad Request
* 404: Resource Not Found
* 422: Not Processable
* 500: Internal Server Error

### Endpoints

* [GET /trademarks](#get-trademarks)
* [GET /trademarks/app_no](#get-trademarksapp_no)
* [POST /trademarks/search](#post-trademarkssearch)
* [POST /trademark_specs/search](#post-trademark_specssearch)
* [PATCH /trademarks/app_no](#patch-trademarksapp_no)
* [PATCH /trademark_specs/id](#patch-trademark_specsid)
* [POST /trademarks](#post-trademarks)
* [POST /trademark_specs](#post-trademark_specs)
* [DELETE /trademarks/app_no](#delete-trademarksapp_no)
* [DELETE /trademark_specs/id](#delete-trademark_specsid)

The first 4 endpoints are publicly accessible. The PATCH endpoints on /trademarks and /trademark_specs requires the role of editor. The role of admin has all the permissions for the latter 6 endpoints. The credentials and API endpoints testing informaiton has been setup in the postman_collection.json.

#### GET /trademarks

- Fetches a list of trademarks with its unique trademark application number (app_no), trademark name (name), trademark owners (owners) and trademark application status (status), each as a JSON object
- Request Arguments: None 
- Sample Request: `curl http://127.0.0.1/trademarks`
- Response: a JSON object with the key "trademarks" that contains a list of objects of four key:value pairs - (1) app_no, (2) name, (3) owners and (4) status, as well as the "success" and "total_trademarks" keys.
- Sample Response:
```bash
{
    "success": true,
    "total_trademarks": 530591,
    "trademarks": [
        ...
        {
            "app_no": "18980004",
            "name": "BOVRIL",
            "owners": "['UNILEVER PLC']",
            "status": "Registered"
        },
        ...
    ]
}
```

#### GET /trademarks/app_no
- Fetches the details of a trademark containing its unique trademark application number (app_no), trademark name (name), trademark owners (owners) and trademark application status (status), trademark applicant (applicant), trademark application type (type), trademarks class(es), trademark application id (id) and the associated specifications (class_numbers_and_specifications), as well as the "success" key.
- Request Arguments: None
- Sample Request: `curl http://127.0.0.1/trademarks/19914141`
- Response: a JSON object with keys of app_no, name, owners, status, applicant, type, and class_numbers_and_specifications, which contains class_number:specifications as the key:value pair(s), as well as success.
- Sample Response:
```bash
{
    "app_no": "19914141",
    "applicant": null,
    "class_numbers_and_specifications": {
        "16": "stationery, paper, printed matter, manuals, catalogues, magazines, advertising material, decals, officer equisites all included in Class16;but not including any such goods relating to fruits."
    },
    "id": "632625_19914141",
    "name": "APPLE",
    "owners": "['Apple Inc.']",
    "status": "Registered",
    "success": true,
    "type": "Ordinary"
}
```

#### POST /trademarks/search
- Searches trademarks whose names contain the search term
- Request Argument: search term
- Sample Request: `curl --header "Content-Type: application/json" --request POST --data{"searchTerm": "apple"} http://127.0.0.1/trademarks/search`
- Reponse: a JSON object with the key "trademarks" that contains a list of objects of four key:value pairs - (1) app_no, (2) name, (3) owners and (4) status, as well as the "success" and "total_trademarks" keys.
- Sample Response:
```bash
{
    "success": true,
    "total_trademarks": 299,
    "trademarks": [
        ...
        {
            "app_no": "19831491",
            "name": "APPLE",
            "owners": "['Apple Inc.']",
            "status": "Registered"
        },
        ...
    ]
}
```

#### POST /trademark_specs/search
- Searches trademark specifications that contains the search term
- Request Argument: search term
- Sample Request: `curl --header "Content-Type: application/json" --request POST --data{"searchTerm": "apple"} http://127.0.0.1/trademark_specs/search`
- Reponse: a JSON object with the key "class_numbers_and_specifications" that contains a list of objects of four key:value pairs - (1) trademark class number (class_no), (2) trademark class specification (class_spec), (3) trademark specifcation id in the database (id), and (4) its associated trademark application number (tm_app_no), as well as the "success" and "total_specifications" keys.
- Sample Response:
```bash
{
    "class_numbers_and_specifications": [
        ...
        {
            "class_no": 31,
            "class_spec": "Fresh bananas;Fresh pineapple.",
            "id": 18327,
            "tm_app_no": "303924946"
        },
        ...
    ],
    "success": true,
    "total_specifications": 1115
}
```

#### PATCH /trademarks/app_no
- Modified the record of a given trademark, the fields that can be updated are: name, status, owners, applicant, type, and id
- Request Argument: trademark application number
- Sample Request: `curl --header "Content-Type: application/json" --request PATCH --data{"name": "apple", "status": "Expired"} http://127.0.0.1/trademarks/19831491`
- Reponse: a JSON object with the key "updated_trademark" that contains an object of seven key:value pairs - (1) app_no, (2) applicant, (3) name, (4) owners, (5) status, (6) id, and (7) type, as well as the "success" key.
- Sample Response:
```bash
{
    "success": true,
    "updated_trademark": {
        "app_no": "19831491",
        "applicant": null,
        "name": "apple",
        "owners": "['Apple Inc.']",
        "status": "Expired",
        "id": "612887_19831491"
        "type": "Ordinary"
    }
}
```

#### PATCH /trademark_specs/id
- Modified the record of a given trademark specification, the fields that can be updated are: trademark class number (class_no), trademark class specification (class_spec), its associated trademark application number (tm_app_no)
- Request Argument: trademark specification id in the database
- Sample Request: `curl --header "Content-Type: application/json" --request PATCH --data{"class_no": 30, "class_spec": "apple"} http://127.0.0.1/trademarks/915609`
- Reponse: a JSON object with the key "updated_spec" that contains an object of four key:value pairs - (1) class_no, (2) class_spec, (3) id, and (4) tm_app_no, as well as the "success" key.
- Sample Response:
```bash
{
    "success": true,
    "updated_spec": {
        "class_no": 30,
        "class_spec": "apple",
        "id": 915609,
        "tm_app_no": "305115159"
    }
}
```

#### POST /trademarks
- Posts a trademark
- Request Arguments: app_no, name, status and owners; applicant, type and trademark_id are optional
- Sample Request: `curl --header "Content-Type: application/json" --request POST --data{"app_no": "00000000", "name": "apple", "status": "Registered", "owners": "['Steve Jobs']", "trademark_id": "1234_00000000"} http://127.0.0.1/trademarks`
- Response: a JSON object with the key "trademarks" that contains a list of objects of four key:value pairs - (1) app_no, (2) name, (3) owners and (4) status, as well as the keys of "added_trademark_app_no", "total_trademarks" and "success".
- Sample Response:
```bash
{
    "added_trademark_app_no": "00000000",
    "success": true,
    "total_trademarks": 530592,
    "trademarks": [
        {
            "app_no": "00000000",
            "name": "apple",
            "owners": "['Steve Jobs']",
            "status": "Registered"
        },
        ...
    ]
}
```

#### POST /trademark_specs
- Posts a trademark specification
- Request Arguments: class_no, class_spec, tm_app_no
- Sample Request: `curl --header "Content-Type: application/json" --request POST --data{"class_no": 30, "class_spec": "apple", "tm_app_no": "19893299"} http://127.0.0.1/trademark_specs`
- Response: a JSON object with the key "specs" that contains a list of objects of four key:value pairs - (1) class_no, (2) class_spec, (3) id and (4) tm_app_no, as well as the keys of "added_spec_class_no", "total_specs" and "success".
- Sample Response:
```bash
{
    "added_spec_class_no": 30,
    "specs": [
        ...
        {
            "class_no": 38,
            "class_spec": "telecommunications;allincludedinClass38.",
            "id": 98,
            "tm_app_no": "PA200000844"
        },
        ...
    ]
    "success": true,
    "total_specs": 965654
}
```

#### DELETE /trademarks/app_no
- Deletes a trademark
- Request Arguments: app_no
- Sample Request: `curl DELETE http://127.0.0.1/questions/19801301`
- Response: a JSON object with the key "trademarks" that contains a list of remaining objects of four key:value pairs - (1) app_no, (2) name, (3) owners and (4) status, as well as the keys of "deleted_trademark_app_no", "total_trademarks" and "success".
- Sample Response:
```bash
{
    "deleted_trademark_app_no": "19801301",
    "success": true,
    "total_trademarks": 530591,
    "trademarks": [
        {
            "app_no": "00000000",
            "name": "apple",
            "owners": "['Steve Jobs']",
            "status": "Registerd"
        },
        ...
    ]
}
```

#### DELETE /trademark_spec/id
- Deletes a trademark specification
- Request Arguments: id
- Sample Request: `curl DELETE http://127.0.0.1/questions/310421`
- Response: a JSON object with the key "specs" that contains a list of objects of four key:value pairs - (1) class_no, (2) class_spec, (3) id and (4) tm_app_no, as well as the keys of "deleted_spec_class_no", "total_specs" and "success".
- Sample Response:
```bash
{
    "deleted_spec_id": 310421,
    "specs": [
        ...
        {
            "class_no": 38,
            "class_spec": "telecommunications;allincludedinClass38.",
            "id": 98,
            "tm_app_no": "PA200000844"
        },
        ...
    ]
    "success": true,
    "total_specs": 965652
}
```

## Testing

There are 22 unit tests in test.py. To test the API endpoints, please run the following:

```bash
dropdb hktm_test
createdb hktm_test
psql hktm_test < hktm.psql
python test.py
```

The tests include at least one test for expected success and error behavior for each endpoint using the unittest library. Moreover, the tests demonstrate role-based access control, attached with the JWT Tokens of (1) Editor and (2) Admin. Editor is permitted to access patch endpoints on trademarks and trademark specifications, so the JWT Token of Editor is given when testing the two endpoints; Admin is permitted to access post and delete endpoints on trademarks and trademark specifications, so the JWT Token of Admin is given when testing the four endpoints.
