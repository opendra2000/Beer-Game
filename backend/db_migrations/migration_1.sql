-- transactional: true

DROP TABLE IF EXISTS Game;
CREATE TABLE Game(
    id INTEGER,
    session_length INTEGER DEFAULT 26,
    retailer_present BOOLEAN,
    wholesaler_present BOOLEAN,
    holding_cost FLOAT,
    backlog_cost FLOAT,
    instructor_id INTEGER NOT NULL,
    active BOOLEAN,
    demand_pattern_id INTEGER,
    starting_inventory INTEGER,
    info_delay INTEGER,
    info_sharing BOOLEAN,
    factory_id INTEGER UNIQUE,
    distributor_id INTEGER UNIQUE,
    retailer_id INTEGER UNIQUE,
    wholesaler_id INTEGER UNIQUE,
    PRIMARY KEY (id),
    FOREIGN KEY (instructor_id) REFERENCES User(id),
    FOREIGN KEY (demand_pattern_id) REFERENCES DemandPattern(id)

    FOREIGN KEY (factory_id) REFERENCES Player(id),
    FOREIGN KEY (distributor_id) REFERENCES Player(id),
    FOREIGN KEY (retailer_id) REFERENCES Player(id),
    FOREIGN KEY (wholesaler_id) REFERENCES Player(id)
);
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
    id INTEGER,
    name VARCHAR(40) NOT NULL,
    encoded_data VARCHAR(500) NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO DemandPattern(name, encoded_data) VALUES ("default", 
'[4,4,4,5,6,7,4,3,5,8,3,2,4,7,6,5,3,7,8,10,12,9,7,6,5,8,6,5,4,8,2,4,6,10,12]');
