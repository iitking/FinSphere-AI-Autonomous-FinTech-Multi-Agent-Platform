/**
 * FinSphere AI - Institutional Multi-Agent Frontend Controller
 */

// Global Chart.js instance holder
let activeChartInstance = null;
let currentAgent = "orchestrator";

// Curated Financial Presets
const PRESET_SCENARIOS = {
  orchestrator: [
    {
      title: "HDFC Bank Q4 Research",
      tag: "NSE Equity",
      query: "Analyze HDFC Bank fundamental multiples, loan book growth, and downside volatility risk."
    },
    {
      title: "₹50L Wealth Allocation",
      tag: "Portfolio",
      query: "Allocate ₹50,00,000 for a moderate Indian investor across Nifty 50, G-Secs, SGBs, and US FoF under current LTCG/STCG tax laws."
    },
    {
      title: "Indian PII Sanitization Test",
      tag: "Guardrails",
      query: "Client PAN is ABCDE1234F, Aadhaar 4532 9876 1234, phone +91 9876543210, and UPI deepak@okhdfcbank. Verify eligibility for SGB investment."
    }
  ],
  financial_analysis: [
    {
      title: "HDFCBANK Valuation",
      tag: "Banking",
      query: "Perform fundamental equity research on HDFCBANK over a 1Y horizon, evaluating P/E, NIM, and credit cycle."
    },
    {
      title: "Tata Motors EV Expansion",
      tag: "Auto / Capex",
      query: "Analyze TATAMOTORS EV margins, debt-to-equity leverage, and Indian commercial vehicle capex demand."
    },
    {
      title: "Reliance O2C vs Retail",
      tag: "Conglomerate",
      query: "Evaluate RELIANCE retail and 5G telecom expansion vs oil-to-chemicals refining headwinds."
    }
  ],
  risk_assessment: [
    {
      title: "NBFC Commercial Paper",
      tag: "Credit Risk",
      query: "Conduct 5-dimension risk evaluation for unsecured NBFC commercial paper offering 11.2% coupon rate."
    },
    {
      title: "Small-Cap Beta Stress Test",
      tag: "Market Risk",
      query: "Assess downside beta, volatility, and liquidity compression of high-growth Indian small-cap portfolio during FII outflows."
    }
  ],
  portfolio: [
    {
      title: "₹50L Balanced Wealth",
      tag: "Balanced",
      query: "Design an optimal diversified portfolio for capital of ₹5,000,000 with moderate risk tolerance over 7 years."
    },
    {
      title: "₹10L High-Alpha Growth",
      tag: "Aggressive",
      query: "Build aggressive high-alpha portfolio for ₹1,000,000 capital focusing on Indian midcaps and US technology FoF."
    },
    {
      title: "₹1Cr Capital Preservation",
      tag: "Conservative",
      query: "Capital preservation portfolio for ₹10,000,000 for retired investor focusing on G-Secs, AAA corporate debt, and Sovereign Gold."
    }
  ],
  fraud_detection: [
    {
      title: "High-Value Geo-Anomaly",
      tag: "UPI / Velocity",
      query: JSON.stringify({
        transactions: [
          { transaction_id: "TXN_IND_8901", amount_inr: 125000, merchant: "Luxury Watch Store", location: "Mumbai, India", user_id: "USR_78", channel: "UPI" },
          { transaction_id: "TXN_IND_8902", amount_inr: 9990, merchant: "Quick Pay Terminal", location: "Bengaluru, India", user_id: "USR_78", channel: "UPI" },
          { transaction_id: "TXN_IND_8903", amount_inr: 45000, merchant: "Unknown POS", location: "Lagos, Nigeria", user_id: "USR_78", channel: "CARD" }
        ]
      }, null, 2)
    },
    {
      title: "Smurfing / Mule Pattern",
      tag: "AML Structuring",
      query: "Analyze user account USR_99 performing 4 consecutive UPI transfers of ₹9,980 within 4 minutes to separate unverified VPA handles."
    }
  ],
  compliance: [
    {
      title: "Digital Lending Disbursal Flow",
      tag: "RBI Master Direction",
      query: "Audit partnership agreement where borrower loan repayments pass through a FinTech intermediary escrow pool account before reaching the regulated NBFC."
    },
    {
      title: "DPDP 2023 Consent Audit",
      tag: "Data Privacy",
      query: "Review customer onboarding consent notice capturing biometric and geolocation data without granular opt-out or explicit purpose specification."
    }
  ]
};

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
});

