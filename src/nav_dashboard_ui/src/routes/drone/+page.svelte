<script>
  import { onMount } from 'svelte';

  const domains = ["ui_nav_drone_monitor", "nav_counts", "nav_ground", "nav_drone"];
  let activeView = domains[0];
  let tableData = [];
  let columns = [];
  let status = "ONLINE";

  async function fetchData(view) {
    activeView = view;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/nav/domain?view=${view}`);
      const data = await res.json();
      tableData = data.telemetry || [];
      columns = tableData.length > 0 ? Object.keys(tableData[0]) : [];
    } catch (e) { status = "OFFLINE"; }
  }

  onMount(() => fetchData(activeView));
</script>

<div class="status-bar">
  NAV_DOMAIN_MONITOR // {status} // DATA_SOURCE: FAST_API_DUCKDB
</div>

<div class="container">
  <div class="sidebar">
    <p class="label">DOMAINS</p>
    {#each domains as domain}
      <button class:active={domain === activeView} onclick={() => fetchData(domain)}>
        {domain}
      </button>
    {/each}
  </div>

  <div class="content">
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            {#each columns as col}
              <th>{col}</th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each tableData as row}
            <tr>
              {#each columns as col}
                <td title={row[col]}>{row[col] ?? '—'}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>

<style>
  :global(body) { margin: 0; background: #000; color: #0f0; font-family: monospace; overflow: hidden; }

  .status-bar {
    background: #020; padding: 2px 10px; font-size: 10px; border-bottom: 1px solid #040;
  }

  .container { display: flex; height: calc(100vh - 16px); }

  .sidebar {
    width: 160px; background: #050505; border-right: 1px solid #111; padding: 10px; flex-shrink: 0;
  }
  .label { color: #444; font-size: 9px; margin: 0 0 10px 0; }

  button {
    display: block; background: none; border: none; color: #06a; cursor: pointer;
    text-align: left; padding: 4px 0; font-family: inherit; font-size: 11px; width: 100%;
  }
  button.active { color: #ff0; font-weight: bold; }

  .content { flex: 1; overflow: hidden; display: flex; }
  .table-wrapper { flex: 1; overflow: auto; }

  table {
    border-collapse: collapse; width: 100%; table-layout: fixed; /* KISS: Fixed layout for squeezing */
  }

  th, td {
    border: 1px solid #111; padding: 2px 4px; font-size: 10px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; color: #888;
  }

  th { background: #0a0a0a; position: sticky; top: 0; z-index: 10; text-align: left; color: #aaa; }

  /* SQUEEZE FIRST TWO COLUMNS */
  th:nth-child(1), td:nth-child(1) { width: 40px; color: #fff; background: #000; position: sticky; left: 0; z-index: 11; }
  th:nth-child(2), td:nth-child(2) { width: 60px; }

  tr:hover td { background: #080808; color: #fff; }
</style>