// Dynamically determine API base URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://127.0.0.1:8000"
    : `${window.location.protocol}//${window.location.hostname}:8000`;

async function authenticatedFetch(endpoint, options = {}) {
    const token = localStorage.getItem("aura_token");
    if (!token) {
        window.location.href = "index.html";
        throw new Error("No token found. Please log in.");
    }

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem("aura_token");
            window.location.href = "index.html";
            throw new Error("Session expired. Please log in again.");
        }

        return response;
    } catch (error) {
        if (error.message.includes("Failed to fetch")) {
            throw new Error("Cannot connect to server. Please check if the backend is running.");
        }
        throw error;
    }
}