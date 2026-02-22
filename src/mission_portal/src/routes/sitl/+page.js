/** * SITL UNIVERSAL LOAD
 * This acts as a bridge between the SITL Server and the SITL UI.
 */
export async function load({ data }) {
    // 1. Pull the telemetry array passed down from +page.server.js
    const telemetry = data?.telemetry || [];

    // 2. Perform Simulation Health Check
    // We check if the simulation results are within nominal flight bounds
    const maxAllowedDrift = 2.5;
    const driftViolation = telemetry.some(row => Math.abs(row.Roll - row.DesRoll) > maxAllowedDrift);

    // 3. Return enriched data to the +page.svelte
    return {
        ...data, // Spreads telemetry: [...] into the return object
        simEnvironment: "VIRTUAL_SITL_VAULT",
        isNominal: !driftViolation,
        integrityScore: telemetry.length > 0 ? "100%" : "0%",
        processedAt: new Date().toISOString().split('T')[1].split('.')[0] // Just the time
    };
}