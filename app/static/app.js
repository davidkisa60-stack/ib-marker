/* IB Marker front end */
(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const el = (tag, attrs = {}, children = []) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "html") node.innerHTML = v;
      else if (k === "text") node.textContent = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v);
    }
    for (const c of [].concat(children)) {
      if (c == null) continue;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return node;
  };
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));

  // When the page is hosted separately from the API (for example on Netlify), static/config.js sets window.IB_MARKER_API.
  const API_BASE = String(window.IB_MARKER_API || "").replace(/\/+$/, "");
  const api = (path) => API_BASE + path;

  const state = {
    rubrics: [],
    guidance: {},
    providers: [],
    groups: [],
    serverKeys: {},
    health: { access_required: false },
    accessCode: localStorage.getItem("ibm_access") || "",
    settingsSaved: false,
    component: "Internal Assessment",
    subject: null,
    rubricId: null,
    file: null,
    settings: { provider: "gemini", remember: false, models: {}, baseUrls: {}, keys: {} },
    custom: { name: "", subject: "", limit: "", criteria: [] },
    timer: null,
    lastResponse: null,
  };

  // ------------------------------------------------------------ settings storage
  function loadSettings() {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem("ibm_settings_v2") || "null"); } catch (_) { /* ignore */ }
    if (saved) {
      state.settingsSaved = true;
      Object.assign(state.settings, saved);
      state.settings.models = saved.models || {};
      state.settings.baseUrls = saved.baseUrls || {};
      state.settings.keys = saved.remember ? (saved.keys || {}) : {};
    } else {
      // migrate the first version of the settings object
      try {
        const old = JSON.parse(localStorage.getItem("ibm_settings") || "null");
        if (old && old.provider) {
          state.settingsSaved = true;
          const pid = (old.provider === "openai" && old.baseUrl) ? "custom" : old.provider;
          state.settings.provider = pid;
          if (old.model) state.settings.models[pid] = old.model;
          if (old.baseUrl) state.settings.baseUrls[pid] = old.baseUrl;
          if (old.apiKey) state.settings.keys[pid] = old.apiKey;
          state.settings.remember = !!old.remember;
        }
      } catch (_) { /* ignore */ }
    }
    if (!state.settings.remember) {
      try { Object.assign(state.settings.keys, JSON.parse(sessionStorage.getItem("ibm_keys") || "{}")); } catch (_) { /* ignore */ }
    }
  }
  function saveSettings() {
    const s = state.settings;
    const persist = { provider: s.provider, remember: s.remember, models: s.models, baseUrls: s.baseUrls, keys: s.remember ? s.keys : {} };
    localStorage.setItem("ibm_settings_v2", JSON.stringify(persist));
    sessionStorage.setItem("ibm_keys", JSON.stringify(s.remember ? {} : s.keys));
    renderKeyStatus();
  }
  function providerById(id) { return state.providers.find((p) => p.id === id) || state.providers[0]; }
  function currentProvider() { return providerById(state.settings.provider); }
  function keyFor(pid) { return (state.settings.keys[pid] || "").trim(); }
  function modelFor(p) { return (state.settings.models[p.id] || "").trim() || p.default_model; }

  function renderKeyStatus() {
    const p = currentProvider();
    const status = $("#key-status");
    if (!p) { status.textContent = ""; return; }
    const usingServerKey = !keyFor(p.id) && !!state.serverKeys[p.id];
    const ready = !p.requires_key || keyFor(p.id) || state.serverKeys[p.id];
    const model = modelFor(p);
    const access = state.health.access_required && !state.accessCode ? " This server also needs an access code; you will be asked for it on the first analysis." : "";
    if (ready && model) {
      status.innerHTML = `Ready: <b>${esc(p.name)}</b>, model <code>${esc(model)}</code>${usingServerKey ? " (using this server's built-in key)" : ""}. <a href="#" id="open-settings-link">Change</a>.${esc(access)}`;
    } else if (ready) {
      status.innerHTML = `${esc(p.name)} is selected but no model name is set. <a href="#" id="open-settings-link">Set one in Settings</a>.`;
    } else {
      const builtIn = state.providers.find((x) => state.serverKeys[x.id]);
      const tip = builtIn ? ` Tip: this server has a built-in key for ${esc(builtIn.name)}; select it in Settings and no key is needed.` : "";
      status.innerHTML = `No API key set for ${esc(p.name)}. <a href="#" id="open-settings-link">Add a free key in Settings</a> (takes two minutes).${tip} The pre-check and the sample report work without one.`;
    }
    const link = $("#open-settings-link");
    if (link) link.addEventListener("click", (e) => { e.preventDefault(); openSettings(); });
  }

  // ------------------------------------------------------------ settings dialog
  function buildProviderSelect() {
    const sel = $("#provider-select");
    sel.innerHTML = "";
    for (const [gid, glabel] of state.groups) {
      const items = state.providers.filter((p) => p.group === gid);
      if (!items.length) continue;
      const og = el("optgroup", { label: glabel });
      for (const p of items) og.appendChild(el("option", { value: p.id, text: p.name }));
      sel.appendChild(og);
    }
  }
  function renderProviderPanel(pid) {
    const p = providerById(pid);
    if (!p) return;
    const s = state.settings;
    const urlInput = $("#base-url-input");
    urlInput.value = s.baseUrls[p.id] || p.base_url || "";
    urlInput.readOnly = !p.base_url_editable;
    urlInput.classList.toggle("readonly", !p.base_url_editable);
    $("#base-url-field").classList.toggle("hidden", p.api === "anthropic");

    const modelInput = $("#model-input");
    modelInput.value = s.models[p.id] || "";
    modelInput.placeholder = p.default_model || "model name (required)";
    const dl = $("#model-options");
    dl.innerHTML = "";
    for (const m of p.models) dl.appendChild(el("option", { value: m }));

    const keyInput = $("#api-key-input");
    keyInput.value = s.keys[p.id] || "";
    keyInput.placeholder = p.requires_key ? "paste the key here" : "not needed for this provider";
    const serverKey = state.serverKeys[p.id];
    $("#key-hint").innerHTML = p.requires_key
      ? (serverKey ? "The server already has a key for this provider; leave this empty to use it, or paste your own." : `Get a key: <a href="${esc(p.key_url)}" target="_blank" rel="noopener">${esc(p.key_url)}</a>`)
      : "No key is needed. Leave empty unless your server requires one.";

    $("#provider-info").innerHTML = `
      ${p.notes ? `<div class="pi-note">${esc(p.notes)}</div>` : ""}
      <div><b>Limits:</b> ${esc(p.limits)}</div>
      ${p.privacy ? `<div><b>Data use:</b> ${esc(p.privacy)}</div>` : ""}
      ${p.key_url && p.requires_key ? `<div><b>Key:</b> <a href="${esc(p.key_url)}" target="_blank" rel="noopener">${esc(p.key_url)}</a></div>` : ""}
      ${p.max_doc_chars ? `<div class="pi-warn">Documents are shortened to about ${Math.round(p.max_doc_chars / 6).toLocaleString()} words for this provider.</div>` : ""}`;
    $("#test-result").textContent = "";
    $("#test-result").className = "test-result";
  }
  function openSettings() {
    $("#provider-select").value = state.settings.provider;
    $("#remember-key").checked = !!state.settings.remember;
    $("#access-field").classList.toggle("hidden", !state.health.access_required);
    $("#access-code-input").value = state.accessCode || "";
    renderProviderPanel(state.settings.provider);
    $("#settings-dialog").showModal();
  }
  function authHeaders(pid) {
    const headers = {};
    const key = pid ? keyFor(pid) : "";
    if (key) headers["X-API-Key"] = key;
    if (state.accessCode) headers["X-Access-Code"] = state.accessCode;
    return headers;
  }
  function askAccessCode(message) {
    const code = window.prompt(message || "This IB Marker server requires an access code. Enter the code from your coordinator:", state.accessCode || "");
    if (code === null) return false;
    state.accessCode = code.trim();
    localStorage.setItem("ibm_access", state.accessCode);
    renderKeyStatus();
    return !!state.accessCode;
  }
  const isAccessError = (status, msg) => status === 401 && /access code/i.test(String(msg || ""));
  function readSettingsForm() {
    const pid = $("#provider-select").value;
    const p = providerById(pid);
    return {
      pid,
      model: $("#model-input").value.trim(),
      baseUrl: p && p.base_url_editable ? $("#base-url-input").value.trim() : "",
      key: $("#api-key-input").value.trim(),
    };
  }
  async function testConnection() {
    const f = readSettingsForm();
    const out = $("#test-result");
    out.className = "test-result";
    out.textContent = "Testing…";
    const fd = new FormData();
    fd.append("provider", f.pid);
    fd.append("model", f.model);
    fd.append("base_url", f.baseUrl);
    const headers = {};
    if (f.key) headers["X-API-Key"] = f.key;
    const code = $("#access-code-input").value.trim() || state.accessCode;
    if (code) headers["X-Access-Code"] = code;
    try {
      const res = await fetch(api("/api/test-provider"), { method: "POST", body: fd, headers });
      const data = await res.json();
      if (data.ok) {
        out.className = "test-result ok";
        out.textContent = `Connected to ${data.provider} (${data.model}) in ${data.elapsed}s.${data.note ? " " + data.note : ""}`;
      } else {
        out.className = "test-result bad";
        out.textContent = data.error || data.detail || "The test failed.";
      }
    } catch (err) {
      out.className = "test-result bad";
      out.textContent = "Could not reach the IB Marker server: " + err.message;
    }
  }

  // ------------------------------------------------------------ rubric selection
  function rubricsFor(component) {
    return state.rubrics.filter((r) => r.component === component);
  }
  function populateSubjects() {
    const sel = $("#subject-select");
    sel.innerHTML = "";
    const seen = new Map();
    for (const r of rubricsFor(state.component)) {
      if (!seen.has(r.subject)) seen.set(r.subject, r.group);
    }
    for (const [subject, group] of seen) sel.appendChild(el("option", { value: subject, text: subject + (group && group !== "DP core" ? `  (${group.replace(/:.*$/, "")})` : "") }));
    state.subject = sel.value;
    populateVersions();
  }
  function populateVersions() {
    const sel = $("#version-select");
    sel.innerHTML = "";
    const list = rubricsFor(state.component).filter((r) => r.subject === state.subject);
    for (const r of list) sel.appendChild(el("option", { value: r.id, text: `${r.task} — ${r.version}` }));
    $("#version-field").classList.toggle("hidden", list.length < 2);
    state.rubricId = sel.value;
    populateLevelAndVariant();
  }
  function currentRubric() {
    return state.rubrics.find((r) => r.id === state.rubricId);
  }
  function populateLevelAndVariant() {
    const r = currentRubric();
    const lvl = $("#level-select");
    lvl.innerHTML = "";
    const levels = r.levels.filter((l) => l !== "SL/HL");
    for (const l of levels) lvl.appendChild(el("option", { value: l, text: l }));
    $("#level-field").classList.toggle("hidden", levels.length === 0);
    const vsel = $("#variant-select");
    vsel.innerHTML = "";
    if (r.variants) {
      $("#variant-label").textContent = r.variants.label;
      for (const o of r.variants.options) vsel.appendChild(el("option", { value: o, text: o }));
    }
    $("#variant-field").classList.toggle("hidden", !r.variants);
    renderRubricCard();
  }
  function renderRubricCard() {
    const r = currentRubric();
    const card = $("#rubric-card");
    if (!r) { card.innerHTML = ""; return; }
    const level = $("#level-select").value;
    const crits = r.criteria.filter((c) => !c.levels || !level || c.levels.includes(level));
    const total = crits.reduce((a, c) => a + c.max, 0);
    const rows = crits.map((c) => `<tr><td><b>${esc(c.code)}</b> ${esc(c.name)}${c.assessable === false ? ' <span class="na">(not from a document)</span>' : ""}</td><td class="n">${c.max}</td></tr>`).join("");
    const bands = crits.map((c) => {
      const bl = (c.bands_by_level && level && c.bands_by_level[level]) ? c.bands_by_level[level] : c.bands;
      return `<li><b style="min-width:0">Criterion ${esc(c.code)}: ${esc(c.name)}</b><div class="muted">${esc(c.focus)}</div><ul class="bands">${bl.map((b) => `<li><b>${esc(b.marks)}</b> ${esc(b.text)}</li>`).join("")}</ul></li>`;
    }).join("");
    const fidelity = r.fidelity === "summarised" ? '<span class="badge warn">descriptors summarised</span>' : '<span class="badge">descriptors paraphrased from the guide</span>';
    card.innerHTML = `
      <h4>${esc(r.task)} ${fidelity}</h4>
      <div class="meta">${esc(r.version)}${r.weighting ? " · " + esc(r.weighting) : ""}</div>
      ${r.word_limit || r.limit_note ? `<div><b>Formal requirements:</b> ${esc(r.limit_note || (r.word_limit + " words"))}</div>` : ""}
      ${r.evidence_note ? `<div class="muted" style="margin-top:4px"><b>What to upload:</b> ${esc(r.evidence_note)}</div>` : ""}
      <table><tr><th>Criterion</th><th>Max</th></tr>${rows}<tr><td><b>Total</b></td><td class="n"><b>${total}</b></td></tr></table>
      <details><summary>Show level descriptors</summary><ul class="bands" style="padding-left:0">${bands}</ul></details>`;
  }

  // ------------------------------------------------------------ custom rubric builder
  function loadCustom() {
    try { Object.assign(state.custom, JSON.parse(localStorage.getItem("ibm_custom") || "{}")); } catch (_) { /* ignore */ }
    if (!state.custom.criteria || !state.custom.criteria.length) {
      state.custom.criteria = [{ code: "A", name: "", max: 6, descriptor: "" }, { code: "B", name: "", max: 6, descriptor: "" }];
    }
  }
  function saveCustom() { localStorage.setItem("ibm_custom", JSON.stringify(state.custom)); }
  function renderCustom() {
    $("#custom-name").value = state.custom.name || "";
    $("#custom-subject").value = state.custom.subject || "";
    $("#custom-limit").value = state.custom.limit || "";
    const wrap = $("#custom-criteria");
    wrap.innerHTML = "";
    state.custom.criteria.forEach((c, i) => {
      const row = el("div", { class: "custom-crit" });
      const code = el("input", { value: c.code, placeholder: "Code", title: "Criterion code" });
      const name = el("input", { value: c.name, placeholder: "Criterion name" });
      const max = el("input", { type: "number", min: "1", max: "100", value: c.max, title: "Maximum marks" });
      const rm = el("button", { type: "button", class: "x", title: "Remove", text: "×" });
      const desc = el("textarea", { rows: "2", placeholder: "What earns full marks? (descriptor, strands, expectations)" });
      desc.value = c.descriptor || "";
      code.oninput = () => { c.code = code.value; saveCustom(); };
      name.oninput = () => { c.name = name.value; saveCustom(); };
      max.oninput = () => { c.max = Number(max.value); saveCustom(); };
      desc.oninput = () => { c.descriptor = desc.value; saveCustom(); };
      rm.onclick = () => { state.custom.criteria.splice(i, 1); saveCustom(); renderCustom(); };
      row.append(code, name, max, rm, desc);
      wrap.appendChild(row);
    });
  }
  function customRubricJson() {
    const crits = state.custom.criteria.filter((c) => c.name || c.descriptor).map((c) => ({ code: c.code, name: c.name, max: c.max, descriptor: c.descriptor }));
    return JSON.stringify({ task: state.custom.name || "Teacher-defined task", subject: state.custom.subject || "Custom", word_limit: state.custom.limit || null, criteria: crits });
  }

  // ------------------------------------------------------------ file handling
  function setFile(f) {
    state.file = f || null;
    const box = $("#dz-file");
    const inner = document.querySelector(".dz-inner");
    if (f) {
      box.innerHTML = `<div><div class="name">${esc(f.name)}</div><div class="size">${(f.size / 1024).toFixed(0)} KB</div></div><button type="button" class="ghost small" id="dz-clear">Change</button>`;
      box.classList.remove("hidden");
      inner.classList.add("hidden");
      $("#dz-clear").onclick = (e) => { e.stopPropagation(); setFile(null); $("#file-input").value = ""; };
    } else {
      box.classList.add("hidden");
      inner.classList.remove("hidden");
    }
  }

  // ------------------------------------------------------------ analysis
  function showProgress(title) {
    $("#results-empty").classList.add("hidden");
    $("#report").classList.add("hidden");
    $("#results-error").classList.add("hidden");
    $("#results-progress").classList.remove("hidden");
    $("#progress-title").textContent = title;
    const start = Date.now();
    clearInterval(state.timer);
    state.timer = setInterval(() => { $("#progress-timer").textContent = Math.round((Date.now() - start) / 1000); }, 500);
  }
  function hideProgress() { clearInterval(state.timer); $("#results-progress").classList.add("hidden"); }
  function showError(msg) {
    hideProgress();
    const box = $("#results-error");
    box.textContent = msg;
    box.classList.remove("hidden");
    $("#results-empty").classList.add("hidden");
  }

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  async function readJson(res) {
    try { return await res.json(); } catch (_) { return { detail: `Server error (${res.status}).` }; }
  }
  // The server runs the marking in the background and we poll, so no hosting platform's
  // request timeout can cut off a long analysis.
  async function pollJob(jobId) {
    const deadline = Date.now() + 15 * 60 * 1000;
    while (Date.now() < deadline) {
      await sleep(2500);
      let res;
      try { res = await fetch(api(`/api/jobs/${encodeURIComponent(jobId)}`)); } catch (_) { continue; }
      const data = await readJson(res);
      if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : `Server error (${res.status}).`);
      if (data.status === "done") return data;
      if (data.status === "error") throw new Error(data.error || "The analysis failed.");
      if (data.stage) $("#progress-detail").textContent = data.stage;
    }
    throw new Error("The analysis took longer than 15 minutes and was abandoned. Try again, or choose a faster model.");
  }

  async function analyse(dryRun) {
    if (!state.file) { showError("Choose a PDF or Word file first."); return; }
    const isCustom = state.component === "custom";
    if (!isCustom && !state.rubricId) { showError("Choose a subject and task first."); return; }
    const p = currentProvider();
    if (!dryRun && p && p.requires_key && !keyFor(p.id) && !state.serverKeys[p.id]) {
      showError(`No API key is set for ${p.name}. Open Settings and paste a key (free keys: ${p.key_url}), or run "Pre-check only".`);
      return;
    }
    if (!dryRun && state.health.access_required && !state.accessCode && !askAccessCode()) {
      showError("An access code is needed to run the examiner on this server.");
      return;
    }
    const fd = new FormData();
    fd.append("file", state.file);
    fd.append("rubric_id", isCustom ? "custom" : state.rubricId);
    fd.append("level", isCustom ? "" : ($("#level-field").classList.contains("hidden") ? "" : $("#level-select").value));
    fd.append("variant", isCustom ? "" : ($("#variant-field").classList.contains("hidden") ? "" : $("#variant-select").value));
    fd.append("teacher_notes", $("#teacher-notes").value);
    fd.append("custom_rubric", isCustom ? customRubricJson() : "");
    fd.append("dry_run", dryRun ? "1" : "0");
    fd.append("mode", dryRun ? "sync" : "async");
    fd.append("provider", state.settings.provider);
    fd.append("model", p ? (state.settings.models[p.id] || "") : "");
    fd.append("base_url", p ? (state.settings.baseUrls[p.id] || "") : "");

    showProgress(dryRun ? "Checking the document…" : `Marking with ${p ? p.name : "the selected provider"}…`);
    $("#btn-analyse").disabled = true;
    $("#btn-precheck").disabled = true;
    try {
      const send = () => fetch(api("/api/analyse"), { method: "POST", body: fd, headers: authHeaders(p && p.id) });
      let res = await send();
      let data = await readJson(res);
      if (isAccessError(res.status, data.detail) && askAccessCode("The access code was missing or wrong. Enter the code from your coordinator:")) {
        res = await send();
        data = await readJson(res);
      }
      if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail));
      if (data.job_id) data = await pollJob(data.job_id);
      hideProgress();
      renderReport(data);
      if (!dryRun) addHistory(data);
    } catch (err) {
      showError(err.message || String(err));
    } finally {
      $("#btn-analyse").disabled = false;
      $("#btn-precheck").disabled = false;
    }
  }

  // ------------------------------------------------------------ rendering
  function markClass(pct) { return pct == null ? "" : pct >= 75 ? "high" : pct >= 45 ? "mid" : "low"; }
  function list(items) { return items && items.length ? `<ul>${items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : '<p class="muted">None noted.</p>'; }
  function modelLabel(analysis) {
    if (!analysis || !analysis.model) return "";
    const m = analysis.model;
    return m.name ? `${m.name} (${m.model})` : (m.model || "");
  }

  function renderReport(data) {
    state.lastResponse = data;
    const { meta, precheck, analysis } = data;
    const rep = $("#report");
    $("#results-empty").classList.add("hidden");
    $("#results-error").classList.add("hidden");
    rep.classList.remove("hidden");
    const when = data.when ? new Date(data.when) : new Date();
    const chips = (precheck || []).map((c) => `<span class="chip ${c.status}" title="${esc(c.detail)}">${esc(c.label)}</span>`).join("");
    const warn = (meta.warnings || []).map((w) => `<li>${esc(w)}</li>`).join("");

    let html = `
      <div class="report-head">
        <div>
          <h2>${esc(meta.rubric.subject)}: ${esc(meta.rubric.task)}</h2>
          <div class="sub">${esc(meta.rubric.version)}${meta.level ? " · " + esc(meta.level) : ""}${meta.variant ? " · " + esc(meta.variant) : ""} · ${esc(meta.filename)} · ${when.toLocaleString()}${analysis ? " · " + esc(modelLabel(analysis)) : ""}${data.elapsed ? " · " + data.elapsed + " s" : ""}</div>
        </div>
        <div class="toolbar">
          <button type="button" class="ghost small" id="rep-print">Print / save PDF</button>
          <button type="button" class="ghost small" id="rep-md">Download Markdown</button>
          <button type="button" class="ghost small" id="rep-json">Download JSON</button>
          <button type="button" class="ghost small" id="rep-new">New analysis</button>
        </div>
      </div>`;

    if (data.sample) {
      html += `<div class="card sample"><h3>Sample report</h3><p>This is a fixed example showing the layout of a report. It was not generated from your document. Add an API key in Settings to mark real work.</p></div>`;
    }

    if (!analysis) {
      html += `<div class="card"><h3>Document pre-check</h3>
        <dl class="kv"><dt>File</dt><dd>${esc(meta.filename)} (${esc(meta.kind)}${meta.pages ? ", " + meta.pages + " pages" : ""})</dd>
        <dt>Extracted words</dt><dd>${meta.word_count.toLocaleString()}${meta.rubric.word_limit ? " of a " + meta.rubric.word_limit.toLocaleString() + "-word limit" : ""}</dd></dl>
        <div class="chips">${chips}</div>
        <table class="mini-table"><tr><th>Check</th><th>Result</th></tr>${(precheck || []).map((c) => `<tr><td><b>${esc(c.label)}</b></td><td>${esc(c.detail)}</td></tr>`).join("")}</table>
        ${warn ? `<h4 style="margin-top:12px">Extraction notes</h4><ul>${warn}</ul>` : ""}
        <details class="evidence" style="margin-top:12px"><summary>Preview of extracted text</summary><blockquote>${esc(meta.preview)}…</blockquote></details>
        <p class="hint" style="margin-top:12px">No marks were generated (pre-check only). Click <em>Analyse and mark</em> to run the examiner.</p></div>`;
      rep.innerHTML = html;
      bindToolbar(data);
      return;
    }

    const ds = analysis.document_summary || {};
    const t = analysis.total || {};
    html += `<div class="card"><h3>What the student is researching</h3>
      <dl class="kv">
        ${ds.title ? `<dt>Title</dt><dd>${esc(ds.title)}</dd>` : ""}
        ${ds.research_question ? `<dt>Research question</dt><dd>${esc(ds.research_question)}</dd>` : ""}
        <dt>Detected as</dt><dd>${esc(ds.subject_and_task_detected || "")} ${ds.matches_selected_rubric === false ? '<span class="badge warn">does not match the selected rubric</span>' : '<span class="badge">matches the selected rubric</span>'}</dd>
        <dt>Length</dt><dd>${meta.word_count.toLocaleString()} words extracted${meta.rubric.word_limit ? " (limit " + meta.rubric.word_limit.toLocaleString() + ")" : ""}${meta.pages ? ", " + meta.pages + " pages" : ""}${meta.sent_words ? `; only the first ${meta.sent_words.toLocaleString()} words were sent to the model` : ""}</dd>
      </dl>
      <p style="margin-top:10px">${esc(ds.summary)}</p>
      ${ds.structure_observations && ds.structure_observations.length ? `<h4 class="muted" style="font-size:.85rem;margin-top:10px">Structure and formal elements</h4>${list(ds.structure_observations)}` : ""}
      <div class="chips">${chips}</div>
      ${warn ? `<details class="evidence"><summary>Extraction notes</summary><ul>${warn}</ul></details>` : ""}
    </div>`;

    if (analysis.integrity_flags && analysis.integrity_flags.length) {
      html += `<div class="card flag"><h3>Flags for the teacher</h3>${list(analysis.integrity_flags)}</div>`;
    }

    const pct = t.percent ?? 0;
    html += `<div class="card total"><h3>Total mark</h3>
      <div class="total-grid">
        <div class="total-mark">${t.mark}<small> / ${t.max}</small>${t.indicative_grade ? `<span class="grade-pill" title="${esc(t.grade_note || "")}">${esc(t.indicative_grade)}</span>` : ""}</div>
        <div>
          <div class="bar"><span style="width:${pct}%"></span></div>
          <p class="muted" style="margin-top:6px">${pct}% of the marks assessable from the document${t.task_max && t.task_max !== t.max ? ` (task total ${t.task_max}; some criteria cannot be judged from a document)` : ""}. Confidence: <b>${esc(analysis.confidence)}</b>${analysis.confidence_reason ? " — " + esc(analysis.confidence_reason) : ""}.</p>
          ${t.indicative_grade ? `<p class="hint">Indicative grade ${esc(t.indicative_grade)}. ${esc(t.grade_note || "")}</p>` : ""}
        </div>
      </div>
      <table class="mini-table"><tr><th>Criterion</th><th>Mark</th><th style="width:40%"></th></tr>
      ${analysis.criteria.map((c) => `<tr><td><b>${esc(c.code)}</b> ${esc(c.name)}</td><td class="n">${c.assessable ? c.mark + " / " + c.max : "n/a"}</td><td>${c.assessable ? `<div class="bar"><span style="width:${c.percent}%"></span></div>` : ""}</td></tr>`).join("")}
      </table></div>`;

    html += `<h3 style="margin:18px 0 10px;font-size:1.05rem">Criterion by criterion</h3>`;
    for (const c of analysis.criteria) {
      html += `<div class="card">
        <div class="crit-head"><h3>Criterion ${esc(c.code)}: ${esc(c.name)}</h3>
          <div class="mark-badge ${c.assessable ? markClass(c.percent) : ""}">${c.assessable ? `${c.mark} <small>/ ${c.max}</small>` : "n/a"}</div></div>
        <div class="band">${c.assessable ? `Band ${esc(c.band)} of ${c.max}` : "Not assessable from a document"}</div>
        <p>${esc(c.justification)}</p>
        ${c.assessable ? `<div class="two-col">
          <div><h4 class="s">Strengths</h4>${list(c.strengths)}</div>
          <div><h4 class="i">Areas for improvement</h4>${list(c.improvements)}</div>
        </div>` : ""}
        ${c.evidence && c.evidence.length ? `<details class="evidence"><summary>Evidence cited (${c.evidence.length})</summary>${c.evidence.map((e) => `<blockquote>${esc(e)}</blockquote>`).join("")}</details>` : ""}
        ${c.next_band_requires ? `<div class="next"><b>To reach the next band:</b> ${esc(c.next_band_requires)}</div>` : ""}
      </div>`;
    }

    html += `<div class="card"><h3>Overall strengths</h3>${list(analysis.overall_strengths)}</div>`;
    html += `<div class="card"><h3>Summary of areas to improve (in priority order)</h3>
      <ol class="priorities">${(analysis.priority_improvements || []).map((p) => `<li><span class="num">${p.priority}</span><div><span class="area">${esc(p.area)}</span>${p.criteria && p.criteria.length ? `<span class="codes">criteria ${esc(p.criteria.join(", "))}</span>` : ""}<div>${esc(p.action)}</div></div></li>`).join("")}</ol></div>`;
    html += `<p class="footnote">Generated by ${esc(modelLabel(analysis) || "an AI examiner")} applying the IB criteria for ${esc(meta.rubric.task)} (${esc(meta.rubric.version)}). ${meta.rubric.fidelity === "summarised" ? "The descriptors for this task are summarised rather than quoted from the guide. " : ""}Marks are indicative and should be confirmed by the teacher against the official guide; final IB marks depend on moderation.</p>`;
    rep.innerHTML = html;
    bindToolbar(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function bindToolbar(data) {
    $("#rep-print").onclick = () => window.print();
    $("#rep-json").onclick = () => download(`${baseName(data)}.json`, JSON.stringify(data, null, 2), "application/json");
    $("#rep-md").onclick = () => download(`${baseName(data)}.md`, toMarkdown(data), "text/markdown");
    $("#rep-new").onclick = () => { $("#report").classList.add("hidden"); $("#results-empty").classList.remove("hidden"); setFile(null); $("#file-input").value = ""; window.scrollTo({ top: 0 }); };
  }
  function baseName(data) { return `ib-marker-${(data.meta.filename || "report").replace(/\.[^.]+$/, "").replace(/[^a-z0-9-_]+/gi, "_")}`; }
  function download(name, content, type) {
    const blob = new Blob([content], { type });
    const a = el("a", { href: URL.createObjectURL(blob), download: name });
    document.body.appendChild(a); a.click(); a.remove();
  }
  function toMarkdown(data) {
    const { meta, precheck, analysis } = data;
    const L = [];
    L.push(`# ${meta.rubric.subject}: ${meta.rubric.task}`);
    L.push(`${meta.rubric.version}${meta.level ? " · " + meta.level : ""}${meta.variant ? " · " + meta.variant : ""}  `);
    L.push(`File: ${meta.filename} · ${meta.word_count} words extracted${meta.rubric.word_limit ? " (limit " + meta.rubric.word_limit + ")" : ""}\n`);
    L.push(`## Pre-check`);
    for (const c of precheck || []) L.push(`- **${c.label}** (${c.status}): ${c.detail}`);
    if (!analysis) return L.join("\n");
    const ds = analysis.document_summary || {};
    L.push(`\n## What the student is researching`);
    if (ds.title) L.push(`**Title:** ${ds.title}  `);
    if (ds.research_question) L.push(`**Research question:** ${ds.research_question}  `);
    L.push(`**Detected as:** ${ds.subject_and_task_detected || ""}${ds.matches_selected_rubric === false ? " (does not match the selected rubric)" : ""}\n`);
    L.push(ds.summary || "");
    if (ds.structure_observations && ds.structure_observations.length) { L.push(`\n**Structure:**`); for (const s of ds.structure_observations) L.push(`- ${s}`); }
    if (analysis.integrity_flags && analysis.integrity_flags.length) { L.push(`\n## Flags`); for (const f of analysis.integrity_flags) L.push(`- ${f}`); }
    const t = analysis.total;
    L.push(`\n## Total: ${t.mark} / ${t.max}${t.indicative_grade ? ` (indicative grade ${t.indicative_grade})` : ""}`);
    L.push(`Confidence: ${analysis.confidence}. ${analysis.confidence_reason || ""}\n`);
    L.push(`| Criterion | Mark |\n|---|---|`);
    for (const c of analysis.criteria) L.push(`| ${c.code}: ${c.name} | ${c.assessable ? c.mark + " / " + c.max : "n/a"} |`);
    L.push(`\n## Criterion by criterion`);
    for (const c of analysis.criteria) {
      L.push(`\n### Criterion ${c.code}: ${c.name} — ${c.assessable ? `${c.mark} / ${c.max} (band ${c.band})` : "not assessable from a document"}`);
      L.push(c.justification);
      if (c.assessable) {
        L.push(`\n**Strengths**`); for (const s of c.strengths) L.push(`- ${s}`);
        L.push(`\n**Areas for improvement**`); for (const s of c.improvements) L.push(`- ${s}`);
      }
      if (c.evidence && c.evidence.length) { L.push(`\n**Evidence**`); for (const e of c.evidence) L.push(`> ${e}`); }
      if (c.next_band_requires) L.push(`\n**To reach the next band:** ${c.next_band_requires}`);
    }
    L.push(`\n## Overall strengths`); for (const s of analysis.overall_strengths || []) L.push(`- ${s}`);
    L.push(`\n## Summary of areas to improve`); for (const p of analysis.priority_improvements || []) L.push(`${p.priority}. **${p.area}**${p.criteria && p.criteria.length ? ` (criteria ${p.criteria.join(", ")})` : ""}: ${p.action}`);
    L.push(`\n---\nGenerated by ${modelLabel(analysis) || "an AI examiner"} applying the IB criteria. Marks are indicative and should be confirmed by the teacher.`);
    return L.join("\n");
  }

  // ------------------------------------------------------------ history
  function getHistory() { try { return JSON.parse(localStorage.getItem("ibm_history") || "[]"); } catch (_) { return []; } }
  function addHistory(data) {
    const h = getHistory();
    h.unshift({ when: new Date().toISOString(), data: Object.assign({ when: new Date().toISOString() }, data) });
    while (h.length > 12) h.pop();
    try { localStorage.setItem("ibm_history", JSON.stringify(h)); } catch (_) { /* quota */ }
  }
  function openHistory() {
    const ul = $("#history-list");
    ul.innerHTML = "";
    const h = getHistory();
    if (!h.length) ul.appendChild(el("li", { class: "muted", text: "No analyses stored yet." }));
    for (const item of h) {
      const d = item.data;
      const li = el("li");
      const left = el("div", { html: `<div><b>${esc(d.meta.filename)}</b> — ${esc(d.meta.rubric.subject)}: ${esc(d.meta.rubric.task)}</div><div class="t">${new Date(item.when).toLocaleString()}${d.analysis ? ` · ${d.analysis.total.mark} / ${d.analysis.total.max}` : " · pre-check"}</div>` });
      const btn = el("button", { type: "button", class: "ghost small", text: "Open", onclick: () => { $("#history-dialog").close(); renderReport(d); } });
      li.append(left, btn);
      ul.appendChild(li);
    }
    $("#history-dialog").showModal();
  }

  // ------------------------------------------------------------ wiring
  async function init() {
    loadSettings();
    loadCustom();
    renderCustom();
    try {
      const [rub, prov, health] = await Promise.all([
        fetch(api("/api/rubrics")).then((r) => r.json()),
        fetch(api("/api/providers")).then((r) => r.json()),
        fetch(api("/api/health")).then((r) => r.json()).catch(() => ({})),
      ]);
      state.rubrics = rub.rubrics;
      state.guidance = rub.ee_subject_guidance || {};
      state.providers = prov.providers || [];
      state.groups = prov.groups || [];
      state.serverKeys = prov.server_keys || {};
      state.health = Object.assign({ access_required: false }, health || {});
      const serverDefault = prov.default_provider || "gemini";
      if (!state.settingsSaved || !state.providers.some((p) => p.id === state.settings.provider)) state.settings.provider = serverDefault;
    } catch (err) {
      showError("Could not load the rubric library from the server: " + err.message);
      return;
    }
    buildProviderSelect();
    populateSubjects();
    renderKeyStatus();

    $("#component-seg").addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      for (const x of $("#component-seg").children) x.classList.toggle("active", x === b);
      state.component = b.dataset.value;
      const custom = state.component === "custom";
      $("#builtin-fields").classList.toggle("hidden", custom);
      $("#custom-fields").classList.toggle("hidden", !custom);
      if (!custom) populateSubjects();
    });
    $("#subject-select").addEventListener("change", (e) => { state.subject = e.target.value; populateVersions(); });
    $("#version-select").addEventListener("change", (e) => { state.rubricId = e.target.value; populateLevelAndVariant(); });
    $("#level-select").addEventListener("change", renderRubricCard);

    $("#custom-name").addEventListener("input", (e) => { state.custom.name = e.target.value; saveCustom(); });
    $("#custom-subject").addEventListener("input", (e) => { state.custom.subject = e.target.value; saveCustom(); });
    $("#custom-limit").addEventListener("input", (e) => { state.custom.limit = e.target.value; saveCustom(); });
    $("#custom-add").addEventListener("click", () => { state.custom.criteria.push({ code: String.fromCharCode(65 + state.custom.criteria.length), name: "", max: 6, descriptor: "" }); saveCustom(); renderCustom(); });
    $("#custom-clear").addEventListener("click", () => { state.custom = { name: "", subject: "", limit: "", criteria: [{ code: "A", name: "", max: 6, descriptor: "" }] }; saveCustom(); renderCustom(); });

    const dz = $("#dropzone");
    const fi = $("#file-input");
    dz.addEventListener("click", () => fi.click());
    dz.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fi.click(); } });
    fi.addEventListener("change", () => setFile(fi.files[0]));
    ["dragenter", "dragover"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("drag"); }));
    ["dragleave", "drop"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("drag"); }));
    dz.addEventListener("drop", (e) => { const f = e.dataTransfer.files && e.dataTransfer.files[0]; if (f) setFile(f); });

    $("#btn-analyse").addEventListener("click", () => analyse(false));
    $("#btn-precheck").addEventListener("click", () => analyse(true));
    $("#btn-sample").addEventListener("click", async (e) => {
      e.preventDefault();
      showProgress("Loading sample…");
      try { const d = await fetch(api("/api/sample")).then((r) => r.json()); hideProgress(); renderReport(d); } catch (err) { showError("Could not load the sample: " + err.message); }
    });

    $("#btn-settings").addEventListener("click", openSettings);
    $("#provider-select").addEventListener("change", (e) => renderProviderPanel(e.target.value));
    $("#settings-test").addEventListener("click", testConnection);
    $("#settings-save").addEventListener("click", (e) => {
      e.preventDefault();
      const f = readSettingsForm();
      state.settings.provider = f.pid;
      state.settings.models[f.pid] = f.model;
      if (f.baseUrl) state.settings.baseUrls[f.pid] = f.baseUrl; else delete state.settings.baseUrls[f.pid];
      if (f.key) state.settings.keys[f.pid] = f.key; else delete state.settings.keys[f.pid];
      state.settings.remember = $("#remember-key").checked;
      state.accessCode = $("#access-code-input").value.trim();
      localStorage.setItem("ibm_access", state.accessCode);
      saveSettings();
      $("#settings-dialog").close();
    });
    $("#settings-cancel").addEventListener("click", () => $("#settings-dialog").close());
    $("#btn-history").addEventListener("click", openHistory);
    $("#history-close").addEventListener("click", () => $("#history-dialog").close());
    $("#history-clear").addEventListener("click", () => { localStorage.removeItem("ibm_history"); openHistory(); });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
