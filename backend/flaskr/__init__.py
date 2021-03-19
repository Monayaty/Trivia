import os
from flask import Flask, request, abort, jsonify , redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json
import time
import datetime
import sys
from models import setup_db, Question, Category, db
from sqlalchemy import func


#paginate function
def paginate_questions(request, selection):
    page =  request.args.get('page', 1, type = int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start  + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


QUESTIONS_PER_PAGE = 10 # show 10 questions in page

def create_app(test_config=None):
  # create and configure the app
  #return the app
  app = Flask(__name__)
  setup_db(app)
  # setting it to * to allow all origins
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  # CORS(app)
  # cors = CORS(app, resources={r"*/*": {"origins": "*"}})
  # cors = CORS(app, resources={r"*": {"origins": "*"}})
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    #adding 'Access-Control-Allow' headers .. passing http response and returning modified http response
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    # response.headers['Access-Control-Allow-Origin'] = '*'
    return response

  #get categories function
  # def categories():
  #   categories = Category.query.order_by(Category.id).all()
  #   category = {category.id: category.type for category in categories}
  #   return category



  #creating endpoint for categories to handle GET requests
  @app.route('/categories')
  @cross_origin()
  def get_categories():
    Error =  False
    try:
        #query categories
        categories = Category.query.order_by(Category.id).all()
        get_category = {category.id: category.type for category in categories}
        # Count_categories = Category.query.order_by(category.id).count()
        #if there is no categories then abort with 404 error not found
        if get_category == 0:
              abort(404)
        #if len>0 show all categories
        return jsonify({#return json
            'success': True,#show message success with true
            'categories': get_category #return all categories
          })
    except:
        Error = True
        print(sys.exc_info())
        abort(500)


  #creating endpoint for getting categories and questions
  # @app.route('/')
  @app.route('/questions')
  @cross_origin()
  def index():
    Error = False
    try:
        #setting page
        page = request.args.get('page',1,type=int)
        #query questions
        questions = [question.format() for question in Question.query.all()]
        #query category
        categoryObject = {category.id: category.type for category in Category.query.all()}
        #setting start and end
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        #return json data
        return jsonify({
        'success': True,
        "questions": questions[start:end],
        "categories": categoryObject,
        "total_categories":len(categoryObject),
        "total_questions": len(questions)
        })
    except:
        error = True
        print(sys.exc_info())
        abort(422)

        # Delete question endpoint
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def deleteQuestion(question_id):
    Error = False
    #query the selected question to delete it
    deletedQuestion = Question.query.filter_by(id = question_id).one_or_none()
    try:
      if deletedQuestion is None:
        abort(404)
      else:
        deletedQuestion.delete()
        #return json data
        return jsonify({
          'success': True,
          'deleted' : question_id
        })
    except:
      Error = True
      print(sys.exc_info())
      db.session.rollback()
      abort(500)
    finally:
      db.session.close()
      # add question endpoint
  @app.route('/questions', methods = ['POST'])
  # @app.route('/add', methods=['POST'])
  def postQuestion():
      Error = False
      #declare myData object
      myData =  request.get_json()
      # get data from user input
      question = myData.get('question')
      category = myData.get('category')
      difficulty =myData.get('difficulty')
      answer = myData.get('answer')
      try:
        # addQuestion = Question(myData['question'], myData['category'], myData['difficulty'], myData['answer'])
        addQuestion = Question(question = question, answer = answer, category =  category, difficulty = difficulty)
        #insert the new QUESTION:
        addQuestion.insert()
        return jsonify({
          'success' : True
        })
      except:
        Error = True
        print(sys.exc_info())
        abort(500)

        #search endpoint
  @app.route('/questions/search', methods = ['POST'])
  def search_for_quesrion():
    print('searchterm')
    Error = False
    try:
        myData = request.get_json()
        search_term = myData.get('searchTerm')
        if search_term is None:
             abort(404)
        search = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
        paginated_questions = paginate_questions(request, search)

        return jsonify({
            "success": True,
            "questions": paginated_questions,
            "total-questions": len(paginated_questions),
            "current_category": None
        })
    except:
        Error = True
        print(sys.exc_info())
        abort(422)

        # getting questions by category endpoint
  @app.route('/categories/<string:category_id>/questions')
  def getQuestionsByCategoryId(category_id):
    Error = False
    try:
        page = request.args.get('page', 1 , type = int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        get_questions = Question.query.filter_by(category = category_id).order_by('id').all()
        questions = [question.format() for question in get_questions[start:end]]
        count_questions = len(questions)
        if count_questions == 0:
            abort(404)
        return jsonify({
            "success": True,
            "questions": questions,
        })
    except:
        Error = True
        print(sys.exc_info())
        abort(422)

        # game play endpoint
  # @app.route('/play', methods = ['POST'])
  @app.route('/quizzes', methods = ['POST'])
  def gamePlay():
        try:
            #declare myData object
            myData = request.get_json()
            #geting previous_question
            previous_questions = myData['previous_questions']
            #getting category as dict
            if isinstance(myData['quiz_category'], dict):
                quiz_category = myData['quiz_category']['id']
            else:
                quiz_category = myData['quiz_category']
            # to return all questions if category is all
            if quiz_category  == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()#all
            else:
                questions = Question.query.filter(Question.category == quiz_category, Question.id.notin_(previous_questions)).all()#only selected category
            # if len = 0  no category
            if len(questions) == 0:
                abort(404)
            #declaring random question
            random_question = random.choice(questions).format()
            if random_question:
                return jsonify({
                    "success": True,
                    "question": random_question #return random question

                })
        except Exception:
            abort(404)

#error handlers for all expected errors including 404 and 422.

  # error handler for 422 error "unprocessable"
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  #error handler for 404 error "not found"
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found"
      }), 404

  #error handler for 405 error "method not allowed"
  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "method not allowed"
      }), 405

  #error handler for 400 error "Bad request error"
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

  #error handler for 500 error "Server Error"
  @app.errorhandler(500)
  def internal_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "internal server error"
      }), 405


  #error handler for 409 error "conflict"
  # @app.errorhandler(409)
  # def conflict(error):
  #       return jsonify({
  #                   'code': 409,
  #                   'message': 'duplicated question',
  #                   'success': False
  #       }), 409

  return app
