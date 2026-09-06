let cy = null;
let currentNetworkData = null;

document.addEventListener("DOMContentLoaded", () => {
  initGraph();
  setupEventListeners();
  loadNetwork();
  loadStats();
});

// Generic Debounce Utility
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Toast Notification System
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;

  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, 3500);
}

// Initialize Cytoscape with High-Contrast Legible Styling
function initGraph() {
  cy = cytoscape({
    container: document.getElementById("cy"),
    style: [
      {
        selector: "node",
        style: {
          "label": "data(label)",
          "color": "#f8fafc",
          "font-size": "11px",
          "font-weight": "600",
          "font-family": "JetBrains Mono, monospace",
          "text-valign": "bottom",
          "text-margin-y": "6px",
          "text-outline-color": "#090d16",
          "text-outline-width": "3px",
          "text-background-color": "rgba(9, 13, 22, 0.75)",
          "text-background-opacity": 0.8,
          "text-background-padding": "3px",
          "text-background-shape": "roundrectangle",
          "background-color": function(ele) {
            const d = ele.data();
            if (!d.is_criminal) return "#475569";
            if (d.community === "COMMUNITY_1") return "#ef4444"; // Alpha Red
            if (d.community === "COMMUNITY_2") return "#f97316"; // Beta Orange
            if (d.community === "COMMUNITY_3") return "#a855f7"; // Gamma Purple
            if (d.community === "COMMUNITY_4") return "#06b6d4"; // Delta Cyan
            return "#ef4444";
          },
          "width": function(ele) {
            const d = ele.data();
            if (d.role && d.role.includes("Kingpin")) return 48;
            if (d.is_bridge) return 40;
            return 28 + (d.threat_score / 5);
          },
          "height": function(ele) {
            const d = ele.data();
            if (d.role && d.role.includes("Kingpin")) return 48;
            if (d.is_bridge) return 40;
            return 28 + (d.threat_score / 5);
          },
          "border-width": function(ele) {
            const d = ele.data();
            if (d.role && d.role.includes("Kingpin")) return 4;
            if (d.is_bridge) return 3;
            return 1.5;
          },
          "border-color": function(ele) {
            const d = ele.data();
            if (d.role && d.role.includes("Kingpin")) return "#eab308"; // Gold
            if (d.is_bridge) return "#38bdf8"; // Light Blue
            return "#1e293b";
          },
          "border-style": function(ele) {
            return ele.data("is_bridge") ? "dashed" : "solid";
          }
        }
      },
      {
        selector: "edge",
        style: {
          "width": function(ele) {
            return Math.min(6, 1.5 + (ele.data("weight") || 1) * 0.4);
          },
          "line-color": function(ele) {
            const d = ele.data();
            if (d.txn_count > 0) return "#10b981"; // Financial Green
            if (d.fir_co_count > 0) return "#f43f5e"; // FIR Red
            return "#334155"; // Default Call
          },
          "curve-style": "bezier",
          "opacity": 0.65
        }
      },
      {
        selector: ".highlighted",
        style: {
          "opacity": 1.0,
          "border-color": "#ffffff",
          "border-width": 4,
          "z-index": 999
        }
      },
      {
        selector: ".dimmed",
        style: {
          "opacity": 0.15
        }
      }
    ],
    layout: {
      name: "cose",
      animate: true,
      randomize: false,
      componentSpacing: 90,
      nodeRepulsion: function(node) { return 450000; },
      nodeOverlap: 20,
      idealEdgeLength: function(edge) { return 100; },
      edgeElasticity: function(edge) { return 100; },
      gravity: 80,
      numIter: 1000
    }
  });

  // Node Click -> Inspect Profile
  cy.on("tap", "node", function(evt) {
    const node = evt.target;
    const eid = node.data("id");
    inspectSuspect(eid);
    highlightNeighborhood(node);
  });

  // Edge Click -> Show relationship summary in inspector
  cy.on("tap", "edge", function(evt) {
    const d = evt.target.data();
    const srcName = evt.target.source().data("label") || d.source;
    const tgtName = evt.target.target().data("label") || d.target;
    const panel = document.getElementById("inspector-panel");
    const container = document.getElementById("inspector-content");
    panel.classList.remove("hidden");
    container.innerHTML = `
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-name-block">
            <h3>${srcName} ↔ ${tgtName}</h3>
            <span class="profile-id">Edge Weight: ${d.weight || 1}</span>
          </div>
        </div>
        <div class="section-box">
          <h4>Relationship Evidence</h4>
          <div class="detail-row"><span class="label">📞 Calls:</span><span class="val">${d.call_count || 0} (${d.call_duration || 0}s total)</span></div>
          <div class="detail-row"><span class="label">💸 Transactions:</span><span class="val">${d.txn_count || 0} — ₹${(d.txn_amount || 0).toLocaleString()}</span></div>
          <div class="detail-row"><span class="label">📋 FIR Co-mentions:</span><span class="val">${d.fir_co_count || 0}</span></div>
          <div class="detail-row"><span class="label">📱 Social Links:</span><span class="val">${d.social_count || 0}</span></div>
        </div>
      </div>`;
  });

  // Background Click -> Reset highlight
  cy.on("tap", function(evt) {
    if (evt.target === cy) {
      cy.elements().removeClass("highlighted dimmed");
    }
  });
}

