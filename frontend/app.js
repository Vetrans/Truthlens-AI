/* ==========================================================================
   TRUTHLENS AI - FRONTEND APPLICATION SCRIPT
   ========================================================================== */

// --- GLOBAL STATE ---
let currentAnalysisReport = null;
let currentHighlightIndex = 0;
let highlightsList = [];

document.addEventListener("DOMContentLoaded", () => {
  // Setup Drag and Drop
  setupDragAndDrop();

  // Default Tab Initialization
  switchInputTab("paste");
});

// --- NAVIGATION & TABS ---
function switchInputTab(tabType) {
  // Buttons
  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) => btn.classList.remove("active"));
  document.getElementById(`tab-${tabType}`).classList.add("active");

  // Content Areas
  document
    .querySelectorAll(".tab-content")
    .forEach((content) => content.classList.remove("active"));
  document.getElementById(`content-${tabType}`).classList.add("active");
}

function showSection(sectionId) {
  document
    .querySelectorAll(".view-section")
    .forEach((sec) => sec.classList.remove("active"));

  // Find the correct section (note: we have duplicate IDs in index.html for page separation, let's select elements carefully)
  const targets = document.querySelectorAll(`.view-section`);
  targets.forEach((t) => {
    if (t.id === sectionId) {
      t.classList.add("active");
    }
  });
}

function backToLanding() {
  // Reset file uploads
  clearSelectedFile(null);
  document.getElementById("terms-textarea").value = "";
  document.getElementById("input-error").style.display = "none";

  showSection("landing-page");
}

// --- DRAG & DROP UTILITIES ---
let selectedFile = null;

function setupDragAndDrop() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");

  // Click triggers file selector
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  });

  // Drag events
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
      },
      false,
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
      },
      false,
    );
  });

  dropZone.addEventListener(
    "drop",
    (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        handleFileSelection(files[0]);
      }
    },
    false,
  );
}

function handleFileSelection(file) {
  const allowedExtensions = ["txt", "pdf", "docx"];
  const extension = file.name.split(".").pop().toLowerCase();

  if (!allowedExtensions.includes(extension)) {
    showInputError(
      "Unsupported file type. Please upload a PDF, DOCX, or TXT document.",
    );
    return;
  }

  if (file.size > 15 * 1024 * 1024) {
    // 15MB
    showInputError("File is too large. Maximum supported file size is 15MB.");
    return;
  }

  selectedFile = file;
  document.getElementById("input-error").style.display = "none";

  // Update UI display
  const fileInfo = document.getElementById("selected-file-info");
  const fileNameSpan = document.getElementById("selected-file-name");

  fileNameSpan.innerText = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
  fileInfo.style.display = "inline-flex";
}

function clearSelectedFile(event) {
  if (event) {
    event.stopPropagation(); // Avoid triggering drop-zone browse click
  }
  selectedFile = null;
  document.getElementById("file-input").value = "";
  document.getElementById("selected-file-info").style.display = "none";
}

function showInputError(message) {
  const errorBanner = document.getElementById("input-error");
  const errorMessage = document.getElementById("error-message");

  errorMessage.innerText = message;
  errorBanner.style.display = "flex";
}

// --- PIPELINE RUNNER (API INTEGRATION) ---
let chartInstances = {};

