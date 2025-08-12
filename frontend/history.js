document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const projectId = params.get("projectId");
    const historyList = document.getElementById("history-list");
    const modal = document.getElementById('confirm-modal');
    const modalText = document.getElementById('modal-text');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    let itemToDeleteId = null;
    let itemToDeleteElement = null;

    if (!projectId) {
        window.location.href = "dashboard.html";
        return;
    }

    function showModal(id, element) {
        itemToDeleteId = id;
        itemToDeleteElement = element;
        modalText.textContent = `Are you sure you want to delete this scan result?`;
        modal.style.display = 'flex';
        setTimeout(() => modal.style.opacity = 1, 10);
    }

    function hideModal() {
        modal.style.opacity = 0;
        setTimeout(() => modal.style.display = 'none', 200);
        itemToDeleteId = null;
        itemToDeleteElement = null;
    }

    modalCancelBtn.addEventListener('click', hideModal);

    modalConfirmBtn.addEventListener('click', async () => {
        if (!itemToDeleteId) return;
        try {
            const response = await authenticatedFetch(`/scan/results/${itemToDeleteId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error("Failed to delete scan.");
            itemToDeleteElement.remove();
        } catch (error) {
            console.error(error);
            alert("Could not delete the scan result.");
        } finally {
            hideModal();
        }
    });

    try {
        const projectRes = await authenticatedFetch(`/projects/${projectId}`);
        if (!projectRes.ok) throw new Error("Could not fetch project details.");
        const project = await projectRes.json();
        document.getElementById("project-name-header").textContent = `Scan History for "${project.projectName}"`;

        const historyRes = await authenticatedFetch(`/projects/${projectId}/history`);
        if (!historyRes.ok) throw new Error("Could not fetch scan history.");
        const history = await historyRes.json();
        
        if (history.length === 0) {
            historyList.innerHTML = '<li>No scans have been run for this project yet.</li>';
        } else {
            history.forEach(scan => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div class="project-info">
                        <strong>Score: ${scan.accessibilityScore}</strong>
                        <span>Scanned on ${new Date(scan.createdAt).toLocaleString()}</span>
                    </div>
                    <div class="project-actions">
                        <a href="results.html?scanId=${scan._id}" class="button-secondary">View Details</a>
                        <button class="delete-scan-button" data-id="${scan._id}" title="Delete Scan">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    </div>
                `;
                historyList.appendChild(li);
            });
        }
    } catch (error) {
        console.error(error);
        historyList.innerHTML = `<li>Error loading scan history: ${error.message}</li>`;
    }

    historyList.addEventListener('click', async (e) => {
        const targetButton = e.target.closest('button');
        if (targetButton && targetButton.classList.contains('delete-scan-button')) {
            const scanId = targetButton.dataset.id;
            const listItem = targetButton.closest('li');
            showModal(scanId, listItem);
        }
    });
});