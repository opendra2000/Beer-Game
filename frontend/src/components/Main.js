import { useEffect } from "react";
import Cookies from "js-cookie";
import { useHistory } from "react-router-dom";
import "./Main.css";

export default function Main() {
  const history = useHistory();
  useEffect(() => {
    let i;
    Cookies.get("SESSION-KEY") !== undefined
      ? Cookies.remove("SESSION-KEY")
      : (i = 0);
  }, []);
  return (
    <div>
      <div
        id="wallpaper"
        className="wallpaper"
        data-image="wallpaper.jpg"
      ></div>
      <div className="content">
        <aside className="side">
          <figure id="picture" className="picture">
            <img
              id="pictureImage"
              className="picture-image"
              src="images/beer_img.png"
              alt="Beer emoji"
              width="500"
              height="500"
            />
          </figure>
        </aside>
        <main className="about">
          <h1 className="name">Beer Game</h1>
          <p className="sub">Learn about Supply Chain</p>
          <hr className="hr" />

          <div className="description">
            <p>
              The Beer Game illustrates how difficult it is to manage dynamic
              systems, in particular supply chains. It was originally developed
              in the late 1950s by Jay Forrester at MIT to introduce the
              concepts of dynamical systems. This website's purpose is to learn about the
              effect of different playing strategies through games. <br />
            </p>
          </div>
          <div id="contact" className="contact">
            <p>
              Please register to start playing.
              <br />
              If you already have an account, proceed to <br />
              Login page.
            </p>
            <div id="buttons" title="dummybutton">
              <a id="button-1" href="/register" className="button">
                Register
              </a>
              <a
                id="button-2"
                data-testid="button-2"
                href="/login"
                className="button"
              >
                Login
              </a>
            </div>
            <p>
              Don't know how to play? Check <a href="\tutorial">here</a> for a quick video to learn more about it.
              <br />
              Note that this video is not made by us, full credits go to <a href="https://www.youtube.com/channel/UCKzzVQyfPCXB1RD5nl31eoA">Min Xiang</a>
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
