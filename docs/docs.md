Files
---------------------------
**NOTE** if you want more detail about each specific function, read the **docstrings** under each function / method definition.

game_route.py
--------------------------
- handles interaction between the players and a game instance, allows players to join a game, send round info, receive round info, etc

main.py
---------------------------
- handles flask server initialization
- handles authentication via /register and /authenticate

instructor.py
---------------------------
- handles the endpoints an instructor can call to interact with a game (create game, get demand patterns, get all games he created, etc)

middleware.py
--------------------------
creates authentication *wrapper functions* used in `instructor.py` and `game_route.py`. These wrapper functions also have the side effect of adding new
parameters to whatever function they decorate, essentially allowing for the appropriate id to be retrieved from the database and given to the routing endpoints
without making the routing functions hard-coded to a specific implementation.

src/connection.py
-------------------------
the only class used to interact with the database, it is used as a singleton pattern so the same database connection is shared accross the entire application.
The api endpoints and the game class rely on this class to interact with the database and get the desired data from it.

src/game.py
-------------------------
A Game class encapsulating the logic used when a game is played. The game class contains a **static variable** conn that must be set to point to the appropriate 
*connector* class instance to properly connect to the database. The game class is mostly used in `game_route.py` to handle requests coming in from players. This
class allows us to create games with custom rules and handles the synchronization logic of when to play a game round.

src/constants.py
-------------------------
a file containing several different enums used throughout the project, mainly *Game_Role* and *Role*