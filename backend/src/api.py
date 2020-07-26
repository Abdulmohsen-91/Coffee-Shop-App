import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()

        drinks_short = [drink.short() for drink in drinks]

        print(drinks_short)

        return jsonify({
            'success': True,
            'drinks': drinks_short
        })
    except:
        abort(404)



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    try:
        drinks = Drink.query.all()

        drinks_long = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drinks_long
        })
    except:
        abort(404)



@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()

    #title = 'testTitle'
    #recipe = 'testRecipe'

    title = body.get('title')
    recipe = body.get('recipe')

    if not title or not recipe:
        abort(422)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })

    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drink(jwt, id):

    drink = Drink.query.get(id)

    #print(drink)
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    if not drink:
        abort(404)

    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):

    drink = Drink.query.get(id)

    if not drink:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True, 'delete': id
        })
    except:
        abort(422)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
