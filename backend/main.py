"""REST Server."""
from flask import Flask, request, abort, make_response
from flask_cors import CORS
from flask_expects_json import expects_json
from src.connection import connector
from src.constants import Role
from src.game_class import Game
import json
import instructor
import game_route
import player

app = Flask(__name__)
Game.conn = connector
app.register_blueprint(instructor.bp)
app.register_blueprint(game_route.bp)
app.register_blueprint(player.bp)
CORS(app)

# TODO: add the length for the password hash
schemas = {
    'authenticate': {
        'type': 'object',
        'properties': {
            'email': {
                'type': 'string',
                'format': 'email'
            },
            'passwordHash': {
                'type': 'string',
            }
        },
        'required': ['email', 'passwordHash']
    },
    'register': {
        'type': 'object',
        'properties': {
            'email': {
                'type': 'string',
                'format': 'idn-email'
            },
            'role': {
                'type': 'string',
                'pattern': '^(instructor|player)$'
            },
            'passwordHash': {
                'type': 'string',
            }
        },
        'required': ['email', 'role', 'passwordHash']
    }
}


@app.route('/authenticate', methods=['POST'])
@expects_json(schemas['authenticate'])
def authentication(name=None):
    """Verify player with name."""
    data = request.json
    user_id = connector.get_user(data['email'], data['passwordHash'])
    if not user_id:
        abort(400, 'Invalid user email or password.')
    token = connector.add_user_session(user_id)
    if not token:
        abort(500, 'could not create session token.')

    resp = make_response(json.dumps({"SESSION-KEY": token, "id": user_id}))
    resp.set_cookie('SESSION-KEY', token)
    return resp, 200


@app.route('/register', methods=['POST'])
@expects_json(schemas['register'])
def register_user():
    """Register User."""
    data = request.json
    role = Role.INSTRUCTOR if Role.INSTRUCTOR.value == data['role'] else Role.PLAYER
    user_id = connector.add_user(data['email'], data['passwordHash'], role)
    if not user_id:
        abort(400, 'Something went wrong while registering.')
    token = connector.add_user_session(user_id)
    if not token:
        abort(500, 'could not create user session token')
    resp = make_response(json.dumps({"SESSION-KEY": token, "id": user_id}))
    resp.set_cookie('SESSION-KEY', token)
    return resp, 200


@app.route('/')
def welcome():
    """Welcome."""
    return 'Welcome!'

if __name__ == '__main__':
    app.run(port=8086, host='0.0.0.0')
