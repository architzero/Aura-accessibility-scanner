document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const scanId = params.get("scanId");
    const resultsContainer = document.getElementById("results-container");
    const loadingState = document.getElementById("loading-state");

    if (!scanId) {
        window.location.href = "dashboard.html";
        return;
    }

    try {
        const response = await authenticatedFetch(`/scan/results/${scanId}`);
        if (!response.ok) throw new Error("Could not fetch scan results.");
        const result = await response.json();
        
        const projectResponse = await authenticatedFetch(`/projects/${result.projectId}`);
        if (!projectResponse.ok) throw new Error("Could not load project details.");
        const project = await projectResponse.json();

        loadingState.style.display = 'none';
        displayResults(result, project.url);

    } catch (error) {
        console.error("Error loading results:", error);
        loadingState.innerHTML = `<h2>Error</h2><p>${error.message}</p><a href="dashboard.html">Go back</a>`;
    }
});

function displayResults(result, url) {
    const resultsContainer = document.getElementById("results-container");

    // Summary Card
    const summaryCard = document.createElement('section');
    summaryCard.className = 'card';
    summaryCard.innerHTML = `
        <h2>Summary</h2>
        <p><strong>Accessibility Score:</strong> <span style="font-size: 1.5rem; font-weight: bold;">${result.accessibilityScore}</span> / 100</p>
        <p><strong>URL Scanned:</strong> <a href="${url}" target="_blank">${url}</a></p>
        <p><strong>Date:</strong> ${new Date(result.createdAt).toLocaleString()}</p>
    `;

    // Screenshot Card
    const screenshotCard = document.createElement('section');
    screenshotCard.className = 'card';
    const screenshotUrl = `${API_BASE_URL}/${result.screenshotUrl}`;
    screenshotCard.innerHTML = `
        <h2>Screenshot</h2>
        <img src="${screenshotUrl}" alt="Page Screenshot" style="width: 100%; border: 1px solid var(--border-color); border-radius: 4px;" 
             onerror="this.parentElement.style.display='none';">
    `;

    // Issues Card
    const issuesCard = document.createElement('section');
    issuesCard.className = 'card';
    let issuesHTML = `<h2>All Issues Found (${result.issues.length})</h2><ul id="issues-list">`;
    if (result.issues.length > 0) {
        result.issues.forEach(issue => {
            issuesHTML += `
                <li>
                    <div class="issue-info">
                        <strong>${issue.guideline}</strong>
                        <span>${issue.description}</span>
                        <code style="margin-top: 0.5rem; display: block;">${escapeHtml(issue.element)}</code>
                    </div>
                </li>
            `;
        });
    } else {
        issuesHTML += "<li>No issues found! Great job!</li>";
    }
    issuesHTML += '</ul>';
    issuesCard.innerHTML = issuesHTML;

    // Suggestions Card
    const suggestionsCard = document.createElement('section');
    suggestionsCard.className = 'card';
    suggestionsCard.id = 'suggestions-card';

    let suggestionsContent = '';

    // AI Suggestions
    if (result.aiSuggestions && result.aiSuggestions.length > 0) {
        suggestionsContent += '<h3>AI-Powered Suggestions</h3><ul>';
        result.aiSuggestions.forEach(text => {
            if (text.startsWith('AI Suggestion for readability:')) {
                const parts = text.split('"');
                suggestionsContent += `
                    <li>
                        <span>${escapeHtml(parts[0])}</span>
                        <blockquote class="text-preview">"${escapeHtml(parts[1])}"</blockquote>
                        <span>${escapeHtml(parts[2] || '')}</span>
                    </li>
                `;
            } else {
                suggestionsContent += `<li>${escapeHtml(text)}</li>`;
            }
        });
        suggestionsContent += '</ul>';
    }

    // General Fixes
    if (result.genericSuggestions && result.genericSuggestions.length > 0) {
        suggestionsContent += '<h3>General Fixes</h3><ul>';
        result.genericSuggestions.forEach(text => {
            suggestionsContent += `<li>${escapeHtml(text)}</li>`;
        });
        suggestionsContent += '</ul>';
    }

    if (suggestionsContent) {
        suggestionsCard.innerHTML = '<h2>Suggestions</h2>' + suggestionsContent;
    }

    // Append cards
    resultsContainer.appendChild(summaryCard);
    resultsContainer.appendChild(screenshotCard);
    resultsContainer.appendChild(issuesCard);
    if (suggestionsContent) {
        resultsContainer.appendChild(suggestionsCard);
    }
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
