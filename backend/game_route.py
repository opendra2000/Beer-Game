import json
from flask import Blueprint, request, abort, request
from src.constants import Game_Role
from flask_expects_json import expects_json
bp = Blueprint('/game', __name__, url_prefix='/game') # I have to do this to avoid concurrency locks
from middleware import player_registered, player_in_game
from src.connection import connector
from main import Game
schemas = {
    'join_game': {
        'type': 'object',
        'properties': {
            'role': { 
                'type': 'string',
                'enum': [i.value for i in Game_Role]
                    },

        },
        'required': ['role']
    },
    'round': {
        'type': 'object',
        'properties': {
            'order': {'type': 'integer'}
        },
        'required': ['order']
    }
}

@bp.route('/join/<game_id>', methods=['POST', 'PUT'])
@expects_json(schemas['join_game'])
@player_registered
def join_game(player_id, game_id):
    '''makes an authenticated player join a game instance identified by game_id'''
    req = request.json
    res = connector.add_player_to_game(player_id, game_id, Game_Role(req['role']))
    if not res:
        abort(400, "something went wrong with the request, please try a different role")
    return json.dumps({"success": True})

@bp.route('/game', methods=['POST', 'PUT'])
@player_in_game
def player_in_game_endpoint(player_id, game_id, role: Game_Role):
    '''an endpoint used for authentication testing, can be safely ignored'''
    return json.dumps({"success": True})

@bp.route('/round', methods=['GET'])
@player_in_game
def get_game_weeks(player_id, game_id, role: Game_Role):
    '''Returns week information for the player who requests it. This method will automatically provide all
    the information if the game instance has 'info_sharing' set as True.
    Returns: 
        weeks(list): A list of week JSON objects. This will show as much information as allowed by the game 
        parameters'''
    game = Game(game_id)

    weeks = game.get_weeks(role=role)
    return json.dumps(weeks)


@bp.route('/round', methods=['POST', 'PUT'])
@expects_json(schemas['round'])
@player_in_game
def send_info(player_id, game_id, role: Game_Role):
    req = request.json
    order = req['order']
    game = Game(game_id)
    res = game.set_player_order(role, order)
    return json.dumps({"success": res })