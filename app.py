import os
import json
import sys

from flask import (
    Flask,
    request,
    abort,
    jsonify,
    flash,
    render_template
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_moment import Moment

from models import setup_db, Trademark, Spec
from auth import AuthError, requires_auth

"""
App Config
"""


def create_app(test_config=None):
    """Create and configure the app."""
    app = Flask(__name__)
    moment = Moment(app)
    db = setup_db(app)
    migrate = Migrate(app, db)

    # Set up CORS that allows any origins for the api resources
    cors = CORS(app, resources={r"/api/*": {"origin": "*"}})

    '''
    Access-Control-Allow headers and methods
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    Results Pagination
    '''
    def paginate_results(request, results, num_results_per_page=100):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * num_results_per_page
        end = start + num_results_per_page

        results_lists = [result.format() for result in results]
        current_results = results_lists[start:end]

        return current_results

    '''
    Controllers
    '''
    @app.route('/trademarks', methods=['GET'])
    def get_trademarks():
        """Handle GET requests for all available trademarks.
        ---
        get:
            description: Get paginated trademarks info and its total number.
            responses:
                200:
                    description: a list of paginaged trademarks and the total
                        number of trademarks in the database.
                    trademarks: a list of trademarks objects with app_no, name,
                        status and owners.
                    total_trademarks: total number of trademarks.
                404:
                    description: trademarks not found.
        """
        try:
            trademarks = Trademark.query.order_by(Trademark.app_no).all()
            current_trademarks = paginate_results(request, trademarks)
            # Output 404 error if no more records in the current page
            if len(current_trademarks) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'trademarks': current_trademarks,
                'total_trademarks': len(trademarks)
            }), 200
        except Exception:
            abort(404)
            print(sys.exc_info())

    @app.route('/trademarks/<string:app_no>', methods=['GET'])
    def get_trademark_class_details(app_no):
        """Handle Get requests for trademark details given application number.
        ---
        get:
            description: Get a trademark given its application number.
            responses:
                200:
                    description: a trademark object to be returned.
                    trademark: a trademark object with more detailed info in
                        long format.
                404:
                    description: trademark not found.
        """
        try:
            trademark = Trademark.query.get(app_no)
            return jsonify({
                'success': True,
                'app_no': app_no,
                'name': trademark.name,
                'status': trademark.status,
                'owners': trademark.owners,
                'applicant': trademark.applicant,
                'type': trademark.type,
                'id': trademark.trademark_id,
                'class_numbers_and_specifications': {
                    spec.class_no: spec.class_spec for spec in trademark.specs
                }
            }), 200
        except Exception:
            abort(404)
            print(sys.exc_info())

    @app.route('/trademarks/search', methods=['POST'])
    def search_trademarks():
        """Handle search on trademarks using POST endpoint.
        ---
        post:
            description: Search trademarks whose names contain the search term.
            parameters:
                - name: searchTerm
                  type: string
                  required: true
            responses:
                200:
                    description: a list of paginated trademarks whose names
                        contain the search term, i.e. relevant trademarks.
                    trademarks: a list of trademarks objects with app_no, name,
                        status and owners.
                    total_trademarks: total number of the relevant trademarks.
                404:
                    description: relevant trademarks not found.
                422:
                    description: search term is None or empty.
        """
        req = request.get_json()
        search_term = req.get('searchTerm')
        if search_term is None or search_term == '':
            abort(422)

        # Case-insensitive search term
        try:
            results = Trademark.query.filter(Trademark.name.ilike(
                "%" + search_term + "%")).all()
            current_results = paginate_results(request, results)
            return jsonify({
                'success': True,
                'trademarks': current_results,
                'total_trademarks': len(results)
            }), 200
        except Exception:
            abort(404)
            print(sys.exc_info())

    @app.route('/trademark_specs/search', methods=['POST'])
    def search_trademark_specs():
        """Handle search on trademark specifications using POST endpoint.
        ---
        post:
            description: Search trademarks whose names contain the search term.
            parameters:
                - name: searchTerm
                  type: string
                  required: true
            responses:
                200:
                    description: a list of paginated trademarks specifcations
                        that contain the search term, i.e. relevant
                        specifications.
                    specs: a list of specification objects with id, class_no,
                        class_spec, and tm_app_no.
                    total_specs: total number of the relevant
                        specifications.
                404:
                    description: relevant specifications not found.
                422:
                    description: search term is None or empty.
        """
        req = request.get_json()
        search_term = req.get('searchTerm')
        if search_term is None or search_term == '':
            abort(422)

        # Case-insensitive search term
        try:
            results = Spec.query.filter(Spec.class_spec.ilike(
                "%" + search_term + "%")).all()
            current_results = paginate_results(request, results)
            return jsonify({
                'success': True,
                'specs': current_results,
                'total_specs': len(results)
            }), 200
        except Exception:
            abort(404)
            print(sys.exc_info())

    @app.route('/trademarks/<string:app_no>', methods=['PATCH'])
    @requires_auth('patch:trademark')
    def update_trademark(payload, app_no):
        """Handle PATCH requests for updating trademark info.
        ---
        patch:
            description: Update trademark specific info.
            security:
                - payload: decoded payload.
            parameters:
                - name: app_no
                  type: string
                  required: true
            responses:
                200:
                    description: updated trademark object to be returned.
                    updated_trademark: trademark object with more detailed info
                        in long format.
                404:
                    description: trademark not found.
                422:
                    description: update cannot be processed.
        """
        req = request.get_json()
        trademark = Trademark.query.filter_by(app_no=app_no).one_or_none()
        if not trademark:
            abort(404)

        try:
            updated_name = req.get('name')
            updated_status = req.get('status')
            updated_owners = req.get('owners')
            updated_applicant = req.get('applicant')
            updated_type = req.get('type')
            updated_id = req.get('trademark_id')
            updated_items = [updated_name, updated_status, updated_owners,
                             updated_applicant, updated_type, updated_id]
            if all(i is None for i in updated_items):
                abort(422)

            if updated_name:
                trademark.name = updated_name
            if updated_status:
                trademark.status = updated_status
            if updated_owners:
                trademark.owners = updated_owners
            if updated_applicant:
                trademark.applicant = updated_applicant
            if updated_type:
                trademark.type = updated_type
            if updated_id:
                trademark.trademark_id = updated_id

            trademark.insert()
            return jsonify({
                'success': True,
                'updated_trademark': trademark.long()
            }), 200
        except Exception:
            abort(422)
            print(sys.exc_info())

    @app.route('/trademark_specs/<int:id>', methods=['PATCH'])
    @requires_auth('patch:trademark_spec')
    def update_spec(payload, id):
        """Handle PATCH requests for updating trademark specification info.
        ---
        patch:
            description: Update specification info.
            security:
                - payload: decoded payload.
            parameters:
                - name: id
                  type: integer
                  required: true
            responses:
                200:
                    description: an updated specification object to be
                        returned.
                    updated_spec: a specifcation object with id, class_no,
                        class_spec, and tm_app_no.
                404:
                    description: specification not found.
                422:
                    description: update cannot be processed.
        """
        req = request.get_json()
        spec = Spec.query.filter(Spec.id == id).one_or_none()
        if not spec:
            abort(404)

        try:
            updated_class_no = req.get('class_no')
            updated_class_spec = req.get('class_spec')
            updated_tm_app_no = req.get('tm_app_no')
            updated_items = [updated_class_spec, updated_class_spec,
                             updated_tm_app_no]
            if all(i is None for i in updated_items):
                abort(422)

            if updated_class_no:
                spec.class_no = updated_class_no
            if updated_class_spec:
                spec.class_spec = updated_class_spec
            if updated_tm_app_no:
                spec.tm_app_no = updated_tm_app_no
            spec.insert()
            return jsonify({
                'success': True,
                'updated_spec': spec.format()
            }), 200
        except Exception:
            abort(422)
            print(sys.exc_info())

    @app.route('/trademarks', methods=['POST'])
    @requires_auth('post:trademark')
    def add_trademark(payload):
        """Handle POST requests for inserting a trademark record.
        ---
        post:
            description: Insert a trademark record.
            security:
                - payload: decoded payload.
            parameters:
                - name: app_no
                  type: string
                  required: true
                - name: name
                  type: string
                  required: true
                - name: status
                  type: string
                  required: true
                - name: owners
                  type: string
                  required: true
                - name: applicant
                  type: string
                  required: false
                - name: type
                  type: string
                  required: false
                - name: trademark_id
                  type: string
                  required: false
            responses:
                200:
                    description: inserted a trademark record.
                    added_trademark_app_no: the inserted trademark application
                        number.
                    trademarks: a list of trademarks objects with app_no, name,
                        status and owners.
                    total_trademarks: total number of trademarks.
                422:
                    description: insertion cannot be processed.
        """
        req = request.get_json()
        app_no = req.get('app_no')
        name = req.get('name')
        status = req.get('status')
        owners = req.get('owners')
        applicant = req.get('applicant')
        tm_type = req.get('type')
        trademark_id = req.get('trademark_id')
        if app_no is None or name is None or status is None or owners is None:
            abort(422)

        try:
            trademark = Trademark(app_no=app_no,
                                  name=name,
                                  status=status,
                                  owners=owners,
                                  applicant=applicant,
                                  type=tm_type,
                                  trademark_id=trademark_id)
            trademark.insert()
            trademarks = Trademark.query.order_by(Trademark.app_no).all()
            current_trademarks = paginate_results(request, trademarks)
            return jsonify({
                'success': True,
                'added_trademark_app_no': app_no,
                'trademarks': current_trademarks,
                'total_trademarks': len(trademarks)
            }), 200
        except Exception:
            abort(422)
            print(sys.exc_info())

    @app.route('/trademark_specs', methods=['POST'])
    @requires_auth('post:trademark_spec')
    def add_spec(payload):
        """Handle POST requests for inserting trademark specification record.
        ---
        patch:
            description: Insert a specification record.
            security:
                - payload: decoded payload.
            parameters:
                - name: class_no
                  type: integer
                  required: true
                - name: class_spec
                  type: string
                  required: true
                - name: tm_app_no
                  type: string
                  required: true
            responses:
                200:
                    description: inserted a trademark specification record.
                    added_spec_class_no: the inserted trademark specification
                        class number.
                    specs: a list of specification objects with id, class_no,
                        class_spec, and tm_app_no.
                    updated_spec: a specifcation object with id, class_no,
                        class_spec, and tm_app_no.
                    total_specs: total number of the specifications.
                422:
                    description: insertion cannot be processed.
        """
        req = request.get_json()
        class_no = req.get('class_no')
        class_spec = req.get('class_spec')
        tm_app_no = req.get('tm_app_no')
        if class_no is None or class_spec is None or tm_app_no is None:
            abort(422)

        try:
            spec = Spec(class_no=class_no,
                        class_spec=class_spec,
                        tm_app_no=tm_app_no)
            spec.insert()
            specs = Spec.query.order_by(Spec.id).all()
            current_specs = paginate_results(request, specs)
            return jsonify({
                'success': True,
                'added_spec_class_no': class_no,
                'specs': current_specs,
                'total_specs': len(specs)
            }), 200
        except Exception:
            abort(422)
            print(sys.exc_info())

    # Handle DELETE requests for a given trademark
    @app.route('/trademarks/<string:app_no>', methods=['DELETE'])
    @requires_auth('delete:trademark')
    def delete_trademark(payload, app_no):
        """Handle DELETE requests for deleting a trademark record.
        ---
        delete:
            description: Delete a trademark record.
            security:
                - payload: decoded payload.
            parameters:
                - name: app_no
                  type: string
                  required: true
            responses:
                200:
                    description: deleted a trademark record.
                    deleted_trademark_app_no: the application number of the
                        deleted trademark.
                    trademarks: a list of trademarks objects with app_no, name,
                        status and owners.
                    total_trademarks: total number of the relevant trademarks.
                404:
                    description: trademark not found.
                422:
                    description: deletion cannot be processed.
        """
        trademark = Trademark.query.filter_by(app_no=app_no).one_or_none()
        if not trademark:
            abort(404)

        try:
            trademark.delete()
            trademarks = Trademark.query.order_by(Trademark.app_no).all()
            current_trademarks = paginate_results(request, trademarks)
            return jsonify({
                'success': True,
                'deleted_trademark_app_no': app_no,
                'trademarks': current_trademarks,
                'total_trademarks': len(trademarks)
            }), 200
        except Exception:
            abort(422)
            print(sys.exc_info())

    @app.route('/trademark_specs/<int:id>', methods=['DELETE'])
    @requires_auth('delete:trademark_spec')
    def delete_spec(payload, id):
        """Handle POST requests for deleting a trademark specification record.
        ---
        patch:
            description: Delete a specification record.
            security:
                - payload: decoded payload.
            parameters:
                - name: id
                  type: integer
                  required: true
            responses:
                200:
                    description: deleted a trademark specification record.
                    deleted_spec_id: the deleted trademark specification id.
                    specs: a list of specification objects with id, class_no,
                        class_spec, and tm_app_no.
                    total_specs: total number of the specifications.
                404:
                    description: specification not found.
                422:
                    description: update cannot be processed.
        """
        spec = Spec.query.filter(Spec.id == id).one_or_none()
        if not spec:
            abort(404)

        try:
            spec.delete()
            specs = Spec.query.order_by(Spec.id).all()
            current_specs = paginate_results(request, specs)
            return jsonify({
                'success': True,
                'deleted_spec_id': id,
                'specs': current_specs,
                'total_specs': len(specs)
            }), 200
        except Exception:
            abort(422)
            print(sys.exc_info())

    '''
    Error Handlers
    '''
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': '400',
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': '404',
            'message': 'Not Found'
        }), 404

    @app.errorhandler(405)
    def not_allowed_error(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify({
            'success': False,
            'error': '422',
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': '500',
            'message': 'Internal Server Error'
        }), 500

    return app


# Initialize flask app
app = create_app()

if __name__ == '__main__':
    app.run()
