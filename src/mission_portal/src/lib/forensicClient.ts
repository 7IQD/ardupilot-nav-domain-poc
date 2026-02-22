// * Forensic Client

const BASE_URL = 'http://127.0.0.1:8000';

// --- Interfaces ---

export interface MissionListResponse {
    missions: string[];
}

export interface MissionSummary {
    mission_id: string;
    start_ns: number;
    end_ns: number;
    duration_sec: number;
}

export interface DomainListResponse {
    domains: string[];
}

export interface TelemetryResponse {
    telemetry: any[];
}

// --- Client Implementation ---

export const forensicClient = {
    /**
     * DOMAINS: List all available DuckDB views/tables
     * Endpoint: GET /api/domains
     */
    async listDomains(): Promise<DomainListResponse> {
        const res = await fetch(`${BASE_URL}/api/domains`);
        if (!res.ok) throw new Error(`Domains Fetch Error: ${res.status}`);
        return res.json();
    },

    /**
     * DOMAINS: Fetch row data for a specific view
     * Endpoint: GET /api/domain?view=...
     */
    async getDomainData(view: string): Promise<TelemetryResponse> {
        // FIXED: Removed /nav/ from the path
        const res = await fetch(`${BASE_URL}/api/domain?view=${view}`);
        if (!res.ok) throw new Error(`Telemetry Fetch Error: ${res.status}`);
        return res.json();
    },

    /**
     * FORENSIC: List all unique missions
     * Endpoint: GET /forensic/missions
     */
    async listMissions(): Promise<MissionListResponse> {
        const res = await fetch(`${BASE_URL}/forensic/missions`);
        if (!res.ok) throw new Error(`Missions Fetch Error: ${res.status}`);
        return res.json();
    },

    /**
     * FORENSIC: Get timing and summary for a mission
     * Endpoint: GET /forensic/mission/{id}/summary
     */
    async getSummary(id: string): Promise<MissionSummary> {
        const res = await fetch(`${BASE_URL}/forensic/mission/${id}/summary`);
        if (!res.ok) throw new Error(`Summary Fetch Error: ${res.status}`);
        return res.json();
    }
};