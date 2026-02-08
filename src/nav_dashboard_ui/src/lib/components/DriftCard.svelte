<script lang="ts">
    export let value: number = 0;
    export let fence: number = 2.0;

    // Calculate percentage for the axis (0 to 2.5m scale)
    $: position = Math.min((value / 2.5) * 100, 100);
    $: status = value > fence ? 'CRIT' : value > (fence * 0.7) ? 'WARN' : 'NOM';
</script>

<div class="instrument">
    <div class="header">
        <span class="label">EKF_DRIFT_INDEX</span>
        <span class="status-tag {status}">{status}</span>
    </div>

    <div class="readout">
        <span class="number">{value.toFixed(2)}</span>
        <span class="unit">METERS</span>
    </div>

    <div class="gauge-area">
        <div class="axis">
            <div class="threshold warn" style="left: 70%"></div>
            <div class="threshold danger" style="left: 80%"></div>

            <div class="bug {status}" style="left: {position}%">
                <div class="pointer"></div>
            </div>
        </div>
        <div class="axis-labels">
            <span>0.0</span>
            <span>1.0</span>
            <span class="danger-text">2.0</span>
        </div>
    </div>
</div>

<style>
    .instrument { width: 100%; color: #00f2ff; font-family: monospace; }
    .header { display: flex; justify-content: space-between; font-size: 0.6rem; opacity: 0.6; margin-bottom: 1rem; }

    .status-tag { padding: 2px 6px; border-radius: 2px; border: 1px solid; }
    .NOM { border-color: #10b981; color: #10b981; }
    .WARN { border-color: #f59e0b; color: #f59e0b; }
    .CRIT { border-color: #ef4444; color: #ef4444; background: rgba(239, 68, 68, 0.1); }

    .readout { display: flex; align-items: baseline; gap: 8px; margin-bottom: 1.5rem; }
    .number { font-size: 3rem; font-weight: bold; text-shadow: 0 0 15px rgba(0, 242, 255, 0.4); }
    .unit { font-size: 0.8rem; opacity: 0.5; }

    .gauge-area { position: relative; padding-top: 10px; }
    .axis { height: 2px; background: rgba(255, 255, 255, 0.1); position: relative; width: 100%; }

    .threshold { position: absolute; height: 10px; width: 2px; top: -4px; }
    .warn { background: #f59e0b; }
    .danger { background: #ef4444; }

    .bug { position: absolute; transition: left 0.3s cubic-bezier(0.17, 0.67, 0.83, 0.67); }
    .pointer { width: 4px; height: 16px; background: #fff; margin-left: -2px; top: -7px; position: relative; box-shadow: 0 0 10px #fff; }

    .bug.WARN .pointer { background: #f59e0b; box-shadow: 0 0 10px #f59e0b; }
    .bug.CRIT .pointer { background: #ef4444; box-shadow: 0 0 15px #ef4444; }

    .axis-labels { display: flex; justify-content: space-between; font-size: 0.5rem; margin-top: 10px; opacity: 0.4; }
    .danger-text { color: #ef4444; opacity: 1; }
</style>