// Highlight connected neighborhood
function highlightNeighborhood(node) {
  cy.elements().removeClass("highlighted dimmed");
  const neighborhood = node.closedNeighborhood();
  cy.elements().difference(neighborhood).addClass("dimmed");
  neighborhood.addClass("highlighted");
}

// Fetch network data with loading & error handling
async function loadNetwork() {
  const loading = document.getElementById("graph-loading");
  const errorBox = document.getElementById("graph-error");

  if (loading) loading.style.display = "flex";
  if (errorBox) errorBox.classList.add("hidden");

  const minThreat = document.getElementById("threat-slider").value;
  const criminalOnly = document.getElementById("toggle-criminal-only").checked;
  const syndicate = document.getElementById("select-syndicate").value;
  const role = document.getElementById("select-role").value;

  const url = `/api/network?min_threat=${minThreat}&criminal_only=${criminalOnly}&syndicate=${encodeURIComponent(syndicate)}&role=${encodeURIComponent(role)}`;
  
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const data = await res.json();
    currentNetworkData = data;

    cy.elements().remove();
    cy.add(data.nodes);
    cy.add(data.edges);

    cy.layout({
      name: "cose",
      animate: true,
      animationDuration: 700,
      componentSpacing: 80,
      nodeRepulsion: 400000
    }).run();

    // Update live count pill if available
    const entCount = document.getElementById("stat-entities");
    if (entCount) entCount.innerText = data.nodes.length;

    // Dynamically populate syndicate options if not already populated
    const syndicateSelect = document.getElementById("select-syndicate");
    if (syndicateSelect && syndicateSelect.options.length <= 1) {
      const comms = new Set();
      data.nodes.forEach(n => {
        if (n.data && n.data.community && n.data.community !== "UNASSIGNED") {
          comms.add(n.data.community);
        }
      });
      const sortedComms = Array.from(comms).sort();
      sortedComms.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        syndicateSelect.appendChild(opt);
      });
    }

    if (loading) loading.style.display = "none";
  } catch (err) {
    console.error("Network load failed:", err);
    if (loading) loading.style.display = "none";
    if (errorBox) errorBox.classList.remove("hidden");
  }
}

// Fetch live telemetry stats
async function loadStats() {
  try {
    const res = await fetch("/api/benchmark");
    if (!res.ok) return;
    const data = await res.json();
    if (data.metrics) {
      document.getElementById("stat-accuracy").innerText = `${data.metrics.accuracy_percent}%`;
    }
    if (data.confusion_matrix) {
      const cm = data.confusion_matrix;
      const criminals = cm.true_positives + cm.false_negatives; // total actual criminals
      const civilians = cm.true_negatives + cm.false_positives; // total actual civilians
      const elCrim = document.getElementById("stat-criminals");
      const elCiv = document.getElementById("stat-civilians");
      if (elCrim) elCrim.innerText = criminals;
      if (elCiv) elCiv.innerText = civilians;
    }
  } catch (e) {
    console.error("Stats load failed:", e);
  }
}

