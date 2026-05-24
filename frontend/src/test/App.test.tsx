import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { App } from "@/app/App";

vi.mock("@/pages/LandingPage", () => ({
  LandingPage: () => <div>Landing Route</div>,
}));

vi.mock("@/pages/ChatPage", () => ({
  ChatPage: () => <div>Chat Route</div>,
}));

vi.mock("@/pages/DashboardPage", () => ({
  DashboardPage: () => <div>Dashboard Route</div>,
}));

describe("App", () => {
  it("renders the JARVIS heading", async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>,
    );

    expect((await screen.findAllByText(/JARVIS/i))[0]).toBeInTheDocument();
  });
});
