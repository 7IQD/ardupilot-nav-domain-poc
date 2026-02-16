<script>
  import { onMount } from 'svelte';

  let domains = [];
  let activeView = "";
  let tableData = [];
  let columns = [];

  // Fetch available domains
  async function fetchDomains() {
    const res = await fetch("http://127.0.0.1:8000/api/nav/domains");
    domains = await res.json();
    if (domains.length > 0) fetchData(domains[0]);
  }

  // Fetch table data for a domain
  async function fetchData(view) {
    activeView = view;
    const res = await fetch(`http://127.0.0.1:8000/api/nav/domain?view=${view}`);
    const data = await res.json();
    tableData = data.telemetry || [];
    columns = tableData.length > 0 ? Object.keys(tableData[0]) : [];
  }

  onMount(() => fetchDomains());
</script>

<style>
  /* --- Layout --- */
  .container {
    display: flex;
    height: 100vh;
    background: #000;
    color: #fff;
    font-family: monospace;
  }

  /* --- Sidebar --- */
  .sidebar {
    width: 220px;
    background: #111;
    padding: 1rem;
    box-sizing: border-box;
    overflow-y: auto;
  }

  .sidebar a {
    display: block;
    margin-bottom: 0.5rem;
    color: #0af;
    text-decoration: none;
    cursor: pointer;
  }

  .sidebar a.active {
    color: #ff0;
    font-weight: bold;
  }

  /* --- Content --- */
.content {
  flex: 1;
  padding: 1rem;
  overflow-x: auto;   /* horizontal scroll enabled */
  display: flex;
  flex-direction: column;
}

table {
  border-collapse: collapse;
  font-size: 10px;
  table-layout: auto; /* natural sizing */
  width: max-content;  /* table can grow beyond container */
  min-width: 100%;    /* fills container at least */
}

th, td {
  border: 1px solid #555;
  padding: 2px 4px;
  white-space: nowrap;
}

</style>

<div class="container">
  <!-- LEFT SIDEBAR -->
  <div class="sidebar">
    <h3>Drone Domains</h3>
    {#each domains as domain}
      <a
        class:active={domain === activeView}
        on:click={() => fetchData(domain)}
      >
        {domain}
      </a>
    {/each}
  </div>

  <!-- RIGHT TABLE -->
  <div class="content">
    {#if activeView}
      <h3>{activeView} | Total Rows: {tableData.length}</h3>
      <table>
        <thead>
          <tr>
            {#each columns as col}
              <th title={col}>{col}</th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each tableData as row}
            <tr>
              {#each columns as col}
                <td title={row[col]}>{row[col]}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>Loading domains...</p>
    {/if}
  </div>
</div>
