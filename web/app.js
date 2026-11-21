const form = document.querySelector("#analyzer");
const message = document.querySelector("#message");
const resultBox = document.querySelector("#result");
const channelInputs = [...document.querySelectorAll('input[name="channel"]')];
let latestResult = null;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function showRoute() {
  const hash = location.hash || "#analyze";
  document.querySelectorAll(".route-section").forEach(section => {
    section.hidden = "#" + section.id !== hash;
  });
  if (hash === "#dashboard") loadDashboard();
}

async function sha256(text) {
  try {
    const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text.trim().toLowerCase().replace(/\s+/g, " ")));
    return [...new Uint8Array(bytes)].map(value => value.toString(16).padStart(2, "0")).join("");
  } catch (_error) {
    return null;
  }
}

function mergeRanges(ranges) {
  const sorted = ranges.filter(range => range && Number.isInteger(range.start) && Number.isInteger(range.end) && range.end > range.start)
    .sort((a, b) => a.start - b.start);
  const merged = [];
  for (const range of sorted) {
    const last = merged[merged.length - 1];
    if (last && range.start <= last.end) last.end = Math.max(last.end, range.end);
    else merged.push({ start: range.start, end: range.end });
  }
  return merged;
}

function appendHighlighted(container, text, signals) {
  const ranges = signals.flatMap(signal => signal.matches || []);
  let cursor = 0;
  for (const range of mergeRanges(ranges)) {
    if (range.start > cursor) container.append(document.createTextNode(text.slice(cursor, range.start)));
    const mark = el("mark", "", text.slice(range.start, range.end));
    container.append(mark);
    cursor = range.end;
  }
  if (cursor < text.length) container.append(document.createTextNode(text.slice(cursor)));
}

function colorForVerdict(verdict) {
  if (verdict === "Likely Scam") return "#c53b40";
  if (verdict === "Suspicious") return "#c77d19";
  return "#21875f";
}

function addSignalRows(container, data) {
  const title = el("h3", "", "Why this looks risky");
  container.append(title);
  const list = el("ul");
  for (const signal of data.signals || []) {
    const item = el("li");
    item.append(el("strong", "", signal.label + ": "));
    item.append(document.createTextNode(signal.explanation));
    list.append(item);
  }
  if (!data.signals || data.signals.length === 0) list.append(el("li", "", "No strong scam indicators detected."));
  container.append(list);
}

function addAdvice(container, advice) {
  const wrapper = el("div");
  wrapper.append(el("h3", "", "What to do"));
  const doList = el("ul", "advice-list");
  (advice.do || []).forEach(item => doList.append(el("li", "", item)));
  wrapper.append(doList);
  wrapper.append(el("h3", "", "What NOT to do"));
  const dontList = el("ul", "advice-list");
  (advice.dont || []).forEach(item => dontList.append(el("li", "", item)));
  wrapper.append(dontList);
  container.append(wrapper);
}

function addUrlCards(container, urls) {
  if (!urls || urls.length === 0) return;
  container.append(el("h3", "", "Link findings"));
  urls.forEach(url => {
    const card = el("div", "url-card");
    card.append(el("strong", "", url.url));
    card.append(el("p", "", `${url.verdict.toUpperCase()} - ${url.score}/100`));
    if (url.findings.length) {
      const list = el("ul");
      url.findings.forEach(finding => list.append(el("li", "", finding.explanation)));
      card.append(list);
    }
    card.append(el("small", "", "Do not open this link."));
    container.append(card);
  });
}

function renderSingle(data) {
  resultBox.replaceChildren();
  const safe = data.score < 30 || data.verdict === "Safe";
  const suspicious = data.verdict === "Suspicious";
  const card = el("div", `risk-card ${safe ? "safe" : suspicious ? "suspicious" : "danger"}`);
  const heading = el("div", "risk-heading");
  const badgeText = safe ? "Safe" : suspicious ? "Suspicious" : "High risk";
  heading.append(
    el("span", `risk-badge ${safe ? "safe" : suspicious ? "suspicious" : "high"}`, badgeText),
    el("span", "threat-score", `${data.score} / 100 Threat Score`)
  );
  card.append(heading);
  const list = el("ul");
  if (safe) {
    list.append(el("li", "", "No strong scam indicators were detected."));
  } else {
    const reasons = (data.signals || []).filter(signal => signal.points > 0).slice(0, 3);
    if (reasons.length === 0) {
      list.append(el("li", "", "The message has elevated risk indicators."));
    } else {
      reasons.forEach(reason => list.append(el("li", "", reason.explanation)));
    }
  }
  card.append(list);
  const probability = Number((data.ml && data.ml.scam_probability) || data.text_model_probability || 0);
  card.append(el("p", "text-model-line", `Text model: ${Math.round(probability * 100)}% similar to scam messages`));
  resultBox.append(card);
}

