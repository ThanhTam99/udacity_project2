import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.getenv('DATABASE_TEST_URL')
        setup_db(self.app, self.database_path)

        # Using app context to create all tables
        with self.app.app_context():
            db = SQLAlchemy()
            db.init_app(self.app)
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db = SQLAlchemy()
            db.init_app(self.app)
            db.drop_all()

    def test_get_categories(self):
        """Test GET /categories success"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['categories']), 0, "Categories should not be empty")

    def test_delete_question(self):
        """Test DELETE /questions/<id> success"""
        question = Question(question="Test question", answer="Test answer", category=1, difficulty=1)
        question.insert()
        question_id = question.id
        
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNone(question)

    def test_404_delete_question_that_does_not_exist(self):
        """Test DELETE /questions/<id> when id does not exist"""
        res = self.client().delete('/questions/123456')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_create_question(self):
        """Test POST /questions to create new question"""
        new_question = {
            'question': 'New question',
            'answer': 'New answer',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_422_create_question_with_missing_information(self):
        """Test POST /questions with missing information"""
        new_question = {
            'question': 'Incomplete question',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    def test_search_questions_with_results(self):
        """Test POST /questions/search with expected results"""
        search = {'searchTerm': 'title'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)

    def test_search_questions_without_results(self):
        """Test POST /questions/search without expected results"""
        search = {'searchTerm': 'xyz123'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 0)

    def test_get_questions_by_category(self):
        """Test GET /categories/<category_id>/questions for success"""
        # Sử dụng một category_id có sẵn. Ví dụ: 1 cho "Science"
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_404_get_questions_by_non_existing_category(self):
        """Test GET /categories/<category_id>/questions for a non-existing category"""
        res = self.client().get('/categories/9999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_play_quiz(self):
        """Test POST /quizzes to play the quiz with provided category and previous questions"""
        quiz_round = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': '1'}
        }
        res = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['question'])
        self.assertEqual(data['question']['category'], 1)

    def test_play_quiz_no_category(self):
        """Test POST /quizzes to play the quiz without specifying a category"""
        quiz_round = {
            'previous_questions': [],
            'quiz_category': {'type': 'click', 'id': 0}  # 'id': 0 meaning include all categories
        }
        res = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['question'])

    def test_404_play_quiz_with_invalid_category(self):
        """Test POST /quizzes with an invalid category id"""
        quiz_round = {
            'previous_questions': [],
            'quiz_category': {'type': 'Non-existing', 'id': '9999'}
        }
        res = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
