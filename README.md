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

# Installation

## Frontend

Current, this web app is built without a frondend.

## Backend

### Installing Dependencies

1. First install dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages selected within the `requirements.txt` file.

2. Then restore a database using the hktm.psql file given. With Postgres running, run the following in terminal:

```bash
psql hktm < hktm.psql
```

3. To run the server, execute:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Setting the `FLASK_APP` variable to `flask` directs flask to find the application `app.py`. 

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

# API Reference

## Introduction
* Base URL: This app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `localhost:5000` or `127.0.0.1:5000`, which is set as a proxy in the frontend configuration. The frondend is hosted at the port `3000`.
* Authentication: This version of the application requires authentication or API keys.

## Error Handling

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

## Endpoints

* [GET /trademarks](#get-/trademarks)
* [GET /trademarks/app_no](#get-/trademarks/<app_no>)
* [POST /trademarks/search](#post-/trademarks/search)
* [POST /trademark_specs/search](#post-/trademark_specs/search)
* [PATCH /trademarks/app_no](#patch-/trademarks/<app_no>)
* [PATCH /trademark_specs/id](#patch-/trademark_specs/id)
* [POST /trademarks](#post-/trademarks)
* [POST /trademark_specs](#post-/trademark_specs)
* [DELETE /trademarks/app_no](#delete-/trademarks/<app_no>)
* [DELETE /trademark_specs/id](#delete-/trademark_specs/id)

### GET /trademarks

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

## GET /trademarks/app_no
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

## POST /trademarks/search
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

## POST /trademark_specs/search
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

## PATCH /trademarks/app_no
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

## PATCH /trademark_specs/id
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

## POST /trademarks
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

## POST /trademark_specs
- Posts a trademark specification
- Request Arguments: class_no, class_spec, tm_app_no
- Sample Request: `curl --header "Content-Type: application/json" --request POST --data{"class_no": 30, "class_spec": "apple", "tm_app_no": "19893299"} http://127.0.0.1/trademark_specs`
- Response: a JSON object with the key "trademarks" that contains a list of objects of four key:value pairs - (1) app_no, (2) name, (3) owners and (4) status, as well as the keys of "added_trademark_app_no", "total_trademarks" and "success".
- Sample Response:
```bash
{
    "created_question": "22",
    "success": true
}
```

## DELETE /trademarks/app_no
- Deletes a trademark
- Request Arguments: app_no
- Sample Request: `curl DELETE http://127.0.0.1/questions/19801301`
- Response: a JSON object with keys of success and deleted_question indicating the removed question id
- Sample Response:
```bash
{
    "deleted_question": "21",
    "success": true
}
```

## DELETE /trademark_spec/id
- Deletes a trademark specification
- Request Arguments: id
- Sample Request: `curl DELETE http://127.0.0.1/questions/310421`
- Response: a JSON object with keys of success and deleted_question indicating the removed question id
- Sample Response:
```bash
{
    "deleted_question": "21",
    "success": true
}
```

# Testing

To run the unit tests, run

```
dropdb hktm_test
createdb hktm_test
psql hktm_test < hktm.psql
python test.py
```
