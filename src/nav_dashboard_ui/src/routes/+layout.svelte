<script lang="ts">
    // ✅ Import favicon
    import favicon from '$lib/assets/favicon.svg';
    import '$lib/app.css'; // Make sure this path points to your Tailwind CSS file

    // Svelte 5: children prop
    let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
  <title>NAV_DOMAIN | Observation Probe</title>
</svelte:head>

<div class="min-h-screen bg-[#0a0a0a] text-zinc-300">
    {@render children()}
</div>

<style>
    /* Global reset */
    :global(html, body) {
        margin: 0;
        padding: 0;
        background-color: #0a0a0a;
        color: #f5f5f5;
        overflow-x: hidden;
        font-family: system-ui, sans-serif;
    }
</style>
