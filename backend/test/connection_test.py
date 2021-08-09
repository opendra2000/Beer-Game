"""Perform unit test for DB Operations."""
import unittest
from src.connection import Connector
from src.constants import Role, Game_Role
from src.game_class import Game
from yoyo import read_migrations
from yoyo import get_backend

import os

test_db = os.getenv('TEST_SQLITE_DB')
migrations = read_migrations('db_migrations')


class DatabaseOperationsTests(unittest.TestCase):
    '''tests operations related to the connector class'''
    def setUp(self):
        # Discard the database if exists 
        if os.path.exists(test_db):
            os.remove(test_db)
        backend = get_backend('sqlite:///{}'.format(test_db))
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))
        self.conn = Connector(True, test_db)

    def test_user_signup(self):
        res = self.conn.add_user('test@test.test', 'asdaqe2sqwswsqw12esdqw', Role.INSTRUCTOR)
        self.assertEqual(res, 1)
        data = self.conn.get_users()
        emails = [row[1] for row in data]
        self.assertTrue('test@test.test' in emails)

    def test_valid_user_session(self):
        # Add a test user
        user_id = self.conn.add_user('test2@test.test', 'asdaqe2sqwswsqw12esdqw', Role.INSTRUCTOR)
        self.assertEqual(user_id, 1)

        # Create a user session
        token = self.conn.add_user_session(user_id)

        # check the session validity
        session_user_id = self.conn.check_session_validity(token)
        self.assertEqual(session_user_id, user_id)

    def test_expired_user_session(self):
        # Add a test user
        user_id = self.conn.add_user('test3@test.test', 'asdaqe2sqwswsqw12esdqw', Role.INSTRUCTOR)
        self.assertEqual(user_id, 1)

        # Add a 35 min old timestamp
        token = 'random_string'
        cur = self.conn.conn.cursor()
        cur.execute(
            "INSERT INTO UserSession (token, user_id, creation_time) VALUES (?, ?, datetime('now', '-35 minutes'))",
            (token, user_id)
        )
        cur.close()

        # verify that there is no session
        session_user_id = self.conn.check_session_validity(token)
        self.assertEqual(session_user_id, None)

    def test_game_creation(self):
        #create game by instructor w/ id 1
        g = self.conn.create_game(1)
        self.assertTrue(g is not None,msg="game creation returnedNone")

    def test_game_info(self):
        #create game
        g = self.conn.create_game(1)
        self.assertTrue(g is not None, msg="none returned for game creation")
        #use created game id
        d = self.conn.get_game(g)
        self.assertTrue(d is not None, msg="game info not properly returned")

    def test_game_creation_custom_params(self):
        d = {
            'session_length': 22,
            'active': False,
            'wholesaler_present': False,
            'retailer_present': True,
            'demand_pattern_id': 2,
            'info_delay': 3,
            'info_sharing': False,
            'holding_cost': 6.9,
            'backlog_cost': 4.20,
        }
        g = self.conn.create_game(1, **d)
        self.assertTrue(g is not None,msg="game instance returned None")
        dict_query = self.conn.get_game(g)
        for i in d:
            self.assertEqual(d[i], dict_query[i], msg=f'error, key {i} differs: {d[i]}, {dict_query[i]}')
    
    def test_password_hash(self):
        p = "hello, world!"
        h = self.conn.hash_password(p)
        self.assertTrue(self.conn.check_password(p, h), msg="hashes do not match!")

    def test_get_instructor_games(self):
        new_ins = self.conn.add_user('get_instructor_games_test', 'asdaqe2sqwswsqw12esdqw', Role.INSTRUCTOR)
        num_games = 5
        for i in range ( num_games):
            self.conn.create_game(new_ins)
        games = self.conn.get_instructor_games(new_ins)
        self.assertEqual(len(games), num_games, msg="the number of games created by the user do not match!")
    
    def test_join_game(self):
        new_player = self.conn.add_user('join-game-test', '12345', Role.PLAYER)
        new_ins = self.conn.add_user('join-game-ins', '12345', Role.INSTRUCTOR)
        new_game = self.conn.create_game(new_ins)
        res = self.conn.add_player_to_game(new_player, new_game, Game_Role.RETAILER)
    
    def test_get_game_week(self):
        ins_id = self.conn.add_user('test_week_ins', '12345', Role.INSTRUCTOR)
        game_id = self.conn.create_game(ins_id)
        cur = self.conn.conn.cursor()
        week = 0
        orders = {
            'factory_order':4,
            'distributor_order':5,
            'retailer_order':6,
            'wholesaler_order':7
        }
        cur.execute('INSERT INTO GameWeeks \
        (week, game_id, factory_order, distributor_order, retailer_order, wholesaler_order) \
             VALUES ( ?, ?, ?, ?, ?, ?)', 
             (week, game_id, *(orders.values()) )
        )
        get_week = self.conn.get_game_week(game_id, week)
        for i in orders:
            self.assertTrue(orders[i] == get_week[i], msg=f"values do not match {orders[i]}, {get_week[i]}")
            
    def test_get_current_game_week(self):
        ins_id = self.conn.add_user('test_current_week_ins', '12345', Role.INSTRUCTOR)
        game_id = self.conn.create_game(ins_id)
        # make instructor create a few more games and populate them to avoid interference
        cur = self.conn.conn.cursor()
        fake_orders = {
                'factory_order': -1,
                'distributor_order':-1,
                'retailer_order': -1,
                'wholesaler_order': -1
            }
        for fake_week in range (0,5):
            g = self.conn.create_game(ins_id)
            for i in range (0, 13):
                cur.execute('INSERT INTO GameWeeks \
                (week, game_id, factory_order, distributor_order, retailer_order, wholesaler_order) \
                VALUES ( ?, ?, ?, ?, ?, ?)', 
                (i, g, *(fake_orders.values()) )
                )

        
        for week in range(0,13):
            orders = {
                'factory_order':4 + week,
                'distributor_order':5,
                'retailer_order':6,
                'wholesaler_order':7 + week
            }
            cur.execute('INSERT INTO GameWeeks \
            (week, game_id, factory_order, distributor_order, retailer_order, wholesaler_order) \
                VALUES ( ?, ?, ?, ?, ?, ?)', 
                (week, game_id, *(orders.values()) )
            )
            get_week = self.conn.get_current_game_week(game_id)

            for i in orders:
                self.assertTrue(orders[i] == get_week[i], msg=f"values do not match {orders[i]}, {get_week[i]}")

    def test_update_week_order(self):
        ins_id = self.conn.add_user('test_update_week_order', '12345', Role.INSTRUCTOR)
        g = self.conn.create_game(ins_id)
        cur = self.conn.conn.cursor()
        orders = {
                'factory_order':4,
                'distributor_order':5,
                'retailer_order':6,
                'wholesaler_order':7
            }
        cur.execute('INSERT INTO GameWeeks \
            (week, game_id, factory_order, distributor_order, retailer_order, wholesaler_order) \
            VALUES ( ?, ?, ?, ?, ?, ?)', 
            (0, g, *(orders.values()) )
        )
        self.conn.conn.commit()
        self.conn.update_week_order(g, 0, Game_Role.DISTRIBUTOR, 100)
        w = self.conn.get_game_week(g, 0)
        self.assertTrue(w['distributor_order'] == 100, msg="updated order does not match for distributor")

    def test_add_game_week(self):
        ins_id = self.conn.add_user('test_add_game_week12', '12345', Role.INSTRUCTOR)
        g = self.conn.create_game(ins_id)
        cur = self.conn.conn.cursor()
        orders = {
                'factory_order':4,
                'distributor_order':5,
                'retailer_order':6,
                'wholesaler_order':7
            }
        cur.execute('INSERT INTO GameWeeks \
            (week, game_id, factory_order, distributor_order, retailer_order, wholesaler_order) \
            VALUES ( ?, ?, ?, ?, ?, ?)', 
            (0, g, *(orders.values()) )
        )
        new_week = self.conn.get_current_game_week(g)
        i = 1
        for role in Game_Role:
            # add some values 
            incoming = 3 +i
            demand = 2 +i
            inventory_brutto = 6 + i
            outgoing = min(inventory_brutto, demand)
            inventory = inventory_brutto - demand
            
            cost = 2 + i
            new_week[f'{role.value}_incoming'] = incoming
            new_week[f'{role.value}_demand'] = demand
            new_week[f'{role.value}_inventory'] = inventory
            new_week[f'{role.value}_cost'] = cost
            new_week[f'{role.value}_outgoing'] = outgoing
            i += 1

        self.conn.add_game_week(g, 1, new_week)

        retrieved_week = self.conn.get_current_game_week(g)
        # do not use week attribute for newly added week to avoid errors
        new_week.pop('week', None)
        for k in new_week:
            self.assertTrue(new_week[k] == retrieved_week[k], 
            msg=f"expected {new_week[k]} to equal {retrieved_week[k]} on key {k}")

    def test_game_parameter_change(self):
        ins_id = self.conn.add_user('test_add_game_week', '12345', Role.INSTRUCTOR)
        g = self.conn.create_game(ins_id)
        updated_keys = {
            'holding_cost': 12,
            'backlog_cost': 1.1,
            'active': False,
            'info_sharing': True,
            'wholesaler_present': False,
            'retailer_present': False,
        }
        self.assertTrue(self.conn.update_game(g, updated_keys))
        updated_game = self.conn.get_game(g)
        for k in updated_keys:
            self.assertTrue(updated_keys[k] == type(updated_keys[k])(updated_game[k]),
            msg=f"expected {updated_keys[k]} to equal {updated_game[k]}")

    def test_get_game_weeks(self):
        ins_id = self.conn.add_user('test_get_game_weeks', '12345', Role.INSTRUCTOR)
        g = self.conn.create_game(ins_id)
        cur = self.conn.conn.cursor()
        orders = {
                'factory_order':4,
                'distributor_order':5,
                'retailer_order':6,
                'wholesaler_order':7
            }
        for i in range(0, 4):
            cur.execute('INSERT INTO GameWeeks \
                (week, game_id, factory_order, distributor_order, retailer_order, wholesaler_order) \
                VALUES ( ?, ?, ?, ?, ?, ?)', 
                (i, g, *(orders.values()) )
            )
        weeks = self.conn.get_game_weeks(g)
        for elem in weeks:
            for k in orders:
                self.assertTrue(orders[k] == elem[k])

    def test_get_demand_patterns(self):
        d = self.conn.get_demand_patterns()
        self.assertTrue(len(d)> 0)

    def test_get_demand_pattern(self):
        d = self.conn.get_demand_pattern(1)
        self.assertTrue(d['name'] == 'default')

if __name__ == '__main__':
    unittest.main()