async function startAnalysis() {
  const activeTab = document.querySelector(".tab-btn.active").id;
  const formData = new FormData();
  let hasData = false;

  if (activeTab === "tab-paste") {
    const pasteText = document.getElementById("terms-textarea").value.trim();
    if (pasteText.length < 50) {
      showInputError(
        "Legal document is too short. Please paste at least 50 characters.",
      );
      return;
    }
    formData.append("text", pasteText);
    hasData = true;
  } else {
    if (!selectedFile) {
      showInputError("Please select a file to upload or paste text.");
      return;
    }
    formData.append("file", selectedFile);
    hasData = true;
  }

  if (!hasData) return;

  // Transition to Loading Screen
  showSection("loading-page");
  updateLoadingProgress(1, "Extracting text and cleaning document...");

  // Simulate animated pipeline step updates for UI feel
  const stepTimer1 = setTimeout(
    () =>
      updateLoadingProgress(2, "Running Natural Language Clause Classifier..."),
    1200,
  );
  const stepTimer2 = setTimeout(
    () =>
      updateLoadingProgress(3, "Evaluating Legal Risk and Heuristics Rules..."),
    2400,
  );
  const stepTimer3 = setTimeout(
    () =>
      updateLoadingProgress(
        4,
        "Synthesizing scores, plain English translations, and recommendations...",
      ),
    3600,
  );

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorDetails = await response.json();
      throw new Error(errorDetails.detail || "Server analysis failed.");
    }

    const data = await response.json();

    // Clean timers
    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    clearTimeout(stepTimer3);

    // Wait a slight fraction for smooth step completion visual
    updateLoadingProgress(4, "Compilation complete!");
    setTimeout(() => {
      renderAnalysisDashboard(data);
      showSection("results-page");
    }, 500);
  } catch (err) {
    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    clearTimeout(stepTimer3);

    console.error(err);
    backToLanding();
    showInputError(`Analysis failed: ${err.message}`);
  }
}

function updateLoadingProgress(stepIndex, statusText) {
  document.getElementById("loading-status-text").innerText = statusText;

  // Clear active/completed classes
  for (let i = 1; i <= 4; i++) {
    const item = document.getElementById(`step-${i}`);
    if (i < stepIndex) {
      item.className = "step-item completed";
    } else if (i === stepIndex) {
      item.className = "step-item active";
    } else {
      item.className = "step-item";
    }
  }
}

// --- DASHBOARD RENDERER ---
function renderAnalysisDashboard(report) {
  currentAnalysisReport = report;

  // 1. Overall Score & SVG Gauge
  const scoreVal = report.overall_score; // 0 - 10
  document.getElementById("risk-score-value").innerText = scoreVal.toFixed(1);

  // Risk Arc Gauge calculations
  // Gauge dasharray is 125.6 (representing the half circle arc length)
  // Offset ranges from 125.6 (0% fill) to 0 (100% fill)
  const fillPercent = scoreVal / 10.0;
  const dashOffset = 125.6 - 125.6 * fillPercent;
  const fillArc = document.getElementById("gauge-fill-arc");
  fillArc.style.strokeDashoffset = dashOffset;

  // Color code the gauge and label
  let label = "Safe";
  let arcColor = "hsl(158deg 64% 52%)";
  let labelClass = "text-green";

  if (scoreVal >= 7.5) {
    label = "Critical Risk";
    arcColor = "hsl(0deg 84% 60%)";
    labelClass = "text-red";
  } else if (scoreVal >= 5.0) {
    label = "High Risk";
    arcColor = "hsl(25deg 95% 53%)";
    labelClass = "text-orange";
  } else if (scoreVal >= 2.5) {
    label = "Medium Risk";
    arcColor = "hsl(48deg 96% 53%)";
    labelClass = "text-yellow";
  }

  fillArc.style.stroke = arcColor;
  const labelSpan = document.getElementById("risk-score-label");
  labelSpan.innerText = label;
  labelSpan.className = `gauge-label ${labelClass}`;

  // Quick statistics
  document.getElementById("estimated-time").innerText =
    `${report.readability.reading_time_minutes}m`;
  document.getElementById("reliability-score").innerText =
    `${report.confidence}%`;

  // 2. Executive Summary
  document.getElementById("executive-summary-text").innerText = report.summary;



  // 4. Six Primary Categories
  const categories = [
    "Privacy",
    "Financial",
    "Legal Rights",
    "User Control",
    "Security",
    "Transparency",
  ];
  categories.forEach((cat) => {
    const score = report.category_scores[cat] || 0.0;
    document.getElementById(`cat-score-${cat}`).innerText = score.toFixed(1);

    // Progress fill
    const fill = document.getElementById(`cat-progress-${cat}`);
    fill.style.width = `${score * 10}%`;

    // Badges
    const badge = document.getElementById(`cat-badge-${cat}`);
    badge.innerText =
      score >= 7.5
        ? "Critical"
        : score >= 5.0
          ? "High"
          : score >= 2.5
            ? "Medium"
            : "Low";
    badge.className =
      `badge-mini ` +
      (score >= 7.5
        ? "badge-red"
        : score >= 5.0
          ? "badge-orange"
          : score >= 2.5
            ? "badge-yellow"
            : "badge-green");
  });





  // 7. Highlights Slide Deck (Critical / High Risks)
  setupHighlights(report.risk_items);

  // 8. Detailed Clause Cards & Search Init
  document.getElementById("clause-search").value = "";
  document.getElementById("severity-filter").value = "all";
  renderClauseCards(report.risk_items, report.positive_features);
}




