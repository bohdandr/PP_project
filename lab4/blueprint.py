import sys
from datetime import datetime

import marshmallow
import sqlalchemy

sys.path.append('F:/bohdan/3_sem/PP_project/lab6')

from flask import Blueprint, jsonify, request, make_response
from lab7 import db_utils
from lab6.models import User, Transaction
from lab7.schemas import(
	UserData,
    GetUser,
    CreateUser,
    UserToUpdate,
    TransactionData,
    CreateTransaction,
)

errors = Blueprint('errors', __name__)
api_blueprint = Blueprint('api', __name__)
STUDENT_ID = 1

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
    try:
        user_data=CreateUser().load(request.json)
        if db_utils.is_name_taken(User, user_data["username"]):
            return StatusResponse(jsonify({"error": "User with entered username already exists"}), 402)
    except marshmallow.ValidationError:
        return StatusResponse(jsonify({"error": "Validation error"}), 400)
    user=db_utils.create_entry(User,**user_data)
    return StatusResponse(jsonify(UserData().dump(user)),200)


@api_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = db_utils.get_entry_by_uid(User, user_id)
    return StatusResponse(jsonify(GetUser().dump(user)), 200)

@api_blueprint.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user_by_id(user_id):
    user = db_utils.get_entry_by_uid(User, user_id)
    user_data = {"userStatus": "0", "username": "0",
                 "firstName": "0", "lastName": "0", "email": "0",
                 "password": "0", "phone": "0",
                 "birthDate": "0-0-0", "wallet": 0, "user": 0}
    db_utils.update_entry(user, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)),200)

@api_blueprint.route("/user/self", methods=["GET","DELETE","PUT"])
def user_self():

    selfid=28

    if request.method=="GET":
        user=db_utils.get_entry_by_uid(User,selfid)
        return StatusResponse(jsonify(UserData().dump(user)),200)


    if request.method=="DELETE":
        user=db_utils.get_entry_by_uid(User,selfid)
        user_data={"userStatus":"0", "username": "0",
	"firstName": "0", "lastName": "0", "email": "0",
    "password": "0", "phone": "0",
    "birthDate": "0-0-0", "wallet": 0, "user":0}
        db_utils.update_entry(user,**user_data)
        return StatusResponse(jsonify(UserData().dump(user)),200)


    if request.method=="PUT":
        user_data=UserToUpdate().load(request.json)
        user=db_utils.get_entry_by_uid(User,selfid)
        db_utils.update_entry(user,**user_data)
        return StatusResponse(jsonify(GetUser().dump(user)),200)

@api_blueprint.route("/user/replenish", methods=["PUT"])
def user_replenish():
    selfid = 30
    val = request.json['value']
    user = db_utils.get_entry_by_uid(User, selfid)
    user.wallet=user.wallet+val
    user_data = {"wallet":user.wallet}
    db_utils.update_entry(user, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)),200)

@api_blueprint.route("/user/withdraw", methods=["PUT"])
def user_withdraw():
    selfid = 30
    val = request.json['value']
    user = db_utils.get_entry_by_uid(User, selfid)
    user.wallet = user.wallet - val
    user_data = {"wallet": user.wallet}
    db_utils.update_entry(user, **user_data)
    return StatusResponse(jsonify(UserData().dump(user)),200)


@api_blueprint.route("/transaction/<string:usrname>", methods=["POST"])
def create_transaction(usrname):
    user_name="beb8"

    transaction_data = CreateTransaction().load(request.json)
    transaction = db_utils.create_entry(Transaction, **transaction_data)
    transaction.datePerformed=datetime.today()

    val = request.json['value']

    user1 = db_utils.get_entry_by_username(User, user_name)
    user2 = db_utils.get_entry_by_username(User, usrname)

    if (user1.wallet-val)<0:
        return StatusResponse(jsonify({"error": "value of wallet must be positive"}), 402)
    user1.wallet = user1.wallet - val
    user2.wallet = user2.wallet + val


    user_data1 = {"wallet": user1.wallet}
    user_data2 = {"wallet": user2.wallet}
    db_utils.update_entry(user1, **user_data1)
    db_utils.update_entry(user2, **user_data2)


    return jsonify(TransactionData().dump(transaction))


    # userid1 = orderinfo.get('userId')
    # userid2 = orderinfo.get('classroomId')
    #
    # userData1=db_utils.get_entry_by_username(User,usrname)
    # userData2 = db_utils.get_entry_by_username(User, user_name)
    #
    #
    # datePerformed = request.json['datePerformed']
    # dt = datetime.strptime(datePerformed, "%Y-%m-%d %H:%M:%S")
    #
    # transaction = db_utils.get_entry_by_username(User, usrname)
    # db_utils.create_transaction(transaction, **transaction_data)
    # return jsonify(TransactionData().dump(transaction))

@api_blueprint.route("/transaction/sent", methods=["GET"])
def sent_transaction():
    selfid=24
    transactions = db_utils.find_transactions_by_userid(selfid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)

@api_blueprint.route("/transaction/recieved", methods=["GET"])
def recieved_transaction():
    selfid=25
    transactions = db_utils.find_transactions_to_userid(selfid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)


@api_blueprint.route("/transaction/sent/<string:usrname>", methods=["GET"])
def sent_transaction_username(usrname):
    user = db_utils.get_entry_by_username(User, usrname)
    uid=user.id
    transactions = db_utils.find_transactions_by_userid(uid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)

@api_blueprint.route("/transaction/recieved/<string:usrname>", methods=["GET"])
def recieved_transaction_username(usrname):
    user = db_utils.get_entry_by_username(User, usrname)
    uid = user.id
    transactions = db_utils.find_transactions_to_userid(uid)
    ans = [TransactionData().dump(x) for x in transactions]

    return StatusResponse(jsonify(ans), 200)








