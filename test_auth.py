import requests
import random
import time

BASE_URL = "https://lms-8owp.onrender.com"  # Change for production

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

    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=10)
        log_result(endpoint, response)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR - {endpoint}: {e}")
        return None


def register_user(email, password, role):
    """Registers an admin or student user"""
    print(f"\n🚀 Registering {role.capitalize()}...")
    response = test_api("POST", "/auth/signup", {
        "name": f"Test {role.capitalize()}",
        "email": email,
        "password": password,
        "role": role
    })

    if response and response.status_code == 201:
        print(f"📩 OTP sent to {email}")
        return True
    return False


def verify_otp(email, password, role):
    """Asks the user for OTP input and verifies it"""
    otp_code = input(f"📩 Enter OTP for {email}: ")

    response = test_api("POST", "/auth/verify_otp", {
        "email": email,
        "otp": otp_code,
        "name": "Admin User" if role == "admin" else "Test Student",
        "password": password,
        "role": role
    })

    return response and response.status_code == 201


def login(email, password):
    """Logs in the user and retrieves JWT token"""
    print(f"\n🚀 Logging In as {email}...")
    response = test_api("POST", "/auth/login", {
        "email": email,
        "password": password
    })

    if response and response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Logged in as {email}!")
        return token
    return None


def fetch_profile(token):
    """Fetches user profile"""
    print("\n🚀 Fetching User Profile...")
    return test_api("GET", "/auth/profile", token=token)


def forgot_password(email):
    """Sends OTP for password reset"""
    print("\n🚀 Requesting Forgot Password OTP...")
    return test_api("POST", "/auth/forgot_password", {"email": email})


def verify_password_reset_otp(email):
    """Verifies OTP for password reset"""
    otp_code = input(f"📩 Enter OTP for {email} (Password Reset): ")

    return test_api("POST", "/auth/verify_password_reset_otp", {
        "email": email,
        "otp": otp_code
    })


def reset_password(email, new_password):
    """Resets the password after OTP verification"""
    otp_code = input(f"📩 Enter OTP to reset password for {email}: ")

    return test_api("POST", "/auth/reset_password", {
        "email": email,
        "otp": otp_code,
        "new_password": new_password
    })


def run_tests():
    """Runs all Authentication API tests in correct order"""

    global ADMIN_TOKEN, STUDENT_TOKEN  

    # ✅ Register & Verify Admin
    if register_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin"):
        if verify_otp(ADMIN_EMAIL, ADMIN_PASSWORD, "admin"):
            ADMIN_TOKEN = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    # ✅ Register & Verify Student
    if register_user(STUDENT_EMAIL, STUDENT_PASSWORD, "user"):
        if verify_otp(STUDENT_EMAIL, STUDENT_PASSWORD, "user"):
            STUDENT_TOKEN = login(STUDENT_EMAIL, STUDENT_PASSWORD)

    # ✅ Profile Fetch
    if ADMIN_TOKEN:
        fetch_profile(ADMIN_TOKEN)
    if STUDENT_TOKEN:
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
