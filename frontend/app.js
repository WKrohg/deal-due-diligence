const API = "http://localhost:8000";

async function screenDeal() {
  const text = document.getElementById("listing-input").value.trim();
  if (!text) return;

  show("loading");
  hide("results");
  hide("error-section");
  document.getElementById("screen-btn").disabled = true;

  try {
    const res = await fetch(`${API}/screen`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ listing_text: text }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${res.status}`);
    }

    const data = await res.json();
    renderResults(data);
    show("results");
  } catch (e) {
    document.getElementById("error-msg").textContent = e.message;
    show("error-section");
  } finally {
    hide("loading");
    document.getElementById("screen-btn").disabled = false;
  }
}

function renderResults(data) {
  // Verdict banner
  const banner = document.getElementById("verdict-banner");
  banner.className = `verdict-banner ${data.verdict === "CALL" ? "call" : "pass"}`;
  document.getElementById("verdict-text").textContent =
    data.verdict === "CALL" ? "✓ CALL — Worth Pursuing" : "✗ PASS — Does Not Meet Criteria";

  // Reasoning
  document.getElementById("reasoning").textContent = data.reasoning;

  // Hard fails
  const hardCard = document.getElementById("hard-fails-card");
  const hardList = document.getElementById("hard-fails");
  if (data.hard_fails.length) {
    hardList.innerHTML = data.hard_fails
      .map(f => `<li class="fail-item">${f}</li>`)
      .join("");
    hardCard.classList.remove("hidden");
  } else {
    hardCard.classList.add("hidden");
  }

  // Soft flags
  const softCard = document.getElementById("soft-flags-card");
  const softList = document.getElementById("soft-flags");
  if (data.soft_flags.length) {
    softList.innerHTML = data.soft_flags
      .map(f => `<li class="flag-item">${f}</li>`)
      .join("");
    softCard.classList.remove("hidden");
  } else {
    softCard.classList.add("hidden");
  }

  // Questions
  document.getElementById("top-questions").innerHTML = data.top_questions
    .map(q => `<li>${q}</li>`)
    .join("");
}

function reset() {
  hide("results");
  hide("error-section");
  show("input-section");
  document.getElementById("listing-input").value = "";
}

function show(id) { document.getElementById(id).classList.remove("hidden"); }
function hide(id) { document.getElementById(id).classList.add("hidden"); }

// Submit on Cmd/Ctrl+Enter
document.addEventListener("keydown", e => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") screenDeal();
});
