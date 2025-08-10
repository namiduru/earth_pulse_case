<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { FileData } from "../types/file";
  import {
    formatFileSize,
    formatDate,
    getFileIcon,
    sanitizeFilename,
  } from "../utils/formatters";
  import { fileActions } from "../stores/files";

  export let file: FileData;
  export let isEditing = false;
  export let editingName = "";

  const dispatch = createEventDispatcher();

  let originalName = "";

  // Initialize original name when editing starts
  $: if (isEditing && !originalName) {
    originalName = file.name;
  }

  function handleDownload() {
    dispatch("download", { fileId: file.file_id, fileName: file.name });
  }

  function handleDelete() {
    if (confirm("Are you sure you want to delete this file?")) {
      dispatch("delete", file.file_id);
    }
  }

  function handleEdit() {
    dispatch("edit", file);
  }

  function handleSave() {
    const trimmedName = editingName.trim();

    // Prevent saving if:
    // 1. Name is empty
    // 2. Name hasn't changed
    // 3. Already saving (checked in the store)
    if (!trimmedName || trimmedName === originalName) {
      if (trimmedName === originalName) {
        // Just cancel if name hasn't changed
        handleCancel();
      }
      return;
    }

    dispatch("save", { fileId: file.file_id, newName: trimmedName });
  }

  function handleCancel() {
    originalName = "";
    dispatch("cancel");
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSave();
    } else if (event.key === "Escape") {
      event.preventDefault();
      handleCancel();
    }
  }

  // Reset original name when editing stops
  $: if (!isEditing) {
    originalName = "";
  }

  // Check if this file is currently being saved
  $: isSaving = fileActions.isSaving(file.file_id);
</script>

<div class="file-item p-4 hover:bg-gray-50 transition-colors">
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-4 flex-1 min-w-0">
      <div class="flex-shrink-0">
        <div
          class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"
        >
          <span class="text-lg">{getFileIcon(file.content_type)}</span>
        </div>
      </div>
      <div class="flex-1 min-w-0">
        {#if isEditing}
          <input
            type="text"
            bind:value={editingName}
            class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            on:keydown={handleKeydown}
            disabled={isSaving}
          />
        {:else}
          <p
            class="text-sm font-medium text-gray-900 truncate cursor-pointer hover:text-blue-600"
            on:dblclick={handleEdit}
            title={file.name}
          >
            {sanitizeFilename(file.name)}
          </p>
        {/if}
        <p class="text-sm text-gray-500">
          {formatFileSize(file.size)} • {formatDate(file.upload_date)}
        </p>
      </div>
    </div>

    <div class="flex items-center space-x-2">
      {#if isEditing}
        <button
          class="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          on:click={handleCancel}
          disabled={isSaving}
          title="Cancel edit"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
        {#if isSaving}
          <div
            class="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"
          />
        {/if}
      {:else}
        <button
          class="text-gray-400 hover:text-blue-600 transition-colors"
          on:click={handleEdit}
          title="Edit name"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>
      {/if}

      <button
        class="text-gray-400 hover:text-green-600 transition-colors"
        on:click={handleDownload}
        title="Download"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </button>

      <button
        class="text-gray-400 hover:text-red-600 transition-colors"
        on:click={handleDelete}
        title="Delete"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  </div>
</div>
