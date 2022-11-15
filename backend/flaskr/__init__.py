import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS'
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        try:
            categories = Category.query.all()

            for category in categories:
                categories_data = {category.id: category.type}
                return jsonify({
                    'success': True,
                    'categories': categories_data
                })

        except Exception:
            abort(404)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():
        try:
            selected_questions = Question.query.order_by(Question.id).all()

            present_questions = paginate(request, selected_questions)
            categories = Category.query.all()
            data = {}
            for category in categories:
                data[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': present_questions,
                'total_questions': len(selected_questions),
                'categories': data,
                'current_category': None
            })

        except Exception:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):

        questions = Question.query.get(question_id)

        try:
            questions.delete()
            return jsonify({
                'success': True,
                'deleted_question': question_id
            })
        except Exception:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/add_questions", methods=['POST'])
    def new_question():
        build = request.get_json()

        add_question = build.get('question')
        answer_text = build.get('answer')
        category = build.get('answer')
        difficulty = build.get('difficulty')

        try:
            questions = Question(question=add_question,
                                 answer=answer_text,
                                 category=category,
                                 difficulty=difficulty)
            questions.insert()
            return jsonify({
                'success': True,
            })

        except BaseException:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/search', methods=['POST'])
    def question_search():
        build = request.get_json()
        search_term = build.get('searchTerm')

        if search_term is not None:
            questions = Question.query.filter(Question.question.ilike('%+search_term+%'.format(search_term)))
            questions_format = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": questions_format,
                "total_questions": len(questions_format)
            })
        else:
            abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def category_questions(category_id):

        try:
            questions = Question.query.filter_by(category=category_id)
            questions_format = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": questions_format,
                "current_category": category_id,
                "total_question": len(questions_format)
            })

        except Exception:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():

        build = request.get_json()
        previous_questions = build.get('previous_questions')
        category = build.get('quiz_category')

        if 'quiz_category' not in build or 'previous_questions' not in build:
            abort(422)

        question = []
        category = category['id']
        if category != 0:
            questions = Question.query.filter_by(category=category[0]).filter(Question.id not in previous_questions)

        else:
            questions = Question.query.filter(Question.id not in previous_questions)

        questions_format = [question.format() for question in questions]
        for question_id in questions_format:
            if question_id['id'] not in previous_questions and Question.query.filter():
                question.append(question_id)

        if question:
            random_question = random.choice(question)
            return jsonify({
                "success": True,
                "question": random_question,
            })
        else:
            return jsonify({
                "success": True,
            })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Something went wrong with the request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        })

    return app
