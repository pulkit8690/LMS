const API_BASE_URL = "http://localhost:5000/books";
const token = localStorage.getItem("token");

// ✅ Fetch Books & Display
async function loadBooks() {
    const response = await fetch(`${API_BASE_URL}/`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const books = await response.json();
    let bookList = document.getElementById("bookList");
    bookList.innerHTML = ""; // Clear previous results

    books.forEach(book => {
        let row = `
            <tr class="border-b">
                <td class="p-2">${book.title}</td>
                <td class="p-2">${book.author}</td>
                <td class="p-2">${book.isbn}</td>
                <td class="p-2 text-center">${book.copies_available > 0 ? "✅" : "❌"}</td>
                <td class="p-2 text-center">
                    ${book.copies_available > 0 ? `<button onclick="borrowBook(${book.id})" class="bg-green-500 text-white px-3 py-1 rounded">Borrow</button>` : ""}
                </td>
            </tr>
        `;
        bookList.innerHTML += row;
    });
}

// ✅ Borrow a Book (Student)
async function borrowBook(bookId) {
    const response = await fetch(`${API_BASE_URL}/borrow/${bookId}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" }
    });

    const data = await response.json();
    alert(data.message);
    loadBooks(); // Refresh book list
}

loadBooks();
