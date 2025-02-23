const API_BASE_URL = "http://localhost:5000/admin";

async function fetchAdminStats() {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE_URL}/reports`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await response.json();
    document.getElementById("totalBooks").innerText = data.total_books || 0;
    document.getElementById("totalStudents").innerText = data.total_students || 0;
    document.getElementById("borrowedBooks").innerText = data.borrowed_books || 0;
}

document.getElementById("logout")?.addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "login.html";
});
checkAuth();
fetchAdminStats();
