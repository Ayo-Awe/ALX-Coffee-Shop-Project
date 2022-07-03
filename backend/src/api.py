from math import perm
import os
from flask import Flask, request, jsonify, abort
from pkg_resources import require
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''

#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=["GET"])
def get_drink():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]

        return jsonify({
            "success":True,
            "drinks": formatted_drinks,
        })
    except:
        abort(422)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail",methods=["GET"])
@requires_auth(permission="get:drink-details")
def get_drinks_details(jwt):
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success":True,
            "drinks":formatted_drinks
        })
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def create_new_drink(jwt):
    body = request.get_json()
    try:
        title = body.get("title",None)
        recipe = body.get("recipe",None)

        if(title == None or recipe == None):
            abort(400)
        
        json_recipe = json.dumps(recipe)
        drink = Drink(title=title,recipe=json_recipe)

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods = ["PATCH"])
@requires_auth("patch:drinks")
def update_drink(jwt,id):
    body = request.get_json()
    try:
        title = body.get("title",None)
        recipe = body.get("recipe",None)
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink == None:
            abort(404)
        
        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            "success":True,
            "drinks": [drink.long()]
        })

    except : 
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods = ["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink == None:
            abort(404)
        
        drink.delete()

        return jsonify({
            "success":True,
            "deleted": drink.id
        })
    
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

@app.errorhandler(AuthError)
def authentication_error(error):
    error_code = error.status_code
    error_message = error.error["description"]

    return jsonify({
        "success": False,
        "error": error_code,
        "message": error_message
    }),error_code


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
