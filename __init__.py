import os
import json

from flask import Flask, request, abort, jsonify, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from models import setup_db, Trademark, Spec

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    db = setup_db(app)
    migrate = Migrate(app, db)

    # Set up CORS that allows any origins for the api resources
    cors = CORS(app, resources={r"/api/*": {"origin": "*"}})

    # Set Access-Control-Allow headers and methods
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
				
    return app