import React, { useState } from 'react';
import axios from 'axios';
import './Forms.css';
import logo from './beergamelogo.png';
import { useEffect } from 'react';
import Cookies from 'js-cookie';
import {useHistory} from 'react-router-dom';
import { withRouter } from "react-router-dom";
// https://getbootstrap.com/docs/4.3/components/forms/
// in react we use className to give class to certain tag instead of class since it follows the rules of jsx code not HTML

function RegistrationForm(props) {
    const history = useHistory();
    useEffect(()=> {
        console.log('im in login')
        Cookies.get('SESSION-KEY') !== undefined ? Cookies.remove('SESSION-KEY') : history.push("/register");
    }, [])
    const [state, setState] = useState({
        name:"",
        email: "",
        password: "",
        confirm_password:"",
        user_type:""
    })

    const bcrypt = require('bcryptjs')


    //this function handles all the changes made to the state variables
    const handleChange = (e) => {
        const { name, value } = e.target
        setState(prevState => ({
            ...prevState,
            [name]: value
        }))
    }
    //console.log(bcrypt.hashSync(state.password, bcrypt.genSaltSync()))
    
    const sendDetailsToServer = () => {
        axios.post('http://0.0.0.0:8086/register', 
        {
            name:state.name,
            email: state.email,
            passwordHash: state.password,
            role:state.user_type
        })
        .then(response => {
            var x = response.data
            console.log(x);
            if (x['SESSION-KEY']!==''){
                document.cookie=`SESSION-KEY=${x['SESSION-KEY']};path='/'`
                console.log(document.cookie)
                alert("Sucess: " + document.cookie)
                if(state.user_type === "player"){
                    props.history.push('/player-welcome'); 
                }
                else{
                    props.history.push('/instructor'); 
                }
            } 
            else{
                alert("Failure")
            }
        })
        .catch(error => {
            console.log(error.response)
            setState(prevState=>({
                ...prevState,
                error_message: "this email is already in use, please use a different one"
            }))
        });
    }

    const handleSubmitClick = (e) => {
        e.preventDefault();
        // prevents the default form submit action to take place
        if(state.password === state.confirm_password && state.password.length > 0) {
            sendDetailsToServer()
             
        } else {
            alert('Password should not be empty and the input in password and confirm password should match ');
        }
        
    }

    console.log(state);
    //(event.target.name,event.target.value) -> id=name; value=value (eg id(or name of the HTML property)= password)
    // i have used name property of <input> to get the variable name
    //we can also use id inplace of name s.t [id]:value but since ids are unique I could not use it with radio button so I had to use name property

    // need to complete this code
    const redirectToLogin= () => {
        props.history.push('/login'); 
    }

    //need to write server side code to check login data from the database

    return (
        <div align="center" className="body-form">
            <form className="form-signin" action="http://0.0.0.0:8086/register" method="POST">
                <img className="mb-4" src={logo} alt="" width="72" height="72"/>
                <h1 className="h3 mb-3 font-weight-normal">Please fill the details to register</h1>

                <div>
                    <label htmlFor="InputName" className="sr-only" />
                    <input type="text" className="form-control" id="name" placeholder="Enter full name" name="name" value={state.name} onChange={handleChange} required/>
                </div>

                <div>
                    <label htmlFor="InputEmail1" className="sr-only" />
                    <input type="email" className="form-control" id="email" name="email" aria-describedby="emailHelp" placeholder="Enter email" value={state.email} onChange={handleChange} required/>
                </div>

                <div>
                    <label htmlFor="InputPassword1" className="sr-only"/>
                    <input type="password" className="form-control" id="password" name="password" placeholder="Password" value={state.password} onChange={handleChange} required/>
                </div>

                <div>
                    <label htmlFor="InputPassword2" className="sr-only"/>
                    <input type="password" className="form-control" id="confirm_password" name="confirm_password" placeholder="Confirm Password" value={state.confirm_password} onChange={handleChange} required/>
                </div>

                <div className="usertype">
                    <span className="first">
                        <label>
                            <input type="radio" name="user_type" value="player" checked={state.user_type==='player'} onChange={handleChange} required/> Player
                        </label>
                     </span>
                
                    <span className="second">
                        <label>
                            <input type="radio" name="user_type" value="instructor" checked={state.user_type==='instructor'}  onChange={handleChange} />Instructor
                        </label>
                    </span>
                </div>
                { state.error_message &&
                        <span className="error"> { state.error_message } </span> }
                <button type="submit" className="btn btn-lg btn-primary btn-block" onClick={handleSubmitClick}> Register </button>
                
                <div className="mt-2">
                    <span>Already have an account? </span>
                    <span className="RegisterHere" onClick={() => redirectToLogin()}>Login here</span>
                </div>

            </form>
        </div>
    )
}
export default withRouter(RegistrationForm);