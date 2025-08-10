<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let disabled = false;
  export let multiple = false;
  export let accept = "";

  const dispatch = createEventDispatcher();

  let dragOver = false;
  let fileInput: HTMLInputElement;

  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = Array.from(target.files || []);

    if (files.length > 0) {
      if (multiple) {
        dispatch("files", files);
      } else {
        dispatch("file", files[0]);
      }
    }

    // Reset input
    if (fileInput) {
      fileInput.value = "";
    }
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    if (!disabled) {
      dragOver = true;
    }
  }

  function handleDragLeave(event: DragEvent) {
    event.preventDefault();
    dragOver = false;
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragOver = false;

    if (disabled) return;

    const files = Array.from(event.dataTransfer?.files || []);

    if (files.length > 0) {
      if (multiple) {
        dispatch("files", files);
      } else {
        dispatch("file", files[0]);
      }
    }
  }

  function triggerFileInput() {
    if (!disabled && fileInput) {
      fileInput.click();
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      triggerFileInput();
    }
  }
</script>

<div
  class="upload-zone {dragOver ? 'drag-over' : ''} {disabled ? 'disabled' : ''}"
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  on:drop={handleDrop}
  on:click={triggerFileInput}
  on:keydown={handleKeydown}
  role="button"
  tabindex="0"
  aria-label="Upload files by clicking or dragging and dropping"
>
  <div class="upload-content">
    <div class="upload-icon">
      <svg
        class="w-12 h-12 text-gray-400"
        stroke="currentColor"
        fill="none"
        viewBox="0 0 48 48"
      >
        <path
          d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </div>
    <p class="upload-text">Drop files here or click to upload</p>
    <p class="upload-hint">Support for documents, images, videos, and more</p>
  </div>

  <input
    bind:this={fileInput}
    type="file"
    {multiple}
    {accept}
    class="hidden"
    on:change={handleFileSelect}
    {disabled}
  />
</div>

<style>
  .upload-zone {
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
    padding: 2rem;
    text-align: center;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    background-color: #ffffff;
  }

  .upload-zone:hover:not(.disabled) {
    border-color: #3b82f6;
    background-color: #f8fafc;
  }

  .upload-zone.drag-over {
    border-color: #3b82f6;
    background-color: #eff6ff;
  }

  .upload-zone.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .upload-content {
    pointer-events: none;
  }

  .upload-icon {
    margin-bottom: 1rem;
  }

  .upload-text {
    font-size: 1.125rem;
    font-weight: 500;
    color: #111827;
    margin-bottom: 0.5rem;
  }

  .upload-hint {
    font-size: 0.875rem;
    color: #6b7280;
  }
</style>
