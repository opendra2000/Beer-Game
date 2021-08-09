import "./create-game.css";
import React, { useState } from "react";
import { StaticRouter, useHistory } from "react-router-dom";
import { useEffect } from "react";
import axios from "axios";
import Cookies from "js-cookie";

export default function Dashboard(props) {
  const history = useHistory();
  const [playerID, setPlayerID] = useState(null);
  useEffect(() => {
    Cookies.get("SESSION-KEY") === undefined
      ? history.push("/login")
      : history.push("/create-game");
    axios
      .get("http://0.0.0.0:8086/instructor/get_players_not_playing", {
        headers: {
          "SESSION-KEY": Cookies.get("SESSION-KEY"),
        },
      })
      .then((response) => {
        setPlayerID(response.data);
      })
      .catch((error) => {
        console.log(error.response);
      });
  }, [setPlayerID]);

  //these are the states that we need to create a game
  //note that none of these is actually required, but obviously for a functional game
  //you would need to have them.
  //Active by default is true and it will stay so, because it doesn't make sense to
  //start a game and it not to be active, but you need it, because you might need to edit it
  //during the game
  const [state, setState] = useState({
    session_length: "",
    retailer_present: false,
    wholesaler_present: false,
    holding_cost: "",
    backlog_cost: "",
    active: true,
    starting_inventory: "",
    info_delay: "",
    info_sharing: false,
    demand_id: "",
  });

  const availablePlayers = () => {
    const players = playerID.map((item) => (
      <option key={item.id} value={item.email}>
        {item.email}
      </option>
    ));
    return players;
  };

  const [demand_pattern, setDemand] = useState({
    name: "",
    encoded_data: "",
  });

  const handleChangeDemand = (e) => {
    const { name, value } = e.target;
    setDemand((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  //this function handles all the changes made to the state variables
  const handleChange = (e) => {
    const { name, value } = e.target;
    if (
      name === "info_sharing" ||
      name === "retailer_present" ||
      name === "wholesaler_present"
    ) {
      setState((prevState) => ({
        ...prevState,
        [name]: e.target.checked,
      }));
    } else {
      setState((prevState) => ({
        ...prevState,
        [name]: value,
      }));
    }
  };

  const [factoryId, setFactoryId] = useState(0);
  const handleChangeFactory = (e) => {
    let i;
    console.log(e.target.value);
    for (var j = 0; j < playerID.length; j++) {
      if (e.target.value === playerID[j].email) {
        i = playerID[j].id;
      }
    }
    setFactoryId(i);
  };

  const [distributorId, setDistributorId] = useState(0);
  const handleChangeDistributor = (e) => {
    let i;
    console.log(e.target.value);
    for (var j = 0; j < playerID.length; j++) {
      if (e.target.value === playerID[j].email) {
        i = playerID[j].id;
      }
    }
    setDistributorId(i);
  };

  const [wholesalerId, setWholesalerId] = useState(0);
  const handleChangeWholesaler = (e) => {
    let i;
    console.log(e.target.value);
    for (var j = 0; j < playerID.length; j++) {
      if (e.target.value === playerID[j].email) {
        i = playerID[j].id;
      }
    }
    setWholesalerId(i);
  };

  const [retailerId, setRetailerId] = useState(0);
  const handleChangeRetailer = (e) => {
    let i;
    console.log(e.target.value);
    for (var j = 0; j < playerID.length; j++) {
      if (e.target.value === playerID[j].email) {
        i = playerID[j].id;
      }
    }
    setRetailerId(i);
  };

  const sendDetailsToServer = () => {
    //checking for validation of demand pattern
    var arr = demand_pattern.encoded_data.split(",").map(Number);
    console.log(arr);
    console.log(state.session_length);
    if (arr.length !== parseInt(state.session_length)) {
      alert(
        "The number of integers you put in demand pattern information should be equal to Session length and please divide the numbers with comma"
      );
      return;
    } else {
      for (let i = 0; i < arr.length; i++) {
        // check if array value is NaN
        if (Number.isNaN(arr[i])) {
          console.log("NaN found at place " + i);
          alert("The demand pattern information should only include numbers");
          return;
        }
      }
    }
    if(factoryId === distributorId || factoryId === wholesalerId || factoryId === retailerId || distributorId === wholesalerId || distributorId === retailerId){
        alert("Please pick different players for different roles")
        return;
    }
    if(retailerId === wholesalerId && retailerId !== 0 && wholesalerId !==0){
        alert("Please pick different players for different roles")
        return;
    }
    axios
      .post("http://0.0.0.0:8086/instructor/add_demand_patterns", {
        name: demand_pattern.name,
        encoded_data: demand_pattern.encoded_data,
      })
      .then((response) => {
        console.log(response.data.demand_pattern);
        state.demand_id = response.data.demand_pattern;
        alert("added a demand pattern with id " + state.demand_id);
        axios
          .post(
            "http://0.0.0.0:8086/instructor/game",
            {
              session_length: parseInt(state.session_length),
              retailer_present: state.retailer_present,
              wholesaler_present: state.wholesaler_present,
              holding_cost: parseInt(state.holding_cost),
              backlog_cost: parseInt(state.backlog_cost),
              active: true,
              starting_inventory: parseInt(state.starting_inventory),
              info_delay: parseInt(state.info_delay),
              info_sharing: state.info_sharing,
              demand_pattern_id: parseInt(state.demand_id),
            },
            {
              headers: {
                "SESSION-KEY": Cookies.get("SESSION-KEY"),
              },
            }
          )
          .then((response) => {
            console.log(response.data);
            alert(
              "Success, game with id" + response.data.game_id + " is created"
            );
            axios
              .post(
                "http://0.0.0.0:8086/instructor/add_player_to_game",
                {
                  factory_id: parseInt(factoryId),
                  distributor_id: parseInt(distributorId),
                  wholesaler_id: parseInt(wholesalerId),
                  retailer_id: parseInt(retailerId),
                  game_id: response.data.game_id,
                },
                {
                  headers: {
                    "SESSION-KEY": Cookies.get("SESSION-KEY"),
                  },
                }
              )
              .then((response) => {
                console.log(response.data);
                alert("you've added players successfully");
                history.push("/instructor");
              })
              .catch((error) => {
                console.log(error.response);
                setState((prevState) => ({
                  ...prevState,
                  error_message: "this is an error message",
                }));
              });
          })
          .catch((error) => {
            console.log(error.response);
            setState((prevState) => ({
              ...prevState,
              error_message: "this is an error message",
            }));
          });
      })
      .catch((error) => {
        console.log(error.response);
        setState((prevState) => ({
          ...prevState,
          error_message: "this is an error message",
        }));
      });
  };

  //you firstly wait for data about players not playing
  if (playerID === null) {
    return <p>Loading</p>;
  }

  const retailer = state.retailer_present ? (
    <div>
      {" "}
      <p>
        <label className="label">Add Retailer: </label>
        <select name="retailer" onChange={handleChangeRetailer}>
          <option value="">Choose a player</option>
          {availablePlayers()}
        </select>
      </p>
    </div>
  ) : null;

  const wholesaler = state.wholesaler_present ? (
    <div>
      {" "}
      <p>
        <label className="label">Add Wholesaler: </label>
        <select name="distributor" onChange={handleChangeWholesaler}>
          <option value="">Choose a player</option>
          {availablePlayers()}
        </select>
      </p>{" "}
    </div>
  ) : null;

  return (
    <div className="body">
      <center>
        <div className="top-bar1">
          <span>Create Game</span>
        </div>
        <div className="form">
          <div>
            <p>
              <label className="label">
                Session Length:
                <input
                  type="number"
                  name="session_length"
                  value={state.session_length}
                  onChange={handleChange}
                  required
                />
              </label>
            </p>

            <fieldset>
              <label className="label">Include:</label>
              <p>
                <label className="label">
                  {" "}
                  <input
                    type="checkbox"
                    name="retailer_present"
                    checked={state.retailer_present === true}
                    onChange={handleChange}
                  />{" "}
                  Retail{" "}
                </label>
              </p>
              <p>
                <label className="label">
                  {" "}
                  <input
                    type="checkbox"
                    name="wholesaler_present"
                    checked={state.wholesaler_present === true}
                    onChange={handleChange}
                  />{" "}
                  Wholesaler
                </label>
              </p>
            </fieldset>

            <p>
              <label className="label">
                Holding cost:
                <input
                  type="number"
                  name="holding_cost"
                  value={state.holding_cost}
                  onChange={handleChange}
                  required
                />
              </label>
            </p>

            <p>
              <label className="label">
                Backlog cost:
                <input
                  type="number"
                  name="backlog_cost"
                  value={state.backlog_cost}
                  onChange={handleChange}
                  required
                />
              </label>
            </p>

            <p>
              <label className="label">
                Starting Inventory:
                <input
                  type="number"
                  name="starting_inventory"
                  value={state.starting_inventory}
                  onChange={handleChange}
                  required
                />
              </label>
            </p>

            <p>
              <label className="label">
                Information delay:
                <input
                  type="number"
                  name="info_delay"
                  value={state.info_delay}
                  onChange={handleChange}
                  required
                />
              </label>
            </p>

            <p>
              <label className="label">
                Demand Pattern Name:
                <input
                  type="text"
                  name="name"
                  value={demand_pattern.name}
                  onChange={handleChangeDemand}
                  required
                />
              </label>
            </p>

            <p>
              <p className="explanation">
                Your input should be numbers divided by a comma, so if
                session_length=3, then an example of a valid input should be
                1,2,3
              </p>
              <label className="label">
                Demand Pattern Information:
                <input
                  type="text"
                  name="encoded_data"
                  value={demand_pattern.encoded_data}
                  onChange={handleChangeDemand}
                  required
                />
              </label>
            </p>

            <p>
              <label className="label">Add Factory: </label>
              <select name="factory" onChange={handleChangeFactory}>
                <option value="">Choose a player</option>
                {availablePlayers()}
              </select>
            </p>

            <p>
              <label className="label">Add Distributor: </label>
              <select name="distributor" onChange={handleChangeDistributor}>
                <option value="">Choose a player</option>
                {availablePlayers()}
              </select>
            </p>

            {wholesaler}
            {retailer}

            <p>
              <label className="label">
                {" "}
                <input
                  type="checkbox"
                  name="info_sharing"
                  checked={state.info_sharing === true}
                  onChange={handleChange}
                />{" "}
                Information Sharing{" "}
              </label>
            </p>
            <center>
              <p>
                <button onClick={sendDetailsToServer}>Submit</button>
              </p>
            </center>
          </div>
        </div>
      </center>
    </div>
  );
}
