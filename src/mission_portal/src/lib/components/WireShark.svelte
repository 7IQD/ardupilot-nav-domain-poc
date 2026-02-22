<script lang="ts">
  import type { LogEntry } from '$lib/types';
  export let entries: LogEntry[] = [];

  const getTime = () =>
    new Date().toLocaleTimeString([], {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
</script>

<div class="wire-container">
  {#each entries as log}
    <div
      class="log-line"
      class:bronze={log.stage === 'BRONZE'}
      class:silver={log.stage === 'SILVER'}
      class:vault={log.stage === 'VAULT'}
      class:mock={log.stage === 'MOCK'}
    >
      <span class="time">[{getTime()}]</span>
      <span class="stage">{log.stage}</span>
      <span class="msg">{log.msg}</span>
      <span class="latency">{log.latency?.toFixed(1) ?? '0.0'}ms</span>
    </div>
  {/each}
</div>

<style>
  .wire-container {
    height: 100%;
    overflow-y: auto;
    font-family: monospace;
    font-size: 10px;
    display: flex;
    flex-direction: column-reverse; /* newest at bottom */
    padding: 4px;
    background-color: rgba(0,0,0,0.4);
    border-radius: 0.5rem;
    border: 1px solid rgba(255,255,255,0.1);
  }

  .log-line {
    display: flex;
    gap: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 2px;
    align-items: center;
  }

  .time { color: #71717a; }
  .stage { font-weight: bold; width: 48px; flex-shrink: 0; }
  .msg { color: #d4d4d8; flex-grow: 1; overflow: hidden; text-overflow: ellipsis; }
  .latency { color: #a1a1aa; width: 40px; text-align: right; flex-shrink: 0; }

  .bronze .stage { color: #f59e0b; }
  .silver .stage { color: #3b82f6; }
  .vault .stage { color: #10b981; }
  .mock .stage { color: #71717a; }
</style>
