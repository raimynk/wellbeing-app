const API_BASE = "https://YOUR-API-NAME.onrender.com"; // Replace after deploying the FastAPI service.
const form = document.querySelector("#form");
const output = document.querySelector("#output");
const button = document.querySelector("#submit");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  output.hidden = false;
  output.textContent = "Getting an estimate…";
  button.disabled = true;
  const f = new FormData(form);
  const payload = {
    age: Number(f.get("age")), gender: f.get("gender"), country: f.get("country"),
    academic_level: f.get("academic_level"), most_used_platform: f.get("most_used_platform"),
    purpose_of_use: f.get("purpose_of_use"), avg_daily_usage_hours: Number(f.get("avg_daily_usage_hours")),
    daily_unlocks: Number(f.get("daily_unlocks")), study_hours: Number(f.get("study_hours")),
    physical_activity_hours: Number(f.get("physical_activity_hours")),
    sleep_hours_per_night: Number(f.get("sleep_hours_per_night")), stress_level: f.get("stress_level")
  };
  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
    output.innerHTML = `<strong>Estimated score: ${Number(data.predicted_score).toFixed(2)}</strong><p>${data.notice}</p><small>Model: ${data.model}</small>`;
  } catch (error) {
    output.textContent = `Could not reach the API: ${error.message}. Check that the backend is live and API_BASE is correct.`;
  } finally { button.disabled = false; }
});
