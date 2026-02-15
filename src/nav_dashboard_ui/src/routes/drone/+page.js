export async function load() {
    const res = await fetch("http://127.0.0.1:8000/api/nav/domain?view=ui_nav_drone_monitor");
    const data = await res.json();

    return {
        telemetry: data.telemetry || []
    };
}
