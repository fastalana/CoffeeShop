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
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except:
        abort(404)

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

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, id):
    drink = Drink.query.get(id)

    if drink:
        try:

            body = request.get_json()

            updated_drink_title = body.get('title', None)
            updated_drink_recipe = body.get('recipe', None)

            if updated_drink_title:
                drink.title = updated_drink_title
            if updated_drink_recipe:
                drink.recipe = updated_drink_recipe

            drink.update()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(422)
    else:
        abort(404)

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    try:
        if drink is None:
            abort(404)
        
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        })
    
    except:
        abort(422)

## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False, 
        'error': 422,
        'message': 'unprocessable'
    }, 422)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }, 404)

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        'success': False,
        'error': e.status_code,
        'message': e.error
    }, 401)
