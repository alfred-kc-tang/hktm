import os
import json

from flask import Flask, request, abort, jsonify, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_moment import Moment

from models import setup_db, Trademark, Spec
from auth import AuthError, requires_auth

'''
App Config
'''
# Create and configure the app
def create_app(test_config=None):
    app = Flask(__name__)
    moment = Moment(app)
    db = setup_db(app)
    #migrate = Migrate(app, db)

    # Set up CORS that allows any origins for the api resources
    cors = CORS(app, resources={r"/api/*": {"origin": "*"}})

    '''
    Access-Control-Allow headers and methods
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
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
    # Handle GET requests for all available trademarks
    @app.route('/trademarks', methods=['GET'])
    def get_trademarks():
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
        except:
            abort(404)

    # Handle GET requests for trademark details given application number
    @app.route('/trademarks/<string:app_no>', methods=['GET'])
    def get_trademark_class_details(app_no):
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
        except:
            abort(404)

    # Handle search on trademarks using POST endpoint
    @app.route('/trademarks/search', methods=['POST'])
    def search_trademarks():
        req = request.get_json()
        search_term = req.get('searchTerm')
        if search_term is None or search_term == '':
            abort(422)

        # Case-insensitive search term
        try:
            results = Trademark.query.filter(Trademark.name.ilike("%" + search_term + "%")).all()
            current_results = paginate_results(request, results)
            return jsonify({
                'success': True,
                'trademarks': current_results,
                'total_trademarks': len(results)
            }), 200
        except:
            abort(404)

    # Handle search on trademark specifications using POST endpoint
    @app.route('/trademark_specs/search', methods=['POST'])
    def search_trademark_specs():
        req = request.get_json()
        search_term = req.get('searchTerm')
        if search_term is None or search_term == '':
            abort(422)

        # Case-insensitive search term
        try:
            results = Spec.query.filter(Spec.class_spec.ilike("%" + search_term + "%")).all()
            if len(results) == 0:
                abort(404)
            current_results = paginate_results(request, results)
            return jsonify({
                'success': True,
                'class_numbers_and_specifications': current_results,
                'total_specifications': len(results)
            }), 200
        except:
            abort(500)

    # Handle PATCH requests for updating trademark info
    @app.route('/trademarks/<string:app_no>', methods=['PATCH'])
    @requires_auth('patch:trademark')
    def update_trademark(payload, app_no):
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
        except:
            abort(422)

    # Handle PATCH requests for updating trademark specification info
    @app.route('/trademark_specs/<int:id>', methods=['PATCH'])
    @requires_auth('patch:trademark_spec')
    def update_spec(payload, id):
        req = request.get_json()
        spec = Spec.query.filter(Spec.id == id).one_or_none()
        if not spec:
            abort(404)
        
        try:
            updated_class_no = req.get('class_no')
            updated_class_spec = req.get('class_spec')
            updated_tm_app_no = req.get('tm_app_no')
            updated_items = [updated_class_spec, updated_class_spec, updated_tm_app_no]
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
        except:
            abort(422)

    # Handle POST requests for inserting trademark info
    @app.route('/trademarks', methods=['POST'])
    @requires_auth('post:trademark')
    def add_trademark(payload):
        req = request.get_json()
        app_no = req.get('app_no')
        name = req.get('name')
        status = req.get('status')
        owners = req.get('owners')
        applicant = req.get('applicant')
        type = req.get('type')
        trademark_id = req.get('trademark_id')
        if app_no is None or name is None or status is None or owners is None:
            abort(422)
        
        try:
            trademark = Trademark(app_no=app_no, 
                                name=name, 
                                status=status, 
                                owners=owners, 
                                applicant=applicant,
                                type=type,
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
        except:
            abort(422)

    # Handle POST requests for inserting trademark specification info
    @app.route('/trademark_specs', methods=['POST'])
    @requires_auth('post:trademark_spec')
    def add_spec(payload):
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
        except:
            abort(422)

    # Handle DELETE requests for a given trademark
    @app.route('/trademarks/<string:app_no>', methods=['DELETE'])
    @requires_auth('delete:trademark')
    def delete_trademark(payload, app_no):
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
        except:
            abort(422)

    # Handle DELETE requests for a given trademark specification
    @app.route('/trademark_specs/<int:id>', methods=['DELETE'])
    @requires_auth('delete:trademark_spec')
    def delete_spec(payload, id):
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
        except:
            abort(422)

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