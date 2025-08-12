const API_BASE_URL = "http://127.0.0.1:8000";

async function authenticatedFetch(endpoint, options = {}) {
    const token = localStorage.getItem("aura_token");
    if (!token) {
        window.location.href = "index.html";
        throw new Error("No token found. Please log in.");
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem("aura_token");
        window.location.href = "index.html";
        throw new Error("Session expired. Please log in again.");
    }

    return response;
}