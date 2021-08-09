"""Handle instructor querries."""
import json
from flask import Blueprint, request, abort, request

from flask_expects_json import expects_json
bp = Blueprint('/instructor', __name__, url_prefix='/instructor') # I have to do this to avoid concurrency locks
from middleware import instructor_registered
from src.connection import connector
from main import Game
schemas = {
    'game': {
        'type': 'object',
        'properties': {
#            'instructor_id': {  'type': 'number' }, CAUSES A VULNERABILITY
            'session_length': { 'type': 'number' },
            'active': { 'type': 'boolean' },
            'wholesaler_present': { 'type': 'boolean' },
            'retailer_present': { 'type': 'boolean' },
            'demand_pattern_id': {' type': 'number' },
            'info_delay': { 'type': 'number' },
            'info_sharing': { 'type': 'boolean' },
            'holding_cost': { 'type': 'number' },
            'backlog_cost': { 'type': 'number' }
        },
        'required': []
    },
    'modify': {
        'type': 'object',
        'properties': {
            'session_length': { 'type': 'number' },
            'active': { 'type': 'boolean' },
            'wholesaler_present': { 'type': 'boolean' },
            'retailer_present': { 'type': 'boolean' },
            'info_delay': { 'type': 'number' },
            'info_sharing': { 'type': 'boolean' },
            'holding_cost': { 'type': 'number' },
            'backlog_cost': { 'type': 'number' }
        },
        'required': []
    },
    'demand_pattern': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'encoded_data': {'type': 'string'},
        },
        'required': ["encoded_data"]
    },
    'player': {
        'type': 'object',
        'properties': {
            'factory_id': {'type': 'number'},
            'distributor_id': {'type': 'number'},
            'wholesaler_id': {'type': 'number'},
            'retailer_id': {'type': 'number'},
            'game_id': {'type': 'number'},
        },
        'required': ["factory_id", "distributor_id", "wholesaler_id", "retailer_id",  "game_id"]
    },
    'delete_player': {
        'type': 'object',
        'properties': {
            'player_id': {'type': 'number'},
        },
        'required': ["player_id"]
    }
}

def parse_schema(input, schema):
    res = {}
    for i in schema:
        if i in input:
            res[i] = input[i]
    return res

@bp.route('game', methods=['POST'])
@expects_json(schemas['game'])
@instructor_registered
def create_game(ins_id):
    """Create a game."""
    data = request.json
    # create game with 
    g_id = connector.create_game(ins_id, **{i:data[i] for i in data if (i in schemas['game']['properties'] )})
    if not g_id:
        abort(400, 'an unexpected error occurred')
    return json.dumps({"game_id": g_id})

@bp.route('game', methods=['GET'])
@instructor_registered
def get_ins_games(ins_id):
    """get all games related to an instructor"""
    games = connector.get_instructor_games(ins_id)
    return json.dumps(games)

@bp.route('game/<id>', methods=['GET'])
@instructor_registered
def get_game(ins_id, id):
    '''gets the information of a game instance. For now any instructor can access any game'''
    return json.dumps(connector.get_game(id))

@bp.route('get_players', methods=['GET'])
@instructor_registered
def get_all_players(ins_id):
    '''gets the information for all players in the User table'''
    return json.dumps(connector.get_players(ins_id))

@bp.route('get_players_table', methods=['GET'])
@instructor_registered
def get_all_players_table(ins_id):
    '''gets the information for all players in the Player table'''
    return json.dumps(connector.get_players_table(ins_id))

@bp.route('modify_game/<game_id>', methods=['PUT'])
@expects_json(schemas['modify'])
@instructor_registered
def modify_game(ins_id, game_id):
    '''modifies a game instance owned by an instructor'''
    games = connector.get_instructor_games(ins_id)
    if int(game_id) not in [int(i['id']) for i in games]:
        abort(405, 'instructor is not allowed to modify this game')
    req = request.json
    req = parse_schema(req, schemas['modify']['properties'])
    g = Game(game_id)
    res = g.modify_game(req)
    return json.dumps(res)


@bp.route('/demand_patterns', methods=['GET'])
def get_demand_patterns():
    return json.dumps(connector.get_demand_patterns())

@bp.route('/add_demand_patterns', methods=['POST'])
@expects_json(schemas['demand_pattern'])
def add_demand_patterns():
    '''adds a demand pattern to the DemandPattern table and return its id'''
    req = request.json
    req = parse_schema(req, schemas['demand_pattern']['properties'])
    a = json.dumps(req["encoded_data"])
    print(a)
    id = connector.add_demand_pattern(a, req["name"])
    return json.dumps({"demand_pattern": id})

@bp.route('/add_player_to_game', methods=['POST'])
@expects_json(schemas['player'])
@instructor_registered
def add_players_to_game(ins_id):
    '''adds a player to Player table and update the game table'''
    req = request.json
    req = parse_schema(req, schemas['player']['properties'])
    print(req)
    id1 = connector.add_player_to_game(req["factory_id"], req["game_id"], "factory")
    id2 = connector.add_player_to_game(req["distributor_id"], req["game_id"], "distributor")
    if(req["wholesaler_id"] != 0):
        id3 = connector.add_player_to_game(req["wholesaler_id"], req["game_id"], "wholesaler")
    if(req["retailer_id"] != 0):
        id3 = connector.add_player_to_game(req["retailer_id"], req["game_id"], "retailer")
    return json.dumps({"success_factory": id1, "success_distributor": id2})

@bp.route('/delete_player_from_player_table', methods=['DELETE'])
@expects_json(schemas['delete_player'])
def delete_players_from_player_table():
    req = request.json
    req = parse_schema(req, schemas['delete_player']['properties'])
    id= connector.delete_player_from_player_table(req["player_id"])
    return json.dumps({"player_id": id})

@bp.route('/get_players_not_playing', methods=['GET'])
@instructor_registered
def get_player_not_playing(ins_id):
    players= connector.get_players_not_playing(ins_id)
    return json.dumps(players)

@bp.route('/check_instructor', methods=['GET'])
@instructor_registered
def check_instructor(ins_id):
    return json.dumps({"success": "true"})