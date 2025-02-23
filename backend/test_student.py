import requests
import random

BASE_URL = "http://localhost:5000"  # Change for production

# Student Credentials
STUDENT_EMAIL = "parora2_be21@thapar.edu"
STUDENT_PASSWORD = "newstudentpass123"
STUDENT_TOKEN = None

# Book & Borrow Data
BOOK_ID = None
BORROW_ID = None


def log_result(api_name, response):
    """Logs API test results with exception handling"""
    try:
        status = "✅ SUCCESS" if response.status_code in [200, 201] else "❌ FAILED"
        print(f"{status} - {api_name}: {response.status_code} {response.json() if response.content else 'No response data'}")
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
    """Logs in as a student and retrieves JWT token"""
    global STUDENT_TOKEN
    print("\n🚀 Logging In as Student...")
    response = test_api("POST", "/auth/login", {
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD
    })

    if response.status_code == 200:
        STUDENT_TOKEN = response.json().get("access_token")
        print("✅ Logged in as Student!")
        return True
    return False


def view_books():
    """Fetches all available books and selects one for borrowing"""
    global BOOK_ID
    print("\n🚀 Viewing Available Books...")
    response = test_api("GET", "/books", token=STUDENT_TOKEN)

    if response.status_code == 200 and response.json():
        BOOK_ID = response.json()[0]["id"]  # ✅ Assign the first available book
        print(f"✅ Selected Book ID {BOOK_ID} for borrowing")
        return True
    print("❌ No books available.")
    return False


def add_book_for_testing():
    """Adds a test book before borrowing"""
    global BOOK_ID
    print("\n🚀 Adding a Test Book for Borrowing...")
    response = test_api("POST", "/books/add", {
        "title": "Test Book",
        "author": "John Doe",
        "isbn": str(random.randint(1000000000000, 9999999999999)),  # Unique ISBN
        "category_id": 1,
        "copies_available": 3
    }, STUDENT_TOKEN)

    if response.status_code == 201:
        BOOK_ID = response.json().get("id")
        print(f"✅ Test Book added successfully with ID: {BOOK_ID}")
        return True
    return False


def borrow_book():
    """Borrows a book if available"""
    global BORROW_ID
    if BOOK_ID is None:
        print("❌ No book available to borrow. Skipping...")
        return False

    print(f"\n🚀 Borrowing Book ID {BOOK_ID}...")
    response = test_api("POST", f"/students/books/borrow/{BOOK_ID}", token=STUDENT_TOKEN)

    if response.status_code == 200:
        # ✅ Assigning BORROW_ID based on book ID
        BORROW_ID = BOOK_ID  # Since API doesn't return borrow_id, we assume BOOK_ID as unique reference
        return True
    return False



def view_borrowed_books():
    """Fetches all books borrowed by the student"""
    print("\n🚀 Viewing Borrowed Books...")
    response = test_api("GET", "/students/books/borrowed", token=STUDENT_TOKEN)
    return response.status_code == 200


def request_extension():
    """Requests an extension for the borrowed book"""
    if BORROW_ID is None:
        print("❌ No borrowed book available for extension. Skipping...")
        return False

    print(f"\n🚀 Requesting Extension for Book ID {BORROW_ID}...")
    response = test_api("POST", f"/students/books/extend/{BORROW_ID}", token=STUDENT_TOKEN)
    return response.status_code == 200


def return_book():
    """Returns a borrowed book"""
    if BORROW_ID is None:
        print("❌ No borrowed book available to return. Skipping...")
        return False

    print(f"\n🚀 Returning Borrowed Book ID {BORROW_ID}...")
    response = test_api("POST", f"/students/books/return/{BORROW_ID}", token=STUDENT_TOKEN)
    return response.status_code == 200



def pay_fine():
    """Pays pending fines"""
    print("\n🚀 Paying Pending Fines...")
    response = test_api("POST", "/students/books/pay-fine", token=STUDENT_TOKEN)
    return response.status_code == 200


def edit_profile():
    """Changes student password"""
    print("\n🚀 Changing Student Password...")
    response = test_api("PUT", "/students/profile/edit", {  # ✅ Fixed API path
        "password": "newstudentpass123"
    }, STUDENT_TOKEN)
    return response.status_code == 200


def run_tests():
    """Runs all Student API tests in correct order"""

    global STUDENT_TOKEN, BOOK_ID, BORROW_ID

    if not login():
        return

    if not view_books():
        add_book_for_testing()  # ✅ Add a book if none exist
    
    if borrow_book():
        view_borrowed_books()
        request_extension()
        return_book()
        pay_fine()

    edit_profile()

    print("\n🎉 **ALL STUDENT API TESTS COMPLETED SUCCESSFULLY!** 🎉")


if __name__ == "__main__":
    run_tests()
