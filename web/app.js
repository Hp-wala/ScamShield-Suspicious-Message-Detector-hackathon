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
  const ring = el("div", "score-ring");
  ring.style.setProperty("--angle", `${data.score * 3.6}deg`);
  ring.style.setProperty("--ring-color", colorForVerdict(data.verdict));
  ring.append(el("span", "", String(data.score)));
  resultBox.append(ring);
  const meta = el("div", "result-meta");
  meta.append(el("div", "badge", data.verdict));
  meta.append(el("p", "", `Category: ${data.category} | Confidence: ${data.confidence}`));
  const textModelProbability = Number(data.text_model_probability || 0);
  meta.append(el("p", "", `Text model: ${Math.round(textModelProbability * 100)}% similar to scam messages`));
  resultBox.append(meta);

  const messageBlock = el("div");
  messageBlock.append(el("h3", "", "Analysed message"));
  const highlighted = el("p");
  appendHighlighted(highlighted, data.text, data.signals || []);
  messageBlock.append(highlighted);
  resultBox.append(messageBlock);
  addUrlCards(resultBox, data.urls);
  addSignalRows(resultBox, data);
  addAdvice(resultBox, data.advice);

  const actions = el("div", "summary-actions");
  const reportButton = el("button", "", "Report this scam");
  const yesButton = el("button", "secondary", "Was this correct?");
  const copyButton = el("button", "secondary", "Copy summary");
  actions.append(reportButton, yesButton, copyButton);
  resultBox.append(actions);

  reportButton.addEventListener("click", () => reportResult(data));
  yesButton.addEventListener("click", () => feedbackResult(data, true));
  copyButton.addEventListener("click", () => copySummary(data));
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
  const body = { channel: data.channel, category: data.category, risk_score: data.score };
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
  message.placeholder = input.value === "url" ? "https://example.com/login" : "Paste the message here...";
}));

document.querySelector("#chat-file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  message.value = await file.text();
});

document.querySelector("#clear-button").addEventListener("click", () => {
  message.value = "";
  latestResult = null;
  resultBox.replaceChildren(el("p", "placeholder", "Risk analysis will appear here."));
  message.focus();
});

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
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ channel, text: message.value }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed");
    latestResult = data;
    data.type === "chat" ? renderChat(data) : renderSingle(data);
  } catch (error) {
    resultBox.replaceChildren(el("p", "", error.message));
  } finally {
    button.disabled = false;
    button.textContent = "Analyze threat";
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
}

window.addEventListener("hashchange", showRoute);
showRoute();
loadExamples();
loadLearn();
