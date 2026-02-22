import { writable } from 'svelte/store';

// 1. Define the Data Contract
export interface LogEntry {
    stage: 'BRONZE' | 'SILVER' | 'VAULT' | 'MOCK';
    msg: string;
    latency: number;
}

export interface NavStore {
    telemetry: {
        drift: number;
        vx_mps: number;
        lat_drift: number;
        alt_drift: number;
        phase: string;
        sensors: { gps: number; imu: number; baro: number };
    };
    logs: LogEntry[];
    pipeline: {
        ingress_hz: number;
        ingest_ms: number;
        vault_ok: boolean;
    };
}

// 2. The Hardcoded Initial State (Prevents 'never' type errors)
const INITIAL_STATE: NavStore = {
    telemetry: {
        drift: 0,
        vx_mps: 0,
        lat_drift: 0,
        alt_drift: 0,
        phase: 'BOOTING...',
        sensors: { gps: 0, imu: 0, baro: 0 }
    },
    logs: [],
    pipeline: {
        ingress_hz: 0,
        ingest_ms: 0,
        vault_ok: true
    }
};

// 3. Create the Store with explicit Generic Type
export const liveTelemetry = writable<NavStore>(INITIAL_STATE);

// 4. The Data Fetcher (The Pulse)
export const fetchPulse = async () => {
    try {
        // Change this URL if your FastAPI is on a different port
        const response = await fetch('http://localhost:8000/api/nav/live');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        liveTelemetry.update((current) => {
            return {
                ...current,
                telemetry: {
                    drift: data.telemetry?.drift ?? current.telemetry.drift,
                    vx_mps: data.telemetry?.vx_mps ?? current.telemetry.vx_mps,
                    lat_drift: data.telemetry?.lat_drift ?? current.telemetry.lat_drift,
                    alt_drift: data.telemetry?.alt_drift ?? current.telemetry.alt_drift,
                    phase: data.telemetry?.phase ?? current.telemetry.phase,
                    sensors: data.telemetry?.sensors ?? current.telemetry.sensors
                },
                pipeline: {
                    ingress_hz: data.pipeline?.ingress_hz ?? current.pipeline.ingress_hz,
                    ingest_ms: data.pipeline?.ingest_ms ?? current.pipeline.ingest_ms,
                    vault_ok: true
                },
                // Keep the last 50 logs, newest first
                logs: data.logs ? [...data.logs, ...current.logs].slice(0, 50) : current.logs
            };
        });
    } catch (error) {
        console.error("Telemetry Sync Failed:", error);
        liveTelemetry.update(s => ({
            ...s,
            pipeline: { ...s.pipeline, vault_ok: false }
        }));
    }
};

/**
 * MOCK DATA GENERATOR (For testing without the backend)
 * Run this in onMount if your FastAPI server isn't ready.
 */
export const startMockHeartbeat = () => {
    return setInterval(() => {
        liveTelemetry.update(s => ({
            ...s,
            telemetry: {
                ...s.telemetry,
                drift: Math.random() * 2,
                phase: 'MOCK_RUNNING'
            },
            logs: [{
                stage: 'MOCK',
                msg: `Simulated Packet Received: ${Math.random().toString(36).substring(7)}`,
                latency: Math.random() * 10
            }, ...s.logs].slice(0, 50)
        }));
    }, 1000);
};