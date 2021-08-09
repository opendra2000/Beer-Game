import React, { useState } from 'react';
import './Forms.css';
import {useHistory} from 'react-router-dom';
import logo from './beergamelogo.png';
import { withRouter } from "react-router-dom";
import { useEffect } from 'react';
import Cookies from 'js-cookie';
import axios from "axios";
const login_backend = 'http://localhost:8086'



// https://getbootstrap.com/docs/4.3/components/forms/
// in react we use className to give class to certain tag instead of class since it follows the rules of jsx code not HTML

function LoginForm(props) {
    const history = useHistory();
    useEffect(()=> {
        Cookies.get('SESSION-KEY') !== undefined ? Cookies.remove('SESSION-KEY') : history.push("/login");
    }, [])
    const [state, setState] = useState({
        email: "",
        password: "",
        user_type:"",
        error_message: ""
    })
    const handleChange = (e) => {
        const { name, value } = e.target
        setState(prevState => ({
            ...prevState,
            [name]: value
        }))
    }
    function loginfailed(){
        setState(prevState => ({
            ...prevState,
            password: "",
            error_message: 'error: invalid username / password. Please try again'
        }))
    }

    async function handleLogin(e){
        console.log(state.user_type)
        if(state.email==='' || state.password==='')
        {
            alert("you have to provide an email and password to sign in");
            return;
        }
        e.preventDefault();
        console.log(JSON.stringify(state));
        console.log("handling login")
        // TA's are not letting us use jquery for now so . . .
        const {email, password, user_type} = state;
        var xhr = new XMLHttpRequest();
        xhr.open('POST', login_backend + '/authenticate', true);
        xhr.setRequestHeader('Content-Type', "application/json;charset=UTF-8");
        xhr.onload= async function(){
            switch(xhr.status){
                case 400:
                    console.log(xhr.responseText)
                    loginfailed()
                    break;
                case 200:
                    console.log(xhr.responseText)
                    let r = JSON.parse(xhr.responseText);
                    let s_key = r['SESSION-KEY']
                    document.cookie = `SESSION-KEY=${s_key};path='/'`
                    alert("success: "+ document.cookie)
                    axios.get("http://0.0.0.0:8086/instructor/check_instructor", {
                      headers: {
                        "SESSION-KEY": Cookies.get("SESSION-KEY"),
                      },
                    })
                    .then((response) => {
                        props.history.push('/instructor');
                    })
                    .catch((error) => {
                        props.history.push('/player-welcome');
                    });
                    

                    break;
                default:
                    alert('an unexpected error occurred, please debug');
                    console.log(xhr.responseText)

            }
        }
        let b = JSON.stringify({
            passwordHash: password,
            email: email, 
             
            role: user_type
        })
        console.log("LOGGING XHR . . .")
        console.log(b);
        xhr.send(b);

    }

    // need to complete this code
    const redirectToRegistration = () => {
        props.history.push('/register'); 
    }

    console.log(state);
    //need to write server side code to check login data from the database

    return (
        <div align="center" className="body-form">
            <form className="form-signin">
                <img className="mb-4" src={logo} alt="" width="72" height="72"/>
                <h1 className="h3 mb-3 font-weight-normal">Please sign in</h1>

                <div>
                    <label htmlFor="InputEmail1" className="sr-only" >Email address</label>
                    <input type="email" className="form-control" id="email" name="email" aria-describedby="emailHelp" placeholder="Enter email" value={state.email} onChange={handleChange} required/>
                </div>

                <div>
                    <label htmlFor="InputPassword1" className="sr-only">Password</label>
                    <input type="password" className="form-control" id="password" name="password" placeholder="Password" value={state.password} onChange={handleChange} required/>
                </div>
                { state.error_message &&
                        <span className="error"> { state.error_message } </span> }

                <div className="checkbox mb-3">
                    <input type="checkbox" value="remember-me"/> 
                    <label> Remember me </label>
                </div>

                <button title="dummybuttoon" type="submit" className="btn btn-lg btn-primary btn-block" onClick={handleLogin}> Login </button>

                <div className="mt-2">
                    <span>Do not have an account? </span>
                    <span className="RegisterHere" onClick={() => redirectToRegistration()}>Register here</span>
                </div>

            </form>
        </div>
    )
}
export default withRouter(LoginForm);