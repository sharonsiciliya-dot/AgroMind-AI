// AgroMind AI Frontend Logic

let currentReportData = null;
let selectedCropName = "Rice";

document.addEventListener("DOMContentLoaded", () => {
    // Set dynamic current date text
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' };
    const dateEl = document.getElementById("current-date-text");
    if (dateEl) dateEl.innerText = now.toLocaleDateString("en-US", options);

    // Initial run
    runAdvisory();

    // Allow Enter key to submit chat
    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendChatMessage();
        });
    }
});

function selectCrop(cropName) {
    selectedCropName = cropName;
    document.querySelectorAll(".commodity-btn").forEach(btn => {
        if (btn.getAttribute("data-crop") === cropName) {
            btn.classList.add("border-agro-500", "bg-agro-50", "border-2");
            btn.classList.remove("border-slate-200", "bg-white");
        } else {
            btn.classList.remove("border-agro-500", "bg-agro-50", "border-2");
            btn.classList.add("border-slate-200", "bg-white");
        }
    });

    const fieldTitle = document.getElementById("field-card-title");
    if (fieldTitle) fieldTitle.innerText = `${cropName} Field Block #1`;

    runAdvisory();
}

function applyPreset(loc, crop, soil, stage) {
    document.getElementById("input-location").value = loc;
    document.getElementById("input-soil").value = soil;
    document.getElementById("input-stage").value = stage;
    selectCrop(crop);
}

function switchTab(tabId) {
    const tabs = ["advisory", "chat", "timeline"];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const content = document.getElementById(`tab-content-${t}`);
        if (t === tabId) {
            btn.classList.add("border-agro-700", "text-agro-900", "font-extrabold");
            btn.classList.remove("border-transparent", "text-slate-600");
            content.classList.remove("hidden");
        } else {
            btn.classList.remove("border-agro-700", "text-agro-900", "font-extrabold");
            btn.classList.add("border-transparent", "text-slate-600");
            content.classList.add("hidden");
        }
    });
}