// Inspect suspect details in right drawer
async function inspectSuspect(eid) {
  const panel = document.getElementById("inspector-panel");
  const container = document.getElementById("inspector-content");
  panel.classList.remove("hidden");

  container.innerHTML = `
    <div class="graph-loading" style="position: relative; top: 0; left: 0; transform: none; margin: 40px auto;">
      <div class="cyber-spinner"></div>
      <span>Loading dossier for ${eid}...</span>
    </div>
  `;

  try {
    const res = await fetch(`/api/entity/${eid}`);
    const data = await res.json();
    if (data.error) {
      container.innerHTML = `<p style="color: var(--alpha-red); text-align: center; padding: 20px;">${data.error}</p>`;
      return;
    }

    const p = data.profile;
    const scoreClass = data.threat_score >= 70 ? "threat-high" : (data.threat_score >= 30 ? "threat-med" : "threat-low");

    let casesHtml = "";
    if (p.prior_cases && p.prior_cases.length > 0) {
      p.prior_cases.forEach(c => {
        casesHtml += `
          <div class="fir-item">
            <strong>${c.prior_case_id}</strong>: ${c.offense_type}<br>
            <span class="label">Date:</span> ${c.date} | <span class="label">Status:</span> ${c.status}
          </div>
        `;
      });
    } else {
      casesHtml = "<p style='font-size: 11px; color: var(--text-muted);'>No prior criminal conviction recorded.</p>";
    }

    let contactsHtml = "";
    if (data.top_contacts && data.top_contacts.length > 0) {
      data.top_contacts.slice(0, 5).forEach(c => {
        contactsHtml += `
          <div class="contact-item">
            <strong>${c.contact_name} (${c.contact_id})</strong><br>
            Calls: ${c.call_count} (${c.total_duration_sec}s) | Threat Score: ${c.threat_score}/100
          </div>
        `;
      });
    } else {
      contactsHtml = "<p style='font-size: 11px; color: var(--text-muted);'>No surveillance calls recorded.</p>";
    }

    let firsHtml = "";
    if (data.fir_involvements && data.fir_involvements.length > 0) {
      data.fir_involvements.forEach(f => {
        firsHtml += `
          <div class="fir-item">
            <strong>${f.fir_id}</strong> (${f.police_station})<br>
            <em>${f.incident_type}</em><br>
            <span style="font-size: 10px; color: #94a3b8;">${f.narrative}</span>
          </div>
        `;
      });
    } else {
      firsHtml = "<p style='font-size: 11px; color: var(--text-muted);'>No co-mentioned FIR reports.</p>";
    }

    container.innerHTML = `
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-name-block">
            <h3>${p.name}</h3>
            <span class="profile-id">${eid} // ${data.detected_role}</span>
          </div>
          <div class="threat-meter">
            <span class="threat-score-badge ${scoreClass}">${data.threat_score}</span>
            <div style="font-size: 9px; color: var(--text-muted); font-family: var(--font-mono);">THREAT SCORE</div>
          </div>
        </div>

        <div class="detail-row"><span class="label">Age / Gender:</span><span class="val">${p.age || 'N/A'} / ${p.gender || 'N/A'}</span></div>
        <div class="detail-row"><span class="label">Mobile:</span><span class="val">${p.phone_number || 'N/A'}</span></div>
        <div class="detail-row"><span class="label">Vehicle Plate:</span><span class="val">${p.vehicle_number || 'None'}</span></div>
        <div class="detail-row"><span class="label">Front Org:</span><span class="val">${p.known_organization || 'None'}</span></div>
        <div class="detail-row"><span class="label">Legal Status:</span><span class="val">${p.criminal_status}</span></div>
        <div class="detail-row"><span class="label">Cell / Cluster:</span><span class="val">${data.community}</span></div>

        <button class="btn-dossier" onclick="downloadDossier('${eid}')">
          📥 Download Case Dossier (.MD)
        </button>
      </div>

      <div class="section-box">
        <h4>Financial Trail & AML Status</h4>
        <div class="detail-row"><span class="label">Total Sent:</span><span class="val">₹${(data.financial_summary.total_sent_inr || 0).toLocaleString()}</span></div>
        <div class="detail-row"><span class="label">Total Received:</span><span class="val">₹${(data.financial_summary.total_received_inr || 0).toLocaleString()}</span></div>
        <div class="detail-row"><span class="label">Smurfing Muling:</span><span class="val">${data.financial_summary.smurf_involved ? '⚠️ FLAGGED' : 'Clean'}</span></div>
        <div class="detail-row"><span class="label">Hawala Transfer:</span><span class="val">${data.financial_summary.hawala_involved ? '⚠️ FLAGGED' : 'Clean'}</span></div>
      </div>

      <div class="section-box">
        <h4>Prior Cases (${(p.prior_cases || []).length})</h4>
        ${casesHtml}
      </div>

      <div class="section-box">
        <h4>Top Phone Contacts</h4>
        ${contactsHtml}
      </div>

      <div class="section-box">
        <h4>FIR Involvements (${(data.fir_involvements || []).length})</h4>
        ${firsHtml}
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p style="color: var(--alpha-red); text-align: center;">Error fetching suspect details: ${err}</p>`;
  }
}

