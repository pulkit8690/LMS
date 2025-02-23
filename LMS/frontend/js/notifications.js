const API_BASE_URL = "http://localhost:5000/notifications";
const token = localStorage.getItem("token");

// ✅ Load Notifications
async function loadNotifications() {
    const response = await fetch(`${API_BASE_URL}/view`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const notifications = await response.json();
    let notificationList = document.getElementById("notificationList");
    notificationList.innerHTML = ""; // Clear previous results

    notifications.forEach(notification => {
        let row = `
            <tr class="border-b">
                <td class="p-2">${notification.message}</td>
                <td class="p-2">${notification.notification_type}</td>
                <td class="p-2">${new Date(notification.sent_at).toLocaleDateString()}</td>
            </tr>
        `;
        notificationList.innerHTML += row;
    });
}

loadNotifications();
