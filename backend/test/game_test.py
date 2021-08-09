"""Perform unit test for DB Operations."""
import unittest
from src.connection import Connector
from src.constants import Role, Game_Role
from src.game_class import Game
from yoyo import read_migrations
from yoyo import get_backend
import pprint

import os

test_db = os.getenv('TEST_SQLITE_DB')
migrations = read_migrations('db_migrations')


class GameOperationsTests(unittest.TestCase):
    '''tests operations related to the game class'''
    def setUp(self):
        # Discard the database if exists 
        if os.path.exists(test_db):
            os.remove(test_db)
        backend = get_backend('sqlite:///{}'.format(test_db))
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))
        
        self.conn = Connector(True, test_db)
        Game.conn = self.conn
        # create a sample game with 4 players in it:
        self.ins= self.conn.add_user('ins_test', '123', Role.INSTRUCTOR)
        self.p1 = self.conn.add_user('p1', '123', Role.PLAYER)
        self.p2 = self.conn.add_user('p2', '123', Role.PLAYER)
        self.p3 = self.conn.add_user('p3', '123', Role.PLAYER)
        self.p4 = self.conn.add_user('p4', '123', Role.PLAYER)
        self.game_id = self.conn.create_game(self.ins)
        self.conn.add_player_to_game(self.p1, self.game_id, Game_Role.FACTORY)
        self.conn.add_player_to_game(self.p2, self.game_id, Game_Role.WHOLESALER)
        self.conn.add_player_to_game(self.p3, self.game_id, Game_Role.DISTRIBUTOR)
        self.conn.add_player_to_game(self.p4, self.game_id, Game_Role.RETAILER)


    def test_default_game_week_creation(self):
        g = Game(self.game_id)
        week_exists = self.conn.get_current_game_week(self.game_id)
        self.assertTrue( week_exists is not None )

    def test_playing_default_game_round(self):
        g = Game(self.game_id)
        self.assertTrue(g.set_player_order(Game_Role.FACTORY, 1))
        self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 2))
        self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 3))
        self.assertTrue(g.set_player_order(Game_Role.RETAILER, 4))
        
        
        newest_week = self.conn.get_current_game_week(self.game_id)
        
        old_week = self.conn.get_game_week(self.game_id, 0)
        indx = 1
        for i in Game_Role:      
            self.assertTrue( old_week[f'{i.value}_demand'] == 4)

        self.assertTrue( old_week['factory_order'] == 1 )
        self.assertTrue( old_week['wholesaler_order'] == 2 )
        self.assertTrue( old_week['distributor_order'] == 3 )
        self.assertTrue( old_week['retailer_order'] == 4 )
        self.assertTrue( old_week['week'] == newest_week['week'] - 1)
    


    def test_delay_works_correctly(self):
        g = Game(self.game_id)
        delay = g.game['info_delay'] + 1

        for i in range(0, delay):
            self.assertTrue(g.set_player_order(Game_Role.FACTORY, 7))
            self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 7))
            self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 7))
            self.assertTrue(g.set_player_order(Game_Role.RETAILER, 7))
        # factory incoming should equal what we ordered by now:
        current_week = self.conn.get_current_game_week(self.game_id)
        self.assertTrue(
            current_week['factory_incoming'] == 7,
             msg=f"expected 7 to equal {current_week['factory_incoming']}")
        # now for the other 2 roles, we can check what their demand is for the current week


        for role in [Game_Role.DISTRIBUTOR, Game_Role.WHOLESALER]:
            self.assertTrue(
                current_week[f'{role.value}_demand'] == 7, 
                msg=f"expected 7 to equal {current_week[f'{role.value}_demand']} for {role}")
        # play 2 more rounds to see incoming for the other 3 roles
        for i in range(0, delay):
            self.assertTrue(g.set_player_order(Game_Role.FACTORY, 8))
            self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 8))
            self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 8))
            self.assertTrue(g.set_player_order(Game_Role.RETAILER, 8))
        current_week = self.conn.get_current_game_week(self.game_id)
        for role in [Game_Role.DISTRIBUTOR, Game_Role.WHOLESALER]:
            self.assertTrue(
                current_week[f'{role.value}_incoming'] == 7, 
                msg=f"expected 7 to equal {current_week[f'{role.value}_incoming']} for {role}")
        

    def test_numerous_weeks_calculate_cost_correctly(self):
        g = Game(self.game_id)
        delay = g.game['info_delay'] 
        backlog_cost = g.game['backlog_cost']
        inventory_cost = g.game['holding_cost']
        self.assertTrue(g.set_player_order(Game_Role.FACTORY, 0))
        self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 8))
        self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 8))
        self.assertTrue(g.set_player_order(Game_Role.RETAILER, 8))
        #order something
        self.assertTrue(g.set_player_order(Game_Role.FACTORY, 0))
        self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 4))
        self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 4))
        self.assertTrue(g.set_player_order(Game_Role.RETAILER, 4)) 
        for i in range(0, delay):
            self.assertTrue(g.set_player_order(Game_Role.FACTORY, 0))
            self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 0))
            self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 0))
            self.assertTrue(g.set_player_order(Game_Role.RETAILER, 0))
        # by now, factory should be receiving the demand of the wholesaler
        new_week = self.conn.get_current_game_week(self.game_id)
        self.assertTrue(new_week['factory_demand'] == 8)
        #furthermore, this should result in a negative inventory . . . 
        prev_week = self.conn.get_game_week(self.game_id, new_week['week'] -1)
        # backlog cost should be calculated correctly   
        self.assertTrue(new_week['factory_cost'] - prev_week['factory_cost'] == 8*backlog_cost)


    def test_game_with_fewer_players_still_works(self):
            self.conn.update_game(self.game_id, {'wholesaler_present': False})
            # need to change game params before generating game class
            g = Game(self.game_id)
            
            self.assertTrue(g.set_player_order(Game_Role.FACTORY, 4))
            self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 4))
            self.assertTrue(g.set_player_order(Game_Role.RETAILER, 4))

            # by now, factory should be receiving the demand of the wholesaler
            new_week = self.conn.get_current_game_week(self.game_id)  
            self.assertTrue(new_week['week'] != 0, msg="week did not progress!")
            for i in range(0, 10):
                self.assertTrue(g.set_player_order(Game_Role.FACTORY, 5))
                self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 5))
                self.assertTrue(g.set_player_order(Game_Role.RETAILER, 5))
            new_week = self.conn.get_current_game_week(self.game_id)
            self.assertTrue(new_week['wholesaler_cost'] is None, 
            msg="cost still being calculated for role not in game!")

    def test_game_with_2_fewer_players_still_works(self):
        self.conn.update_game(self.game_id, {'wholesaler_present': False, 'retailer_present': False})
        # need to change game params before generating game class
        g = Game(self.game_id)
        
        self.assertTrue(g.set_player_order(Game_Role.FACTORY, 4))
        self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 4))

        # by now, factory should be receiving the demand of the wholesaler
        new_week = self.conn.get_current_game_week(self.game_id)  
        self.assertTrue(new_week['week'] != 0, msg="week did not progress!")
        for i in range(0, 10):
            self.assertTrue(g.set_player_order(Game_Role.FACTORY, 5))
            self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 5))
        new_week = self.conn.get_current_game_week(self.game_id)
        self.assertTrue(new_week['wholesaler_cost'] is None, 
        msg="cost still being calculated for role not in game!")
        self.assertTrue(new_week['retailer_cost'] is None, 
        msg="cost still being calculated for role not in game!")
    
    def test_get_weeks(self):
        g = Game(self.game_id)
        num_completed_rounds =5
        for i in range(0, num_completed_rounds):
            self.assertTrue(g.set_player_order(Game_Role.FACTORY, 2))
            self.assertTrue(g.set_player_order(Game_Role.WHOLESALER, 2))
            self.assertTrue(g.set_player_order(Game_Role.DISTRIBUTOR, 2))
            self.assertTrue(g.set_player_order(Game_Role.RETAILER, 2))
        weeks = g.get_weeks(Game_Role.DISTRIBUTOR)
        self.assertTrue(len(weeks) == num_completed_rounds + 1)
        for i in range(0, num_completed_rounds):
            self.assertTrue(weeks[i]['distributor_order'] == 2,
            msg=f"incorrect ordered value in weeks!" )
        # now check no other data is being leaked
        for role in [Game_Role.FACTORY, Game_Role.RETAILER, Game_Role.WHOLESALER]:
            role = role.value
            for elem in weeks:
                for k in elem:
                    self.assertTrue(role not in k, msg="incorrect info sharing being done!")
        #now check info sharing happens correctly when we set it
        self.conn.update_game(self.game_id, {'info_sharing' : True,})
        g = Game(self.game_id)
        weeks = g.get_weeks(Game_Role.DISTRIBUTOR)
        for i in range(0, num_completed_rounds):
            for role in Game_Role:
                self.assertTrue(weeks[i][f'{role.value}_order'] == 2,
                msg=f"incorrect info sharing when toggled on!" )
       



if __name__ == '__main__':
    unittest.main()