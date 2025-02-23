const API_BASE_URL = "http://localhost:5000/auth";
const token = localStorage.getItem("token");

// ✅ Load Profile
async function loadProfile() {
    const response = await fetch(`${API_BASE_URL}/profile`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const user = await response.json();
    document.getElementById("name").value = user.name;
    document.getElementById("email").value = user.email;
}

// ✅ Update Profile
async function updateProfile() {
    const name = document.getElementById("name").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_BASE_URL}/profile/edit`, {
        method: "PUT",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ name, password })
    });

    const data = await response.json();
    alert(data.message);
}

// ✅ Logout
function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

loadProfile();
