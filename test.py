import os
import unittest
import json

from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Trademark, Spec

class HKTMTestCase(unittest.TestCase):
    """This class represents the Regmarkable website test case"""

    def setUp(self):
        """"Define test variables and intialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "hktm_test"
        self.database_path = "postgresql://{}/{}".format('postgres@localhost:5432', self.database_name)
        db = setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_trademarks(self):
        res = self.client().get('/trademarks')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['trademarks']))
        self.assertTrue(data['total_trademarks'])

    def test_404_requesting_beyond_valid_page(self):
        res = self.client().get('/trademarks?page=10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_trademark_with_app_no(self):
        res = self.client().get('/trademarks/19914141')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data)
        self.assertEqual(data['app_no'], '19914141')
        self.assertIsNotNone(data['name'])
        self.assertIsNotNone(data['class_numbers_and_specifications'])
    
    def test_get_trademark_with_nonexistent_app_no(self):
        res = self.client().get('/trademarks/0000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    def test_search_trademarks(self):
        res = self.client().post('/trademarks/search', json={'searchTerm': 'apple'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['trademarks']))
        self.assertTrue(data['total_trademarks'])
        
    def test_422_search_trademarks_without_search_term(self):
        res = self.client().post('/trademarks/search', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_search_trademark_specs(self):
        res = self.client().post('/trademark_specs/search', json={'searchTerm': 'apple'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['class_numbers_and_specifications']))
        self.assertTrue(data['total_specifications'])
    
    def test_422_search_trademark_specs_without_search_term(self):
        res = self.client().post('/trademark_specs/search', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_patch_trademark(self):
        res = self.client().patch('/trademarks/19831491', json={'name': 'apple', 'status': 'Expired'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated_trademark'])
    
    def test_404_patch_nonexistent_trademark(self):
        res = self.client().patch('/trademarks/0000000', json={'name': 'apple', 'status': 'Registered'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Not Found')
    
    def test_422_patch_trademark_without_info(self):
        res = self.client().patch('/trademarks/19831491', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_patch_trademark_spec(self):
        res = self.client().patch('/trademark_specs/915609', json={'class_no': 30, 'class_spec': 'apple'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated_spec'])
    
    def test_404_patch_nonexistent_trademark_spec(self):
        res = self.client().patch('/trademark_specs/99999999', json={'class_no': 30, 'class_spec': 'apple'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Not Found')

    def test_422_patch_trademark_spec_without_info(self):
        res = self.client().patch('/trademark_specs/915609', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_post_trademark(self):
        res = self.client().post('/trademarks', 
                                 json={'app_no': '00000000', 
                                       'name': 'apple', 
                                       'status': 'Registered', 
                                       'owners': '["Steve Jobs"]',
                                       'trademark_id': '1234_00000000'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added_trademark_app_no'], '00000000')
        self.assertTrue(len(data['trademarks']))
        self.assertTrue(data['total_trademarks'])
    
    def test_422_post_trademark_without_required_info(self):
        res = self.client().post('/trademarks', json={'app_no': '00000000'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_post_trademark_spec(self):
        res = self.client().post('/trademark_specs', 
                                 json={'class_no': 30, 
                                       'class_spec': 'apple',
                                       'tm_app_no': '19893299'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added_spec_class_no'], 30)
        self.assertTrue(len(data['specs']))
        self.assertTrue(data['total_specs'])
    
    def test_422_post_trademark_spec_without_required_info(self):
        res = self.client().post('/trademark_specs', json={'class_no': 30})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_delete_trademark(self):
        res = self.client().delete('/trademarks/19801301')
        data = json.loads(res.data)
        trademark = Trademark.query.filter(Trademark.app_no == '19801301').one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_trademark_app_no'], '19801301')
        self.assertIsNone(trademark)
        self.assertTrue(len(data['trademarks']))
        self.assertTrue(data['total_trademarks'])
    
    def test_404_delete_nonexistent_trademark(self):
        res = self.client().delete('/trademarks/0000000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    def test_delete_trademark_spec(self):
        res = self.client().delete('/trademark_specs/120310')
        data = json.loads(res.data)
        spec = Spec.query.filter(Spec.id == 120310).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_spec_id'], 120310)
        self.assertIsNone(spec)
        self.assertTrue(len(data['specs']))
        self.assertTrue(data['total_specs'])
    
    def test_404_delete_nonexistent_trademark_spec(self):
        res = self.client().delete('/trademark_specs/9999999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