function renderChat(data) {
  resultBox.replaceChildren();
  const summary = el("div");
  summary.append(el("h2", "", "WhatsApp chat scan"));
  summary.append(el("p", "", `${data.chat.total} messages | ${data.chat.flagged} flagged | ${data.chat.scam} likely scams`));
  resultBox.append(summary);
  const table = el("table", "chat-table");
  const thead = el("thead");
  const headRow = el("tr");
  ["Sender", "Risk", "Verdict", "Details"].forEach(text => headRow.append(el("th", "", text)));
  thead.append(headRow);
  table.append(thead);
  const tbody = el("tbody");
  [...data.messages].sort((a, b) => b.result.score - a.result.score).forEach(message => {
    const row = el("tr");
    row.append(el("td", "", message.sender || "Unknown"), el("td", "", String(message.result.score)), el("td", "", message.result.verdict));
    const detailCell = el("td");
    const details = el("details");
    details.append(el("summary", "", "Why"));
    const reasons = el("ul");
    (message.result.signals || []).forEach(signal => reasons.append(el("li", "", signal.label)));
    details.append(reasons);
    detailCell.append(details);
    row.append(detailCell);
    tbody.append(row);
  });
  table.append(tbody);
  resultBox.append(table);
}

async function reportResult(data) {
  const hash = await sha256(data.text);
  const body = {
    channel: data.channel,
    category: data.category,
    risk_score: data.score,
    state: document.querySelector("#state-select")?.value || "",
  };
  if (hash) body.message_hash = hash;
  else body.text = data.text;
  const response = await fetch("/api/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const result = await response.json();
  alert(response.ok ? (result.status === "duplicate" ? "This report was already submitted." : "Scam report submitted.") : result.error);
}

async function feedbackResult(data, correct) {
  await fetch("/api/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ channel: data.channel, verdict: data.verdict, correct }) });
  alert("Thank you. Your feedback was recorded without saving message text.");
}

async function copySummary(data) {
  const summary = `ScamShield: ${data.verdict} (${data.score}/100)\nCategory: ${data.category}\nConfidence: ${data.confidence}\nWhy: ${(data.signals || []).map(signal => signal.label).join(", ")}`;
  try {
    await navigator.clipboard.writeText(summary);
    alert("Summary copied.");
  } catch (_error) {
    alert("Copy unavailable in this browser.");
  }
}

channelInputs.forEach(input => input.addEventListener("change", () => {
  document.querySelector("#chat-upload").hidden = input.value !== "whatsapp";
  message.placeholder = input.value === "url" ? "https://example.com/login" : "Email, post or paste any message...";
}));

document.querySelector("#chat-file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  message.value = await file.text();
});

document.querySelector("#image-file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("image", file);
  formData.append("mode", "ocr");
  resultBox.replaceChildren(el("p", "placeholder", "Scanning image locally..."));
  try {
    const response = await fetch("/api/analyze-image", { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Image analysis failed");
    if (data.ocr_analysis) renderSingle(data.ocr_analysis);
    else if (data.qr && data.qr.status === "ok") {
      resultBox.replaceChildren(el("h2", "", "QR scan"), el("p", "", `${data.qr.urls.length} URL(s) decoded and analysed locally.`));
    } else {
      resultBox.replaceChildren(el("p", "", data.ocr.reason || data.qr.reason || "No text or QR content detected."));
    }
  } catch (error) {
    resultBox.replaceChildren(el("p", "", error.message));
  } finally {
    event.target.value = "";
  }
});

document.querySelector("#voice-analyze").addEventListener("click", async () => {
  const transcript = document.querySelector("#voice-text").value;
  if (!transcript.trim()) {
    resultBox.replaceChildren(el("p", "", "Paste a call transcript first."));
    return;
  }
  try {
    const response = await fetch("/api/voice", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ text: transcript }),
    });
    const data = await response.json();
    if (data.status === "ok") renderSingle(data.analysis);
    else resultBox.replaceChildren(el("p", "", data.reason || "Voice analysis unavailable."));
  } catch (error) {
    resultBox.replaceChildren(el("p", "", error.message));
  }
});