async function initDashboard() {
  if (window.lucide) {
    lucide.createIcons();
  }

  await fetchEngineStatus();
  setupNavigation();
  setupEventListeners();
  setupGuardrailsSandbox();
  switchAgentView("orchestrator");
}

async function fetchEngineStatus() {
  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error("Health check failed");
    const data = await res.json();

    const statusBadge = document.getElementById("engineStatusBadge");
    const statusText = document.getElementById("engineStatusText");
    const modelLabel = document.getElementById("activeModelLabel");

    if (data.simulation_mode) {
      statusText.textContent = "Simulation Mode (Offline Mock Engine)";
      statusBadge.classList.add("border-amber-500/30");
      statusBadge.querySelector(".relative span:last-child").className = "relative inline-flex rounded-full h-2 w-2 bg-amber-500";
      statusBadge.querySelector(".relative span:first-child").className = "animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75";
    } else {
      statusText.textContent = "Live Claude Agent Active";
    }

    if (modelLabel) {
      modelLabel.textContent = data.active_model || "claude-3-7-sonnet";
    }
  } catch (err) {
    console.error("Status fetch error:", err);
    document.getElementById("engineStatusText").textContent = "Service Offline";
  }
}

function setupNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      navBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const agentKey = btn.getAttribute("data-agent");
      switchAgentView(agentKey);
    });
  });
}

function switchAgentView(agent) {
  currentAgent = agent;

  const viewMeta = {
    orchestrator: {
      title: "Autonomous Router",
      badge: "Semantic Dispatch",
      desc: "Intelligently classifies intent, routes to optimal agents, or chains sequential pipelines."
    },
    financial_analysis: {
      title: "Financial Intelligence Agent",
      badge: "Fundamental Valuation",
      desc: "Deep equity research, balance sheet health, P/E multiples, and Indian macroeconomic catalysts."
    },
    risk_assessment: {
      title: "Risk Assessment Agent",
      badge: "5-Factor Quant Matrix",
      desc: "Evaluates Market, Credit, Liquidity, Regulatory, and Operational exposures with stress testing."
    },
    portfolio: {
      title: "Portfolio Optimization Agent",
      badge: "MPT Asset Allocation",
      desc: "Synthesizes risk-adjusted asset allocations across Indian equities, G-Secs, Gold, and US FoF with tax awareness."
    },
    fraud_detection: {
      title: "Fraud Watchtower Agent",
      badge: "Dual Heuristic & LLM Shield",
      desc: "Real-time transaction anomaly screening, velocity burst defense, and UPI fraud vector detection."
    },
    compliance: {
      title: "Regulatory Compliance Agent",
      badge: "Statutory Audit",
      desc: "Automated legal compliance audits against RBI Master Directions, SEBI LODR, PMLA 2002, and DPDP Act 2023."
    },
    parameters: {
      title: "System Parameters Studio",
      badge: "Runtime Configuration",
      desc: "Inspect and customize live risk model weights, economic indicators, tax rates, and fraud rules."
    },
    guardrails_inspector: {
      title: "Guardrails Live Sandbox",
      badge: "Security Perimeter",
      desc: "Test real-time masking of Indian PII (PAN, Aadhaar, UPI, Phone, IFSC) and prompt injection interception."
    }
  };

  const meta = viewMeta[agent] || viewMeta.orchestrator;
  document.getElementById("viewTitle").textContent = meta.title;
  document.getElementById("viewBadge").textContent = meta.badge;
  document.getElementById("viewDesc").textContent = meta.desc;

  const queryConsole = document.getElementById("queryConsoleCard");
  const pipelineVisual = document.getElementById("pipelineFlowVisual");
  const parametersView = document.getElementById("parametersView");
  const guardrailsView = document.getElementById("guardrailsView");
  const resultsDeck = document.getElementById("resultsDeck");

  // View Visibility Toggles
  if (agent === "parameters") {
    queryConsole.classList.add("hidden");
    pipelineVisual.classList.add("hidden");
    parametersView.classList.remove("hidden");
    guardrailsView.classList.add("hidden");
    resultsDeck.classList.add("hidden");
    loadParametersGrid();
  } else if (agent === "guardrails_inspector") {
    queryConsole.classList.add("hidden");
    pipelineVisual.classList.add("hidden");
    parametersView.classList.add("hidden");
    guardrailsView.classList.remove("hidden");
    resultsDeck.classList.add("hidden");
  } else {
    queryConsole.classList.remove("hidden");
    parametersView.classList.add("hidden");
    guardrailsView.classList.add("hidden");
    pipelineVisual.classList.toggle("hidden", agent !== "orchestrator");
    renderPresetChips(agent);
  }

  if (window.lucide) lucide.createIcons();
}

