import json
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_helper import not_found
import random
from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app, test_config.get("SQLALCHEMY_DATABASE_URI") if test_config else None)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )

        return response
    
    @app.errorhandler(HTTPException)
    def handle_exceptions(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        response.data = json.dumps({
            "success": False
        })
        response.content_type = "application/json"

        return response

    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        return questions[start:end]

    @app.route("/categories")
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {category.id: category.type for category in categories}
        return jsonify({"success": True, "categories": formatted_categories})

    @app.route("/questions")
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {category.id: category.type for category in categories}
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": formatted_categories,
                "current_category": None,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                return not_found()
            question.delete()
            return jsonify({"success": True, "deleted": question_id})
        except:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        if not (
            "question" in body
            and "answer" in body
            and "difficulty" in body
            and "category" in body
        ):
            abort(422)
        try:
            question = Question(
                question=body.get("question"),
                answer=body.get("answer"),
                difficulty=body.get("difficulty"),
                category=body.get("category"),
            )
            question.insert()
            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                }
            )
        except:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", "")
        selection = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        current_questions = paginate_questions(request, selection)
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
            }
        )

    @app.route("/categories/<int:category_id>/questions")
    def retrieve_questions_by_category(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        if category is None:
            return not_found()
        selection = Question.query.filter(Question.category == str(category_id)).all()
        current_questions = paginate_questions(request, selection)
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "current_category": category.type,
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get("previous_questions", [])
        quiz_category = body.get(
            "quiz_category", {"type": "click", "id": 0}
        )
        try:
            if quiz_category["id"] == 0:
                available_questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()
            else:
                # Just to check category is exist or not
                category = Category.query.filter(
                    Category.id == str(quiz_category["id"])
                ).first()

                if category is None:
                    return not_found()
                
                available_questions = (
                    Question.query.filter_by(category=quiz_category["id"])
                    .filter(Question.id.notin_(previous_questions))
                    .all()
                )

            if not available_questions:
                return jsonify({"success": True, "question": None})

            new_question = random.choice(available_questions).format()
            return jsonify({"success": True, "question": new_question})
        except:
            abort(422)

    return app
