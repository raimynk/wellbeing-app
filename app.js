const form = document.querySelector("#checkin-form");
const result = document.querySelector("#result");
const sleep = document.querySelector("#sleep");
const movement = document.querySelector("#movement");
const screen = document.querySelector("#screen");

const hours = value => `${Number(value).toLocaleString()} ${Number(value) === 1 ? "hour" : "hours"}`;
sleep.addEventListener("input", () => document.querySelector("#sleep-value").textContent = hours(sleep.value));
movement.addEventListener("input", () => document.querySelector("#movement-value").textContent = `${movement.value} minutes`);
screen.addEventListener("input", () => document.querySelector("#screen-value").textContent = hours(screen.value));

function scoreHabits({ sleepHours, movementMinutes, screenHours, stress }) {
  // A simple, explicit heuristic for reflection; this is not a trained or validated model.
  const sleepPoints = Math.max(0, 35 - Math.abs(sleepHours - 8) * 7);
  const movementPoints = Math.min(25, movementMinutes / 4);
  const screenPoints = Math.max(0, 20 - Math.max(0, screenHours - 2) * 2.5);
  const stressPoints = (4 - stress) * (20 / 3);
  return Math.round(sleepPoints + movementPoints + screenPoints + stressPoints);
}

function suggestions(values) {
  const tips = [];
  if (values.sleepHours < 7) tips.push("If possible, try a calm wind-down routine and give yourself a little more time for sleep.");
  if (values.movementMinutes < 30) tips.push("A short walk or stretch break could be an easy way to add movement today.");
  if (values.screenHours > 5) tips.push("Consider taking a screen break or setting aside a screen-free moment before bed.");
  if (values.stress >= 3) tips.push("Try a small reset: slow breathing, a brief pause, or talking with someone you trust.");
  if (!tips.length) tips.push("Your selected habits look fairly balanced today. Keep noticing what helps you feel well.");
  return tips;
}

form.addEventListener("submit", event => {
  event.preventDefault();
  const values = {
    sleepHours: Number(sleep.value),
    movementMinutes: Number(movement.value),
    screenHours: Number(screen.value),
    stress: Number(document.querySelector("#stress").value)
  };
  const score = scoreHabits(values);
  document.querySelector("#score").textContent = score;
  document.querySelector("#result-title").textContent = score >= 70 ? "A steadier day" : score >= 45 ? "Some things to build on" : "Take things one step at a time";
  document.querySelector("#result-copy").textContent = "This number is only a summary of the habit sliders you selected. It is not a measure of your mental health.";
  const list = document.querySelector("#tips");
  list.replaceChildren(...suggestions(values).map(text => { const li = document.createElement("li"); li.textContent = text; return li; }));
  result.hidden = false;
  result.scrollIntoView({ behavior: "smooth", block: "start" });
});

document.querySelector("#reset").addEventListener("click", () => {
  result.hidden = true;
  form.scrollIntoView({ behavior: "smooth", block: "start" });
});
