// AgroMind AI Frontend Logic

let currentReportData = null;
let selectedCropName = "Rice";
let activeFilter = "all";

// Default commodities list with categories and water needs
let availableCrops = [
    { name: "Rice", icon: "🍚", category: "grains", water_need: "High" },
    { name: "Corn / Maize", icon: "🌽", category: "grains", water_need: "Medium" },
    { name: "Wheat", icon: "🌾", category: "grains", water_need: "Medium" },
    { name: "Cotton", icon: "☁️", category: "cash", water_need: "Medium" },
    { name: "Tomato", icon: "🍅", category: "vegetables", water_need: "Medium" },
    { name: "Potato", icon: "🥔", category: "vegetables", water_need: "Medium" },
    { name: "Olive", icon: "🫒", category: "cash", water_need: "Low" }
];

document.addEventListener("DOMContentLoaded", () => {
    // Check if intro screen was previously dismissed
    const introDismissed = sessionStorage.getItem("agromind_intro_dismissed");
    const introEl = document.getElementById("wheat-intro-screen");
    if (introDismissed === "true" && introEl) {
        introEl.style.display = "none";
    }

    // Set dynamic current date text
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' };
    const dateEl = document.getElementById("current-date-text");
    if (dateEl) dateEl.innerText = now.toLocaleDateString("en-US", options);

    // Load custom crops from localStorage if any
    loadSavedCrops();

    // Fetch crops from backend
    fetchBackendCrops();

    // Render commodity grid
    renderCommodityGrid();

    // Initial advisory run
    runAdvisory();

    // Universal Search Bar Enter key trigger
    const searchInput = document.getElementById("universal-search-input");
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") handleUniversalSearch();
        });
    }

    // Chat Enter key trigger
    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendChatMessage();
        });
    }
});

// 🌾 Intro Screen Dismiss & Transition into Home Page
function dismissIntroScreen() {
    const introEl = document.getElementById("wheat-intro-screen");
    if (introEl) {
        introEl.style.transform = "translateY(-100%)";
        introEl.style.opacity = "0";
        sessionStorage.setItem("agromind_intro_dismissed", "true");
        setTimeout(() => {
            introEl.style.display = "none";
        }, 700);
    }
}

// 🌾 Re-open Wheat Intro Animation for presentation/demo
function reopenIntroScreen() {
    const introEl = document.getElementById("wheat-intro-screen");
    if (introEl) {
        introEl.style.display = "flex";
        introEl.style.transform = "translateY(0%)";
        introEl.style.opacity = "1";
    }
}

// Load custom crops from localStorage
function loadSavedCrops() {
    try {
        const saved = localStorage.getItem("agromind_custom_crops");
        if (saved) {
            const parsed = JSON.parse(saved);
            parsed.forEach(c => {
                if (!availableCrops.some(existing => existing.name.toLowerCase() === c.name.toLowerCase())) {
                    availableCrops.push(c);
                }
            });
        }
    } catch (e) {
        console.warn("Could not load custom crops from localStorage", e);
    }
}

// Fetch crop list from backend API
async function fetchBackendCrops() {
    try {
        const res = await fetch("/api/crops");
        if (res.ok) {
            const data = await res.json();
            if (data.crops && data.crops.length > 0) {
                data.crops.forEach(c => {
                    if (!availableCrops.some(existing => existing.name.toLowerCase() === c.name.toLowerCase())) {
                        availableCrops.push({
                            name: c.name,
                            icon: c.icon || "🌱",
                            category: "vegetables",
                            water_need: c.water_need || "Medium"
                        });
                    }
                });
                renderCommodityGrid();
            }
        }
    } catch (e) {}
}

// 🏷️ Filter commodities by category or water demand
function filterCommodities(filterType) {
    activeFilter = filterType;

    // Update filter pill UI
    document.querySelectorAll(".filter-pill").forEach(pill => {
        if (pill.getAttribute("data-filter") === filterType) {
            pill.className = "filter-pill px-3 py-1 rounded-full font-bold bg-agro-700 text-white flex-shrink-0 transition";
        } else {
            pill.className = "filter-pill px-3 py-1 rounded-full font-medium bg-white text-slate-600 border border-slate-200 hover:border-agro-400 hover:text-agro-700 flex-shrink-0 transition";
        }
    });

    renderCommodityGrid();
}

