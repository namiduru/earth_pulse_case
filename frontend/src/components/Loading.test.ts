import { render, screen } from "@testing-library/svelte";
import { describe, it, expect } from "vitest";
import Loading from "./Loading.svelte";

describe("Loading Component", () => {
  it("renders with default props", () => {
    render(Loading);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("h-6", "w-6"); // default md size
  });

  it("renders with custom text", () => {
    render(Loading, { props: { text: "Please wait..." } });

    expect(screen.getByText("Please wait...")).toBeInTheDocument();
  });

  it("renders with empty text", () => {
    render(Loading, { props: { text: "" } });

    expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
  });

  it("applies correct size classes for small size", () => {
    render(Loading, { props: { size: "sm" } });

    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toHaveClass("h-4", "w-4");
  });

  it("applies correct size classes for medium size", () => {
    render(Loading, { props: { size: "md" } });

    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toHaveClass("h-6", "w-6");
  });

  it("applies correct size classes for large size", () => {
    render(Loading, { props: { size: "lg" } });

    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toHaveClass("h-8", "w-8");
  });

  it("has correct container styling", () => {
    render(Loading);

    const container = document.querySelector(".loading-container");
    expect(container).toHaveClass("text-center");
  });

  it("has correct spinner styling", () => {
    render(Loading);

    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toHaveClass(
      "inline-block",
      "animate-spin",
      "rounded-full",
      "border-b-2",
      "border-blue-600"
    );
  });
});
