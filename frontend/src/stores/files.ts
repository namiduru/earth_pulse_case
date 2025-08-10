import { writable, derived, get } from "svelte/store";
import type { FileData, FileUploadState, FileEditState } from "../types/file";
import { apiService, ApiError } from "../lib/api";

// File store
export const files = writable<FileData[]>([]);
export const loading = writable(false);
export const error = writable<string | null>(null);

// Upload state store
export const uploadState = writable<FileUploadState>({
  isUploading: false,
  progress: 0,
});

// Edit state store
export const editState = writable<FileEditState>({
  editingFileId: null,
  editingName: "",
});

// Saving state store
export const savingState = writable<{ [fileId: string]: boolean }>({});

// Derived stores
export const filesCount = derived(files, ($files) => $files.length);
export const totalSize = derived(files, ($files) =>
  $files.reduce((total, file) => total + file.size, 0)
);

// File operations
export const fileActions = {
  async loadFiles() {
    loading.set(true);
    error.set(null);

    try {
      const fileList = await apiService.getFiles();
      files.set(fileList);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to load files";
      error.set(message);
    } finally {
      loading.set(false);
    }
  },

  async uploadFile(file: File) {
    uploadState.set({
      isUploading: true,
      progress: 0,
      fileName: file.name,
    });

    try {
      await apiService.uploadFile(file);
      await this.loadFiles(); // Refresh file list
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Upload failed";
      error.set(message);
      throw err;
    } finally {
      uploadState.set({
        isUploading: false,
        progress: 0,
      });
    }
  },

  async downloadFile(fileId: string, fileName: string) {
    try {
      const blob = await apiService.downloadFile(fileId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Download failed";
      error.set(message);
      throw err;
    }
  },

  async deleteFile(fileId: string) {
    try {
      await apiService.deleteFile(fileId);
      await this.loadFiles(); // Refresh file list
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Delete failed";
      error.set(message);
      throw err;
    }
  },

  async updateFileName(fileId: string, newName: string) {
    // Check if already saving this file
    const currentSavingState = get(savingState);
    if (currentSavingState[fileId]) {
      return; // Already saving, ignore duplicate request
    }

    // Set saving state for this file
    savingState.update((state) => ({ ...state, [fileId]: true }));

    try {
      await apiService.updateFileName(fileId, newName);

      // Update the local file data immediately instead of reloading all files
      files.update((fileList) =>
        fileList.map((file) =>
          file.file_id === fileId ? { ...file, name: newName } : file
        )
      );

      // Also update the edit state to clear the editing mode
      editState.set({
        editingFileId: null,
        editingName: "",
      });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Update failed";
      error.set(message);
      throw err;
    } finally {
      // Clear saving state for this file
      savingState.update((state) => {
        const newState = { ...state };
        delete newState[fileId];
        return newState;
      });
    }
  },

  startEdit(file: FileData) {
    editState.set({
      editingFileId: file.file_id,
      editingName: file.name,
    });
  },

  cancelEdit() {
    editState.set({
      editingFileId: null,
      editingName: "",
    });
  },

  clearError() {
    error.set(null);
  },

  // Get saving state for a specific file
  isSaving(fileId: string): boolean {
    const currentState = get(savingState);
    return currentState[fileId] || false;
  },
};
