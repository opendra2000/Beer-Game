import LoginForm from "./LoginForm";
import React from "react";
import Adapter from "enzyme-adapter-react-16";
import { configure, shallow } from "enzyme";
configure({ adapter: new Adapter() });

describe("<Login />", () => {

  const wrapper = shallow(
    <LoginForm.WrappedComponent/>
);

it('snapshot test', () => {
  expect(wrapper).toMatchSnapshot();
})

  it("should have input for email and password ", () => {
    //Email and password input field should be present
    expect(wrapper.find('input#email')).toHaveLength(1);
    expect(wrapper.find('input[type="password"]')).toHaveLength(1);
  });

  it("should have one button for logging in", () => {
    //Email and password input field should be present
    expect(wrapper.find('button[type="submit"]')).toHaveLength(1);
  });
  
});


// describe("<Login />", () => {
//   it("renders correctly", () => {
//     shallow(<LoginForm />);
//     <LoginForm.WrappedComponent/>
//   });
