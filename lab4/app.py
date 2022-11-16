from flask import Flask
from wsgiref.simple_server import make_server

from blueprint import api_blueprint
from blueprint import errors

app = Flask(__name__)

with make_server('', 5000, app) as server:
    app.debug = True
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")
    app.register_blueprint(errors, url_prefix="")
    server.serve_forever()
