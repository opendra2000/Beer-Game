# Beer-game
Beer Game : Supply Chain Project

The beer game is based on supply chain and involves 4 players where each player represents one of the four stages in the chain i.e the retailer,
the manufacturer, the wholesaler, the consumer. The goal of this game is to teach students who use this software about The Bullwhip Efect which 
is a supply chain phenomenon describing how small fluctuations in demand at the retail level can cause progressively larger fluctuations in 
demand at the wholesale, distributor, manufacturer and raw material supplier levels.

Architecture Notes
------------------
* Backend is written in Python and uses Flask as a light weight server
* For Database the system uses Sqlite for local testing and mariadb for production
* The frontend is written in js + react and served using a node.js server.
* The frontend communicates with the backend using REST architecture.
* Back-end authentication is carried out by a **Header** file called *SESSION-KEY* **OR** a cookie set after authentication. In case the header file is used, this header file must be sent in all subsequent requests to the API to verify that the sender is authenticated and has the proper permissions to interact with the endpoint. The cookie should be sent automatically by the browser and is thus simpler to use
* you may find a brief explanation of what each file in the backend does in docs/docs.md, but look at the docstrings under each function/method for more detailed documentation



REST API Documentation
----------------------
* a YAML-style documentation can be found in the docs/ directory, you can upload this file to swagger on your account to continue developing the API
* link: https://app.swaggerhub.com/apis-docs/api-test7/group-22-modified/1.0.0/
    - For the TA's, you can consider this an 'expansion of the specifications', as we implemented all the functionalities described in this API . . . since the winning specification said absolutely nothing about the API . . .

Steps to setup & start the backend server
---------------------------------------------
* Make sure you have python virtual env installed. Create a python virtual environment in the **root directory of the backend**: `virtualenv venv`. if this doesn't work, try: `python3 -m venv venv`.
* Switch to the venv: `source venv/bin/activate`
* Install dependency for mariadb:  `sudo apt-get install libmariadb-dev` or `brew install mariadb` on macOS. 
* Install all the python requirements: `pip3 install -r requirements.txt`
* Copy .env.sample to .env `cp .env.sample .env` (For production you need to modify the env variables appropriately to point to correct mariadb instance)
    * To use a mysql database, modify the variables in .env.sample accordingly and run `cp .env.sample .env` 
        - set `DATABASE=mariadb`, 
        - uncomment and set all mariadb connection variables and set them to appropriate values
        - Manually pipe the sql migration script into the database. ie `mysql -u {user_name} -p {database_name} < migration_mysql.sql`
    * start the flask session, run `flask run` or `python3 main.py`
    * **WARNING** Since CLAMV does not currently support mariadb connector, it is impossible to connect to the CLAMV database
* If you don't want that hassle, just run the inital db migration from the root backend directory for sqlite `yoyo apply` (remember to be in a virtual environment)
    * set `DATABASE=sqlite` in .env.sample  and run `cp .env.sample .env`
* From the root backend directory run `flask run` or `python3 main.py`


Steps to setup & start the frontend server
------------------------------------------
* Make sure you have `node.js` installed. Locate the frontend directory and install all the required packages using `npm install`.
* Run `npm start` to run in the development mode. 

Steps to run the Frontend test
--------------------------
* Locate the frontend directory and run `run npm test` 


Steps to run the unittests
--------------------------
* run `cp .env.sample .env` in the terminal instance, make sure you are inside a python virtual environment
* From the backend root directory run `python3 -m unittest test.connection_test` to test the connector class, `python3 -m unittest test.game_test` to test the game class



Steps to run the endpoint tests
--------------------------------
* From the frontend directory, open `BROWSER_TESTS.html` in your default browser. Make sure you ran `npm install` beforehand to install dependencies

