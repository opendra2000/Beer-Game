import os.path
import secrets
import os
from dotenv import load_dotenv
import sqlite3
import mariadb
import logging
from .constants import Role, Game_Role
from .connection import Connector

class Game:
    conn = None
    def __init__(self, game_id):
        '''
        Args:
            game_id(int): the game id to build the Game object from and query the database
        '''
        self.game = self.conn.get_game(game_id)
        if self.conn.get_current_game_week(game_id) is None:
            self.create_default_week(0)

    def create_default_week(self, week_number: int):
        '''creates a default week (IE using default values for incoming and outgoing'''
        self.conn.add_game_week(self.game['id'], week_number, None)


    def round_is_ready(self):
        '''returns whether a game is ready to play a new round
        Args:
            game_id(int): the specified game id
        Returns
            success(bool): whether the round is ready'''
        game = self.game
        #TODO refactor this into comprehensive reasons why round is not ready
        if bool(game['active']) is not True:
            #print('game is not active!!')
            return False
        current_week = self.conn.get_current_game_week(game['id'])
        for role in self._get_game_roles_active_in_game():
            if current_week[f'{role.value}_order'] is None:
                #print(f'{role.value} IS NOT READY!!')
                return False
        return True
        
    def _get_game_roles_active_in_game(self):
        '''Returns a list containing the Roles that are active in a game instance
        Args: 
        Returns:
            roles(list: Game_Role): a list of Game_Role objects in the current game instance'''
        roles = [Game_Role.DISTRIBUTOR, Game_Role.FACTORY]
        game_dict = self.game
        if bool(game_dict['retailer_present']) is True:
            roles.append(Game_Role.RETAILER)
        if bool(game_dict['wholesaler_present']) is True:
            roles.append(Game_Role.WHOLESALER)
        return roles

    def _get_demand_pattern_week( self, week):
        """gets the demand for a given week
        args: 
            week(int): the desired week
        returns:
            demand(int): the demand for the given week, 4 is returned if the demand pattern is not large enough"""
        
        demand_pattern = self.conn.get_demand_pattern(self.game['demand_pattern_id'])
        if len(demand_pattern['encoded_data']) < week:
            return 4
        else:
            return demand_pattern['encoded_data'][week]

    def _get_demand (self, game_week_dict: dict, role: Game_Role):
        """Gets the demand from a required week, the week_dict is the (delayed) week dictionary from which each demand is extracted
        Args:
            game_week_dict(dict): a connection.get_game_week dictionary object, it should be
        AT LEAST the delay period before the current week. if None is provided, a default_demand() v
        alue will be used (this is the value that is used during the start of the week). By construction the first few weeks
        will have a constant demand of 4 for all players
            role(Game_Role): the game role that you wish to get the demand for
        """

        def default_demand():
            return 4


        def factory_demand():
            if self.game['wholesaler_present']:
                return game_week_dict['wholesaler_order'] 
            else:
                return wholesaler_demand()
        def wholesaler_demand():
            return game_week_dict['distributor_order'] 
        
        def distributor_demand():
            if self.game['retailer_present']:
                return game_week_dict['retailer_order'] 
            else:
                return retailer_demand()

        def retailer_demand():
            return self._get_demand_pattern_week(game_week_dict['week'] + self.game['info_delay'])

        if not game_week_dict:
            return default_demand()

        hashtable = {
            Game_Role.FACTORY: factory_demand,
            Game_Role.WHOLESALER: wholesaler_demand,
            Game_Role.DISTRIBUTOR: distributor_demand,
            Game_Role.RETAILER: retailer_demand
        }
        return hashtable[role]()
        
    def _get_incoming_order(self, game_week_dict: dict, role: Game_Role):
        """Gets the incoming order for the week after game_week's delay
        Args:
            game_week(dict): a connection.get_game_week dictionary object, it should be
        AT LEAST the delay period before the current week. if None is provided, a default value will be used
            role(Game_Role): the game role that you wish to get the demand for
        """
        def default_incoming():
            return 4

        def factory_incoming():
            return game_week_dict['factory_order']

        def wholesaler_incoming():
            return game_week_dict['factory_outgoing']
        
        def distributor_incoming():
            if self.game['wholesaler_present']:
                return game_week_dict['wholesaler_outgoing']
            else:
                return wholesaler_incoming()
        def retailer_incoming():
            return game_week_dict['distributor_outgoing']

        if not game_week_dict:
            return default_incoming()

        hashtable = {
            Game_Role.FACTORY: factory_incoming,
            Game_Role.WHOLESALER: wholesaler_incoming,
            Game_Role.DISTRIBUTOR: distributor_incoming,
            Game_Role.RETAILER: retailer_incoming
        }
        return hashtable[role]()

    def get_inventory_cost(self, inventory: int):
        '''returns the cost associated with an inventory number. A negative inventory is a backlog, positive inventory is storage
        args:
            inventory(int): the current inventory that we want to get the cost for. Negative inventory means backlog
        '''
        if inventory < 0:
            return abs(inventory * self.game['backlog_cost'])
        else:
             return inventory * self.game['holding_cost']

    def _play_game_round(self):
        '''plays a game round. This method is protected so it only be called from inside the class
        when a new round is ready to be played. it calculates the demand, cost, inventory,  etc values for each of the
        roles present in the game. note that a NEGATIVE INVENTORY denotes a backlog'''
        game_id = self.game['id']
        current_week = self.conn.get_current_game_week(game_id)
        delay_week = current_week['week'] - self.game['info_delay']
        desired_week = self.conn.get_game_week(game_id, delay_week)
        new_week = {}
        for role in self._get_game_roles_active_in_game():
            
            incoming = self._get_incoming_order(desired_week, role)
            previous_inventory = current_week[f'{role.value}_inventory']    
            # calculate demand for the current week
            demand = self._get_demand(desired_week, role)
            backlogged_demand = abs(previous_inventory) if previous_inventory < 0 else 0
            demand = demand + backlogged_demand

            inventory_brutto = previous_inventory + incoming
            
            # case: we are still backlogged: this means that
            # our inventory is negative, so our backlog is equal to outgoing minus total demand
            if previous_inventory <= 0:
                outgoing = incoming
                inventory = outgoing - demand
            # "normal" case: the inventory was positive, no backlog cost calculation necessary
            else:
                
                inventory = inventory_brutto - demand
                outgoing = min(inventory_brutto, demand)

            prev_cost = current_week[f'{role.value}_cost']
            if not prev_cost:
                prev_cost = 0.0
            cost = self.get_inventory_cost(inventory)+ prev_cost
        #    DEBUG output for each role

            # if role == Game_Role.FACTORY:
            #     print("week: {}".format(current_week['week']))
            #     print("incoming: "+str(incoming))
            #     print("previous_inventory: " + str(previous_inventory))
            #     print('inventory_brutto: '+str(inventory_brutto))
            #     print("demand: "+str(demand))
            #     print("inventory: " + str(inventory))
            #     print("outgoing: "+str(outgoing))
            #     print("cost: " + str(cost) )
            #     print("order(last): "+str(current_week[f'{role.value}_order']))
            #     print("\n")

            new_week[f'{role.value}_incoming'] = incoming
            new_week[f'{role.value}_demand'] = demand
            new_week[f'{role.value}_inventory'] = inventory
            new_week[f'{role.value}_cost'] = cost
            new_week[f'{role.value}_outgoing'] = outgoing
        res = self.conn.add_game_week(game_id, current_week['week'] + 1, new_week)
        if not res:
            #TODO use a better exception
            raise Exception("unexpected failure playing game round")



    def set_player_order(self, role: Game_Role, order):
        """Sets a player's orders for the current week
        Args:
            role(Game_Role): the role that is placing the order
            order(int): the amount that is being ordered
        returns:
            succeeded(bool): whether the player order was properly set"""
        #test to see if player has already ordered
        game_id = self.game['id']

        current_week = self.conn.get_current_game_week(game_id)
        res = self.conn.update_week_order(game_id, current_week['week'], role, order)
        if self.round_is_ready():
            self._play_game_round()
        return res
        
    def get_weeks(self, role: Game_Role  = None):
        weeks = self.conn.get_game_weeks(self.game['id'])
        if not role:
            return weeks
        if bool(self.game['info_sharing']):
            game_roles = self._get_game_roles_active_in_game()
            game_roles = [str(r.value) for r in game_roles]
        else:
            game_roles = [role.value]
            
        # filter out all game roles not present in game / not allowed by info sharing
        res = []
        for elem in weeks:
            _week = {}
            for k in elem:
                for i in game_roles:
                    if i in str(k):
                        _week[k] = elem[k]
            _week['week'] = elem['week']
            _week['game_id'] = elem['game_id']
            res.append(_week.copy())
        return res
    
    def modify_game(self, game_dict: dict):
        ''''
        Modifies a game given key-value pairs defined in a dict object
        Args:
            game_dict(dict): a dict of colmumn-value pairs of the Game table
        Returns:
            succeeded(bool): whether the operation succeeded'''
        res = self.conn.update_game(self.game['id'], game_dict)
        self.game = self.conn.get_game(self.game['id'])
        if (self.round_is_ready()):
            self._play_game_round()
        return self.game.copy()


         

