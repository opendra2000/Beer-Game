import json
from flask import Blueprint, request, abort, request

from flask_expects_json import expects_json
bp = Blueprint('/player', __name__, url_prefix='/player') # I have to do this to avoid concurrency locks
from middleware import player_registered
from src.connection import connector
from main import Game

@bp.route('/current_game', methods=['GET'])
@player_registered
def get_players_game(player_id):
    id= connector.get_player_game(player_id)
    return json.dumps(id)

@bp.route('game/<id>', methods=['GET'])
@player_registered
def get_game(player_id, id):
    '''gets the information of a game instance. For now any instructor can access any game'''
    return json.dumps(connector.get_game(id))