document.querySelector("#voice-audio-analyze").addEventListener("click", async () => {
  const file = document.querySelector("#voice-audio").files[0];
  if (!file) {
    resultBox.replaceChildren(el("p", "", "Choose a WAV audio file first."));
    return;
  }
  const formData = new FormData();
  formData.append("audio", file);
  try {
    const response = await fetch("/api/voice", { method: "POST", body: formData });
    const data = await response.json();
    resultBox.replaceChildren(el("p", "", data.reason || data.status || "Audio analysis unavailable."));
  } catch (error) {
    resultBox.replaceChildren(el("p", "", error.message));
  } finally {
    document.querySelector("#voice-audio").value = "";
  }
});

const clearButton = document.querySelector("#clear-button");
if (clearButton) {
  clearButton.addEventListener("click", () => {
    message.value = "";
    latestResult = null;
    resultBox.replaceChildren(el("p", "placeholder", "Risk analysis will appear here."));
    message.focus();
  });
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (!message.value.trim()) {
    resultBox.replaceChildren(el("p", "placeholder", "Please enter a message or link."));
    message.focus();
    return;
  }
  const channel = new FormData(form).get("channel");
  const button = document.querySelector("#analyze-button");
  button.disabled = true;
  button.textContent = "Analyzing...";
  resultBox.replaceChildren(el("p", "placeholder", "Checking local threat indicators..."));
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        channel,
        text: message.value,
        deep_scan: document.querySelector("#deep-scan")?.checked || false,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed");
    latestResult = data;
    data.type === "chat" ? renderChat(data) : renderSingle(data);
  } catch (error) {
    resultBox.replaceChildren(el("p", "", error.message));
  } finally {
    button.disabled = false;
    button.textContent = "Check now";
  }
});

async function loadExamples() {
  try {
    const response = await fetch("/api/examples");
    const data = await response.json();
    const container = document.querySelector("#examples");
    container.replaceChildren();
    data.examples.forEach(example => {
      const chip = el("button", "example-chip", example.label);
      chip.type = "button";
      chip.addEventListener("click", () => {
        const radio = document.querySelector(`input[name="channel"][value="${example.channel}"]`);
        radio.checked = true;
        radio.dispatchEvent(new Event("change"));
        message.value = example.text;
        message.focus();
      });
      container.append(chip);
    });
  } catch (_error) {}
}

async function loadDashboard() {
  const container = document.querySelector("#dashboard-content");
  try {
    const response = await fetch("/api/stats");
    const data = await response.json();
    container.replaceChildren();
    if (data.total_reports === 0) {
      container.append(el("p", "", "No reports yet. Analyze a message to populate the dashboard."));
      return;
    }
    const stats = el("div", "stat-row");
    const total = el("div", "stat"); total.append(el("strong", "", String(data.total_reports)), el("span", "", "Total reports"));
    const average = el("div", "stat"); average.append(el("strong", "", String(data.average_risk_score)), el("span", "", "Average risk"));
    const categories = el("div", "stat"); categories.append(el("strong", "", String(data.categories.length)), el("span", "", "Categories"));
    stats.append(total, average, categories);
    container.append(stats);
    container.append(el("h3", "", "By category"));
    data.categories.forEach(item => appendBar(container, item.category, item.count, data.total_reports));
    container.append(el("h3", "", "By channel"));
    data.channels.forEach(item => appendBar(container, item.channel, item.count, data.total_reports));
  } catch (_error) {
    container.replaceChildren(el("p", "", "Statistics unavailable."));
  }
  loadModelAccuracy();
  loadTimelineAndHeatmap();
}

async function loadTimelineAndHeatmap() {
  const container = document.querySelector("#dashboard-content");
  try {
    const [timelineResponse, heatmapResponse] = await Promise.all([
      fetch("/api/timeline"),
      fetch("/api/heatmap"),
    ]);
    const timeline = await timelineResponse.json();
    const heatmap = await heatmapResponse.json();
    container.append(el("h3", "", "Recent scam timeline"));
    (timeline.timeline || []).slice(0, 10).forEach(item =>
      container.append(el("p", "", `${item.day}: ${item.category} — ${item.count} report(s)`))
    );
    if (!timeline.timeline || timeline.timeline.length === 0) {
      container.append(el("p", "", "No timeline reports yet."));
    }
    container.append(el("h3", "", "State-level report heatmap"));
    (heatmap.states || []).slice(0, 12).forEach(item =>
      container.append(el("p", "", `${item.state}: ${item.count} report(s) — ${item.category}`))
    );
    if (!heatmap.states || heatmap.states.length === 0) {
      container.append(el("p", "", "No state reports yet."));
    }
  } catch (_error) {
    container.append(el("p", "", "Timeline and state map unavailable."));
  }
}

