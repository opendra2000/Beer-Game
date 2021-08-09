import { useHistory } from "react-router-dom";
import "./Instructor_dashboard.css";
import { useEffect } from "react";
import Cookies from "js-cookie";
import axios from "axios";
import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBeer } from "@fortawesome/free-solid-svg-icons";
import EditMeetup from "./EditMeetup.js";

export default function Dashboard() {
  const history = useHistory();
  let j = 0;

  const [rows, setRows] = useState(null);
  useEffect(() => {
    Cookies.get("SESSION-KEY") === undefined
      ? history.push("/login")
      : history.push("/instructor");
      axios
          .get("http://0.0.0.0:8086/instructor/game", {
            headers: {
              "SESSION-KEY": Cookies.get("SESSION-KEY"),
            },
          })
          .then((response) => {
            setRows(response.data);
          })
          .catch((error) => {
            console.log(error.response);
          });
  }, [setRows]);
 

  const renderRow = () => {
    if (rows !== null) {
      return rows.map((item) => {
        j++;
        return (
          <tr key={item.id}>
            <td>{j}</td>
            <td>{item.session_length}</td>
            <td>{item.retailer_present === 1 ? "Yes" : "No"}</td>
            <td>{item.wholesaler_present === 1 ? "Yes" : "No"}</td>
            <td>{item.holding_cost}</td>
            <td>{item.backlog_cost}</td>
            <td>{item.starting_inventory}</td>
            <td>{item.active === 1 ? "Yes" : "No"}</td>
            <td>{item.info_delay}</td>
            <td>{item.info_sharing === 1 ? "Yes" : "No"}</td>
            <td>
              <EditMeetup gameid={item.id} />
            </td>
          </tr>
        );
      });
    }
  };

  const addGame = () => {
    history.push("/create-game");
  };

  const logout = () => {
    Cookies.remove("SESSION-KEY");
    history.push("/login");
  };

  return (
    <div className="body">
      <nav className="navbar navbar-expand-lg">
        <div className="container">
          <div id="brand">
            <FontAwesomeIcon icon={faBeer} />
            <a class="navbar-brand ml-2" href="/">
              Your games
            </a>
          </div>
          <div className="navbar-nav">
            <a className="nav-link active" href="#">
              Account Settings
            </a>
            <a className="nav-link active" onClick={logout}>
              Logout
            </a>
          </div>
        </div>
      </nav>
      <div>
        <div className="container">
          <div className="buttons">
            <button type="btn btn-primary btn-lg" onClick={addGame}>
              Create Game
            </button>
          </div>
          <table className="table table-striped table-bordered">
            <thead>
              <tr>
                <th scope="col">Games</th>
                <th scope="col">Session Length</th>
                <th scope="col">Retailer</th>
                <th scope="col">Wholesaler</th>
                <th scope="col">Holding Cost</th>
                <th scope="col">Backlog Cost</th>
                <th scope="col">Starting Inventory</th>
                <th scope="col">Active Game</th>
                <th scope="col">Info Delay</th>
                <th scope="col">Info Sharing</th>
                <th scope="col">Edit Game</th>
              </tr>
            </thead>
            <tbody>{renderRow()}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