// Download Dossier with Toast Notification
function downloadDossier(eid) {
  showToast(`📥 Downloading Case Dossier for ${eid}...`, "success");
  window.open(`/api/dossier/${eid}`, '_blank');
}

// Reset All Filters
function resetFilters() {
  document.getElementById("search-input").value = "";
  document.getElementById("threat-slider").value = 0;
  document.getElementById("threat-slider-val").innerText = "0";
  document.getElementById("toggle-criminal-only").checked = true;
  document.getElementById("select-syndicate").value = "";
  document.getElementById("select-role").value = "";

  if (cy) {
    cy.elements().removeClass("dimmed highlighted");
  }

  showToast("↺ Filters reset to default view", "info");
  loadNetwork();
}

// Setup Event Listeners
function setupEventListeners() {
  // Threat Slider
  const slider = document.getElementById("threat-slider");
  const sliderVal = document.getElementById("threat-slider-val");
  slider.addEventListener("input", (e) => {
    sliderVal.innerText = e.target.value;
  });
  slider.addEventListener("change", loadNetwork);

  // Filters
  document.getElementById("toggle-criminal-only").addEventListener("change", loadNetwork);
  document.getElementById("select-syndicate").addEventListener("change", loadNetwork);
  document.getElementById("select-role").addEventListener("change", loadNetwork);

  // Reset Filters Button
  const resetBtn = document.getElementById("btn-reset-filters");
  if (resetBtn) {
    resetBtn.addEventListener("click", resetFilters);
  }

  // Debounced Search
  const searchInput = document.getElementById("search-input");
  const handleSearch = debounce((query) => {
    const q = query.toLowerCase().trim();
    if (!q) {
      cy.elements().removeClass("dimmed highlighted");
      return;
    }
    cy.elements().addClass("dimmed");
    const matches = cy.nodes().filter(n => {
      const d = n.data();
      return (d.label && d.label.toLowerCase().includes(q)) ||
             (d.id && d.id.toLowerCase().includes(q)) ||
             (d.phone && d.phone.toLowerCase().includes(q)) ||
             (d.vehicle && d.vehicle.toLowerCase().includes(q)) ||
             (d.organization && d.organization.toLowerCase().includes(q));
    });
    matches.removeClass("dimmed").addClass("highlighted");
    if (matches.length > 0) {
      cy.animate({ center: { eles: matches }, zoom: 1.5, duration: 500 });
    }
  }, 250);

  searchInput.addEventListener("input", (e) => handleSearch(e.target.value));

  document.getElementById("btn-search-clear").addEventListener("click", () => {
    searchInput.value = "";
    cy.elements().removeClass("dimmed highlighted");
  });

  // Buttons: Kingpins
  document.getElementById("btn-kingpins").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/kingpins");
      const data = await res.json();
      const kingpinIds = data.kingpins.map(k => k.entity_id);
      
      cy.elements().addClass("dimmed");
      const kingpinNodes = cy.nodes().filter(n => kingpinIds.includes(n.id()));
      kingpinNodes.removeClass("dimmed").addClass("highlighted");
      cy.animate({ center: { eles: kingpinNodes }, zoom: 1.2, duration: 800 });
      showToast(`👑 Highlighted ${kingpinIds.length} Syndicate Kingpins`, "info");
    } catch (e) {
      console.error(e);
    }
  });

  // Buttons: Bridges
  document.getElementById("btn-bridges").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/bridges");
      const data = await res.json();
      const bridgeIds = data.bridges.map(b => b.entity_id);
      
      cy.elements().addClass("dimmed");
      const bridgeNodes = cy.nodes().filter(n => bridgeIds.includes(n.id()));
      bridgeNodes.removeClass("dimmed").addClass("highlighted");
      cy.animate({ center: { eles: bridgeNodes }, zoom: 1.3, duration: 800 });
      showToast(`🌉 Highlighted ${bridgeIds.length} Cross-Network Bridges`, "info");
    } catch (e) {
      console.error(e);
    }
  });

  // Buttons: Smurfing Rings
  document.getElementById("btn-smurfing").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/alerts");
      const data = await res.json();
      const ringIds = new Set();
      data.smurfing_rings.forEach(r => {
        ringIds.add(r.beneficiary_id);
        r.mule_senders.forEach(m => ringIds.add(m.id));
      });

      cy.elements().addClass("dimmed");
      const smurfNodes = cy.nodes().filter(n => ringIds.has(n.id()));
      const smurfEdges = cy.edges().filter(e => ringIds.has(e.source().id()) && ringIds.has(e.target().id()));
      smurfNodes.removeClass("dimmed").addClass("highlighted");
      smurfEdges.removeClass("dimmed").addClass("highlighted");
      cy.animate({ center: { eles: smurfNodes }, zoom: 1.2, duration: 800 });
      showToast(`🚨 Highlighted Smurfing Mule Rings`, "info");
    } catch (e) {
      console.error(e);
    }
  });

  // Buttons: Benchmark Scorecard
  document.getElementById("btn-benchmark").addEventListener("click", openBenchmarkModal);
  document.getElementById("btn-close-modal").addEventListener("click", () => {
    document.getElementById("benchmark-modal").classList.remove("active");
  });

  // Buttons: Copilot
  const copilotDrawer = document.getElementById("copilot-drawer");
  document.getElementById("btn-copilot").addEventListener("click", () => {
    copilotDrawer.classList.toggle("active");
  });
  document.getElementById("btn-close-copilot").addEventListener("click", () => {
    copilotDrawer.classList.remove("active");
  });

  // Copilot Send
  document.getElementById("btn-send-copilot").addEventListener("click", sendCopilotMessage);
  document.getElementById("copilot-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendCopilotMessage();
  });

  // Prompt chips
  document.querySelectorAll(".prompt-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      document.getElementById("copilot-input").value = prompt;
      sendCopilotMessage();
    });
  });

  // Graph actions
  document.getElementById("btn-fit-graph").addEventListener("click", () => cy.fit());
  document.getElementById("btn-reset-layout").addEventListener("click", () => {
    cy.layout({ name: "cose", animate: true }).run();
  });

  document.getElementById("btn-close-inspector").addEventListener("click", () => {
    document.getElementById("inspector-panel").classList.add("hidden");
  });

  // Retry Connection Button
  const retryBtn = document.getElementById("btn-retry-graph");
  if (retryBtn) {
    retryBtn.addEventListener("click", loadNetwork);
  }
}

