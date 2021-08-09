import React, { useState } from "react";
import { Tabs } from "@feuer/react-tabs";
import { useEffect } from "react";
import Cookies from "js-cookie";
import { useHistory } from "react-router-dom";
import "./player_dashboard.css";
import axios from "axios";

export default function Player() {
  const history = useHistory();
  const [currentgameId, setCurrentGameId] = useState(null);
  //
  useEffect(() => {
    let i;
    Cookies.get("SESSION-KEY") === undefined ? history.push("/login") : (i = 0);
    axios
      .get("http://0.0.0.0:8086/player/current_game", {
        headers: {
          "SESSION-KEY": Cookies.get("SESSION-KEY"),
        },
      })
      .then((response) => {
        console.log(response.data);
        setCurrentGameId(response.data);
      })
      .catch((error) => {
        console.log(error.response);
      });
  }, [setCurrentGameId]);

  const [state, setState] = useState({
    session_length: "",
    retailer_present: "",
    wholesaler_present: "",
    holding_cost: "",
    backlog_cost: "",
    active: true,
    starting_inventory: "",
    info_delay: "",
    info_sharing: "",
  });

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
  console.log(state);
  const [join_game, setJoinGame] = useState({
    email: "",
    code: "",
  });
  const handleJoinGame = (e) => {
    const { id, value } = e.target;
    setJoinGame((prevState) => ({
      ...prevState,
      [id]: value,
    }));
  };

  const handleSubmitClick = (e) => {
    e.preventDefault();
    const payload = {
      email: join_game.email,
      code: join_game.code,
    };
    history.push("/player");
  };

  const logout = () => {
    Cookies.remove("SESSION-KEY");
    history.push("/login");
  };

  if (currentgameId === null) {
    return <p>Loading</p>;
  }

  const joinGame =
    currentgameId === -1 ? (
      <div>
        <p>
          You haven't been assigned to any game at the moment. Please ask your
          instructor to assign you to a game and reload the page.
        </p>
        <hr />
        <div className="buttonsContainer">
          <div>
              <div id="submit-button">
              <button
                type="submit"
                className="btn btn-primary"
                onClick={logout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    ) : ( 
      <div>
        <p>
          You have been assigned to game with id {currentgameId[0]} in the role of {currentgameId[1]}. Please click
          the button below to start playing.
          <hr />
          <div className="buttonsContainer">
            <div id="submit-button">
              <button
                type="submit"
                className="btn btn-primary mb-4"
                onClick={handleSubmitClick}
              >
                Join Game
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                onClick={logout}
              >
                Logout
              </button>
            </div>
          </div>
        </p>
      </div>
    );

  return (
    <div id="parent" class="col-12">
      <div class="box">
        <div className="welcome-page col-lg-10 hv-center">
          <Tabs
            tabsProps={{
              style: {
                textAlign: "left",
              },
            }}
            activeTab={{
              id: "tab1",
            }}
          >
            <div class="tabs">
              <Tabs.Tab id="tab1" title="Join games">
                <div className="join-games">{joinGame}</div>
              </Tabs.Tab>
              <Tabs.Tab id="tab2" title="Create games">
                <div class="container create-game">
                  <label id="rounds-title">Session Length</label>
                  <input
                    type="number"
                    className="form-control"
                    id="friend-text"
                    name="session_length"
                    value={state.session_length}
                    onChange={handleChange}
                    min="1"
                    max="24"
                  />
                  <hr id="hr-create-game" />
                  <label id="inventory-title">Players Present</label>
                  <fieldset>
                    <p class="checkboxes">
                      <label>
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
                    <p class="checkboxes">
                      <label>
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
                  <hr id="hr-create-game" />
                  <label id="cost-title">Costs</label>
                  <div class="invite-friends">
                    <label id="costs">Holding</label>
                    <input
                      type="text"
                      className="form-control"
                      name="holding_cost"
                      value={state.holding_cost}
                      onChange={handleChange}
                      id="friend-text"
                      placeholder="initial inventory"
                    />
                  </div>
                  <div class="invite-friends">
                    <label id="costs">Backlog</label>
                    <input
                      type="text"
                      className="form-control"
                      name="backlog_cost"
                      value={state.backlog_cost}
                      onChange={handleChange}
                      id="friend-text"
                      placeholder="initial inventory"
                    />
                  </div>
                  <hr id="hr-create-game" />
                  <label id="rounds-title">Starting inventory:</label>
                  <input
                    type="text"
                    className="form-control"
                    name="starting_inventory"
                    id="friend-text"
                    value={state.starting_inventory}
                    onChange={handleChange}
                  />
                  <hr id="hr-create-game" />
                  <label id="cost-title">Information</label>
                  <div class="invite-friends">
                    <label id="costs">Delay</label>
                    <input
                      type="text"
                      className="form-control"
                      name="info_delay"
                      value={state.info_delay}
                      onChange={handleChange}
                      id="friend-text"
                      placeholder="initial inventory"
                    />
                  </div>
                  <p class="checkboxes">
                    <label>
                      {" "}
                      <input
                        type="checkbox"
                        name="info_sharing"
                        checked={state.info_sharing === true}
                        onChange={handleChange}
                      />{" "}
                      Sharing
                    </label>
                  </p>
                  <hr id="hr-create-game" />
                  <div id="submit-button">
                    <button type="submit" className="btn btn-primary">
                      Submit
                    </button>
                  </div>
                </div>
              </Tabs.Tab>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
