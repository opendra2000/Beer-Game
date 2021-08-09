import RegistrationForm from "../components/Forms/RegistrationForm";
import React from "react";
import { shallow } from "enzyme";

describe("<RegistrationForm />", () => {
  const wrapper = shallow(<RegistrationForm.WrappedComponent />);
  it("snapshot test", () => {
    expect(wrapper).toMatchSnapshot();
  });
  it("should have input for fullname,email, and password", () => {
    //Email and password input field should be present
    expect(wrapper.find('input[type="text"]')).toHaveLength(1);
    expect(wrapper.find('input[type="email"]')).toHaveLength(1);
    expect(wrapper.find('input[type="password"]')).toHaveLength(2);
  });

  it("should have one button for registration", () => {
    expect(wrapper.find('button[type="submit"]')).toHaveLength(1);
  });
});
