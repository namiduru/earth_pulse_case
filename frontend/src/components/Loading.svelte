<script lang="ts">
  export let text = "Loading...";
  export let size: "sm" | "md" | "lg" = "md";

  $: sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8",
  };
</script>

<div class="loading-container text-center">
  <div
    class="inline-block animate-spin rounded-full border-b-2 border-blue-600 {sizeClasses[
      size
    ]}"
  />
  {#if text}
    <p class="mt-2 text-gray-600 text-sm">{text}</p>
  {/if}
</div>

<style>
  .loading-container {
    padding: 1rem;
  }
</style>