// --- DANGEROUS CLAUSES CAROUSEL HIGHLIGHTS ---
function setupHighlights(riskItems) {
  highlightsList = riskItems.filter(
    (r) => r.severity === "Critical" || r.severity === "High",
  );
  currentHighlightIndex = 0;

  const track = document.getElementById("highlights-carousel");
  const nav = document.getElementById("carousel-nav");

  if (highlightsList.length === 0) {
    track.innerHTML = `
            <div class="carousel-slide empty-slide">
                <i class="fa-solid fa-circle-check text-green" style="font-size: 2.5rem; margin-bottom: 0.5rem;"></i>
                <p>No Critical or High Risk clauses highlighted. This is a very clean contract!</p>
            </div>
        `;
    nav.style.display = "none";
    return;
  }

  track.innerHTML = "";
  highlightsList.forEach((item) => {
    const slide = document.createElement("div");
    slide.className = "carousel-slide";
    slide.innerHTML = `
            <div class="carousel-slide-content">
                <div class="highlight-header">
                    <span class="highlight-title text-red"><i class="fa-solid fa-triangle-exclamation mr-2"></i> ${item.name}</span>
                    <span class="badge badge-red">${item.severity} Risk</span>
                </div>
                <div class="highlight-clause-text">"${item.original_clause}"</div>
                <div class="highlight-explanation"><strong>Plain Meaning:</strong> ${item.plain_english}</div>
                <div class="highlight-why-matters"><strong>Why it Matters:</strong> ${item.why_it_matters}</div>
            </div>
        `;
    track.appendChild(slide);
  });

  nav.style.display = "flex";
  updateCarouselPosition();
}

function moveCarousel(direction) {
  currentHighlightIndex += direction;
  if (currentHighlightIndex < 0) {
    currentHighlightIndex = highlightsList.length - 1;
  } else if (currentHighlightIndex >= highlightsList.length) {
    currentHighlightIndex = 0;
  }
  updateCarouselPosition();
}

function updateCarouselPosition() {
  const track = document.getElementById("highlights-carousel");
  const indicator = document.getElementById("carousel-indicator-text");

  track.style.transform = `translateX(-${currentHighlightIndex * 100}%)`;
  indicator.innerText = `${currentHighlightIndex + 1} / ${highlightsList.length}`;
}

// --- CLAUSE CARDS & LIVE FILTERING ---
let cachedCombinedClauses = [];

function renderClauseCards(risks, positives) {
  cachedCombinedClauses = [];

  // Normalize and combine all findings
  risks.forEach((r) => {
    cachedCombinedClauses.push({
      ...r,
      isPositive: false,
    });
  });

  positives.forEach((p) => {
    cachedCombinedClauses.push({
      ...p,
      isPositive: true,
      severity: "Safe", // Positive cards have "Safe" severity in filters
    });
  });

  // Sort items: Critical -> High -> Medium -> Low -> Protections (Safe)
  const severityWeight = { Critical: 5, High: 4, Medium: 3, Low: 2, Safe: 1 };
  cachedCombinedClauses.sort(
    (a, b) => severityWeight[b.severity] - severityWeight[a.severity],
  );

  filterClauses(); // Run initial filter render
}

