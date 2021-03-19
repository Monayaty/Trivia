import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        print ("Your test passed")
        pass

    # Questions test
    def show_questions_in_exist_page_test(self):
        response = self.client().get('/questions?page=1')
        data = response.get_json()
        #  Status Code check
        self.assertEqual(response.status_code,200)
        # Check response
        self.assertTrue(data['success'])
        # check response data
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    #questions test in non exist page
    def show_questions_in_exist_page_test(self):
        response = self.client().get('/questions?page=1000')
        data = response.get_json()
        self.assertEqual(response.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'Resource Not Found')

    # Categories test
    def show_categories_test(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        #  Status Code check
        self.assertEqual(response.status_code, 200)
        # Check response
        self.assertEqual(data['success'], True)
        # Check if categories is in the response
        self.assertEqual(data['categories'])

    # Delete Questions Test
    def delete_questions_test(self):
        response = self.client().delete('/questions/1')
        data = json.loads(response.data)
        # Status Code check
        self.assertEqual(response.status_code, 200)
        # Check response
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'])

    # adding questions test
    def test_add_new_question_with_correct_parameters(self):
        response = self.client().post('/questions',json = {
            "question":"What year was the very first model of the iPhone released?",
            "answer": "2007",
            "category": 4,
            "difficulty": 2
            })
        data = response.get_json()
        # Status Code check
        self.assertEqual(res.status_code,200)
        # Check response
        self.assertTrue(data['success'])

    # search test
    def search_test(self):
        res = self.client().post('/questions/search', json = {
            "search_term":"title"
            })
        data = res.get_json()
        # Status Code check
        self.assertEqual(res.status_code,200)
        # Check response
        self.assertTrue(data['success'])
        # Check response data
        self.assertTrue(len(data['questions']))

    # Get qustions by category Test
    def get_questions_category_test(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        # Status Code check
        self.assertEqual(response.status_code, 200)
        # Check response
        self.assertEqual(data['success'], True)
        # Check response data
        self.assertEqual(data['questions'])

        # check random test
    def test_get_random_question_for_quiz(self):
        response = self.client().post("/quizzes", json = {
            "quiz_category": 4,
            "previous_questions": [12]
        })
        data  = response.get_json()
        # Check response
        self.assertTrue(data['success'])
        # Check data
        self.assertFalse(data['empty'])
        # Check response data
        self.assertTrue(data['question']['id'] != 12)

    # test error(404)
    def test_error(self):
        response = self.client().get('/categoriesnotNotFound')
        data = json.loads(response.data)
        # Status Code check
        self.assertEqual(response.status_code, 404)
        # Check respons
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
