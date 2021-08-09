import React, {  useState, useEffect } from "react";
import axios from "axios";
import Cookies from "js-cookie";
import Modal from "react-modal";

export default function EditMeetup(props) {
  const { gameid } = props;
  const [ModalIsOpen, setModalIsOpen] = useState(false);
  function fun1(){
    setModalIsOpen(false)
  }

  function fun2(id){
      editMeetup()
  }

  function callBoth(){
      fun1()
      fun2()
  }
  const [state, setState] = useState({
    session_length:"",
    holding_cost: "",
    backlog_cost:"",
    active: true,
    starting_inventory:"",
    info_delay:"",
    info_sharing:false,
})


useEffect(() => {
    axios.get("http://0.0.0.0:8086/instructor/game/" + gameid, {
      headers: {
        "SESSION-KEY": Cookies.get("SESSION-KEY"),
      },
    })
      .then((response) => {
        console.log(response.data)
        var info_sharing
        response.data.info_sharing === 1 ? info_sharing = true : info_sharing=false;

        setState(
          {
            session_length: response.data.session_length,
            holding_cost: response.data.holding_cost,
            backlog_cost: response.data.backlog_cost,
            active: response.data.active,
            starting_inventory: response.data.starting_inventory,
            info_delay: response.data.info_delay,
            info_sharing: info_sharing,
          },
        );
      })
      .catch((err) => console.log(err));
}, [setState])

  const editMeetup = () => {
    console.log(state)
    axios.put('http://0.0.0.0:8086/instructor/modify_game/' + gameid, 
    {
        "session_length": parseInt(state.session_length),
        "holding_cost": parseInt(state.holding_cost),
        "backlog_cost": parseInt(state.backlog_cost),
        "active": true,
        "starting_inventory": parseInt(state.starting_inventory),
        "info_delay":parseInt(state.info_delay),
        "info_sharing":state.info_sharing,
    },
    {
        headers: {
            "SESSION-KEY": Cookies.get('SESSION-KEY')
        }
    })
    .then(response => {
        console.log(response.data)
        alert("Success, game with id " + gameid + " is updated")
        window.location = "/instructor-dashboard"
        window.location.reload()
    })
    .catch(error => {
        console.log(error.response)
        setState(prevState=>({
            ...prevState,
            error_message: "this is an error message"
        }))
    });
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    if(name === "info_sharing")
    { 
        setState(prevState => ({
            ...prevState,
            [name]: e.target.checked
        }))
    }
    else{
        setState(prevState => ({
            ...prevState,
            [name]: value
        }))
    }
}
    return (
      <div>
      <button
                type="btn btn-primary"
                onClick={() => setModalIsOpen(true)}
              >
                Edit
              </button>
            <Modal
              ariaHideApp={false}
              isOpen={ModalIsOpen}
              shouldCloseOnOverlayClick={false}
              onRequestClose={() => setModalIsOpen(false)}
              style={{
                overlay: {
                  backgroundColor: 'white',
                  height: 600,
                  width: 600,
                  left: '50%',
                },
                content: {
                  color: 'blue',
                }
              }}
            >
              <p>
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
                  </div>
                </div>
              </p>
              <div>
                <button onClick={callBoth}>Update</button>
                <button style={{margin:40 }} onClick={() => setModalIsOpen(false)} >Cancel</button>
              </div>
            </Modal> 
      </div>
  )}


