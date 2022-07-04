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

@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def create_new_drink(jwt):
    body = request.get_json()
    try:
        title = body.get("title",None)
        recipe = body.get("recipe",None)

        if(title == None or recipe == None):
            abort(400)
        
        json_recipe = json.dumps([recipe])
        drink = Drink(title=title,recipe=json_recipe)

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except:
        abort(422)

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


@app.route("/drinks/<int:id>", methods = ["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt,id):
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