async function loadModelAccuracy() {
  const container = document.querySelector("#model-accuracy");
  if (!container) return;
  try {
    const response = await fetch("/api/metrics");
    const data = await response.json();
    container.replaceChildren();
    if (!response.ok || data.available === false || !data.rules_plus_ml) {
      container.append(el("p", "", "Not evaluated yet"));
      return;
    }
    const metrics = data.rules_plus_ml.flexible;
    const cards = el("div", "stat-row");
    [
      ["Accuracy", metrics.accuracy],
      ["Precision", metrics.precision],
      ["Recall", metrics.recall],
    ].forEach(([label, value]) => {
      const card = el("div", "stat");
      card.append(el("strong", "", `${Math.round(value * 100)}%`), el("span", "", label));
      cards.append(card);
    });
    container.append(cards);
    const extra = el("div", "stat-row");
    [
      ["F1", metrics.f1],
      ["False-positive rate", metrics.false_positive_rate],
    ].forEach(([label, value]) => {
      const card = el("div", "stat");
      card.append(el("strong", "", `${(value * 100).toFixed(1)}%`), el("span", "", label));
      extra.append(card);
    });
    container.append(extra);
    const matrix = metrics.confusion_matrix;
    container.append(el("h4", "", "Confusion matrix"));
    const table = el("table", "chat-table");
    table.append(el("tr"));
    const header = el("tr");
    header.append(el("th", "", "Actual / Predicted"), el("th", "", "Scam"), el("th", "", "Genuine"));
    table.append(header);
    const scamRow = el("tr");
    scamRow.append(el("th", "", "Scam"), el("td", "", String(matrix.tp)), el("td", "", String(matrix.fn)));
    const genuineRow = el("tr");
    genuineRow.append(el("th", "", "Genuine"), el("td", "", String(matrix.fp)), el("td", "", String(matrix.tn)));
    table.append(scamRow, genuineRow);
    container.append(table);
    container.append(el("h4", "", "Per-category recall"));
    Object.entries(metrics.per_category_recall || {}).forEach(([label, value]) => appendBar(container, label, value, 1));
    container.append(el("h4", "", "Per-language accuracy"));
    Object.entries(metrics.per_language_accuracy || {}).forEach(([label, value]) => appendBar(container, label, value, 1));
    container.append(el("p", "", `Evaluated on ${data.test_size} held-out messages (synthetic dataset). Not a guarantee of real-world accuracy.`));
  } catch (_error) {
    container.replaceChildren(el("p", "", "Not evaluated yet"));
  }
}

function appendBar(container, label, count, total) {
  const row = el("div", "bar-row");
  row.append(el("span", "", label));
  const bar = el("div", "bar");
  const fill = el("span");
  fill.style.width = `${total ? count / total * 100 : 0}%`;
  bar.append(fill);
  row.append(bar, el("strong", "", String(count)));
  container.append(row);
}

function loadLearn() {
  const cards = [
    ["Bank/KYC", "KYC blocked, OTP required", ["Urgency", "Credential request", "Unknown link"]],
    ["Delivery", "Parcel held, redelivery fee", ["Fee pressure", "Address ask", "Short link"]],
    ["Government", "Tax or police fine", ["Authority spoof", "Video call", "Immediate payment"]],
    ["Lottery", "Won a lucky draw", ["Prize lure", "Fee to claim", "Personal details"]],
    ["Job", "Earn daily from Telegram", ["Easy money", "Registration fee", "WhatsApp shift"]],
    ["UPI", "Collect request or QR", ["Receive money", "UPI PIN ask", "Sent by mistake"]],
    ["Digital arrest", "CBI/NCB arrest call", ["Secrecy", "Video call", "Payment threat"]],
    ["Impersonation", "Relative on new number", ["New number", "Urgent money", "No verification"]],
  ];
  const container = document.querySelector("#scam-cards");
  cards.forEach(([title, example, flags]) => {
    const card = el("article", "card");
    card.append(el("h3", "", title), el("p", "", example));
    const list = el("ul");
    flags.forEach(flag => list.append(el("li", "", flag)));
    card.append(list, el("small", "", "Verify through an official app or printed number."));
    container.append(card);
  });
  loadQuiz();
}

