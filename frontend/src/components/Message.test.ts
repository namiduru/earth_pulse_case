import { render, screen, fireEvent } from "@testing-library/svelte";
import { describe, it, expect, vi } from "vitest";
import Message from "./Message.svelte";
import type { Message as MessageType } from "../types/file";

describe("Message Component", () => {
  const mockMessage: MessageType = {
    id: "1",
    text: "Test message",
    type: "success",
  };

  it("renders message text correctly", () => {
    render(Message, { props: { message: mockMessage } });

    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("displays correct icon for success type", () => {
    render(Message, { props: { message: mockMessage } });

    expect(screen.getByText("✓")).toBeInTheDocument();
  });

  it("displays correct icon for error type", () => {
    const errorMessage = { ...mockMessage, type: "error" as const };
    render(Message, { props: { message: errorMessage } });

    expect(screen.getByText("✕")).toBeInTheDocument();
  });

  it("displays correct icon for warning type", () => {
    const warningMessage = { ...mockMessage, type: "warning" as const };
    render(Message, { props: { message: warningMessage } });

    expect(screen.getByText("⚠")).toBeInTheDocument();
  });

  it("displays correct icon for info type", () => {
    const infoMessage = { ...mockMessage, type: "info" as const };
    render(Message, { props: { message: infoMessage } });

    expect(screen.getByText("ℹ")).toBeInTheDocument();
  });

  it("applies correct background color for success type", () => {
    render(Message, { props: { message: mockMessage } });

    const messageElement = document.querySelector(".message");
    expect(messageElement).toHaveClass(
      "bg-green-50",
      "border-green-200",
      "text-green-800"
    );
  });

  it("applies correct background color for error type", () => {
    const errorMessage = { ...mockMessage, type: "error" as const };
    render(Message, { props: { message: errorMessage } });

    const messageElement = document.querySelector(".message");
    expect(messageElement).toHaveClass(
      "bg-red-50",
      "border-red-200",
      "text-red-800"
    );
  });

  it("applies correct background color for warning type", () => {
    const warningMessage = { ...mockMessage, type: "warning" as const };
    render(Message, { props: { message: warningMessage } });

    const messageElement = document.querySelector(".message");
    expect(messageElement).toHaveClass(
      "bg-yellow-50",
      "border-yellow-200",
      "text-yellow-800"
    );
  });

  it("applies correct background color for info type", () => {
    const infoMessage = { ...mockMessage, type: "info" as const };
    render(Message, { props: { message: infoMessage } });

    const messageElement = document.querySelector(".message");
    expect(messageElement).toHaveClass(
      "bg-blue-50",
      "border-blue-200",
      "text-blue-800"
    );
  });

  it("dispatches close event when close button is clicked", async () => {
    const { component } = render(Message, { props: { message: mockMessage } });

    const closeHandler = vi.fn();
    component.$on("close", closeHandler);

    const closeButton = screen.getByLabelText("Close message");
    await fireEvent.click(closeButton);

    expect(closeHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: "1",
      })
    );
  });

  it("has correct close button styling", () => {
    render(Message, { props: { message: mockMessage } });

    const closeButton = screen.getByLabelText("Close message");
    expect(closeButton).toHaveClass(
      "text-gray-400",
      "hover:text-gray-600",
      "transition-colors"
    );
  });

  it("has correct message container styling", () => {
    render(Message, { props: { message: mockMessage } });

    const container = document.querySelector(".message-container");
    expect(container).toBeInTheDocument();
  });

  it("has correct message styling", () => {
    render(Message, { props: { message: mockMessage } });

    const messageElement = document.querySelector(".message");
    expect(messageElement).toHaveClass(
      "border",
      "rounded-lg",
      "p-4",
      "mb-3",
      "flex",
      "items-center",
      "justify-between",
      "shadow-sm"
    );
  });
});
