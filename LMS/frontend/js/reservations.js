const API_BASE_URL = "http://localhost:5000/reservations";
const token = localStorage.getItem("token");

// ✅ Load Reservations
async function loadReservations() {
    const response = await fetch(`${API_BASE_URL}/view`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const reservations = await response.json();
    let reservationList = document.getElementById("reservationList");
    reservationList.innerHTML = ""; // Clear previous results

    reservations.forEach(reservation => {
        let row = `
            <tr class="border-b">
                <td class="p-2">${reservation.book_title}</td>
                <td class="p-2">${new Date(reservation.reserved_at).toLocaleDateString()}</td>
                <td class="p-2">${reservation.status}</td>
                <td class="p-2">
                    <button onclick="cancelReservation(${reservation.id})" class="bg-red-500 text-white px-3 py-1 rounded">Cancel</button>
                </td>
            </tr>
        `;
        reservationList.innerHTML += row;
    });
}

// ✅ Cancel Reservation
async function cancelReservation(reservationId) {
    const response = await fetch(`${API_BASE_URL}/cancel/${reservationId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await response.json();
    alert(data.message);
    loadReservations(); // Refresh list
}

loadReservations();
