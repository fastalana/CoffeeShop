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
The following line initializes the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    return jsonify({
        "success": True,
        "drinks": drinks
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    drinks = list(map(Drink.long, Drink.query.all()))
    return jsonify({
        "success": True,
        "drinks": drinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    body = request.get_json()

    if not ('title' in body and 'recipe' in body):
        abort(422)

    new_drink_title = body.get('title', None)
    new_drink_recipe = body.get('recipe', None)

    try:
        drink = Drink(title=new_drink_title, recipe=json.dumps(new_drink_recipe))
        drink.insert()

        return jsonify({
          'success': True,
          'drinks': [drink.long()]
        })
    
    except:
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
# @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
# @requires_auth('patch:drinks')
# def update_drink(token):


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
# @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
# @requires_auth('delete:drinks')
# def delete_drink(token):


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
    }, 404)

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code
