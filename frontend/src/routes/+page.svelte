<script lang="ts">
  import { onMount } from "svelte";
  import {
    files,
    loading,
    error,
    uploadState,
    editState,
    savingState,
    fileActions,
  } from "../stores/files";
  import { messages, messageActions } from "../stores/messages";
  import Message from "../components/Message.svelte";
  import FileUpload from "../components/FileUpload.svelte";
  import FileItem from "../components/FileItem.svelte";
  import Loading from "../components/Loading.svelte";
  import { formatFileSize } from "../utils/formatters";

  // Subscribe to stores
  $: fileList = $files;
  $: isLoading = $loading;
  $: currentError = $error;
  $: isUploading = $uploadState.isUploading;
  $: uploadFileName = $uploadState.fileName;
  $: editingFileId = $editState.editingFileId;
  $: editingName = $editState.editingName;
  $: messageList = $messages;
  $: currentSavingState = $savingState;

  onMount(() => {
    loadFiles();
  });

  async function loadFiles() {
    try {
      await fileActions.loadFiles();
    } catch (err) {
      messageActions.error("Failed to load files");
    }
  }

  async function handleFileUpload(event: any) {
    const file = event.detail;
    try {
      await fileActions.uploadFile(file);
      messageActions.success("File uploaded successfully");
    } catch (err) {
      messageActions.error("Upload failed");
    }
  }

  async function handleFileDownload(event: any) {
    const { fileId, fileName } = event.detail;
    try {
      await fileActions.downloadFile(fileId, fileName);
      messageActions.success("Download started");
    } catch (err) {
      messageActions.error("Download failed");
    }
  }

  async function handleFileDelete(event: any) {
    const fileId = event.detail;
    try {
      await fileActions.deleteFile(fileId);
      messageActions.success("File deleted successfully");
    } catch (err) {
      messageActions.error("Delete failed");
    }
  }

  async function handleFileEdit(event: any) {
    const file = event.detail;
    fileActions.startEdit(file);
  }

  async function handleFileSave(event: any) {
    const { fileId, newName } = event.detail;

    // Check if already saving this file
    if (currentSavingState[fileId]) {
      return; // Already saving, ignore duplicate request
    }

    try {
      await fileActions.updateFileName(fileId, newName);
      // Success message will be shown only once since we're not reloading files
      messageActions.success("File name updated successfully");
    } catch (err) {
      messageActions.error("Update failed");
    }
  }

  function handleFileCancel() {
    fileActions.cancelEdit();
  }

  function handleMessageClose(event: any) {
    const messageId = event.detail;
    messageActions.remove(messageId);
  }

  function handleErrorClear() {
    fileActions.clearError();
  }
</script>

<svelte:head>
  <title>FileDrive - Your Personal Cloud Storage</title>
  <meta
    name="description"
    content="Upload, manage, and share your files securely"
  />
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <header class="text-center mb-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-2">FileDrive</h1>
      <p class="text-gray-600">Your personal cloud storage solution</p>
    </header>

    <!-- Messages -->
    {#if messageList.length > 0}
      <div class="mb-4">
        {#each messageList as message (message.id)}
          <Message {message} on:close={handleMessageClose} />
        {/each}
      </div>
    {/if}

    <!-- Error Display -->
    {#if currentError}
      <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center justify-between">
          <p class="text-red-800">{currentError}</p>
          <button
            on:click={handleErrorClear}
            class="text-red-600 hover:text-red-800"
          >
            ✕
          </button>
        </div>
      </div>
    {/if}

    <!-- File Upload Section -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <FileUpload disabled={isUploading} on:file={handleFileUpload} />

      {#if isUploading}
        <div class="mt-4">
          <Loading text="Uploading {uploadFileName}..." />
        </div>
      {/if}
    </div>

    <!-- Files Section -->
    <div class="bg-white rounded-lg shadow-md">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">Your Files</h2>
          {#if fileList.length > 0}
            <div class="text-sm text-gray-500">
              {fileList.length} file{fileList.length !== 1 ? "s" : ""} • {formatFileSize(
                fileList.reduce((total, file) => total + file.size, 0)
              )}
            </div>
          {/if}
        </div>
      </div>

      {#if isLoading}
        <Loading text="Loading files..." size="lg" />
      {:else if fileList.length === 0}
        <div class="p-8 text-center text-gray-500">
          <div class="mb-4">
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p>No files uploaded yet. Upload your first file to get started!</p>
        </div>
      {:else}
        <div class="divide-y divide-gray-200">
          {#each fileList as file (file.file_id)}
            <FileItem
              {file}
              isEditing={editingFileId === file.file_id}
              editingName={editingFileId === file.file_id ? editingName : ""}
              on:download={handleFileDownload}
              on:delete={handleFileDelete}
              on:edit={handleFileEdit}
              on:save={handleFileSave}
              on:cancel={handleFileCancel}
            />
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>
