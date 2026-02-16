<script>
    let { children } = $props();
</script>

<div class="sitl-frame">
    <div class="header">
        <span>[VIRTUAL_SITL_ENVIRONMENT]</span>
    </div>
    <div class="view-content">
        {@render children()}
    </div>
</div>

<style>
    .sitl-frame {
        border: 4px solid #164e63;
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: #020617;
    }
    .header {
        background: #164e63;
        color: #a5f3fc;
        padding: 5px 20px;
        font-weight: bold;
        text-align: right;
    }
    .view-content { flex-grow: 1; }
</style>