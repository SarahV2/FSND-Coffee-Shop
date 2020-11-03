import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@(Done) uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
"""
# db_drop_and_create_all()


# ROUTES
"""
@(Done) implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and
    json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["GET"])
def get_drinks():
    drinks = Drink.query.all()
    # if len(drinks) == 0:
    #     abort(404)
    drinks = [drink.short() for drink in drinks]

    return jsonify({"success": True, "drinks": drinks}), 200


"""
@(Done) implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and
    json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_details(token):
    drinks = Drink.query.all()
    # if len(drinks) == 0:
    #     abort(404)
    drinks = [drink.long() for drink in drinks]

    return jsonify({"success": True, "drinks": drinks})


"""
@(Done) implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and
    json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drink(payload):
    error = False
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = json.dumps(body.get("recipe", None))
        if title is None or recipe is None:
            error = True
        else:
            newDrink = Drink(title=title, recipe=recipe)
            newDrink.insert()
    except:
        error = True
        print(sys.exc_info(), file=sys.stderr)
    if error:
        abort(400)
    return jsonify({"success": True, "drink": newDrink.long()})


"""
@(Done) implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200
    and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(token, drink_id):
    error = False
    try:
        drink = Drink.query.get(drink_id)
        body = request.get_json()
        updated_title = body.get("title", None)
        updated_recipe = json.dumps(body.get("recipe", None))
        if updated_title is not None:
            drink.title = updated_title
        if updated_recipe is not None:
            drink.recipe = updated_recipe
        drink.update()
    except:
        error = True
        print(sys.exc_info(), file=sys.stderr)
        abort(400)
    return jsonify({"success": True, "drinks": [drink.long()]})


"""
@(Done) implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200
    and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(token, drink_id):
    error = False
    try:
        drink = Drink.query.get(drink_id)
        id = drink.id
        drink.delete()
    except BaseException:
        error = True
        print(sys.exc_info(), file=sys.stderr)
        abort(404)
    return jsonify({"success": True, "delete": id})


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False,
                    "error": 422,
                    "message": "unprocessable"}), 422


"""
@(Done) implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""

"""
@(Done) implement error handler for 404
    error handler should conform to general task above
"""


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False,
                 "error": 404,
                 "message": "resource not found"}),
        404,
    )


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify({"success": False, "error": 400,
                 "message": "bad request"}),
        400,
    )


@app.errorhandler(500)
def internal_server_error(error):
    return (
        jsonify({"success": False, "error": 500,
                 "message": "internal server error"}),
        500,
    )


@app.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({"success": False, "error": 401,
                 "message": "unauthorized"}),
        401,
    )


"""
@(Done) implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def handle_auth_errors(error):
    return (
        jsonify({"success": False,
                 "error": error.status_code,
                 "message": error.error}),
        401,)
