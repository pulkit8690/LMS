const API_BASE_URL = "http://127.0.0.1:5000"; // Change for production
const token = localStorage.getItem("token");

// ✅ Check if User is Logged In
function checkAuth(role) {
    if (!token) {
        window.location.href = "error.html?type=403"; // Unauthorized access
    }

    fetch(`${API_BASE_URL}/auth/profile`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(user => {
        if (role && user.role !== role) {
            window.location.href = "error.html?type=403"; // Role mismatch
        }
    })
    .catch(() => {
        window.location.href = "error.html?type=403"; // API Error
    });
}


// ✅ Logout User
function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

// ✅ Fetch API Helper Function
async function fetchData(endpoint, method = "GET", body = null) {
    const options = {
        method,
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" }
    };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return response.json();
}

// ✅ Format Date Utility
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

// ✅ Event Listener for Logout Button
document.getElementById("logout")?.addEventListener("click", logout);
