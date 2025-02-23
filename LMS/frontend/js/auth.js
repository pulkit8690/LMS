const API_BASE_URL = "http://localhost:5000/auth"; // Adjust based on your backend URL

// ✅ Handle Login
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (response.ok) {
        localStorage.setItem("token", data.access_token);
        alert("Login successful!");
        window.location.href = data.role === "admin" ? "dashboard_admin.html" : "dashboard_student.html";
    } else {
        document.getElementById("error").textContent = data.error;
        document.getElementById("error").classList.remove("hidden");
    }
});


// ✅ Handle Signup
document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    const response = await fetch(`${API_BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role })
    });

    const data = await response.json();
    if (response.ok) {
        alert("Signup successful! Please log in.");
        window.location.href = "login.html";
    } else {
        document.getElementById("error").textContent = data.error;
        document.getElementById("error").classList.remove("hidden");
    }
});


async function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "error.html?type=403"; // Redirect to unauthorized error page
    }
}

// Call this function on protected pages
checkAuth();

