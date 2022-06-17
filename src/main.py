"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Task
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route("/task", methods=["POST"])
def create_task():
    body = request.get_json()

    task = Task(text=body["text"], done=False)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.serialize())


@app.route('/task', methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    all_tasks = list(map(lambda task: task.serialize(), tasks))

    return jsonify(all_tasks)


@app.route('/task/<int:task_id>', methods=["PUT", "GET", "DELETE"])
def handle_task(task_id):
    if request.method == "PUT":
        task = Task.query.get(task_id)
        if task is None:
            raise APIException("Tarea No Encontrada", 404)
        body = request.get_json()

        if not ("done" in body):
            raise APIException("parametro done no encontrado", 404)
        task.done = body["done"]
        db.session.commit()

        return jsonify(task.serialize())

    elif request.method == "GET":
        task = Task.query.get(task_id)
        if task is None:
            raise APIException("Tarea No Encontrada", 404)

        return jsonify(task.serialize())

    elif request.method == "DELETE":
        task = Task.query.get(task_id)
        if task is None:
            raise APIException("Tarea No Encontrada", 404)
        db.session.delete(task)
        db.session.commit()
        return jsonify(task.serialize())


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)