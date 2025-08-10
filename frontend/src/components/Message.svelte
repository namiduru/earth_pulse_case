<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { Message } from "../types/file";

  export let message: Message;

  const dispatch = createEventDispatcher();

  function handleClose() {
    dispatch("close", message.id);
  }

  const iconMap: Record<Message["type"], string> = {
    success: "✓",
    error: "✕",
    warning: "⚠",
    info: "ℹ",
  };

  const bgColorMap: Record<Message["type"], string> = {
    success: "bg-green-50 border-green-200 text-green-800",
    error: "bg-red-50 border-red-200 text-red-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    info: "bg-blue-50 border-blue-200 text-blue-800",
  };
</script>

<div class="message-container">
  <div
    class="message {bgColorMap[
      message.type
    ]} border rounded-lg p-4 mb-3 flex items-center justify-between shadow-sm"
  >
    <div class="flex items-center space-x-3">
      <span class="text-lg font-semibold">{iconMap[message.type]}</span>
      <span class="text-sm font-medium">{message.text}</span>
    </div>
    <button
      on:click={handleClose}
      class="text-gray-400 hover:text-gray-600 transition-colors"
      aria-label="Close message"
    >
      <svg
        class="w-4 h-4"
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
  </div>
</div>

<style>
  .message-container {
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