const QUIZ = [
  ["A bank asks for your OTP on a phone call. What is safest?", ["Share only because it is a bank", "Never share it", "Share only after a PIN"], 1, "Banks never ask for OTP or PIN."],
  ["A parcel fee arrives as a short link. What should you do?", ["Pay quickly", "Verify in the official courier app", "Forward to friends"], 1, "Verify parcel status using the official app."],
  ["Your relative from a new number asks for urgent money. Next step?", ["Send immediately", "Verify by calling the saved number", "Share UPI PIN"], 1, "Confirm the person through a known number."],
  ["A UPI app asks you to enter PIN to receive money. What is true?", ["Receiving needs PIN", "No PIN is required to receive", "Scan and enter PIN"], 1, "UPI PIN is used for sending money, not receiving."],
  ["An electricity officer says disconnection tonight unless you pay now.", ["Pay the private link", "Verify on the official utility account", "Share Aadhaar"], 1, "Use official bills and utility apps."],
  ["A caller claims to be CBI and demands secrecy and a video call.", ["Stay silent and pay", "Disconnect and report 1930", "Download AnyDesk"], 1, "Do not join secret video calls or pay."],
  ["An unknown lucky-draw message asks for a claim fee.", ["Pay to claim", "Ignore and verify official channels", "Send bank details"], 1, "Legitimate prizes do not require advance fees."],
  ["A job asks for registration money before work.", ["Pay immediately", "Verify the employer officially", "Share CVV"], 1, "Real employers do not require an advance job fee."],
  ["A QR on a poster says it will give cashback.", ["Scan and enter PIN", "Only scan trusted official sources", "Share OTP"], 1, "Inspect the source and never enter PIN for cashback."],
  ["An email display name says SBI but sender address looks unrelated.", ["Trust the display name", "Verify sender domain and Reply-To", "Download the attachment"], 1, "Verify the full address and official domain."],
  ["A digital arrest caller asks you to stay on video and move money.", ["Follow instructions", "Disconnect and report", "Share screen"], 1, "No agency conducts this process over a private video call."],
  ["A normal order SMS provides an official retailer tracking link.", ["It is always safe", "Still verify domain and account", "Ignore HTTPS"], 1, "Official links reduce risk but context should still be checked."],
];

function loadQuiz() {
  const container = document.querySelector("#quiz");
  if (!container) return;
  let index = 0;
  let score = 0;
  container.replaceChildren();
  function renderQuestion() {
    container.replaceChildren();
    if (index >= QUIZ.length) {
      container.append(el("p", "", `Quiz score: ${score}/${QUIZ.length}`));
      const reset = el("button", "", "Try again");
      reset.addEventListener("click", () => { index = 0; score = 0; renderQuestion(); });
      container.append(reset);
      return;
    }
    const [question, options, correct, explanation] = QUIZ[index];
    container.append(el("p", "", `${index + 1}. ${question}`));
    options.forEach((option, optionIndex) => {
      const button = el("button", "secondary", option);
      button.addEventListener("click", () => {
        if (optionIndex === correct) score++;
        container.append(el("p", "", `${optionIndex === correct ? "Correct." : "Incorrect."} ${explanation}`));
        const next = el("button", "", "Next");
        next.addEventListener("click", () => { index++; renderQuestion(); });
        container.append(next);
      });
      container.append(button);
    });
  }
  renderQuestion();
}

const breachButton = document.querySelector("#breach-run");
if (breachButton) {
  breachButton.addEventListener("click", async () => {
    const result = document.querySelector("#breach-result");
    const payload = {
      email: document.querySelector("#breach-email").value,
      password: document.querySelector("#breach-password").value,
      phone: document.querySelector("#breach-phone").value,
    };
    document.querySelector("#breach-password").value = "";
    try {
      const response = await fetch("/api/breach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      result.replaceChildren();
      result.append(el("p", "", `Email: ${data.email.status}${data.email.breach_names?.length ? " — " + data.email.breach_names.join(", ") : ""}`));
      result.append(el("p", "", `Password: ${data.password.status}${data.password.pwned ? " — found in breach data" : ""}`));
      result.append(el("p", "", `Phone: ${data.phone.status} — ${data.phone.reason}`));
    } catch (error) {
      result.replaceChildren(el("p", "", error.message));
    }
  });
}

window.addEventListener("hashchange", showRoute);
showRoute();
loadExamples();
loadLearn();