// Render dynamic commodity buttons matching active filter
function renderCommodityGrid() {
    const grid = document.getElementById("commodity-grid");
    if (!grid) return;

    let filtered = availableCrops;
    if (activeFilter === "grains") {
        filtered = availableCrops.filter(c => c.category === "grains");
    } else if (activeFilter === "vegetables") {
        filtered = availableCrops.filter(c => c.category === "vegetables");
    } else if (activeFilter === "cash") {
        filtered = availableCrops.filter(c => c.category === "cash");
    } else if (activeFilter === "low_water") {
        filtered = availableCrops.filter(c => c.water_need === "Low");
    } else if (activeFilter === "high_water") {
        filtered = availableCrops.filter(c => c.water_need === "High");
    }

    const badge = document.getElementById("crop-count-badge");
    if (badge) badge.innerText = `${filtered.length} items`;

    let html = "";
    filtered.forEach(c => {
        const isSelected = (c.name.toLowerCase() === selectedCropName.toLowerCase());
        const borderClass = isSelected ? "border-agro-500 bg-agro-50 border-2" : "border-slate-200 bg-white hover:border-agro-300";
        const cleanDisplayName = c.name.split("/")[0].trim();
        html += `
            <button onclick="selectCrop('${c.name}')" data-crop="${c.name}" class="commodity-btn flex flex-col items-center p-2 rounded-xl border ${borderClass} transition shadow-2xs">
                <span class="text-xl mb-0.5">${c.icon || '🌱'}</span>
                <span class="text-[11px] font-bold text-slate-800 truncate w-full text-center">${cleanDisplayName}</span>
            </button>
        `;
    });

    // Add "+ Add" shortcut button
    html += `
        <button onclick="openAddCropModal()" title="Add custom crop" class="flex flex-col items-center justify-center p-2 rounded-xl border-2 border-dashed border-agro-300 bg-agro-50/50 hover:bg-agro-100/50 text-agro-700 transition">
            <span class="text-base"><i class="fa-solid fa-plus"></i></span>
            <span class="text-[10px] font-bold mt-0.5">Add</span>
        </button>
    `;

    grid.innerHTML = html;
}

// 📍 Location Dropdown Handler
function handleLocationSelect(locationName) {
    if (!locationName) return;
    document.getElementById("input-location").value = locationName;
    const searchInput = document.getElementById("universal-search-input");
    if (searchInput) searchInput.value = locationName;
    runAdvisory();
}

// 🛰️ GPS Auto-Detect Location
function detectGPSLocation() {
    const gpsBtn = document.getElementById("gps-btn");
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    if (gpsBtn) {
        gpsBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-agro-600"></i><span>Locating...</span>`;
    }

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            try {
                // Reverse geocode with BigDataCloud
                const geoResp = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
                if (geoResp.ok) {
                    const geoData = await geoResp.json();
                    const detectedCity = geoData.city || geoData.locality || geoData.principalSubdivision || "Mangaluru";
                    document.getElementById("input-location").value = detectedCity;
                    const searchInput = document.getElementById("universal-search-input");
                    if (searchInput) searchInput.value = detectedCity;
                    runAdvisory();
                } else {
                    document.getElementById("input-location").value = "Mangaluru";
                    runAdvisory();
                }
            } catch (err) {
                runAdvisory();
            } finally {
                if (gpsBtn) gpsBtn.innerHTML = `<i class="fa-solid fa-crosshairs text-agro-600"></i><span class="hidden sm:inline">GPS Auto</span>`;
            }
        },
        (error) => {
            if (gpsBtn) gpsBtn.innerHTML = `<i class="fa-solid fa-crosshairs text-agro-600"></i><span class="hidden sm:inline">GPS Auto</span>`;
            alert("Unable to retrieve your location. Please select a region from the dropdown.");
        },
        { timeout: 8000 }
    );
}

// Modal functions for adding a new crop
function openAddCropModal() {
    const modal = document.getElementById("add-crop-modal");
    if (modal) {
        modal.classList.remove("hidden");
        document.getElementById("new-crop-name").focus();
    }
}

function closeAddCropModal() {
    const modal = document.getElementById("add-crop-modal");
    if (modal) modal.classList.add("hidden");
}

function setNewCropIcon(icon) {
    document.getElementById("new-crop-selected-icon").value = icon;
    document.querySelectorAll(".icon-opt").forEach(btn => {
        if (btn.innerText.trim() === icon) {
            btn.classList.add("border-2", "border-agro-500", "bg-agro-50");
            btn.classList.remove("border-slate-200", "bg-slate-50");
        } else {
            btn.classList.remove("border-2", "border-agro-500", "bg-agro-50");
            btn.classList.add("border-slate-200", "bg-slate-50");
        }
    });
}

