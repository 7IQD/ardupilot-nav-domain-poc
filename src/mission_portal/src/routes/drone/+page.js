import { forensicClient } from '$lib/forensicClient';

/** @type {import('./$types').PageLoad} */
export async function load() {
    try {
        const [domainRes, missionRes] = await Promise.all([
            forensicClient.listDomains(),
            forensicClient.listMissions()
        ]);

        return {
            domains: domainRes?.domains || [],
            missions: missionRes?.missions || [],
            error: null
        };
    } catch (e) {
        console.error("Fetch Error:", e);
        return {
            domains: [],
            missions: [],
            error: "Backend Offline"
        };
    }
}