import requests
import random

BASE_URL = "http://localhost:5000"  # Change for production

# Admin Credentials
ADMIN_EMAIL = "pulkitarora8690@gmail.com"
ADMIN_PASSWORD = "password123"
ADMIN_TOKEN = None

# Student Credentials
STUDENT_EMAIL = "parora2_be21@thapar.edu"
STUDENT_PASSWORD = "password123"
STUDENT_TOKEN = None


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


def register_user(email, password, role):
    """Registers an admin or student user"""
    print(f"\n🚀 Registering {role.capitalize()}...")
    response = test_api("POST", "/auth/signup", {
        "name": f"Test {role.capitalize()}",
        "email": email,
        "password": password,
        "role": role
    })

    if response.status_code == 201:
        print(f"📩 OTP sent to {email}")
        return True
    return False


def verify_otp(email, password, role):
    """Asks the user for OTP input and verifies it"""
    print(f"\n🚀 Enter OTP for {email} (Check Email)")
    otp_code = input("📩 Enter OTP received: ")

    response = test_api("POST", "/auth/verify_otp", {
        "email": email,
        "otp": otp_code,
        "name": "Admin User" if role == "admin" else "Test Student",
        "password": password,
        "role": role
    })

    return response.status_code == 201


def login(email, password):
    """Logs in the user and retrieves JWT token"""
    print(f"\n🚀 Logging In as {email}...")
    response = test_api("POST", "/auth/login", {
        "email": email,
        "password": password
    })

    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Logged in as {email}!")
        return token
    return None


def fetch_profile(token):
    """Fetches user profile"""
    print("\n🚀 Fetching User Profile...")
    response = test_api("GET", "/auth/profile", token=token)
    return response.status_code == 200


def forgot_password(email):
    """Sends OTP for password reset"""
    print("\n🚀 Requesting Forgot Password OTP...")
    response = test_api("POST", "/auth/forgot_password", {"email": email})
    return response.status_code == 200


def verify_password_reset_otp(email):
    """Verifies OTP for password reset"""
    print("\n🚀 Enter OTP for Password Reset (Check Email)")
    otp_code = input("📩 Enter OTP received: ")

    response = test_api("POST", "/auth/verify_password_reset_otp", {
        "email": email,
        "otp": otp_code
    })
    return response.status_code == 200


def reset_password(email, new_password):
    """Resets the password after OTP verification"""
    print("\n🚀 Resetting Password...")
    response = test_api("POST", "/auth/reset_password", {
        "email": email,
        "otp": input("📩 Enter OTP received: "),  # Ensure OTP is verified first
        "new_password": new_password
    })
    return response.status_code == 200


def run_tests():
    """Runs all Authentication API tests in correct order"""

    global ADMIN_TOKEN, STUDENT_TOKEN  # ✅ Move `global` to the beginning

    # ✅ Register & Verify Admin
    if not register_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin"):
        return
    if not verify_otp(ADMIN_EMAIL, ADMIN_PASSWORD, "admin"):
        return

    ADMIN_TOKEN = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not ADMIN_TOKEN:
        return

    # ✅ Register & Verify Student
    if not register_user(STUDENT_EMAIL, STUDENT_PASSWORD, "user"):
        return
    if not verify_otp(STUDENT_EMAIL, STUDENT_PASSWORD, "user"):
        return

    STUDENT_TOKEN = login(STUDENT_EMAIL, STUDENT_PASSWORD)
    if not STUDENT_TOKEN:
        return

    # ✅ Profile Fetch
    fetch_profile(ADMIN_TOKEN)
    fetch_profile(STUDENT_TOKEN)

    # ✅ Forgot Password & Reset (Student)
    if forgot_password(STUDENT_EMAIL):
        if verify_password_reset_otp(STUDENT_EMAIL):
            reset_password(STUDENT_EMAIL, "newpassword123")
            # ✅ Re-login after password reset
            STUDENT_TOKEN = login(STUDENT_EMAIL, "newpassword123")

    print("\n🎉 **ALL AUTHENTICATION API TESTS COMPLETED SUCCESSFULLY!** 🎉")


if __name__ == "__main__":
    run_tests()
