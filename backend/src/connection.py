"""Class to manage the DB Operations."""
import os.path
import secrets
import os
import datetime
import traceback
from dotenv import load_dotenv
import sqlite3
import mariadb
import logging
import mysql.connector
from .constants import Role, Game_Role
import bcrypt
import json

load_dotenv()

database_used = os.getenv("DATABASE")
if not database_used:
    raise Exception("DATABASE environment variable not defined!")
database_used = database_used.lower()

if database_used not in ['mysql', 'sqlite', 'mariadb']:
    raise Exception("DATABASE environment variable should be 'mysql', 'sqlite', or 'mariadb'")
sqlite_file = os.getenv("SQLITE_DB")

class Connector:
    """Manage Databse connection."""

    def __init__(self, is_testing=False, test_sqlite=None):
        """Init Databse connection."""
        if is_testing:
            self.conn = sqlite3.connect(
                test_sqlite, check_same_thread=False
            )
        elif database_used == 'sqlite':
            
            self.conn = sqlite3.connect(
                sqlite_file, check_same_thread=False)
        elif database_used == 'mariadb':
            try:
                self.conn = mariadb.connect(
                    user=os.getenv("MYSQL_USERNAME"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    host=os.getenv("MYSQL_HOST"),
                    port=int(os.getenv("MYSQL_PORT", 3306)),
                    database=os.getenv("MYSQL_DATABASE")
                )
            except mariadb.Error as e:
                logging.error('Error_Connector: {}'.format(e))
        else:
            try:
                self.conn = mysql.connector.connect(
                    user=os.getenv("MYSQL_USERNAME"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    host=os.getenv("MYSQL_HOST"),
                    port=int(os.getenv("MYSQL_PORT", 3306)),
                    database=os.getenv("MYSQL_DATABASE")
                )
            except mysql.connector.Error as e:
                logging.error('Error_Connector: {}'.format(e))

            

    def __to_dict(self, cursor, values):
        """turns a tuple of values into a dictionary
        Args:
            cursor: database connection cursor, use right after required query
            values(tuple): a SINGLE TUPLE filled with desired values
        Returns:
            d(dict): a dictionary of key-value pairs"""
        
        d= {}
        if not values:
            return None
        for i, v in zip(cursor.description, values):
            d[i[0]] = v
        return d

    def hash_password(self, password: str) -> str:
        """hashes a player's password to add it to the databse
        Args:
            password(str): the password as a standard string
        Returns:
            hash(str): a string representation of the hashed password
        """
        password = str.encode(password)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')

    def check_password(self, password, hash) -> bool:
        """checks that a given password and hash match
        Args:
            password(str): the password as a standard string
            hash(str): the hash representation as a utf-8 string
        """
        if type(password) is str:
            password = str.encode(password)
        if type(hash) is str:
            hash = str.encode(hash)
        return bcrypt.checkpw(password, hash)


    def add_user(self, email, password_hash, role):
        """Add User to user table.

        Args:
            email (string): email address of the user
            password_hash (string): password
        """
        cur = self.conn.cursor()
        try:
            password_hash = self.hash_password(password_hash)
            cur.execute(
                'INSERT INTO User(email, password_hash, role) VALUES (?, ?, ?)',
                (email, password_hash, role.value)
            )
            self.conn.commit()
            cur.execute(
                'SELECT id FROM User WHERE email = ?',
                (email,)
            )
            _id = cur.fetchall()[0][0]
            return _id
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error('Error_Connector_add_user: {}'.format(e))
            #traceback.print_exc()
            return None
        finally:
            cur.close()

    def get_user(self, email, password):
        """Get A user
        Args:
            email(str): the user's email
            password(str): the user's password, as a string"""
        cur = self.conn.cursor()
        try:
            cur.execute(
                'SELECT id, password_hash  FROM User WHERE email = ?',
                (email, )
            )
            res = cur.fetchall()
            if len(res) < 1:
                return None
            return res[0][0]
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error(
                'Error_Connector_get_users: {}'.format(e)
            )
            return None
        finally:
            cur.close()

    def add_user_session(self, user_id):
        """Add session for user authentication.

        Args:
            user_id (int): the id of the user
        Returns:
            session_id (string): session id
        """
        cur = self.conn.cursor()
        try:
            token = secrets.token_urlsafe()
            cur.execute(
                'INSERT INTO UserSession (token, user_id) VALUES (?, ?)',
                (token, user_id)
            )
            self.conn.commit()
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error('Error_Connector_add_user_session: {}'.format(e))
            return None
        finally:
            cur.close()
        return token

    def check_session_validity(self, token, role=None):
        """Check the session validity.

        Args:
            token (string): session token
            ROLE (Role): optional role to specify for instructor/player
        Returns:
            user_id (int): the user id associated with the session,
            None if session id is expired or invalid
        """
        cur = self.conn.cursor()
        try:
            if role not in [None, Role.PLAYER, Role.INSTRUCTOR]:
                raise TypeError("expected None, Role.Player, Role.instructor in ROLE")
            date_30_min_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
            if role:
                
                cur.execute (
                    "SELECT s.user_id FROM UserSession s \
                    INNER JOIN User u on u.role = ? AND u.id = s.user_id WHERE token = ? AND\
                    s.creation_time >= ? ",
                    (role.value, token, date_30_min_ago)
                )
            else:
                cur.execute(
                    "SELECT user_id FROM UserSession WHERE token = ? AND\
                    creation_time >= ?",
                    (token, date_30_min_ago)
                )
            res = cur.fetchall()
            if len(res) < 1:
                return None

            cur.execute(
                "UPDATE UserSession SET creation_time=CURRENT_TIMESTAMP WHERE token = ?",
                (token,)
            )
            #delete  extra sessions related to user
            cur.execute(
                "DELETE FROM UserSession WHERE user_id=? AND creation_time < ?", (res[0][0], date_30_min_ago)
            )

            self.conn.commit()
            return res[0][0]

        except (sqlite3.Error, mariadb.Error) as e:
            logging.error(
                'Error_Connector_check_session_validity: {}'.format(e)
            )
            return None
        finally:
            cur.close()

    def get_users(self):
        """Get All Users."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                'SELECT id, email FROM user'
            )
            res = cur.fetchall()
            return res
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error(
                'Error_Connector_get_users: {}'.format(e)
            )
            return None
        finally:
            cur.close()
        # maintaining clarity
    def create_game(self, instructor_id, factory_id=0, distributor_id=0, wholesaler_id=0, retailer_id=0, session_length=26, active=True, wholesaler_present=True,
     retailer_present=True, demand_pattern_id=1, info_delay=2, info_sharing=False,
     holding_cost=0.5, backlog_cost=1, starting_inventory=5) -> int:
        """Creates a game

        Args:
            instructor_id(int): instructor id
            session_length(int): length of game session, default 26
            active(bool): whether the game is active, default True
            wholesaler_present(bool): whether wholesaler is present. Default True
            retailer present(bool): whether retailer is present. Default True
            demand_pattern_id(int): what demand pattern to use TODO IMPLEMENT (WIP)
            info_delay(int): how long it takes for orders to reach successor / predecessor. Default 2
            info_sharing(bool): whther info sharing between players is enabled. Default False
            holding_cost(float): holding cost for players. Default 0.5
            backlog_cost(float): cost for backlogged beer. Default 1
        Returns:
            Game_id(int): the id of the game created
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                'INSERT INTO Game ( instructor_id, session_length, retailer_present, wholesaler_present, \
                    holding_cost, backlog_cost, active, demand_pattern_id, \
                starting_inventory, info_delay, info_sharing ) VALUES \
                ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                ( instructor_id, session_length, retailer_present, wholesaler_present, 
                    holding_cost, backlog_cost, active, demand_pattern_id, 
                starting_inventory, info_delay, info_sharing  )
            )
            id_ = cur.lastrowid
            self.conn.commit()
            return id_
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error('Error_Connector_create_game: {}'.format(e))
            return None
        finally:
            cur.close()
    
    def get_game(self, game_id):
        """gets a game's description as a dict object
        Args:
            game_id(int): the id of the game querried
        Returns:
            d(dict): A dictionary of key-value pairs corresponding to column-value, None if error
        """
        try:
            cur = self.conn.cursor()
            cur.execute("select * from Game where id = ?", (game_id,))         
            d = self.__to_dict(cur, cur.fetchone())
            return d
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error('Error_Connector_get_game: {}'.format(e))
            return None
        finally: 
            cur.close()


    def update_game(self, game_id, updated_rules: dict):
        '''updates a game using column names and values in the updated_rules dictionary
        Args:
            game_id(int): the id of the game to update
            updated_rules(dict): a dictionary containing key value pairs of column names and values
        Returns:
            success(bool) whether the operation succeeded'''
        try:
            # not the best practice but xd
            #TODO: USE A SCHEMA TO VERIFY THAT week_dict IS SAFE FOR USE
            cursor = self.conn.cursor()
            if not updated_rules:
                raise TypeError('updated_rules should not be None!')
            keys = ','.join([ f'{k} = ?' for k in updated_rules])
            query_string = f"UPDATE Game SET {keys} WHERE id = ?"
            cursor.execute(query_string, (*[updated_rules[k] for k in updated_rules], game_id))
            self.conn.commit()
            return True
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_update_game{}'.format(e))
            return False
        finally:
            cursor.close()

    def add_player_to_game(self, player_id,  game_id, player_type: Game_Role):
        """Adds a player to a game
        Args:
            user_id(int): id of the user to be added to game
            game_id(int): id of the game to add the user to
            player_type(Game_Role): type of player
        Returns:
            success(bool): whether the player was added to the game 
        """
        try:
            cur = self.conn.cursor()
            cur.execute(f'SELECT {player_type}_id from Game where id=?', (game_id, ))
            r = cur.fetchone()
            if r[0] is not None:
                return False
            # now we can add the player to the Player table
            cur.execute('INSERT OR IGNORE into Player (id, current_game_id, role) values (?, ?, ?)', 
            (player_id, game_id, player_type))
            self.conn.commit()
            cur.execute(f'UPDATE Game SET {player_type}_id = ? WHERE id = ?',
             (player_id, game_id))
            self.conn.commit()
            return True
        except (sqlite3.Error, mariadb.Error) as e:
            logging.error('Error_Connector_add_player: {}'.format(e))
            return False
        finally: 
            cur.close()
            
    def get_instructor_games(self, ins_id: int):
        """
            Args:
                ins_id(int): the instructor's id of the
            Returns:
                games(list): a list of dictionary objects containing each game
                """
        try:    
            cur = self.conn.cursor()
            cur.execute( "SELECT * from Game where instructor_id = ?", (ins_id, ))
            games = []
            for i in cur.fetchall():
                games.append(self.__to_dict(cur, i))
            return games
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_instructor_games: {}'.format(e))
        finally:
            cur.close()

    def get_players(self, ins_id: int):
        """
            Args:
                ins_id(int): the instructor's id that's calling this function
            Returns:
                players(list): a list of dictionary objects containing each player information
                """
        try:    
            cur = self.conn.cursor()
            cur.execute( "SELECT * from User where role='player'")
            players = []
            for i in cur.fetchall():
                players.append(self.__to_dict(cur, i))
            return players
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_instructor_games: {}'.format(e))
        finally:
            cur.close()

    def get_players_table(self, ins_id: int):
        """
            Args:
                ins_id(int): the instructor's id that's calling this function
            Returns:
                players(list): a list of dictionary objects containing each player information from Player table
                """
        try:    
            cur = self.conn.cursor()
            cur.execute( "SELECT * from Player")
            players = []
            for i in cur.fetchall():
                players.append(self.__to_dict(cur, i))
            return players
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_players_table: {}'.format(e))
        finally:
            cur.close()

    def delete_player_from_player_table(self, player_id):
        """
            Args:
                Deletes the player from Player table with the given player_id and also the game row
                with that player, because when you delete a role from the game, means the game's finished
                player_id(int): the player you want to delete from player table
            Returns:
                player_id: the id of player you deleted
                """
        try:    
            cur = self.conn.cursor()
            cur.execute( "DELETE FROM Player WHERE id=?", (player_id,))
            cur.execute( "DELETE FROM Game WHERE factory_id=? OR distributor_id=? OR wholesaler_id=? OR retailer_id=?", (player_id,player_id,player_id,player_id))
            return player_id
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_delete_player_from_player_table: {}'.format(e))
        finally:
            cur.close()

    def get_players_not_playing(self, ins_id: int):
        """
            Args:
                ins_id(int): the instructor's id that's calling this function
            Returns:
                players(list): a list of dictionary objects containing each player information from Player table
                """
        try:    
            cur = self.conn.cursor()
            cur.execute("SELECT id,email FROM User WHERE role='player' AND id NOT IN (SELECT id FROM Player)")
            players = []
            for i in cur.fetchall():
                players.append(self.__to_dict(cur, i))
            return players
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_players_not_playing: {}'.format(e))
        finally:
            cur.close()

    def get_game_week(self, game_id, week):
        """gets a game week of a specific game_id 
        Args:
            game_id(int): the id of the game
            week(int): the week that is requested
        Returns:
            week_info(dict): key-value pairs of the week's order"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM GameWeeks WHERE week = ? AND game_id = ?",
            (week, game_id))
            res = self.__to_dict(cur, cur.fetchone())
            return res
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_game_week: {}'.format(e))
        finally:
            cur.close()
    
    def get_game_weeks(self, game_id):
        """Gets all weeks associated with a game
        args: 
            game_id(int): the game id requested
        returns
            weeks(list: dict): a list of dicts representing each week"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM GameWeeks WHERE game_id = ? ",
            ( game_id, ))
            res = []
            for row in cur.fetchall():
                res.append(self.__to_dict(cur, row))
            return res
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_game_week: {}'.format(e))
        finally:
            cur.close()


    def get_player_game(self, player_id):
        """Returns the game that the player is currently in
        Args:
            player_id(int): the id of the player
        Returns:
            game_id(int): the game id if the player's assigned to any game and -1 if the user is not assigned inany game"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT current_game_id, role FROM Player WHERE id = ?",
            (player_id, ))
            r=cur.fetchone()
            if r is not None:
                return r
            return -1
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_player_game: {}'.format(e))
        finally:
            cur.close()
    
    def get_player_role(self, player_id) -> Game_Role: 
        """Returns the role that the player is currently in
        Args:
            player_id(int): the id of the player
        Returns:
            role(string): the role of the player in the game"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT role FROM Player WHERE id = ?",
            (player_id, ))
            return Game_Role(cur.fetchone()[0])
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_player_role: {}'.format(e))
        finally:
            cur.close()

    def get_current_game_week(self, game_id):
        """gets the current week related to a game
        Args:
            game_id(int): the id of the game requested
        Returns:
            week(dict): a dictionary representation of the current week found in GameWeeks"""
        try:
            cur = self.conn.cursor()
            #mariadb connector throws an error if I am not redundant here . .. .
            cur.execute("SELECT GameWeeks.* FROM GameWeeks INNER JOIN \
                (SELECT game_id, Max(week) MaxPoint FROM GameWeeks where game_id=? GROUP BY game_id) tbl ON GameWeeks.week = \
                    tbl.MaxPoint AND GameWeeks.game_id=?", (game_id, game_id))

            res =  self.__to_dict(cur, cur.fetchone())
            return res
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_current_game_week {}'.format(e))
        finally:
            cur.close()

    def update_week_order(self, game_id, week, role: Game_Role, order):
        """ updates the orders for a specific week
        Args:
            game_id(int): the id of the game requested
            week(int): the week that will be changed
            role(Game_Role): the player's game role
            order(int): how much the player is ordering
        Returns:
            None
            an exception is thrown in case the week or game_id do not exist
        
        """
        try:
            cur = self.conn.cursor()
            cur.execute(f'UPDATE GameWeeks set {role.value}_order = ? WHERE game_id = ? AND week = ?',
            (order, game_id, week))
            self.conn.commit()
            return True
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_update_week_order: {}'.format(e))
            return False
        finally:
            cur.close()


    def add_game_week(self, game_id, week, week_dict: dict):
        '''adds a game week to an existing game, this is bad practice but it's fast
        Args:
            game_id(int): the game's id
            week(int): the desired week
            week_dict(dict): a game_dict object containing the same keys as column names in mysql table
        Returns:
            success(bool): whether the operation worked'''
        try:
            # not the best practice but xd
            #TODO: USE A SCHEMA TO VERIFY THAT week_dict IS SAFE FOR USE . . . this is currently vulnerable to sql injections in the dict keys
            cursor = self.conn.cursor()
            if week_dict:
                for k in ['game_id', 'week']:
                    week_dict.pop(k, None)
                query_string = f"INSERT INTO GameWeeks (game_id, week, \
                    {','.join( [k for k in week_dict])} ) VALUES (?, ?, {','.join('?' for k in week_dict)} ) "
            else:
                week_dict = {}
                query_string = f"INSERT INTO GameWeeks(game_id, week) VALUES (?, ?)"
            
            cursor.execute(query_string, (game_id, week, *[week_dict[k] for k in week_dict]))
            self.conn.commit()
            return True
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_add_game_week{}'.format(e))
            return False
        finally:
            cursor.close()
        
    def  get_demand_patterns(self):
        '''gets all demand patterns
        Returns:
            patterns(list: dict): a list containing dict objects representing the patterns. None if a db error occurred'''
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM DemandPattern')
            patterns = []
            for row in cur.fetchall():
                d = self.__to_dict(cur, row)
                d['encoded_data'] = json.loads(d['encoded_data'])
                patterns.append(d)
            return patterns
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_demand_patterns{}'.format(e))
            return None
        finally:
            cur.close()
    
    def get_demand_pattern(self, demand_pattern_id):
        '''returns a demand pattern identified by its id
        Args:
            demand_pattern_id(int): the id of the demand pattern
        Returns:
            pattern(dict): a dict object representing the pattern, None if an error occurred'''
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM DemandPattern WHERE id = ?', (demand_pattern_id, ))

            d = self.__to_dict(cur, cur.fetchone())
            d['encoded_data'] = json.loads(d['encoded_data'])
            return d
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_get_demand_pattern{}'.format(e))
            return None
        finally:
            cur.close()
    
    def add_demand_pattern(self, encoded_data, name="default"):
        '''adds a demand pattern to the demand pattern table
        Args:
            name(string): it's an optional argument
            encoded_data(string): array of numbers
        Returns:
            demand pattern id(number): the demand pattern id of the added demand pattern '''
        try:
            cur = self.conn.cursor()
            cur.execute('INSERT INTO DemandPattern(name, encoded_data) VALUES (?, ?)', (name, encoded_data,)) 
            id_ = cur.lastrowid
            self.conn.commit()
            return id_
        except (mariadb.Error, sqlite3.Error) as e:
            logging.error('Error_Connector_add_demand_pattern: {}'.format(e))
            return None
        finally:
            cur.close()

    

connector = Connector()
