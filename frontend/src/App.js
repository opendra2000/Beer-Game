import './App.css';
import LoginForm from './components/Forms/LoginForm';
import RegistrationForm from './components/Forms/RegistrationForm';
import MainPage from './components/Main';
import Tutorial from './components/tutorial';
import InstructorDashboard from './components/instructor/Instructor_dashboard';
import CreateGame from './components/instructor/create-game';
import PlayerWelcome from './components/player/player_welcome';
import Player from './components/player/player.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';


import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";

function App() {

  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/" exact={true}>
            <MainPage />
          </Route>
          <Route path="/register">
            <RegistrationForm/>
          </Route>
          <Route path="/login">
            <LoginForm/>
          </Route>
          <Route path="/instructor">
            <InstructorDashboard/>
          </Route>
          <Route path="/create-game">
            <CreateGame/>
          </Route>
          <Route path="/player">
            <Player/>
          </Route>
          <Route path="/tutorial">
            <Tutorial/>
          </Route>
          <Route path="/player-welcome">
            <PlayerWelcome/>
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
