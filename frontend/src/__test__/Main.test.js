import { render,fireEvent } from '@testing-library/react';
import Main from '../components/Main';

it("renders ", () => {
    render(<Main />);
  });

it("checkButtonrender", () =>{
    const { queryByTitle } = render(<Main />);
    const btn = queryByTitle("dummybutton");
    expect(btn).toBeTruthy();
});

describe ("clickButton", ()=>{
    it("onClick", () => {
        const {queryByTitle} = render(<Main />);
        const button = queryByTitle("dummybutton");
        fireEvent.click(button);
    });
});