function filterClauses() {
  const searchQuery = document
    .getElementById("clause-search")
    .value.toLowerCase();
  const severityFilter = document.getElementById("severity-filter").value;
  const container = document.getElementById("clause-cards-container");

  container.innerHTML = "";
  let matchesFound = 0;

  cachedCombinedClauses.forEach((item, index) => {
    // Apply Filters
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery) ||
      item.original_clause.toLowerCase().includes(searchQuery) ||
      item.plain_english.toLowerCase().includes(searchQuery);

    let matchesSeverity = true;
    if (severityFilter === "Critical") {
      matchesSeverity = item.severity === "Critical";
    } else if (severityFilter === "High") {
      matchesSeverity =
        item.severity === "Critical" || item.severity === "High";
    } else if (severityFilter === "Medium") {
      matchesSeverity =
        item.severity === "Critical" ||
        item.severity === "High" ||
        item.severity === "Medium";
    } else if (severityFilter === "Low") {
      matchesSeverity = item.severity !== "Safe"; // Everything except protections
    } else if (severityFilter === "Safe") {
      matchesSeverity = item.severity === "Safe";
    }

    if (matchesSearch && matchesSeverity) {
      matchesFound++;

      // Determine severity colors and icons
      let sevBadgeClass = "badge-green";
      let leftBorderClass = "clause-risk-safe";
      let leftIcon = "fa-circle-check";

      if (!item.isPositive) {
        if (item.severity === "Critical") {
          sevBadgeClass = "badge-red";
          leftBorderClass = "clause-risk-critical";
          leftIcon = "fa-circle-xmark";
        } else if (item.severity === "High") {
          sevBadgeClass = "badge-red";
          leftBorderClass = "clause-risk-high";
          leftIcon = "fa-triangle-exclamation";
        } else if (item.severity === "Medium") {
          sevBadgeClass = "badge-orange";
          leftBorderClass = "clause-risk-medium";
          leftIcon = "fa-circle-exclamation";
        } else {
          sevBadgeClass = "badge-yellow";
          leftBorderClass = "clause-risk-low";
          leftIcon = "fa-circle-info";
        }
      }

      const card = document.createElement("div");
      card.id = `clause-card-${index}`;
      card.className = `clause-detail-card ${leftBorderClass}`;

      card.innerHTML = `
                <div class="clause-card-header" onclick="toggleClauseCard(${index})">
                    <div class="clause-header-title">
                        <i class="fa-solid ${leftIcon}"></i>
                        <h4>${item.name}</h4>
                    </div>
                    <div class="clause-badges">
                        <span class="badge ${sevBadgeClass}">${item.severity}</span>
                        ${item.needs_review ? `<span class="badge badge-orange"><i class="fa-solid fa-user-pen"></i> Needs Review</span>` : ""}
                        <button class="btn-toggle-expand"><i class="fa-solid fa-chevron-down"></i></button>
                    </div>
                </div>
                <div class="clause-card-body">
                    <h5>Original Clause</h5>
                    <div class="original-clause-box">"${item.original_clause}"</div>
                    
                    <div class="clause-analysis-grid">
                        <div class="analysis-col">
                            <h5>Plain Meaning</h5>
                            <p>${item.plain_english}</p>
                        </div>
                        <div class="analysis-col">
                            <h5>Why it Matters & Recommendation</h5>
                            <p class="mb-4">${item.why_it_matters}</p>
                            <h5>Recommendation</h5>
                            <p>${item.recommendation}</p>
                        </div>
                    </div>
                </div>
            `;

      container.appendChild(card);
    }
  });

  if (matchesFound === 0) {
    container.innerHTML = `
            <div class="card text-center p-5 text-muted">
                <i class="fa-solid fa-magnifying-glass-minus mb-2" style="font-size: 2rem;"></i>
                <p>No clauses match your search or filter options.</p>
            </div>
        `;
  }
}

function toggleClauseCard(index) {
  const card = document.getElementById(`clause-card-${index}`);
  if (card) {
    card.classList.toggle("expanded");
  }
}

function scrollToCategory(categoryName) {
  // Select filter and query detailed breakdown
  const severityDropdown = document.getElementById("severity-filter");
  const searchBar = document.getElementById("clause-search");

  searchBar.value = categoryName;
  severityDropdown.value = "all";
  filterClauses();

  // Smooth scroll down to detailed breakdowns section
  const section = document.querySelector(".clause-analysis-section");
  if (section) {
    section.scrollIntoView({ behavior: "smooth" });
  }
}