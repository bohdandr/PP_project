from flask import Flask
from wsgiref.simple_server import make_server

from blueprint import api_blueprint
from blueprint import errors

app = Flask(__name__)

with make_server('', 5000, app) as server:
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")
    app.register_blueprint(errors, url_prefix="")
    server.serve_forever()


# curl -v -XGET http://localhost:5000/api/v1/hello-world
# curl -v -XPOST http://localhost:5000/api/v1/user
# curl -v -XGET http://localhost:5000/api/v1/user/1

# {
#     "username": "beb",
#     "firstName": "b",
#     "lastName": "eb",
#     "email": "bebbeb@gmail.com",
#     "password": "qwerty",
#     "phone": "0672720544",
#     "birthDate": "2000-10-10",
#     "wallet": 5000,
#     "userStatus": 1
# }