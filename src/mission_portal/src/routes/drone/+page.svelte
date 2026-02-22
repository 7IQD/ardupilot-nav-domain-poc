<script>
  import { onMount } from 'svelte';

  let domains = ["com", "est", "nav", "power", "sys"];
  let missionList = [];
  let selectedDomain = "com";
  let selectedMission = "-- ALL MISSIONS --";
  let telemetryData = [];
  let visibleCount = 14;

  async function loadInitialData() {
    try {
      const res = await fetch('http://localhost:8000/forensic/missions');
      const json = await res.json();
      missionList = json.missions || [];
      await fetchDomainData(selectedDomain);
    } catch (e) { console.error(e); }
  }

  async function fetchDomainData(domain) {
    selectedDomain = domain;
    visibleCount = 14;
    try {
      const apiView = `${domain}_df_master`;
      const url = `http://localhost:8000/api/domain?view=${apiView}&mission=${selectedMission}`;
      const res = await fetch(url);
      const json = await res.json();
      telemetryData = json.telemetry || [];
    } catch (e) { telemetryData = []; }
  }

  function formatValue(val) {
    if (val === null || val === undefined) return '—';
    if (typeof val === 'number' && !Number.isInteger(val)) return val.toFixed(4);
    return val;
  }

  function loadMore() { visibleCount += 14; }

  // Simple reactivity: change mission -> reload data
  $: if (selectedMission) { fetchDomainData(selectedDomain); }
  onMount(loadInitialData);
</script>

<style>
  :global(body) { background-color: #000; margin: 0; font-family: 'Courier New', monospace; overflow: hidden; }

  .top-bar { background: #0a2a0a; color: #00ff41; padding: 10px; border-bottom: 2px solid #00ff41; text-align: center; font-weight: bold; }

  .main-container { display: flex; height: calc(100vh - 45px); }

  /* Slim Sidebar */
  .sidebar { width: 70px; border-right: 1px solid #1a3a1a; display: flex; flex-direction: column; gap: 8px; padding: 10px; }

  .content-area { flex-grow: 1; padding: 15px; display: flex; flex-direction: column; }

  /* Table Container: Fixed height for 14 rows, no vertical scroll */
  .table-wrapper { border: 1px solid #333; height: 520px; background: #050505; overflow-x: auto; overflow-y: hidden; }

  table { width: 100%; border-collapse: collapse; table-layout: auto; }

  th { background: #111; color: #fbff00; padding: 12px; border-bottom: 2px solid #00ff41; text-align: center; font-size: 0.85rem; white-space: nowrap; }

  /* Bold Yellow Readable Data */
  td { padding: 12px; border-bottom: 1px solid #222; text-align: center; color: #fbff00; font-weight: bold; font-size: 1.1rem; white-space: nowrap; }

  .domain-btn { width: 100%; padding: 8px 0; background: none; border: 1px solid #00ff41; color: #00ff41; cursor: pointer; font-size: 0.7rem; font-weight: bold; }
  .domain-btn.active { background: #00ff41; color: #000; }

  /* Green Bottom Row Button */
  .load-more-btn { background: #0a2a0a; color: #00ff41; border: 2px solid #00ff41; padding: 15px; width: 100%; cursor: pointer; margin-top: 10px; font-weight: bold; font-size: 1rem; text-transform: uppercase; }
  .load-more-btn:hover { background: #00ff41; color: #000; }
</style>

<div class="top-bar">DRONE_DATA_FINAL_VIEW</div>

<div class="main-container">
  <div class="sidebar">
    {#each domains as d}
      <button class="domain-btn {selectedDomain === d ? 'active' : ''}" on:click={() => fetchDomainData(d)}>
        {d.toUpperCase()}
      </button>
    {/each}
  </div>

  <div class="content-area">
    <div style="margin-bottom: 10px;">
        <select style="background:#000; color:#fbff00; border:1px solid #00ff41; padding:5px; font-weight: bold;" bind:value={selectedMission}>
            <option>-- ALL MISSIONS --</option>
            {#each missionList as m} <option value={m}>{m}</option> {/each}
        </select>
    </div>

    <div class="table-wrapper">
      {#if telemetryData.length > 0}
        <table>
          <thead>
            <tr>
              {#each Object.keys(telemetryData[0]) as header}
                {#if header !== 'mission_id'}
                   <th>{header}</th>
                {/if}
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each telemetryData.slice(visibleCount - 14, visibleCount) as row}
              <tr>
                {#each Object.keys(telemetryData[0]) as key}
                  {#if key !== 'mission_id'}
                    <td>{formatValue(row[key])}</td>
                  {/if}
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>

    <button class="load-more-btn" on:click={loadMore}>
      NEXT 14 ROWS ➔
    </button>
  </div>
</div>