import json
import sys
from flask_bcrypt import check_password_hash
from flask_httpauth import HTTPBasicAuth
import marshmallow
import sqlalchemy

sys.path.append('F:/bohdan/3_sem/PP_project/lab6')

from flask import Blueprint, jsonify, request, make_response
from lab7 import db_utils
from lab6.models import User, Transaction
from lab7.schemas import (
    UserData,
    GetUser,
    CreateUser,
    UserToUpdate,
    TransactionData,
    CreateTransaction,
)

errors = Blueprint('errors', __name__)
auth = HTTPBasicAuth()
api_blueprint = Blueprint('api', __name__)
STUDENT_ID = 1


def verify_password(username, password):
    user = db_utils.get_entry_by_username(User, username)
    if check_password_hash(user.password, password):
        return username
    return None


def admin_required(func):
    def wrapper(*args, **kwargs):
        username = auth.current_user()
        user = db_utils.get_entry_by_username(User, username)
        if user.isAdmin == '1':
            return func(*args, **kwargs)
        else:
            return StatusResponse(jsonify({"error": f"User must be an admin to use {func.__name__}."}), 401)

    wrapper.__name__ = func.__name__
    return wrapper


@errors.app_errorhandler(sqlalchemy.exc.NoResultFound)
def handle_error(error):
    response = {
        'code': 404,
        'error': 'Not found'
    }

    return jsonify(response), 404


@errors.app_errorhandler(KeyError)
def handle_error(error):
    response = {
        'code': 400,
        'error': str(error.args[0]) + 'isnt presented in keys, add it or check existed one'
    }

    return jsonify(response), 400


@errors.app_errorhandler(sqlalchemy.exc.IntegrityError)
def handle_error(error):
    response = {
        'code': 400,
        'error': 'Not enough data'
    }

    return jsonify(response), 400


@errors.app_errorhandler(marshmallow.exceptions.ValidationError)
def handle_error(error):
    response = {
        'code': 400,
        'error': str(error.args[0])
    }

    return jsonify(response), 400


def StatusResponse(response, code):
    param = response.json
    if isinstance(param, list):
        param.append({"code": code})
    else:
        param.update({"code": code})
    end_response = make_response(jsonify(param), code)
    return end_response


@api_blueprint.route("/hello-world")
def hello_world_def():
    return f"Hello world"


@api_blueprint.route(f"/hello-world-{STUDENT_ID}")
def hello_world():
    return f"Hello world {STUDENT_ID}"


@api_blueprint.route("/user", methods=["POST"])
def create_user():
    user_data = CreateUser().load(request.json)
    if db_utils.is_name_taken(User, user_data["username"]):
        return StatusResponse(jsonify({"error": "Username is already taken"}), 401)

    user = None
    if request.authorization is not None:
        username = request.authorization.username
        password = request.authorization.password
        user = verify_password(username, password)

    if (request.authorization is None or user is None
            or db_utils.get_entry_by_username(User, username).isAdmin == '0') and \
            'isAdmin' in user_data.keys() and user_data['isAdmin'] == '1':
        return StatusResponse(jsonify({"error": "Only admins can create other admins"}), 405)

    user = db_utils.create_entry(User, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)), 200)


@api_blueprint.route("/login")
@auth.verify_password
def login(username, password):
    user = db_utils.get_entry_by_username(User, username)
    if check_password_hash(user.password, password):
        return True

    return False


@api_blueprint.route("/user/<int:user_id>", methods=["GET"])
@auth.login_required
@admin_required
def get_user_by_id(user_id):
    user = db_utils.get_entry_by_uid(User, user_id)
    return StatusResponse(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route("/user/<int:user_id>", methods=["DELETE"])
@auth.login_required
@admin_required
def delete_user_by_id(user_id):
    user = db_utils.get_entry_by_uid(User, user_id)
    user_data = {"userStatus": "0", "username": "0"}
    db_utils.update_entry(user, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)), 200)


