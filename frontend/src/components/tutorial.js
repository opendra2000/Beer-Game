import React from 'react';
import { withRouter } from "react-router-dom";
import {Link } from "react-router-dom";
import './Main.css'
function Tutorial(props) {
    return (
        <div align="center" className="dis-container">
        <iframe width="900" height="600" src="https://www.youtube.com/embed/e03mW4FUeTg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            <Link to="/"> <button className="button">Go back</button>
            </Link>
        </div>
    );
}

export default withRouter(Tutorial)