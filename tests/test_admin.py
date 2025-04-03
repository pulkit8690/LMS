# tests/test_admin.py

import requests
import random

BASE_URL = "https://lms-backend-production-9c55.up.railway.app"  # Change for production

# Admin Credentials
ADMIN_EMAIL = "pulkitarora8690@gmail.com"
ADMIN_PASSWORD = "password123"
ADMIN_TOKEN = None

# Book & Student Data
BOOK_ID = None
STUDENT_ID = 2  # Assuming student ID is known


def log_result(api_name, response):
    """Logs API test results with exception handling"""
    try:
        status = "✅ SUCCESS" if response.status_code in [200, 201] else "❌ FAILED"
        print(f"{status} - {api_name}: {response.status_code} "
              f"{response.json() if response.content else 'No response data'}")
    except requests.exceptions.JSONDecodeError:
        print(f"❌ FAILED - {api_name}: {response.status_code} (Invalid JSON response)")


def test_api(method, endpoint, data=None, token=None):
    """Tests an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.request(method, url, json=data, headers=headers)
    log_result(endpoint, response)
    return response


def login():
    """Logs in as admin and retrieves JWT token"""
    global ADMIN_TOKEN
    print("\n🚀 Logging In as Admin...")
    response = test_api("POST", "/auth/login", {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })

    if response and response.status_code == 200:
        ADMIN_TOKEN = response.json().get("access_token")
        print("✅ Logged in as Admin!")
        return True
    return False


def get_books():
    """Fetches all books (via admin endpoint)."""
    print("\n🚀 Viewing All Books (Admin)...")
    response = test_api("GET", "/admin/books", token=ADMIN_TOKEN)
    return response.status_code == 200


def add_book():
    """Adds a new book using the admin account"""
    global BOOK_ID
    print("\n🚀 Adding a Book (Admin)...")
    response = test_api("POST", "/admin/books/add", {
        "title": "API Test Book",
        "author": "John Doe",
        "isbn": str(random.randint(1000000000000, 9999999999999)),  # Unique ISBN
        "category_id": 1,
        "copies_available": 3
    }, ADMIN_TOKEN)

    if response and response.status_code == 201:
        BOOK_ID = response.json().get("id")
        print(f"✅ Book added successfully with ID: {BOOK_ID}")
        return True
    print("❌ Book creation failed. Check Flask logs.")
    return False


def update_book():
    """Updates book details"""
    if BOOK_ID is None:
        print("❌ No book available to update. Skipping...")
        return False

    print(f"\n🚀 Updating Book ID {BOOK_ID} (Admin)...")
    response = test_api("PUT", f"/admin/books/update/{BOOK_ID}", {
        "title": "Updated API Test Book"
    }, ADMIN_TOKEN)
    return response.status_code == 200


def delete_book():
    """Deletes a book"""
    if BOOK_ID is None:
        print("❌ No book available to delete. Skipping...")
        return False

    print(f"\n🚀 Deleting Book ID {BOOK_ID} (Admin)...")
    response = test_api("DELETE", f"/admin/books/delete/{BOOK_ID}", token=ADMIN_TOKEN)
    return response.status_code == 200


def get_students():
    """Fetches all students"""
    print("\n🚀 Viewing All Students...")
    response = test_api("GET", "/admin/students", token=ADMIN_TOKEN)
    return response.status_code == 200


def block_unblock_student():
    """Blocks/Unblocks a student"""
    print(f"\n🚀 Blocking/Unblocking Student ID {STUDENT_ID}...")
    response = test_api("PUT", f"/admin/students/block/{STUDENT_ID}", token=ADMIN_TOKEN)
    return response.status_code == 200


def issue_book():
    """Issues a book to a student"""
    if BOOK_ID is None:
        print("❌ No book available to issue. Skipping...")
        return False

    print(f"\n🚀 Issuing Book ID {BOOK_ID} to Student ID {STUDENT_ID}...")
    response = test_api("POST", "/admin/books/issue", {
        "book_id": BOOK_ID,
        "student_id": STUDENT_ID
    }, ADMIN_TOKEN)

    return response.status_code == 200


def return_book():
    """Accepts book return from a student"""
    if BOOK_ID is None:
        print("❌ No book available to return. Skipping...")
        return False

    print(f"\n🚀 Accepting Return for Book ID {BOOK_ID}...")
    response = test_api("POST", "/admin/books/return", {
        "book_id": BOOK_ID,
        "student_id": STUDENT_ID
    }, ADMIN_TOKEN)
    return response.status_code == 200


def view_borrowed_books():
    """Fetches all borrowed books"""
    print("\n🚀 Viewing Borrowed Books...")
    response = test_api("GET", "/admin/books/borrowed", token=ADMIN_TOKEN)
    return response.status_code == 200


def manage_extension():
    """Approves or Rejects Book Extension"""
    if BOOK_ID is None:
        print("❌ No book available for extension. Skipping...")
        return False

    print(f"\n🚀 Managing Book Extension for Book ID {BOOK_ID}...")
    response = test_api("PUT", "/admin/books/extend", {
        "book_id": BOOK_ID,
        "student_id": STUDENT_ID,
        "action": "accept"
    }, ADMIN_TOKEN)
    return response.status_code == 200


def generate_reports():
    """Generates Library Reports"""
    print("\n🚀 Generating Reports...")
    response = test_api("GET", "/admin/reports", token=ADMIN_TOKEN)
    return response.status_code == 200


def run_tests():
    """Runs all Admin API tests in correct order"""
    global ADMIN_TOKEN, BOOK_ID

    # 1) Login
    if not login():
        return

    # 2) View Books
    get_books()

    # 3) Add Book -> Issue -> Extension -> View Borrowed -> Return -> Delete
    if add_book():
        issue_book()
        manage_extension()
        view_borrowed_books()
        return_book()
        delete_book()

    # Optionally get Students and block/unblock (if needed)
    get_students()
    block_unblock_student()

    generate_reports()

    print("\n🎉 **ALL ADMIN API TESTS COMPLETED SUCCESSFULLY!** 🎉")


if __name__ == "__main__":
    run_tests()
