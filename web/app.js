async function loadHealth() {
  try {
    const r = await fetch("/health");
    const j = await r.json();
    document.getElementById("health-out").textContent = JSON.stringify(j, null, 2);
  } catch (e) {
    document.getElementById("health-out").textContent = "API not reachable. Run: python3 -m agent.api";
  }
}

async function runTask() {
  const task = document.getElementById("task").value.trim();
  if (!task) return;
  const out = document.getElementById("result");
  out.textContent = "running…";
  try {
    const r = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task }),
    });
    const j = await r.json();
    out.textContent = JSON.stringify(j.verification, null, 2);
  } catch (e) {
    out.textContent = "error: " + e;
  }
}

document.getElementById("run").addEventListener("click", runTask);
loadHealth();
