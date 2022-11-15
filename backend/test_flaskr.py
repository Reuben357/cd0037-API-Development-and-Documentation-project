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
        self.database_path = f"postgresql://postgres:password@localhost:5432/{self.database_name}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_categories_not_found(self):
        res = self.client().get('/category')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_add_question(self):
        new_question = {
            'question': 'How many eyes does a cow have',
            'answer': '2',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.load(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_add_question_not_found(self):
        new_question = {
            'question': 'How many eyes does a cow have',
            'answer': '2',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        question = Question(
            question='new question',
            answer='new answer',
            difficulty=1,
            category=1
        )
        question.insert()
        question_id = question.id
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions_per_category(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']), 1)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'], 'Entertainment')

    def test_questions_per_category_not_found(self):
        res = self.client().get('/categories/400/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_search(self):
        new_search = {'searchTerm': 'Who'}
        res = self.client().post('/search', json=new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_resource_not_found(self):
        search = {
            'searchTerm': 'when',
        }
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quizzes(self):
        new_quiz = {'previous_questions': [],
                    'quiz_category': {
                        'type': 'Entertainment',
                        'id': 5
                    }
                    }

        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_quizzes_not_found(self):
        new_quiz = {'previous_questions': [],
                    'quiz_category': {
                        'type': 'Entertainment',
                        'id': 5
                    }
                    }

        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
