const API_BASE_URL = "http://localhost:5000/students";

async function fetchStudentStats() {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE_URL}/books/borrowed`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await response.json();
    document.getElementById("booksBorrowed").innerText = data.length || 0;

    let dueBooks = data.filter(book => new Date(book.due_date) < new Date()).length;
    document.getElementById("dueBooks").innerText = dueBooks || 0;

    let pendingFines = data.reduce((acc, book) => acc + (book.fine_due || 0), 0);
    document.getElementById("pendingFines").innerText = `₹${pendingFines}`;
}

document.getElementById("logout")?.addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "login.html";
});
checkAuth();
fetchStudentStats();
