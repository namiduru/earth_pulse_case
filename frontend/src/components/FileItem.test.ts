import { render, screen, fireEvent } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import FileItem from "./FileItem.svelte";
import type { FileData } from "../types/file";

// Mock the stores
vi.mock("../stores/files", () => ({
  fileActions: {
    isSaving: vi.fn(() => false),
  },
}));

// Mock the formatters
vi.mock("../utils/formatters", () => ({
  formatFileSize: vi.fn((size) => `${size} bytes`),
  formatDate: vi.fn((date) => "formatted date"),
  getFileIcon: vi.fn(() => "📁"),
  sanitizeFilename: vi.fn((name) => name),
}));

describe("FileItem Component", () => {
  const mockFile: FileData = {
    file_id: "1",
    name: "test-file.txt",
    size: 1024,
    content_type: "text/plain",
    upload_date: "2023-01-01T00:00:00Z",
    extension: "txt",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock confirm dialog
    (window as any).confirm = vi.fn(() => true);
  });

  it("renders file information correctly", () => {
    render(FileItem, { props: { file: mockFile } });

    expect(screen.getByText("test-file.txt")).toBeInTheDocument();
    expect(screen.getByText(/1024 bytes/)).toBeInTheDocument();
    expect(screen.getByText(/formatted date/)).toBeInTheDocument();
  });

  it("displays file icon", () => {
    render(FileItem, { props: { file: mockFile } });

    const iconElement = document.querySelector(".text-lg");
    expect(iconElement).toHaveTextContent("📁");
  });

  it("dispatches download event when download button is clicked", async () => {
    const { component } = render(FileItem, { props: { file: mockFile } });

    const downloadHandler = vi.fn();
    component.$on("download", downloadHandler);

    const downloadButton = screen.getByTitle("Download");
    await fireEvent.click(downloadButton);

    expect(downloadHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: { fileId: "1", fileName: "test-file.txt" },
      })
    );
  });

  it("dispatches delete event when delete button is clicked and confirmed", async () => {
    const { component } = render(FileItem, { props: { file: mockFile } });

    const deleteHandler = vi.fn();
    component.$on("delete", deleteHandler);

    const deleteButton = screen.getByTitle("Delete");
    await fireEvent.click(deleteButton);

    expect((window as any).confirm).toHaveBeenCalledWith(
      "Are you sure you want to delete this file?"
    );
    expect(deleteHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: "1",
      })
    );
  });

  it("does not dispatch delete event when delete is cancelled", async () => {
    (window as any).confirm = vi.fn(() => false);

    const { component } = render(FileItem, { props: { file: mockFile } });

    const deleteHandler = vi.fn();
    component.$on("delete", deleteHandler);

    const deleteButton = screen.getByTitle("Delete");
    await fireEvent.click(deleteButton);

    expect(deleteHandler).not.toHaveBeenCalled();
  });

  it("dispatches edit event when edit button is clicked", async () => {
    const { component } = render(FileItem, { props: { file: mockFile } });

    const editHandler = vi.fn();
    component.$on("edit", editHandler);

    const editButton = screen.getByTitle("Edit name");
    await fireEvent.click(editButton);

    expect(editHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: mockFile,
      })
    );
  });

  it("shows input field when in editing mode", () => {
    render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "new-name.txt",
      },
    });

    const input = screen.getByDisplayValue("new-name.txt");
    expect(input).toBeInTheDocument();
  });

  it("dispatches save event when Enter key is pressed with valid name", async () => {
    const { component } = render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "new-name.txt",
      },
    });

    const saveHandler = vi.fn();
    component.$on("save", saveHandler);

    const input = screen.getByDisplayValue("new-name.txt");
    await fireEvent.keyDown(input, { key: "Enter" });

    expect(saveHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: { fileId: "1", newName: "new-name.txt" },
      })
    );
  });

  it("does not dispatch save event when name is empty", async () => {
    const { component } = render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "",
      },
    });

    const saveHandler = vi.fn();
    component.$on("save", saveHandler);

    const input = screen.getByDisplayValue("");
    await fireEvent.keyDown(input, { key: "Enter" });

    expect(saveHandler).not.toHaveBeenCalled();
  });

  it("does not dispatch save event when name is unchanged", async () => {
    const { component } = render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "test-file.txt",
      },
    });

    const saveHandler = vi.fn();
    component.$on("save", saveHandler);

    const input = screen.getByDisplayValue("test-file.txt");
    await fireEvent.keyDown(input, { key: "Enter" });

    expect(saveHandler).not.toHaveBeenCalled();
  });

  it("dispatches cancel event when cancel button is clicked", async () => {
    const { component } = render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "new-name.txt",
      },
    });

    const cancelHandler = vi.fn();
    component.$on("cancel", cancelHandler);

    const cancelButton = screen.getByTitle("Cancel edit");
    await fireEvent.click(cancelButton);

    expect(cancelHandler).toHaveBeenCalled();
  });

  it("handles Escape key to cancel", async () => {
    const { component } = render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "new-name.txt",
      },
    });

    const cancelHandler = vi.fn();
    component.$on("cancel", cancelHandler);

    const input = screen.getByDisplayValue("new-name.txt");
    await fireEvent.keyDown(input, { key: "Escape" });

    expect(cancelHandler).toHaveBeenCalled();
  });

  it("has correct file item styling", () => {
    render(FileItem, { props: { file: mockFile } });

    const fileItem = document.querySelector(".file-item");
    expect(fileItem).toHaveClass(
      "p-4",
      "hover:bg-gray-50",
      "transition-colors"
    );
  });

  it("has correct file icon container styling", () => {
    render(FileItem, { props: { file: mockFile } });

    const iconContainer = document.querySelector(".w-10.h-10");
    expect(iconContainer).toHaveClass(
      "w-10",
      "h-10",
      "bg-blue-100",
      "rounded-lg",
      "flex",
      "items-center",
      "justify-center"
    );
  });

  it("shows action buttons when not in editing mode", () => {
    render(FileItem, { props: { file: mockFile } });

    expect(screen.getByTitle("Download")).toBeInTheDocument();
    expect(screen.getByTitle("Edit name")).toBeInTheDocument();
    expect(screen.getByTitle("Delete")).toBeInTheDocument();
  });

  it("shows cancel button when in editing mode", () => {
    render(FileItem, {
      props: {
        file: mockFile,
        isEditing: true,
        editingName: "new-name.txt",
      },
    });

    expect(screen.getByTitle("Cancel edit")).toBeInTheDocument();
  });
});