@api_blueprint.route("/user/self", methods=["GET", "DELETE", "PUT"])
@auth.login_required
def user_self():
    username = auth.current_user()
    user = db_utils.get_entry_by_username(User, username)
    selfid = user.id

    if request.method == "GET":
        user = db_utils.get_entry_by_uid(User, selfid)
        return StatusResponse(jsonify(UserData().dump(user)), 200)

    if request.method == "DELETE":
        user = db_utils.get_entry_by_uid(User, selfid)
        user_data = {"userStatus": "0", "username": "0"}
        db_utils.update_entry(user, **user_data)
        return StatusResponse(jsonify(UserData().dump(user)), 200)

    if request.method == "PUT":
        user_data = UserToUpdate().load(request.json)
        user = db_utils.get_entry_by_uid(User, selfid)
        db_utils.update_entry(user, **user_data)
        return StatusResponse(jsonify(GetUser().dump(user)), 200)


@api_blueprint.route("/user/replenish", methods=["PUT"])
@auth.login_required
def user_replenish():
    username = auth.current_user()
    user = db_utils.get_entry_by_username(User, username)
    selfid = user.id

    val = request.json['value']
    user = db_utils.get_entry_by_uid(User, selfid)
    user.wallet = user.wallet + val
    user_data = {"wallet": user.wallet}
    db_utils.update_entry(user, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)), 200)


@api_blueprint.route("/user/withdraw", methods=["PUT"])
@auth.login_required
def user_withdraw():
    username = auth.current_user()
    user = db_utils.get_entry_by_username(User, username)
    selfid = user.id

    val = request.json['value']
    user = db_utils.get_entry_by_uid(User, selfid)
    if (user.wallet - val) < 0:
        return StatusResponse(jsonify({"error": "user has not enough money to withdraw"}), 402)
    user.wallet = user.wallet - val
    user_data = {"wallet": user.wallet}
    db_utils.update_entry(user, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)), 200)


@api_blueprint.route("/transaction/<string:usernameto>", methods=["POST"])
@auth.login_required
def create_transaction(usernameto):
    username = auth.current_user()
    user = db_utils.get_entry_by_username(User, username)
    selfid = user.id

    userto = db_utils.get_entry_by_username(User, usernameto)
    useridto = userto.id

    param = request.json
    param.update({"sentByUser": selfid, "sentToUser": useridto, })
    paramjson = json.dumps(param)

    transaction_data = CreateTransaction().load(json.loads(paramjson))
    transaction = db_utils.create_entry(Transaction, **transaction_data)

    val = request.json['value']

    user1 = db_utils.get_entry_by_username(User, username)
    user2 = db_utils.get_entry_by_username(User, usernameto)

    if (user1.wallet - val) < 0:
        return StatusResponse(jsonify({"error": "user do not have enough money to send"}), 402)

    user1.wallet = user1.wallet - val
    user2.wallet = user2.wallet + val

    user_data1 = {"wallet": user1.wallet}
    user_data2 = {"wallet": user2.wallet}

    db_utils.update_entry(user1, **user_data1)
    db_utils.update_entry(user2, **user_data2)

    return jsonify(TransactionData().dump(transaction))


@api_blueprint.route("/transaction/sent", methods=["GET"])
@auth.login_required
def sent_transaction():
    username = auth.current_user()
    user = db_utils.get_entry_by_username(User, username)
    selfid = user.id

    transactions = db_utils.find_transactions_by_userid(selfid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)


@api_blueprint.route("/transaction/recieved", methods=["GET"])
@auth.login_required
def recieved_transaction():
    username = auth.current_user()
    user = db_utils.get_entry_by_username(User, username)
    selfid = user.id

    transactions = db_utils.find_transactions_to_userid(selfid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)


@api_blueprint.route("/transaction/sent/<string:username>", methods=["GET"])
@auth.login_required
@admin_required
def sent_transaction_username(username):
    user = db_utils.get_entry_by_username(User, username)
    uid = user.id
    transactions = db_utils.find_transactions_by_userid(uid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)


@api_blueprint.route("/transaction/recieved/<string:username>", methods=["GET"])
@auth.login_required
@admin_required
def recieved_transaction_username(username):
    user = db_utils.get_entry_by_username(User, username)
    uid = user.id
    transactions = db_utils.find_transactions_to_userid(uid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)
