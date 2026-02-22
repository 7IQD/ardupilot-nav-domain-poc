<script>
    /** @type {{ data: { telemetry: Array<{Roll: number, DesRoll: number, Alt: number, timestamp_sec: number}> } }} */
    let { data } = $props();

    // 1. DATA EXTRACTION
    // JSDoc above silences the 'telemetry does not exist' error in the IDE
    let telemetry = $derived(data?.telemetry || []);

    // SITL_SNAPSHOT: Final row of the simulation log
    let latestEntry = $derived(telemetry[telemetry.length - 1] || { Roll: 0, DesRoll: 0, Alt: 0, timestamp_sec: 0 });

    // SITL_METRICS: Aggregate analysis for simulation validation
    let sitlMetrics = $derived({
        maxDrift: telemetry.length > 0
            ? Math.max(...telemetry.map(r => Math.abs(r.Roll - r.DesRoll))).toFixed(4)
            : "0.0000",
        avgAlt: telemetry.length > 0
            ? (telemetry.reduce((acc, r) => acc + r.Alt, 0) / telemetry.length).toFixed(2)
            : "0.00",
        totalRows: telemetry.length
    });

    // Overwrite for SITL testing [2026-01-15]
    async function triggerReset() {
        if (!confirm("CRITICAL: Overwrite SITL simulation database?")) return;
        try {
            // Assuming your SITL backend handles the same reset endpoint
            await fetch('http://localhost:8000/api/test/overwrite-db', { method: 'POST' });
            window.location.reload();
        } catch (e) { console.error("SITL Reset failed", e); }
    }
</script>

<div class="cli-dashboard sitl-theme">
    <header class="terminal-header">
        <span>NAV_DOMAIN_SITL // PATH: /sitl</span>
        <span>MODE: SIMULATION_STATIC_SNAPSHOT</span>
    </header>

    <main class="cli-grid">
        <section class="cli-card">
            <div class="label">SITL_CURRENT_STATE (T+{latestEntry.timestamp_sec.toFixed(2)}s)</div>
            <div class="content">
                <div class="big-metric">SIM_DRIFT: {Math.abs(latestEntry.Roll - latestEntry.DesRoll).toFixed(4)}</div>
                <div class="big-metric">SIM_ALT: {latestEntry.Alt?.toFixed(2)}m</div>
            </div>
        </section>

        <section class="cli-card">
            <div class="label">SITL_VAULT_ANALYSIS</div>
            <div class="content stats-list">
                <p>MAX_SIM_DRIFT:     <span class="cyan">{sitlMetrics.maxDrift}</span></p>
                <p>AVG_SIM_ALT:       <span class="cyan">{sitlMetrics.avgAlt}m</span></p>
                <p>SIM_PACKET_COUNT:  <span class="cyan">{sitlMetrics.totalRows}</span></p>
                <div class="btn-group">
                    <button class="cli-btn" onclick={triggerReset}>RESET_SIM_VAULT</button>
                    <a href="/drone" class="nav-link">BACK_TO_HARDWARE ←</a>
                </div>
            </div>
        </section>
    </main>

    <footer class="terminal-footer">
        READY > SITL_PATH_STABLE
    </footer>
</div>

<style>
    :global(html, body) {
        background: #000; color: #0ff; /* Cyan theme for SITL to distinguish from Green hardware */
        font-family: 'Courier New', monospace;
        margin: 0; padding: 0; overflow: hidden;
    }
    .cli-dashboard { height: 100vh; display: flex; flex-direction: column; padding: 10px; box-sizing: border-box; }

    .terminal-header, .terminal-footer {
        display: flex; justify-content: space-between;
        background: #0ff; color: #000;
        padding: 2px 10px; font-weight: bold; font-size: 14px;
    }

    .cli-grid { flex-grow: 1; display: grid; grid-template-rows: 1fr 1fr; gap: 10px; margin: 10px 0; }

    .cli-card {
        border: 1px solid #0ff; position: relative;
        padding: 20px; display: flex; flex-direction: column; justify-content: center;
    }

    .label { position: absolute; top: 0; left: 0; background: #0ff; color: #000; padding: 0 10px; font-size: 12px; }

    .big-metric { font-size: 3rem; font-weight: bold; margin: 10px 0; }

    .stats-list p { font-size: 1.5rem; margin: 5px 0; white-space: pre; }
    .cyan { color: #fff; text-shadow: 0 0 5px #0ff; }

    .btn-group { display: flex; gap: 20px; margin-top: 15px; }

    .cli-btn, .nav-link {
        background: #000; color: #f0f; border: 1px solid #f0f;
        padding: 5px 10px; cursor: pointer; text-decoration: none; font-size: 14px;
    }
    .nav-link { color: #0ff; border-color: #0ff; }
</style>