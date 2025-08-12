document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("aura_token")) {
        window.location.href = "dashboard.html";
        return;
    }

    const authCard = document.getElementById("auth-card");
    const authForm = document.getElementById("auth-form");
    const formTitle = document.getElementById("form-title");
    const authButton = document.getElementById("auth-button");
    const toggleLink = document.getElementById("toggle-link");
    
    let isLoginMode = true;

    toggleLink.addEventListener("click", (e) => {
        e.preventDefault();
        isLoginMode = !isLoginMode;
        
        authForm.reset();
        document.getElementById("auth-error").textContent = "";
        document.getElementById("auth-success").textContent = "";

        authCard.style.opacity = 0;
        setTimeout(() => {
            if (isLoginMode) {
                formTitle.textContent = "Login";
                authButton.textContent = "Login";
                toggleLink.innerHTML = "Don't have an account? <b>Register.</b>";
            } else {
                formTitle.textContent = "Register";
                authButton.textContent = "Create Account";
                toggleLink.innerHTML = "Already have an account? <b>Login.</b>";
            }
            authCard.style.opacity = 1;
        }, 200);
    });

    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("auth-email").value;
        const password = document.getElementById("auth-password").value;
        const errorEl = document.getElementById("auth-error");
        const successEl = document.getElementById("auth-success");
        errorEl.textContent = "";
        successEl.textContent = "";

        if (isLoginMode) {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);
            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData,
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Login failed");
                localStorage.setItem("aura_token", data.access_token);
                window.location.href = "dashboard.html";
            } catch (error) {
                errorEl.textContent = error.message;
            }
        } else {
            try {
                const response = await fetch(`${API_BASE_URL}/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password }),
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Registration failed");
                successEl.textContent = "Registration successful! Please login.";
                toggleLink.click();
            } catch (error) {
                errorEl.textContent = error.message;
            }
        }
    });
});