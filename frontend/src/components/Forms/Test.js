import React, { useState } from 'react';
import './Forms.css';
import logo from './beergamelogo.png';

// https://getbootstrap.com/docs/4.3/components/forms/
// in react we use className to give class to certain tag instead of class since it follows the rules of jsx code not HTML

function LoginForm(props) {

    const [state, setState] = useState({
        email: "",
        password: ""
    })
    const handleChange = (e) => {
        const { id, value } = e.target
        setState(prevState => ({
            ...prevState,
            [id]: value
        }))
    }

    // need to complete this code
    const redirectToRegistration = () => {
        props.updateTitle('Register')
        props.history.push('/Register'); 
    }

    //need to write server side code to check login data from the database

    return (
        <div className="card col-12 col-lg-4 login-card mt-2 hv-center">
            <form>
                <img class="mb-4" src={logo} alt="" width="72" height="72"/>
                <div className="form-group text-left">
                    <label htmlFor="exampleInputEmail1">Email address</label>
                    <input type="email" className="form-control" id="email" aria-describedby="emailHelp" placeholder="Enter email" value={state.email} onChange={handleChange} required/>
                </div>

                <div className="form-group text-left">
                    <label htmlFor="exampleInputPassword1">Password</label>
                    <input type="password" className="form-control" id="password" placeholder="Password" value={state.password} onChange={handleChange} required/>
                </div>

                <button type="submit" className="btn btn-primary"> Login </button>

                <div className="mt-2">
                    <span>Do not have an account? </span>
                    <span className="RegisterHere" onClick={() => redirectToRegistration()}>Register here</span>
                </div>

            </form>
        </div>
    )
}
export default LoginForm;