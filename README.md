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