async function runAdvisory() {
    const runBtn = document.getElementById("run-btn");
    const loc = document.getElementById("input-location").value.trim() || "Mangaluru";
    const soil = document.getElementById("input-soil").value;
    const stage = document.getElementById("input-stage").value;
    const acres = parseFloat(document.getElementById("input-acres").value) || 2.5;

    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>Analyzing Telemetry & Coordinating Agents...</span>`;
    }

    try {
        const response = await fetch("/api/advisory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                location: loc,
                crop: selectedCropName,
                soil: soil,
                stage: stage,
                farm_size_acres: acres
            })
        });

        if (!response.ok) throw new Error("API call failed");
        const data = await response.json();
        currentReportData = data;
        renderAdvisory(data);
    } catch (err) {
        console.error("Advisory error:", err);
    } finally {
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = `<i class="fa-solid fa-brain"></i><span>Run Multi-Agent Advisory</span>`;
        }
    }
}

function renderAdvisory(report) {
    const weather = report.weather_intelligence || {};
    const cropInfo = report.crop_analysis || {};
    const recs = report.recommendations || {};
    const conflicts = report.conflicts_detected || [];
    const timeline = report.multi_agent_timeline || [];

    // Weather card updates
    document.getElementById("weather-location-name").innerText = weather.location || "Farm Field";
    document.getElementById("weather-temp").innerText = `+${weather.temperature || 28}°C`;
    document.getElementById("weather-soil-temp").innerText = `+${weather.soil_temp_est || 26}°C`;
    document.getElementById("weather-humidity").innerText = `${weather.humidity || 65}%`;
    document.getElementById("weather-wind").innerText = `${weather.wind_speed || 12} km/h`;
    document.getElementById("weather-rain").innerText = `${weather.forecast_3d_rain_mm || 0} mm`;
    
    const riskBadge = document.getElementById("weather-risk-badge");
    const risk = weather.overall_weather_risk || "LOW";
    riskBadge.innerText = `${risk} Risk`;
    riskBadge.className = `text-xs font-semibold px-2.5 py-0.5 rounded-full ${
        risk === 'HIGH' ? 'bg-rose-500 text-white' : (risk === 'MEDIUM' ? 'bg-amber-500 text-white' : 'bg-white/20 text-white')
    }`;

    // Executive summary (formatted markdown paragraphs)
    const summaryText = report.executive_summary || "Synthesis complete.";
    document.getElementById("executive-summary-text").innerHTML = summaryText
        .split("\n\n")
        .map(p => `<p>${p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>`)
        .join("");

    // Irrigation
    const irri = recs.irrigation || {};
    document.getElementById("irrigation-text").innerText = irri.guideline || "Maintain scheduled irrigation.";
    const irriBadge = document.getElementById("irrigation-urgency");
    if (irriBadge) {
        irriBadge.innerText = irri.urgency || "NORMAL";
        irriBadge.className = `text-[10px] font-bold px-2 py-0.5 rounded-full ${
            irri.urgency === 'HIGH' || irri.urgency === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700'
        }`;
    }

    // Fertilizer
    const fert = recs.fertilizer || {};
    let fertText = fert.guideline || "Apply standard balanced nutrients.";
    if (fert.caution) fertText += ` (${fert.caution})`;
    document.getElementById("fertilizer-text").innerText = fertText;

    // Pest & Disease list
    const pestContainer = document.getElementById("pest-list");
    if (pestContainer) {
        const pests = recs.pest_and_disease || [];
        if (pests.length > 0) {
            pestContainer.innerHTML = pests.map(p => `
                <div class="border-b border-slate-100 pb-1.5 mb-1.5 last:border-0 last:pb-0 last:mb-0">
                    <span class="font-bold text-slate-800">• ${p.target}:</span> 
                    <span class="text-slate-600">${p.action}</span>
                </div>
            `).join("");
        } else {
            pestContainer.innerHTML = "<div>• No active pest outbreaks detected under current conditions.</div>";
        }
    }

    // Field Operations Feasibility
    const opsContainer = document.getElementById("ops-list");
    if (opsContainer) {
        const ops = recs.field_operations || {};
        opsContainer.innerHTML = Object.entries(ops).map(([k, v]) => {
            const icon = v.permitted ? "✅" : "🛑";
            const name = k.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
            return `<div>${icon} <strong>${name}:</strong> ${v.reason}</div>`;
        }).join("");
    }

    // Conflicts panel
    const conflictPanel = document.getElementById("conflict-panel");
    const conflictDesc = document.getElementById("conflict-desc");
    if (conflicts.length > 0) {
        conflictPanel.classList.remove("hidden");
        conflictDesc.innerHTML = conflicts.map(c => `
            <div class="mt-1">
                <strong>${c.agents_involved}:</strong> ${c.resolution}
            </div>
        `).join("");
    } else {
        conflictPanel.classList.add("hidden");
    }

    // Timeline
    const timelineContainer = document.getElementById("timeline-container");
    if (timelineContainer) {
        timelineContainer.innerHTML = timeline.map(e => `
            <div class="relative pl-6 pb-3 border-l-2 border-agro-300 last:border-0">
                <span class="absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full bg-agro-700"></span>
                <div class="text-[10px] text-slate-400 font-mono">${e.timestamp}</div>
                <div class="text-xs font-bold text-agro-900">${e.sender} ➔ <span class="text-sky-700">${e.recipient}</span></div>
                <div class="text-xs font-semibold text-slate-700 mt-0.5">${e.action}</div>
                <div class="text-[11px] text-slate-500 mt-0.5">${e.details}</div>
            </div>
        `).join("");
    }
}

async function sendChatMessage() {
    const input = document.getElementById("chat-input");
    const query = input.value.trim();
    if (!query) return;

    const chatBox = document.getElementById("chat-messages");
    
    // Add User Message
    chatBox.innerHTML += `
        <div class="flex items-start justify-end space-x-2.5">
            <div class="bg-agro-700 text-white rounded-2xl rounded-tr-none px-4 py-2 text-xs max-w-[85%] leading-relaxed">
                ${query}
            </div>
        </div>
    `;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Loading indicator
    const loadingId = `load-${Date.now()}`;
    chatBox.innerHTML += `
        <div id="${loadingId}" class="flex items-start space-x-2.5">
            <div class="w-7 h-7 rounded-full bg-agro-700 text-white flex items-center justify-center text-xs flex-shrink-0">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="bg-slate-100 rounded-2xl rounded-tl-none px-4 py-2 text-xs text-slate-500 italic">
                Gemini AI is reasoning...
            </div>
        </div>
    `;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: query,
                context: {
                    crop: selectedCropName,
                    location: document.getElementById("input-location").value,
                    stage: document.getElementById("input-stage").value,
                    soil: document.getElementById("input-soil").value
                }
            })
        });

        const data = await res.json();
        const loadEl = document.getElementById(loadingId);
        if (loadEl) loadEl.remove();

        chatBox.innerHTML += `
            <div class="flex items-start space-x-2.5">
                <div class="w-7 h-7 rounded-full bg-agro-700 text-white flex items-center justify-center text-xs flex-shrink-0">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="bg-slate-100 rounded-2xl rounded-tl-none px-4 py-2.5 text-xs text-slate-800 max-w-[85%] leading-relaxed">
                    ${data.answer || "No response received."}
                </div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (e) {
        const loadEl = document.getElementById(loadingId);
        if (loadEl) loadEl.remove();
        chatBox.innerHTML += `
            <div class="text-xs text-rose-500 px-4">Connection to Gemini agent failed.</div>
        `;
    }
}

function downloadReport() {
    if (!currentReportData) return;
    const meta = currentReportData.farm_metadata || {};
    const text = `# AgroMind AI Farming Advisory
Generated on: ${meta.generated_at}
Location: ${meta.location}
Crop: ${meta.crop} (${meta.stage}) | Soil: ${meta.soil}

---
## Executive Summary
${currentReportData.executive_summary}

---
## Recommendations
- Irrigation: ${currentReportData.recommendations.irrigation.guideline}
- Fertilizer: ${currentReportData.recommendations.fertilizer.guideline}
`;
    const blob = new Blob([text], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `AgroMind_Report_${meta.crop}_${meta.location}.md`;
    a.click();
}
