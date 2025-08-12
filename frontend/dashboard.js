document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("aura_token");
    if (!token) {
        window.location.href = "index.html";
        return;
    }
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        document.getElementById("user-email").textContent = payload.sub;
    } catch(e) { console.error("Could not decode token", e); }
    
    const projectsList = document.getElementById("projects-list");
    const newProjectForm = document.getElementById("new-project-form");
    const logoutButton = document.getElementById("logout-button");
    const modal = document.getElementById('confirm-modal');
    const modalText = document.getElementById('modal-text');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    let itemToDeleteId = null;

    logoutButton.addEventListener("click", () => {
        localStorage.removeItem("aura_token");
        window.location.href = "index.html";
    });

    function showModal(id, type) {
        itemToDeleteId = id;
        modalText.textContent = `Are you sure you want to delete this ${type}? This action cannot be undone.`;
        modal.style.display = 'flex';
        setTimeout(() => modal.style.opacity = 1, 10);
    }

    function hideModal() {
        modal.style.opacity = 0;
        setTimeout(() => modal.style.display = 'none', 200);
        itemToDeleteId = null;
    }

    modalCancelBtn.addEventListener('click', hideModal);

    modalConfirmBtn.addEventListener('click', async () => {
        if (!itemToDeleteId) return;
        try {
            const response = await authenticatedFetch(`/projects/${itemToDeleteId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error("Failed to delete project.");
            fetchProjects();
        } catch (error) {
            console.error(error);
            alert("Could not delete the project.");
        } finally {
            hideModal();
        }
    });

    async function fetchProjects() {
        try {
            const response = await authenticatedFetch("/projects");
            if (!response.ok) throw new Error("Could not fetch projects.");
            
            const projects = await response.json();
            projectsList.innerHTML = ""; 

            if (projects.length === 0) {
                projectsList.innerHTML = "<li>No projects yet. Create one!</li>";
            } else {
                projects.forEach(project => {
                    const li = document.createElement("li");
                    li.innerHTML = `
                        <div class="project-info">
                            <strong>${project.projectName}</strong>
                            <span>${project.url}</span>
                        </div>
                        <div class="project-actions">
                            <a href="history.html?projectId=${project._id}" class="button-secondary">View History</a>
                            <button class="scan-button" data-id="${project._id}">Scan Now</button>
                            <button class="delete-project-button" data-id="${project._id}" title="Delete Project">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    `;
                    projectsList.appendChild(li);
                });
            }
        } catch (error) {
            console.error(error);
            projectsList.innerHTML = "<li>Error loading projects.</li>";
        }
    }
    
    newProjectForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const projectName = document.getElementById("project-name").value;
        const url = document.getElementById("project-url").value;
        const errorEl = document.getElementById("form-error");
        errorEl.textContent = "";

        try {
            const response = await authenticatedFetch("/projects", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ projectName, url })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail);
            
            newProjectForm.reset();
            fetchProjects();
        } catch (error) {
            console.error(error);
            errorEl.textContent = error.message;
        }
    });

    projectsList.addEventListener("click", async (e) => {
        const targetButton = e.target.closest('button');
        if (!targetButton) return;

        if (targetButton.classList.contains("scan-button")) {
            const projectId = targetButton.dataset.id;
            targetButton.textContent = "Scanning...";
            targetButton.disabled = true;
            try {
                const response = await authenticatedFetch(`/scan/${projectId}`, { method: "POST" });
                const result = await response.json();
                if (!response.ok) throw new Error(result.detail);
                window.location.href = `results.html?scanId=${result._id}`;
            } catch (error) {
                console.error(error);
                alert("An error occurred during the scan: " + error.message);
                targetButton.textContent = "Scan Now";
                targetButton.disabled = false;
            }
        }
        
        if (targetButton.classList.contains("delete-project-button")) {
            const projectId = targetButton.dataset.id;
            showModal(projectId, 'project');
        }
    });

    fetchProjects();
});