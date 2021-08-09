import './player.css';
import {useEffect, useState} from 'react';
import Cookies from 'js-cookie';
import {useHistory} from 'react-router-dom'
import axios from "axios";

export default function Player_view() {
    const history = useHistory();
    const [currentgameId, setCurrentGameId] = useState(null);

    const [state, setState] = useState(null);

    useEffect(()=> {
        let i;
        Cookies.get('SESSION-KEY') === undefined ? history.push("/login") : i=0;
        axios
        .get("http://0.0.0.0:8086/player/current_game", {
          headers: {
            "SESSION-KEY": Cookies.get("SESSION-KEY"),
          },
        })
        .then((response) => {
          console.log(response.data);
          setCurrentGameId(response.data);
          console.log(currentgameId[0])
          if(currentgameId !== -1)
          {
            axios
          .get("http://0.0.0.0:8086/player/game/" + currentgameId[0], {
            headers: {
              "SESSION-KEY": Cookies.get("SESSION-KEY"),
            },
          })
          .then((response) => {
            setState(response.data);
            console.log(state)
          })
          .catch((error) => {
            console.log(error.response);
          });
        }}).catch((error) => {
            console.log(error.response);
          });
  }, [setCurrentGameId], [setState])
 
  if (state === null) {
    return <p>Loading</p>;
  }

  const upstreamPlayer = () => {
      let upstreamplayer;
      if(currentgameId[1] === "factory") upstreamplayer="NA";
      if(currentgameId[1] === "distributor") upstreamplayer="Factory";
      if(currentgameId[1] === "wholesaler") upstreamplayer="Distributor";
      if(currentgameId[1] === "retailer") upstreamplayer="Wholesaler";
      return upstreamplayer;
  }

  const downstreamPlayer = () => {
    let downstreamplayer;
    if(currentgameId[1] === "factory") downstreamplayer="Distributor";
    if(currentgameId[1] === "distributor") downstreamplayer="Wholesaler";
    if(currentgameId[1] === "wholesaler") downstreamplayer="Retailer";
    if(currentgameId[1] === "retailer") downstreamplayer="NA";
    return downstreamplayer;
}


    return(
        <div className="main-container">
            <div className="row-1">
                <div className="section-1">
                    <h1 className="titles-special mb-3">{currentgameId[1]} - GAME {state.id} - WEEK 1</h1>
                    <h2 className="titles mb-5">INPUT SCREEN</h2>
                    <div className="section-1-table mb-5">  
                        <table className="table-input-screen px-2 py-4">
                            <tbody>
                                <tr>
                                    <td className="table-cell">
                                        Demand from Customer:
                                    </td>
                                    <td className="numbers border-right">4</td>
                                    <td className="table-cell">
                                        Beginning Inventory: 
                                    </td>
                                    <td className="numbers">{state.starting_inventory}</td>
                                </tr>
                                <tr className="second-row">
                                    <td className="table-cell">
                                        Backlog:
                                    </td>
                                    <td className="numbers border-right">0</td>
                                    <td className="table-cell">
                                        Incomings Shipment:
                                    </td>
                                    <td className="numbers">0</td>
                                </tr>
                                <tr>
                                    <td className="table-cell">
                                        Total Requirements:
                                    </td>
                                    <td className="numbers border-right">4</td>
                                    <td className="table-cell">
                                        Total Available:
                                    </td>
                                    <td className="numbers">5</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div>
                        <p className="mb-3 p-0">Place your order:</p>
                        <div id="input-order" className="form-group">
                            <input className="mr-3 form-control" type="text"/>
                            <button className="btn btn-primary">Submit</button>
                        </div>
                    </div>
                </div>
                <div className="section-2">
                    <h1 className="titles mb-5">INFORMATION FOR ALL WEEKS - {currentgameId[1]}</h1>
                    <table className="table table-bordered">
                        <thead className="thead-dark">
                            <tr>
                                <th scope="col">Week Number</th>
                                <th scope="col">Inventory</th>
                                <th scope="col">Backlog</th>
                                <th scope="col">Demand</th>
                                <th scope="col">Incoming Shipment</th>
                                <th scope="col">Outgoing Shipment</th>
                                <th scope="col">Order Placed</th>
                                <th scope="col">Current Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{state.starting_inventory}</td>
                                <td>5</td>
                                <td>0</td>
                                <td>4</td>
                                <td>0</td>
                                <td>0</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div className="row-2">
                <div className="section-3">
                    <h1 className="mb-2 titles">STATUS OF OTHER SUPPLY CHAIN MEMBERS - WEEK 2</h1>
                    <h3 className="mb-5 sub-title">Once all players have placed an order, you can continue to next week.</h3>
                    <table className="table">
                        <thead>
                            <tr>
                                <th scope="col">Factory</th>
                                <th scope="col">Distributor</th>
                                <th scope="col">Wholesaler</th>
                                <th scope="col">Retailer</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Order not placed yet</td>
                                <td>Order not placed yet</td>
                                <td>Order placed</td>
                                <td>Order placed</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div className="section-4">
                    <h1 className="mb-5 titles">INVENTORY AND STATUS PLOTS - {currentgameId[1]}</h1>
                    <div>
                        <button className="btn btn-primary mr-2">Incoming Shipment</button>
                        <button className="btn btn-primary mr-2">Outgoing Shipment</button>
                        <button className="btn btn-primary mr-2">Inventory</button>
                        <button className="btn btn-primary mr-2">Demand</button>
                        <button className="btn btn-primary mr-2">Order</button>
                        <button className="btn btn-primary mr-2">Plot All</button>
                    </div>
                    <h5 className=" mt-5 mb-3">SUPPLY CHAIN SETTINGS - Retailer</h5>
                    <div className="group">
                        <p className="mb-0 p-0 mr-3">Holding cost: </p>
                        <p className="numbers mb-0 p-0">1</p>
                    </div>
                    <div className="group">
                        <p className="mb-0 p-0 mr-3">Backorder cost: </p>
                        <p className="numbers mb-0 p-0">1</p>
                    </div>
                    <div className="group">
                        <p className="mb-0 p-0 mr-3">Downstream Player: </p>
                        <p className="numbers mb-0 p-0">{downstreamPlayer()}</p>
                    </div>
                    <div className="group">
                        <p className="mb-0 p-0 mr-3">Upstream Player: </p>
                        <p className="numbers mb-0 p-0">{upstreamPlayer()}</p>
                    </div>
                    <div className="group">
                        <p className="mb-0 p-0 mr-3">Shipping Delay: </p>
                        <p className="numbers mb-0 p-0">2 weeks</p>
                    </div>
                    <div className="group">
                        <p className="mb-0 p-0 mr-3">Information Delay: </p>
                        <p className="numbers mb-0 p-0">{state.info_delay} weeks</p>
                    </div>
                </div>
            </div>
        </div>
    )
}