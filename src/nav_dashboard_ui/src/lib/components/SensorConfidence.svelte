<script lang="ts">
    export let stats = { gps: 0, imu: 0, baro: 0 };
</script>

<div class="matrix">
    {#each Object.entries(stats) as [key, value]}
        <div class="module {value === 1 ? 'active' : 'offline'}">
            <div class="led-container">
                <div class="led"></div>
                <div class="label">{key.toUpperCase()}</div>
            </div>
            <div class="status-text">{value === 1 ? 'LOCK' : 'LOST'}</div>
        </div>
    {/each}
</div>

<style>
    .matrix { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; width: 100%; }

    .module {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 10px;
        text-align: center;
        border-radius: 4px;
        font-family: monospace;
    }

    .led { width: 8px; height: 8px; border-radius: 50%; margin: 0 auto 8px; background: #27272a; transition: 0.3s; }

    .active .led { background: #10b981; box-shadow: 0 0 12px #10b981; }
    .active { color: #10b981; border-color: rgba(16, 185, 129, 0.3); }

    .offline .led { background: #ef4444; box-shadow: 0 0 12px #ef4444; animation: flash 1s infinite; }
    .offline { color: #ef4444; border-color: rgba(239, 68, 68, 0.3); opacity: 0.8; }

    .label { font-size: 0.6rem; letter-spacing: 1px; margin-bottom: 4px; color: #fff; }
    .status-text { font-size: 0.5rem; font-weight: bold; }

    @keyframes flash { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
</style>