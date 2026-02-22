<script>
    /** @type {import('./$types').LayoutProps} */
    let { children } = $props();
</script>

<style>
    :global(html, body) {
        margin: 0;
        padding: 0;
        background: #000; /* Deep terminal black */
        color: #0f0;    /* Classic CRT Green */
        font-family: 'Courier New', monospace;
        overflow: hidden; /* Prevent scrollbars from breaking the UI */
    }

    .app-viewport {
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
    }
</style>

<div class="app-viewport">
    {@render children()}
</div>