async function submitNewCrop() {
    const nameInput = document.getElementById("new-crop-name");
    const name = nameInput.value.trim();
    if (!name) {
        alert("Please enter a crop or food item name.");
        return;
    }

    const icon = document.getElementById("new-crop-selected-icon").value || "🌱";
    const water = document.getElementById("new-crop-water").value || "Medium";
    const soil = document.getElementById("new-crop-soil").value || "Loamy soil";

    const submitBtn = document.getElementById("submit-crop-btn");
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>Saving...</span>`;
    }

    // 1. Post to backend
    try {
        await fetch("/api/crops", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: name,
                icon: icon,
                water_need: water,
                best_soil: soil
            })
        });
    } catch (e) {
        console.warn("Backend crop registration warning:", e);
    }

    // 2. Add to local list and localStorage
    const newCropObj = { name: name, icon: icon, category: "vegetables", water_need: water };
    if (!availableCrops.some(c => c.name.toLowerCase() === name.toLowerCase())) {
        availableCrops.push(newCropObj);
        try {
            const saved = JSON.parse(localStorage.getItem("agromind_custom_crops") || "[]");
            saved.push(newCropObj);
            localStorage.setItem("agromind_custom_crops", JSON.stringify(saved));
        } catch (e) {}
    }

    // 3. Reset form and close modal
    nameInput.value = "";
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-check"></i><span>Save & Select</span>`;
    }
    closeAddCropModal();

    // 4. Update UI and immediately select the new crop
    renderCommodityGrid();
    document.getElementById("input-soil").value = soil;
    selectCrop(name);
}

// Universal Search Handler
function handleUniversalSearch() {
    const searchInput = document.getElementById("universal-search-input");
    if (!searchInput) return;
    const query = searchInput.value.trim().toLowerCase();
    if (!query) return;

    let matchedCrop = null;
    for (const c of availableCrops) {
        if (query.includes(c.name.toLowerCase())) {
            matchedCrop = c.name;
            break;
        }
    }

    if (matchedCrop) {
        selectCrop(matchedCrop);
    }

    // Extract potential location if not purely crop
    const cleanedLocation = query
        .replace(/rice|paddy|wheat|corn|maize|cotton|tomato|potato|olive|grapes/gi, "")
        .replace(/in|at|farm|field|district|crop|for/gi, "")
        .trim();

    if (cleanedLocation.length > 2) {
        const formattedLoc = cleanedLocation.charAt(0).toUpperCase() + cleanedLocation.slice(1);
        document.getElementById("input-location").value = formattedLoc;
    } else if (!matchedCrop && query.length > 2) {
        const formattedLoc = query.charAt(0).toUpperCase() + query.slice(1);
        document.getElementById("input-location").value = formattedLoc;
    }

    runAdvisory();
}

function selectCrop(cropName) {
    selectedCropName = cropName;

    // Update active style on all buttons
    renderCommodityGrid();

    const fieldTitle = document.getElementById("field-card-title");
    if (fieldTitle) fieldTitle.innerText = `${cropName} Field Block #1`;

    runAdvisory();
}

function applyPreset(loc, crop, soil, stage) {
    document.getElementById("input-location").value = loc;
    document.getElementById("input-soil").value = soil;
    document.getElementById("input-stage").value = stage;
    const searchInput = document.getElementById("universal-search-input");
    if (searchInput) searchInput.value = `${loc} • ${crop}`;
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
    const searchBtn = document.getElementById("search-action-btn");
    const loc = document.getElementById("input-location").value.trim() || "Mangaluru";
    const soil = document.getElementById("input-soil").value;
    const stage = document.getElementById("input-stage").value;
    const acres = parseFloat(document.getElementById("input-acres").value) || 2.5;

    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>Analyzing Telemetry & Coordinating Agents...</span>`;
    }
    if (searchBtn) {
        searchBtn.disabled = true;
        searchBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
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
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.innerHTML = `<i class="fa-solid fa-bolt text-amber-300"></i><span>Search</span>`;
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
                AgroMind AI is reasoning...
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
                <div class="bg-slate-100 rounded-2xl rounded-tl-none px-4 py-2 text-xs text-slate-800 max-w-[85%] leading-relaxed">
                    ${data.answer || "No response received."}
                </div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (e) {
        const loadEl = document.getElementById(loadingId);
        if (loadEl) loadEl.remove();
        chatBox.innerHTML += `
            <div class="text-xs text-rose-500 px-4">Connection to AI assistant failed.</div>
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
