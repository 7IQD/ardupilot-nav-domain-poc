<script lang="ts">
    // @ts-nocheck
    import { onMount } from 'svelte';
    import { liveTelemetry, fetchPulse } from '$lib/liveTelemetry';

    import DriftCard from '$lib/components/DriftCard.svelte';
    import SensorConfidence from '$lib/components/SensorConfidence.svelte';
    import MissionPhaseBar from '$lib/components/MissionPhaseBar.svelte';
    import WireShark from '$lib/components/WireShark.svelte';

    let data = $derived($liveTelemetry);

    onMount(() => {
        fetchPulse();
        const interval = setInterval(fetchPulse, 200);
        return () => clearInterval(interval);
    });

    async function triggerReset() {
        if (!confirm("CRITICAL: Overwrite database?")) return;
        try {
            await fetch('http://localhost:8000/api/test/overwrite-db', { method: 'POST' });
        } catch (e) { console.error("Reset failed", e); }
    }
</script>

<div class="ops-room">
    <main class="quadrant-grid">
        <section class="ops-card q-top q-left">
            <div class="axis-label">EKF_PRECISION_AXIS</div>
            <div class="inner-content">
                <DriftCard value={data.telemetry?.drift ?? 0} fence={2.0} />
            </div>
        </section>

        <section class="ops-card q-top q-right">
            <div class="axis-label">SENSOR_HEALTH_ARRAY</div>
            <div class="inner-content">
                <SensorConfidence stats={data.telemetry?.sensors ?? {gps:0, imu:0, baro:0}} />
            </div>
        </section>

        <section class="ops-card q-bottom q-left">
            <div class="axis-label">MISSION_CONTROL_UNIT</div>
            <div class="inner-content">
                <MissionPhaseBar {data} {triggerReset} />
            </div>
        </section>

        <section class="ops-card q-bottom q-right log-container">
            <div class="axis-label">PIPELINE_FLOW_STREAM</div>
            <div class="log-scroll">
                <WireShark entries={data.logs ?? []} />
            </div>
        </section>
    </main>

    <footer class="ops-footer">
        <div class="status-group">
            <span class="stat">INGRESS: <span class="highlight">{data.pipeline?.ingress_hz ?? 0}Hz</span></span>
            <span class="stat {data.pipeline?.vault_ok ? 'stable' : 'error'}">
                VAULT: {data.pipeline?.vault_ok ? 'STABLE' : 'ERROR'}
            </span>
        </div>
        <div class="branding">NAV_DOMAIN // OPS_PROBE_V1.3_FIXED_AXIS</div>
    </footer>
</div>

<style>
    /* 1. Global: High Contrast "Linux" Base */
    :global(html, body) {
        margin: 0; padding: 0;
        height: 100vh; width: 100vw;
        background: #020617;
        color: #4ade80;
        font-family: 'Courier New', Courier, monospace;
        overflow: hidden;
    }

    .ops-room {
        height: 100vh; width: 100vw;
        display: flex; flex-direction: column;
        padding: 10px; box-sizing: border-box;
    }

    /* 2. FIXED AXES GRID */
    .quadrant-grid {
        display: grid;
        /* Using fixed calc to ensure exactly 50% split minus spacing */
        grid-template-columns: 50% 50%;
        grid-template-rows: 50% 50%;
        width: 100%;
        height: calc(100vh - 60px); /* Leave room for footer */
        flex-grow: 1;
    }

    .ops-card {
        background: #020617;
        border: 1px solid #22c55e; /* Thin green axis lines */
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-sizing: border-box;
        overflow: hidden; /* CRITICAL: Stops content from pushing borders */
    }

    /* 3. Fixing the varying sizes: force children to stay inside */
    .inner-content {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    /* 4. Labels (Increased Font & Florescent Green) */
    .axis-label {
        position: absolute;
        top: 0; left: 0;
        background: #22c55e;
        color: #020617;
        padding: 4px 15px;
        font-size: 16px; /* High visibility */
        font-weight: 900;
        letter-spacing: 2px;
        z-index: 10;
    }

    /* 5. Logs (Fixed size to prevent expansion) */
    .log-container { align-items: stretch; justify-content: flex-start; padding-top: 40px; }
    .log-scroll {
        height: 100%;
        overflow-y: auto;
        font-size: 13px;
        color: #4ade80;
        font-weight: 600;
    }

    /* 6. Footer */
    .ops-footer {
        height: 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 2px solid #22c55e;
        padding: 0 10px;
        font-size: 14px;
        font-weight: bold;
    }

    .status-group { display: flex; gap: 40px; }
    .highlight { color: #86efac; text-shadow: 0 0 10px #4ade80; }
    .stable { color: #4ade80; }
    .error { color: #f43f5e; background: #000; padding: 0 5px; }
</style>