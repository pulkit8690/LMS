const API_BASE_URL = "http://localhost:5000/payments";
const token = localStorage.getItem("token");

// ✅ Load Unpaid Fines
async function loadFines() {
    const response = await fetch(`${API_BASE_URL}/view`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const fines = await response.json();
    let fineList = document.getElementById("fineList");
    fineList.innerHTML = ""; // Clear previous results

    fines.forEach(fine => {
        let row = `
            <tr class="border-b">
                <td class="p-2 text-red-500">₹${fine.amount}</td>
                <td class="p-2">${fine.payment_status}</td>
                <td class="p-2">
                    ${fine.payment_status === "pending" ? `<button onclick="payFine(${fine.id}, ${fine.amount})" class="bg-green-500 text-white px-3 py-1 rounded">Pay Now</button>` : "✔️ Paid"}
                </td>
            </tr>
        `;
        fineList.innerHTML += row;
    });
}

// ✅ Pay Fine
async function payFine(fineId, amount) {
    const response = await fetch(`${API_BASE_URL}/create-payment`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ amount })
    });

    const data = await response.json();
    if (data.order_id) {
        alert("Redirecting to payment gateway...");
        // You can integrate Razorpay or Stripe here
        loadFines();
    } else {
        alert("Payment failed!");
    }
}

loadFines();
