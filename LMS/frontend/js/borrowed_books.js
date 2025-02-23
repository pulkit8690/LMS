const API_BASE_URL = "http://localhost:5000/students/books/borrowed";
const token = localStorage.getItem("token");

// ✅ Load Borrowed Books
async function loadBorrowedBooks() {
    const response = await fetch(API_BASE_URL, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const books = await response.json();
    let borrowedList = document.getElementById("borrowedList");
    borrowedList.innerHTML = ""; // Clear previous data

    books.forEach(book => {
        let row = `
            <tr class="border-b">
                <td class="p-2">${book.title}</td>
                <td class="p-2">${book.due_date}</td>
                <td class="p-2 text-red-500">${book.fine_due ? `₹${book.fine_due}` : "No Fine"}</td>
                <td class="p-2">
                    <button onclick="returnBook(${book.id})" class="bg-red-500 text-white px-3 py-1 rounded">Return</button>
                </td>
            </tr>
        `;
        borrowedList.innerHTML += row;
    });
}

// ✅ Return a Book
async function returnBook(bookId) {
    const response = await fetch(`http://localhost:5000/students/books/return/${bookId}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" }
    });

    const data = await response.json();
    alert(data.message);
    loadBorrowedBooks(); // Refresh list
}

loadBorrowedBooks();
