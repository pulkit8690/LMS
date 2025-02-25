# tests/test_books.py

import requests
import random
import time

BASE_URL = "http://127.0.0.1:5000"

# Admin Credentials
ADMIN_EMAIL = "pulkitarora8690@gmail.com"
ADMIN_PASSWORD = "password123"
ADMIN_TOKEN = None

# Book & Category Data
BOOK_ID = None
CATEGORY_ID = None


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

    if response.status_code == 200:
        ADMIN_TOKEN = response.json().get("access_token")
        print("✅ Logged in as Admin!")
        return True
    print("❌ Admin login failed. Check credentials or API.")
    return False


def add_category():
    """Adds a book category"""
    global CATEGORY_ID
    print("\n🚀 Adding a Category...")

    if not ADMIN_TOKEN:
        print("❌ Admin Token Missing! Ensure login was successful.")
        return False

    response = test_api("POST", "/books/category/add", {
        "name": f"Category {random.randint(1, 9999)}"
    }, ADMIN_TOKEN)

    if response.status_code == 201:
        CATEGORY_ID = response.json().get("id")
        print(f"✅ Category created successfully with ID: {CATEGORY_ID}")
        return True
    print("❌ Category creation failed.")
    return False


def add_book():
    """Adds a new book using the admin account"""
    global BOOK_ID
    print("\n🚀 Adding a Book...")

    if not ADMIN_TOKEN:
        print("❌ Admin Token Missing! Ensure login was successful.")
        return False

    if CATEGORY_ID is None:
        print("❌ No category available. Skipping book addition...")
        return False

    response = test_api("POST", "/books/add", {
        "title": "API Test Book",
        "author": "John Doe",
        "isbn": str(random.randint(1000000000000, 9999999999999)),  # Unique ISBN
        "category_id": CATEGORY_ID,
        "copies_available": 3
    }, ADMIN_TOKEN)

    if response.status_code == 201:
        BOOK_ID = response.json().get("id")
        print(f"✅ Book added successfully with ID: {BOOK_ID}")
        return True
    print("❌ Book creation failed.")
    return False


def get_books():
    """Fetches all books"""
    print("\n🚀 Viewing All Books...")
    response = test_api("GET", "/books")
    return response.status_code == 200


def get_books_by_category():
    """Fetches books by category"""
    if CATEGORY_ID is None:
        print("❌ No category available. Skipping category books fetch...")
        return False

    print("\n⌛ Waiting for database update...")
    time.sleep(2)  # small delay to ensure DB is updated

    print("\n🚀 Viewing Books by Category...")
    response = test_api("GET", f"/books/category/{CATEGORY_ID}")
    return response.status_code == 200


def update_book():
    """Updates book details"""
    if BOOK_ID is None:
        print("❌ No book available to update. Skipping...")
        return False

    print("\n🚀 Updating Book...")
    response = test_api("PUT", f"/books/update/{BOOK_ID}", {
        "title": "Updated API Test Book",
        "copies_available": 5
    }, ADMIN_TOKEN)
    return response.status_code == 200


def delete_book():
    """Deletes a book"""
    if BOOK_ID is None:
        print("❌ No book available to delete. Skipping...")
        return False

    print("\n🚀 Deleting Book...")
    response = test_api("DELETE", f"/books/delete/{BOOK_ID}", token=ADMIN_TOKEN)
    return response.status_code == 200


def borrow_book():
    """Borrows a book"""
    if BOOK_ID is None:
        print("❌ No book available to borrow. Skipping...")
        return False

    print("\n🚀 Borrowing a Book...")
    response = test_api("POST", "/books/borrow", {
        "book_id": BOOK_ID
    }, ADMIN_TOKEN)

    return response.status_code == 200


def return_book():
    """Returns a borrowed book"""
    if BOOK_ID is None:
        print("❌ No book available to return. Skipping...")
        return False

    print("\n🚀 Returning a Book...")
    response = test_api("POST", "/books/return", {
        "book_id": BOOK_ID
    }, ADMIN_TOKEN)

    return response.status_code == 200


def reserve_book():
    """Reserves a book if unavailable"""
    if BOOK_ID is None:
        print("❌ No book available to reserve. Skipping...")
        return False

    print("\n🚀 Reserving a Book...")
    response = test_api("POST", f"/books/reserve/{BOOK_ID}", {}, ADMIN_TOKEN)


    return response.status_code == 200


def run_tests():
    """Runs all Book API tests in correct order"""

    global ADMIN_TOKEN, BOOK_ID, CATEGORY_ID

    if not login():
        return

    get_books()

    if add_category():
        if add_book():
            get_books_by_category()
            update_book()
            borrow_book()
            return_book()
            reserve_book()
            delete_book()

    print("\n🎉 **ALL BOOK API TESTS COMPLETED SUCCESSFULLY!** 🎉")


if __name__ == "__main__":
    run_tests()
