import { render, screen, fireEvent } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import FileUpload from "./FileUpload.svelte";

describe("FileUpload Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders with default props", () => {
    render(FileUpload);

    const uploadZone = screen.getByRole("button");
    expect(uploadZone).toBeInTheDocument();
    expect(uploadZone).toHaveAttribute(
      "aria-label",
      "Upload files by clicking or dragging and dropping"
    );
  });

  it("renders with custom accept prop", () => {
    render(FileUpload, { props: { accept: ".pdf,.doc" } });

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    expect(fileInput).toHaveAttribute("accept", ".pdf,.doc");
  });

  it("renders with multiple prop", () => {
    render(FileUpload, { props: { multiple: true } });

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    expect(fileInput).toHaveAttribute("multiple");
  });

  it("renders with disabled prop", () => {
    render(FileUpload, { props: { disabled: true } });

    const uploadZone = screen.getByRole("button");
    expect(uploadZone).toHaveClass("disabled");
  });

  it("dispatches file event for single file upload", async () => {
    const { component } = render(FileUpload);

    const fileHandler = vi.fn();
    component.$on("file", fileHandler);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    const mockFile = new File(["test content"], "test.txt", {
      type: "text/plain",
    });

    Object.defineProperty(fileInput, "files", {
      value: [mockFile],
      writable: true,
    });

    await fireEvent.change(fileInput);

    expect(fileHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: mockFile,
      })
    );
  });

  it("dispatches files event for multiple file upload", async () => {
    const { component } = render(FileUpload, { props: { multiple: true } });

    const filesHandler = vi.fn();
    component.$on("files", filesHandler);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    const mockFiles = [
      new File(["test content 1"], "test1.txt", { type: "text/plain" }),
      new File(["test content 2"], "test2.txt", { type: "text/plain" }),
    ];

    Object.defineProperty(fileInput, "files", {
      value: mockFiles,
      writable: true,
    });

    await fireEvent.change(fileInput);

    expect(filesHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: mockFiles,
      })
    );
  });

  it("handles drag over event", async () => {
    render(FileUpload);

    const uploadZone = screen.getByRole("button");
    await fireEvent.dragOver(uploadZone);

    expect(uploadZone).toHaveClass("drag-over");
  });

  it("handles drag leave event", async () => {
    render(FileUpload);

    const uploadZone = screen.getByRole("button");
    await fireEvent.dragOver(uploadZone);
    expect(uploadZone).toHaveClass("drag-over");

    await fireEvent.dragLeave(uploadZone);
    expect(uploadZone).not.toHaveClass("drag-over");
  });

  it("handles drop event for single file", async () => {
    const { component } = render(FileUpload);

    const fileHandler = vi.fn();
    component.$on("file", fileHandler);

    const uploadZone = screen.getByRole("button");
    const mockFile = new File(["test content"], "test.txt", {
      type: "text/plain",
    });

    const dropEvent = new Event("drop", { bubbles: true });
    Object.defineProperty(dropEvent, "dataTransfer", {
      value: {
        files: [mockFile],
      },
      writable: true,
    });

    await fireEvent(uploadZone, dropEvent);

    expect(fileHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: mockFile,
      })
    );
  });

  it("handles drop event for multiple files", async () => {
    const { component } = render(FileUpload, { props: { multiple: true } });

    const filesHandler = vi.fn();
    component.$on("files", filesHandler);

    const uploadZone = screen.getByRole("button");
    const mockFiles = [
      new File(["test content 1"], "test1.txt", { type: "text/plain" }),
      new File(["test content 2"], "test2.txt", { type: "text/plain" }),
    ];

    const dropEvent = new Event("drop", { bubbles: true });
    Object.defineProperty(dropEvent, "dataTransfer", {
      value: {
        files: mockFiles,
      },
      writable: true,
    });

    await fireEvent(uploadZone, dropEvent);

    expect(filesHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: mockFiles,
      })
    );
  });

  it("does not handle drop when disabled", async () => {
    const { component } = render(FileUpload, { props: { disabled: true } });

    const fileHandler = vi.fn();
    component.$on("file", fileHandler);

    const uploadZone = screen.getByRole("button");
    const mockFile = new File(["test content"], "test.txt", {
      type: "text/plain",
    });

    const dropEvent = new Event("drop", { bubbles: true });
    Object.defineProperty(dropEvent, "dataTransfer", {
      value: {
        files: [mockFile],
      },
      writable: true,
    });

    await fireEvent(uploadZone, dropEvent);

    expect(fileHandler).not.toHaveBeenCalled();
  });

  it("handles keyboard events for accessibility", async () => {
    const { component } = render(FileUpload);

    const fileHandler = vi.fn();
    component.$on("file", fileHandler);

    const uploadZone = screen.getByRole("button");

    // Mock file input click
    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    const clickSpy = vi.spyOn(fileInput, "click");

    await fireEvent.keyDown(uploadZone, { key: "Enter" });
    expect(clickSpy).toHaveBeenCalled();

    clickSpy.mockClear();
    await fireEvent.keyDown(uploadZone, { key: " " });
    expect(clickSpy).toHaveBeenCalled();
  });

  it("has correct upload zone styling", () => {
    render(FileUpload);

    const uploadZone = screen.getByRole("button");
    expect(uploadZone).toHaveClass("upload-zone");
  });

  it("has correct upload content styling", () => {
    render(FileUpload);

    const uploadContent = document.querySelector(".upload-content");
    expect(uploadContent).toBeInTheDocument();
  });

  it("has correct upload icon", () => {
    render(FileUpload);

    const uploadIcon = document.querySelector(".upload-icon svg");
    expect(uploadIcon).toBeInTheDocument();
  });
});
