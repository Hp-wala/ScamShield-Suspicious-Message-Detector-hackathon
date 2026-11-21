const form = document.querySelector("#analyzer");
const message = document.querySelector("#message");
const result = document.querySelector("#result");
const statsBox = document.querySelector("#stats");

async function loadStats() {
  const response = await fetch("/api/stats");
  if (!response.ok) return;
  const data = await response.json();
  statsBox.innerHTML = `
    <div class="stat-row">
      <div class="stat"><strong>${data.total_reports}</strong><span>Reports analysed</span></div>
      <div class="stat"><strong>${data.average_risk_score}</strong><span>Average risk</span></div>
      <div class="stat"><strong>${data.categories.length}</strong><span>Categories seen</span></div>
    </div>`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const channel = new FormData(form).get("channel");
  const button = document.querySelector("#analyze-button");
  button.disabled = true;
  button.textContent = "Analyzing...";
  result.innerHTML = "<p class=\"placeholder\">Checking local threat indicators...</p>";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel, text: message.value })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed");

    const color = data.risk_level === "high_risk" ? "#c74732" :
      data.risk_level === "suspicious" ? "#f0a04b" : "#155d46";
    result.innerHTML = `
      <div class="score-ring" style="--score:${data.risk_score * 3.6}deg;background:conic-gradient(${color} ${data.risk_score * 3.6}deg,#ece8dd 0)">
        <span>${data.risk_score}</span>
      </div>
      <h2>${data.risk_level.replaceAll("_", " ")}</h2>
      <p><strong>Category:</strong> ${data.category}</p>
      <ul>${data.reasons.map(reason => `<li>${reason}</li>`).join("")}</ul>`;
    await loadStats();
  } catch (error) {
    result.innerHTML = `<p>${error.message}</p>`;
  } finally {
    button.disabled = false;
    button.textContent = "Analyze threat";
  }
});

loadStats();
