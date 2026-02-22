<script>
    let { data } = $props();
</script>

<div class="selector-screen">
    <div class="header">
        <h1>NAV_DOMAIN_POC // SYSTEM_BOOT</h1>
        <p class="meta">VER: {data.version} | {data.timestamp}</p>
    </div>

    <div class="nav-grid">
        <a href="/drone" class="nav-card hardware">
            <span class="code">01</span>
            <span class="label">HARDWARE_VAULT</span>
            <span class="desc">Direct DuckDB access for physical drone telemetry.</span>
        </a>

        <a href="/sitl" class="nav-card sim">
            <span class="code">02</span>
            <span class="label">SITL_SIM_VAULT</span>
            <span class="desc">Virtualized environment snapshot analysis.</span>
        </a>
    </div>
</div>

<style>
    .selector-screen {
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #000;
        color: #0f0;
    }

    .header { text-align: center; margin-bottom: 50px; }
    .meta { font-size: 10px; color: #064e3b; }

    .nav-grid { display: flex; gap: 30px; }

    .nav-card {
        width: 300px;
        padding: 40px;
        border: 1px solid #0f0;
        text-decoration: none;
        color: inherit;
        display: flex;
        flex-direction: column;
        gap: 10px;
        transition: 0.2s;
    }

    .nav-card:hover {
        background: #0f0;
        color: #000;
    }

    .sim { border-color: #0ff; color: #0ff; }
    .sim:hover { background: #0ff; color: #000; }

    .code { font-size: 10px; opacity: 0.7; }
    .label { font-size: 20px; font-weight: bold; }
    .desc { font-size: 12px; opacity: 0.8; }
</style>