function renderPresetChips(agent) {
  const container = document.getElementById("presetsList");
  container.innerHTML = "";

  const presets = PRESET_SCENARIOS[agent] || [];
  presets.forEach(p => {
    const btn = document.createElement("button");
    btn.className = "preset-btn";
    btn.innerHTML = `<span>${p.title}</span><span class="text-[9px] px-1 py-0.2 bg-slate-800 text-slate-400 rounded">${p.tag}</span>`;
    btn.addEventListener("click", () => {
      document.getElementById("promptInput").value = p.query;
      updateCharCount();
    });
    container.appendChild(btn);
  });

  if (presets.length > 0 && !document.getElementById("promptInput").value) {
    document.getElementById("promptInput").value = presets[0].query;
    updateCharCount();
  }
}

function setupEventListeners() {
  const promptInput = document.getElementById("promptInput");
  promptInput.addEventListener("input", updateCharCount);

  const executeBtn = document.getElementById("executeBtn");
  executeBtn.addEventListener("click", runExecution);

  const copyBtn = document.getElementById("copyJsonBtn");
  copyBtn.addEventListener("click", () => {
    const raw = document.getElementById("rawJsonCode").textContent;
    navigator.clipboard.writeText(raw).then(() => {
      document.getElementById("copyBtnText").textContent = "Copied!";
      setTimeout(() => {
        document.getElementById("copyBtnText").textContent = "Copy Output";
      }, 2000);
    });
  });

  const toggleRawBtn = document.getElementById("toggleRawJsonBtn");
  toggleRawBtn.addEventListener("click", () => {
    const drawer = document.getElementById("rawJsonDrawer");
    drawer.classList.toggle("hidden");
  });

  const refreshParamsBtn = document.getElementById("refreshParamsBtn");
  if (refreshParamsBtn) {
    refreshParamsBtn.addEventListener("click", loadParametersGrid);
  }
}

function updateCharCount() {
  const text = document.getElementById("promptInput").value;
  document.getElementById("charCount").textContent = `${text.length} chars`;
}

async function runExecution() {
  const query = document.getElementById("promptInput").value.trim();
  if (!query) {
    alert("Please enter a query or transaction payload.");
    return;
  }

  const executeBtn = document.getElementById("executeBtn");
  const btnSpinner = document.getElementById("btnSpinner");
  const btnIcon = document.getElementById("btnIcon");
  const btnText = document.getElementById("btnText");

  executeBtn.disabled = true;
  btnSpinner.classList.remove("hidden");
  btnIcon.classList.add("hidden");
  btnText.textContent = "Synthesizing...";

  // Animate Stepper
  advanceStepper(1);

  try {
    let endpoint = "/api/v1/query/";
    let payload = { query: query };

    const isPipeline = currentAgent === "orchestrator" && document.getElementById("pipelineToggleCheckbox").checked;

    if (isPipeline) {
      payload.pipeline = ["financial_analysis", "risk_assessment", "portfolio"];
    } else if (currentAgent === "financial_analysis") {
      endpoint = "/api/v1/analysis/";
      payload = { ticker: query.length < 15 ? query : "HDFCBANK", timeframe: "1Y", include_sentiment: true };
    } else if (currentAgent === "risk_assessment") {
      endpoint = "/api/v1/risk/";
      payload = { asset_description: query, investor_profile: "moderate" };
    } else if (currentAgent === "portfolio") {
      endpoint = "/api/v1/portfolio/";
      payload = { capital_inr: 5000000, risk_tolerance: "moderate", horizon_years: 5, assets: ["Nifty 50", "Midcap 150", "G-Sec 10Y", "Gold SGB", "Nasdaq 100 FoF"] };
    } else if (currentAgent === "fraud_detection") {
      endpoint = "/api/v1/fraud/";
      try {
        const parsed = JSON.parse(query);
        payload = parsed.transactions ? parsed : { transactions: [parsed] };
      } catch (e) {
        endpoint = "/api/v1/query/";
        payload = { query: query };
      }
    } else if (currentAgent === "compliance") {
      endpoint = "/api/v1/compliance/";
      payload = { document_text: query, regulation_context: "RBI Digital Lending, SEBI, PMLA 2002, DPDP Act 2023" };
    }

    advanceStepper(2);
    advanceStepper(3);

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    advanceStepper(4);
    const data = await res.json();
    advanceStepper(5);

    renderExecutionResults(data, isPipeline);
  } catch (err) {
    console.error("Execution error:", err);
    alert("Execution failed: " + err.message);
  } finally {
    executeBtn.disabled = false;
    btnSpinner.classList.add("hidden");
    btnIcon.classList.remove("hidden");
    btnText.textContent = "Execute Intelligence";
    if (window.lucide) lucide.createIcons();
  }
}

