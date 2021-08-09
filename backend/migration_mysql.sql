-- transactional: true
-- TODO: sqlite doesn't suport enum structure for the role.
-- come up with a clean way to constrain role
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS User;
CREATE TABLE User(
    id INTEGER AUTO_INCREMENT,
    email VARCHAR(40) NOT NULL UNIQUE,
    role VARCHAR(40) NOT NULL,
    password_hash VARCHAR(60) NOT NULL,
    PRIMARY KEY (id)
);
DROP TABLE IF EXISTS UserSession;
CREATE TABLE UserSession(
  id INTEGER AUTO_INCREMENT,
  token VARCHAR(60) UNIQUE,
  creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  user_id INTEGER,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES User(id)
);
DROP TABLE IF EXISTS Instructor;
CREATE TABLE Instructor(
   id INTEGER AUTO_INCREMENT,
   PRIMARY KEY (id),
   FOREIGN KEY (id) REFERENCES User(id)
);
DROP TABLE IF EXISTS DemandPattern;
CREATE TABLE DemandPattern(
    id INTEGER AUTO_INCREMENT,
    weeks INTEGER NOT NULL,
    name VARCHAR(40) NOT NULL,
    encoded_data VARCHAR(200) NOT NULL,
    PRIMARY KEY (id)
);
DROP TABLE IF EXISTS Game;
CREATE TABLE Game(
    id INTEGER AUTO_INCREMENT,
    session_length INTEGER,
    retailer_present BOOLEAN,
    wholesaler_present BOOLEAN,
    holding_cost DOUBLE,
    backlog_cost DOUBLE,
    instructor_id INTEGER NOT NULL,
    active BOOLEAN,
    demand_pattern_id INTEGER,
    starting_inventory INTEGER,
	info_sharing BOOLEAN,
    info_delay INTEGER,
    factory_id INTEGER UNIQUE,
    distributor_id INTEGER UNIQUE,
    retailer_id INTEGER UNIQUE,
    wholesaler_id INTEGER UNIQUE,
    PRIMARY KEY (id),
    FOREIGN KEY (instructor_id) REFERENCES User(id),
    FOREIGN KEY (factory_id) REFERENCES Player(id),
    FOREIGN KEY (distributor_id) REFERENCES Player(id),
    FOREIGN KEY (retailer_id) REFERENCES Player(id),
    FOREIGN KEY (wholesaler_id) REFERENCES Player(id)
);
DROP TABLE IF EXISTS Player;
CREATE TABLE Player(
    id INTEGER AUTO_INCREMENT,
    current_game_id INTEGER,
    role VARCHAR(20),
    PRIMARY KEY (id),
    FOREIGN KEY (id) REFERENCES User(id),
    FOREIGN KEY (current_game_id) REFERENCES Game(id)
);
DROP TABLE IF EXISTS InstructorGames;
CREATE TABLE InstructorGames(
    game_id INTEGER AUTO_INCREMENT,
    instructor_id INTEGER,
    PRIMARY KEY (instructor_id, game_id),
    FOREIGN KEY (game_id) REFERENCES Game(id),
    FOREIGN KEY (instructor_id)  REFERENCES Instructor(id)
);
DROP TABLE IF EXISTS GameState;

DROP TABLE IF EXISTS GameWeeks;
CREATE TABLE GameWeeks(
    week INTEGER NOT NULL,
    game_id INTEGER,
    factory_inventory INTEGER DEFAULT 4,
    factory_demand INTEGER DEFAULT 4,
    factory_incoming INTEGER DEFAULT 4,
    factory_outgoing INTEGER DEFAULT 4,
    factory_order INTEGER,
    factory_cost DOUBLE,

    wholesaler_inventory INTEGER DEFAULT 4,
    wholesaler_demand INTEGER DEFAULT 4,
    wholesaler_incoming INTEGER DEFAULT 4,
    wholesaler_outgoing INTEGER DEFAULT 4,
    wholesaler_order INTEGER,
    wholesaler_cost DOUBLE,

    distributor_inventory INTEGER DEFAULT 4,
    distributor_demand INTEGER DEFAULT 4,
    distributor_incoming INTEGER DEFAULT 4,
    distributor_outgoing INTEGER DEFAULT 4,
    distributor_order INTEGER,
    distributor_cost DOUBLE,

    retailer_inventory INTEGER DEFAULT 4,
    retailer_demand INTEGER DEFAULT 4,
    retailer_incoming INTEGER DEFAULT 4,
    retailer_outgoing INTEGER DEFAULT 4,
    retailer_order INTEGER,
    retailer_cost DOUBLE,

    PRIMARY KEY (week, game_id),
    FOREIGN KEY (game_id) REFERENCES Game(id)
);
DROP TABLE IF EXISTS DemandPattern;
CREATE TABLE DemandPattern(
    id INTEGER AUTO_INCREMENT,
    name VARCHAR(40) NOT NULL,
    encoded_data VARCHAR(500) NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO DemandPattern(name, encoded_data) VALUES ("default", 
'[4,4,4,5,6,7,4,3,5,8,3,2,4,7,6,5,3,7,8,10,12,9,7,6,5,8,6,5,4,8,2,4,6,10,12]');
SET FOREIGN_KEY_CHECKS = 1;
COMMIT;