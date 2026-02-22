<script lang="ts">
    // @ts-nocheck
    export let data = {};
    export let triggerReset = () => {};

    // Reactively extract the phase
    $: currentPhase = data?.telemetry?.phase ?? 'INITIALIZING...';
</script>

<div class="mission-wrapper">
    <div class="phase-box">
        <span class="label">CURRENT_PHASE</span>
        <div class="value">{currentPhase}</div>
    </div>

    <button on:click={triggerReset} class="nuclear-btn">
        OVERWRITE_DATABASE
    </button>
</div>

<style>
    .mission-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        width: 100%;
    }
    .label { font-size: 0.6rem; opacity: 0.5; letter-spacing: 2px; }
    .value { font-size: 1.5rem; color: #00f2ff; font-weight: bold; }

    .nuclear-btn {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #ef4444;
        padding: 8px 16px;
        font-family: monospace;
        font-size: 10px;
        cursor: pointer;
        transition: 0.3s;
    }
    .nuclear-btn:hover {
        background: #ef4444;
        color: white;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
    }
</style>