// Open Benchmark Modal
async function openBenchmarkModal() {
  const modal = document.getElementById("benchmark-modal");
  const content = document.getElementById("benchmark-content");
  modal.classList.add("active");

  content.innerHTML = `
    <div class="graph-loading" style="position: relative; top: 0; left: 0; transform: none; margin: 40px auto;">
      <div class="cyber-spinner"></div>
      <span>Loading live evaluation scorecard against ground truth...</span>
    </div>
  `;

  try {
    const res = await fetch("/api/benchmark");
    const data = await res.json();
    const m = data.metrics;
    const cm = data.confusion_matrix;

    const gt = data.ground_truth_targets || {};
    const detectedKingpins = (gt.detected_kingpins || []).join(", ") || "None detected";
    const detectedBridges  = (gt.detected_bridges  || []).join(", ") || "None detected";
    const gtKingpins       = (gt.kingpins || []).join(", ") || "N/A";
    const gtBridges        = (gt.bridges  || []).join(", ") || "N/A";
    const totalCriminals   = gt.total_criminals ?? "?";
    const totalCivilians   = gt.total_civilians  ?? "?";

    content.innerHTML = `
      <div class="score-grid">
        <div class="score-box"><div class="num">${m.accuracy_percent}%</div><div class="lbl">ACCURACY</div></div>
        <div class="score-box"><div class="num">${m.precision_percent}%</div><div class="lbl">PRECISION</div></div>
        <div class="score-box"><div class="num">${m.recall_percent}%</div><div class="lbl">RECALL</div></div>
        <div class="score-box"><div class="num">${m.f1_score}</div><div class="lbl">F1 SCORE</div></div>
        <div class="score-box"><div class="num">${m.kingpin_detection_rate}%</div><div class="lbl">KINGPIN DETECTION</div></div>
        <div class="score-box"><div class="num">${m.bridge_detection_rate}%</div><div class="lbl">BRIDGE DETECTION</div></div>
      </div>

      <div class="section-box" style="margin-bottom: 16px;">
        <h4>Confusion Matrix (N = ${cm.total_eval_samples})</h4>
        <div class="detail-row"><span class="label">True Positives (Criminals Caught):</span><span class="val" style="color: var(--green-accent);">${cm.true_positives} / ${totalCriminals}</span></div>
        <div class="detail-row"><span class="label">True Negatives (Civilians Protected):</span><span class="val" style="color: var(--green-accent);">${cm.true_negatives} / ${totalCivilians}</span></div>
        <div class="detail-row"><span class="label">False Positives (Innocent Falsely Flagged):</span><span class="val" style="color: var(--alpha-red);">${cm.false_positives}</span></div>
        <div class="detail-row"><span class="label">False Negatives (Criminals Missed):</span><span class="val" style="color: var(--alpha-red);">${cm.false_negatives}</span></div>
      </div>

      <div class="section-box">
        <h4>Detected vs Ground Truth</h4>
        <div class="detail-row"><span class="label">👑 GT Kingpins:</span><span class="val">${gtKingpins}</span></div>
        <div class="detail-row"><span class="label">👑 Detected Kingpins:</span><span class="val">${detectedKingpins}</span></div>
        <div class="detail-row"><span class="label">🌉 GT Bridges:</span><span class="val">${gtBridges}</span></div>
        <div class="detail-row"><span class="label">🌉 Detected Bridges:</span><span class="val">${detectedBridges}</span></div>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<p style="color: var(--alpha-red); text-align: center;">Error loading benchmark: ${err}</p>`;
  }
}

