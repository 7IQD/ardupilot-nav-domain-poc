<script>
    let { children } = $props();
</script>

<div class="drone-frame">
    <div class="header">
        <span class="pulse">●</span> HARDWARE_DOMAIN_ACTIVE
    </div>
    <div class="view-content">
        {@render children()}
    </div>
</div>

<style>
    .drone-frame {
        border: 4px solid #14532d;
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: #000;
    }
    .header {
        background: #14532d;
        color: #86efac;
        padding: 5px 20px;
        font-weight: bold;
        letter-spacing: 2px;
    }
    .pulse { animation: blink 1s infinite; margin-right: 10px; }
    @keyframes blink { 50% { opacity: 0; } }
    .view-content { flex-grow: 1; }
</style>