function advanceStepper(stepIndex) {
  const steps = ["stepInput", "stepRouting", "stepAgent", "stepOutput", "stepPayload"];
  steps.forEach((s, idx) => {
    const el = document.getElementById(s);
    if (!el) return;
    if (idx + 1 < stepIndex) {
      el.className = "step-card completed";
    } else if (idx + 1 === stepIndex) {
      el.className = "step-card active";
    } else {
      el.className = "step-card";
    }
  });
}

function renderExecutionResults(data, isPipeline) {
  const resultsDeck = document.getElementById("resultsDeck");
  resultsDeck.classList.remove("hidden");

  const raw = Array.isArray(data) ? data[data.length - 1] : data;

  // Header meta bar
  const statusBadge = document.getElementById("resStatusBadge");
  if (raw.success) {
    statusBadge.className = "flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    statusBadge.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5"></i><span>SUCCESS</span>`;
  } else {
    statusBadge.className = "flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20";
    statusBadge.innerHTML = `<i data-lucide="x-circle" class="w-3.5 h-3.5"></i><span>BLOCKED / FAILED</span>`;
  }

  document.getElementById("resAgentName").textContent = isPipeline ? `Sequential Pipeline (${data.length} Agents)` : `Agent: ${formatAgentTitle(raw.agent)}`;
  document.getElementById("resLatency").textContent = `Latency: ${raw.elapsed_s || 0.0}s`;

  // Raw JSON display
  document.getElementById("rawJsonCode").textContent = JSON.stringify(data, null, 2);

  // Render Stats Grid
  renderStatCards(raw);

  // Render Visual Chart
  renderChart(raw);

  // Render Narrative Body via Marked (Markdown to HTML)
  const narrativeContainer = document.getElementById("narrativeContent");
  const fullText = isPipeline
    ? data.map(d => `## 🤖 [AGENT: ${d.agent.toUpperCase()}]\n\n${d.output}`).join("\n\n---\n\n")
    : raw.output;

  if (window.marked) {
    narrativeContainer.innerHTML = marked.parse(fullText);
  } else {
    narrativeContainer.textContent = fullText;
  }

  // Guardrail Badges
  const badgesContainer = document.getElementById("guardrailBadges");
  badgesContainer.innerHTML = "";
  if (raw.guardrail_flags && raw.guardrail_flags.length > 0) {
    raw.guardrail_flags.forEach(f => {
      const b = document.createElement("span");
      b.className = "px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-rose-500/10 text-rose-400 border border-rose-500/20";
      b.textContent = `Masked ${f}`;
      badgesContainer.appendChild(b);
    });
  } else {
    const b = document.createElement("span");
    b.className = "px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    b.textContent = "Guardrail Clean";
    badgesContainer.appendChild(b);
  }

  resultsDeck.scrollIntoView({ behavior: "smooth" });
  if (window.lucide) lucide.createIcons();
}

function renderStatCards(raw) {
  const grid = document.getElementById("statsGrid");
  grid.innerHTML = "";
  const meta = raw.metadata || {};

  if (meta.risk_score !== undefined) {
    grid.appendChild(createStatCard("Overall Risk Score", `${meta.risk_score} / 100`, meta.risk_level?.toUpperCase(), "text-amber-400"));
  }
  if (meta.metrics?.pe_ratio) {
    grid.appendChild(createStatCard("P/E Multiple", meta.metrics.pe_ratio, "Valuation Indicator", "text-cyan-400"));
  }
  if (meta.metrics?.analyst_rating) {
    grid.appendChild(createStatCard("Consensus Rating", meta.metrics.analyst_rating.toUpperCase(), "Equity Research", "text-emerald-400"));
  }
  if (meta.expected_return_pct !== undefined) {
    grid.appendChild(createStatCard("Target Return", `${meta.expected_return_pct}%`, "Annual CAGR", "text-emerald-400"));
  }
  if (meta.sharpe_estimate !== undefined) {
    grid.appendChild(createStatCard("Sharpe Ratio", meta.sharpe_estimate, "Risk-Adjusted Alpha", "text-blue-400"));
  }
  if (meta.flagged_transactions !== undefined) {
    const count = meta.flagged_transactions.length;
    grid.appendChild(createStatCard("Flagged Alerts", `${count} Txns`, count > 0 ? "Review Required" : "Clean Batch", count > 0 ? "text-rose-400" : "text-emerald-400"));
  }
  if (meta.compliant !== undefined) {
    grid.appendChild(createStatCard("Compliance Stance", meta.compliant ? "COMPLIANT" : "VIOLATION", meta.kyc_aml_status?.toUpperCase() || "AUDITED", meta.compliant ? "text-emerald-400" : "text-rose-400"));
  }
}

function createStatCard(label, val, subtext, colorClass = "text-white") {
  const card = document.createElement("div");
  card.className = "stat-card";
  card.innerHTML = `
    <span class="stat-label">${label}</span>
    <span class="stat-value ${colorClass}">${val}</span>
    <span class="stat-subtext">${subtext}</span>
  `;
  return card;
}

function renderChart(raw) {
  const chartCard = document.getElementById("chartContainerCard");
  const ctx = document.getElementById("agentChart");
  if (!ctx || !window.Chart) return;

  if (activeChartInstance) {
    activeChartInstance.destroy();
    activeChartInstance = null;
  }

  const meta = raw.metadata || {};

  // Case 1: Portfolio Allocation Donut Chart
  if (meta.allocation && Object.keys(meta.allocation).length > 0) {
    chartCard.classList.remove("hidden");
    document.getElementById("chartTitle").textContent = "Portfolio Asset Weight Allocation";
    document.getElementById("chartSubtitle").textContent = "Modern Portfolio Theory (MPT) Optimization";

    const labels = Object.keys(meta.allocation);
    const values = Object.values(meta.allocation);

    activeChartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: [
            "#06b6d4", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"
          ],
          borderColor: "#0f172a",
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
            labels: { color: "#cbd5e1", font: { family: "Plus Jakarta Sans", size: 11 } }
          }
        }
      }
    });
    return;
  }

  // Case 2: Risk 5-Factor Radar Chart
  if (meta.breakdown) {
    chartCard.classList.remove("hidden");
    document.getElementById("chartTitle").textContent = "5-Factor Multi-Dimensional Risk Radar";
    document.getElementById("chartSubtitle").textContent = "Weighted Institutional Risk Breakdown (0-100 scale)";

    const b = meta.breakdown;
    const labels = ["Market Risk", "Credit Risk", "Liquidity Risk", "Regulatory Risk", "Operational Risk"];
    const scores = [b.market || 40, b.credit || 30, b.liquidity || 35, b.regulatory || 45, b.operational || 25];

    activeChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [{
          label: "Asset Risk Score",
          data: scores,
          backgroundColor: "rgba(6, 182, 212, 0.25)",
          borderColor: "#06b6d4",
          borderWidth: 2,
          pointBackgroundColor: "#06b6d4"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: "#1e293b" },
            grid: { color: "#1e293b" },
            pointLabels: { color: "#94a3b8", font: { size: 10 } },
            ticks: { display: false, max: 100, min: 0 }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
    return;
  }

  // Case 3: Fraud Scores Bar Chart
  if (meta.fraud_scores && Object.keys(meta.fraud_scores).length > 0) {
    chartCard.classList.remove("hidden");
    document.getElementById("chartTitle").textContent = "Transaction Fraud Probability Scores";
    document.getElementById("chartSubtitle").textContent = "Scored 0 (Safe) to 100 (Critical Fraud Alert)";

    const txns = Object.keys(meta.fraud_scores);
    const scores = Object.values(meta.fraud_scores);

    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: txns,
        datasets: [{
          label: "Fraud Score",
          data: scores,
          backgroundColor: scores.map(s => s > 60 ? "#f43f5e" : (s > 30 ? "#f59e0b" : "#10b981")),
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { color: "#94a3b8" } },
          y: { max: 100, min: 0, grid: { color: "#1e293b" }, ticks: { color: "#94a3b8" } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
    return;
  }

  chartCard.classList.add("hidden");
}

function setupGuardrailsSandbox() {
  const inputEl = document.getElementById("guardrailTestInput");
  const outputEl = document.getElementById("guardrailTestOutput");
  if (!inputEl || !outputEl) return;

  inputEl.addEventListener("input", () => {
    let text = inputEl.value;
    if (!text) {
      outputEl.innerHTML = "Type on the left to see live masking...";
      return;
    }

    // Client-side visual masking simulator
    text = text.replace(/\b[A-Z]{5}[0-9]{4}[A-Z]\b/gi, '<span class="redacted-tag">[REDACTED_PAN]</span>');
    text = text.replace(/\b[2-9]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b/gi, '<span class="redacted-tag">[REDACTED_AADHAAR]</span>');
    text = text.replace(/(?:\+91[\-\s]?|91[\-\s]?|0)?[6-9]\d{9}\b/gi, '<span class="redacted-tag">[REDACTED_PHONE]</span>');
    text = text.replace(/\b[a-zA-Z0-9.\-_]{2,64}@(okhdfcbank|okaxis|okicici|oksbi|paytm|upi|ybl)\b/gi, '<span class="redacted-tag">[REDACTED_UPI_VPA]</span>');
    text = text.replace(/\b[A-Z]{4}0[A-Z0-9]{6}\b/gi, '<span class="redacted-tag">[REDACTED_IFSC]</span>');
    text = text.replace(/\b\d{3}-\d{2}-\d{4}\b/gi, '<span class="redacted-tag">[REDACTED_SSN]</span>');

    outputEl.innerHTML = text;
  });
}

async function loadParametersGrid() {
  const grid = document.getElementById("parametersGrid");
  grid.innerHTML = "<p class='text-xs text-slate-400'>Loading configuration parameters...</p>";

  try {
    const res = await fetch("/api/v1/config/parameters");
    const data = await res.json();
    grid.innerHTML = "";

    const sectionIcons = {
      economics: "coins",
      risk_model_weights: "bar-chart-2",
      portfolio_caps: "pie-chart",
      fraud_rules: "shield-alert"
    };

    for (const [section, params] of Object.entries(data)) {
      const card = document.createElement("div");
      card.className = "p-5 rounded-xl bg-dark-card border border-dark-border space-y-3";

      const icon = sectionIcons[section] || "settings";
      const title = section.replace(/_/g, " ").toUpperCase();

      const rows = Object.entries(params).map(([k, v]) => {
        let valStr = typeof v === "object" ? JSON.stringify(v) : v;
        return `
          <div class="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 last:border-none">
            <span class="text-slate-400 font-medium">${k}</span>
            <span class="font-mono font-semibold text-cyan-400">${valStr}</span>
          </div>
        `;
      }).join("");

      card.innerHTML = `
        <div class="flex items-center gap-2 pb-2 border-b border-dark-border">
          <i data-lucide="${icon}" class="w-4 h-4 text-cyan-400"></i>
          <h4 class="text-xs font-bold tracking-wider text-white uppercase">${title}</h4>
        </div>
        <div>${rows}</div>
      `;
      grid.appendChild(card);
    }
  } catch (err) {
    grid.innerHTML = `<p class="text-xs text-rose-400">Error loading parameters: ${err.message}</p>`;
  }

  if (window.lucide) lucide.createIcons();
}

function formatAgentTitle(agentKey) {
  const map = {
    financial_analysis: "Financial Analysis",
    risk_assessment: "Risk Assessment",
    portfolio: "Portfolio Optimization",
    fraud_detection: "Fraud Detection",
    compliance: "Regulatory Compliance",
    orchestrator: "Autonomous Router"
  };
  return map[agentKey] || agentKey || "Intelligence Engine";
}