// Send Copilot Query
async function sendCopilotMessage() {
  const input = document.getElementById("copilot-input");
  const query = input.value.trim();
  if (!query) return;

  const messages = document.getElementById("copilot-messages");

  // Add user message
  const userDiv = document.createElement("div");
  userDiv.className = "message user-message";
  userDiv.innerText = query;
  messages.appendChild(userDiv);
  input.value = "";
  messages.scrollTop = messages.scrollHeight;

  // Add thinking indicator
  const botDiv = document.createElement("div");
  botDiv.className = "message assistant-message";
  botDiv.innerText = "Interrogating knowledge graph...";
  messages.appendChild(botDiv);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch("/api/copilot/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query })
    });
    const data = await res.json();

    // Safe renderer: escape HTML first, then apply trusted markdown only
    function safeMd(text) {
      const div = document.createElement("div");
      div.textContent = text;           // escapes all HTML entities
      return div.innerHTML
        .replace(/### (.*?)(\n|$)/g, "<h4>$1</h4>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/`(.*?)`/g, "<code>$1</code>")
        .replace(/\n/g, "<br>");
    }

    botDiv.innerHTML = safeMd(data.response);
    messages.scrollTop = messages.scrollHeight;
  } catch (err) {
    botDiv.innerText = "Error contacting Copilot: " + err;
  }
}
