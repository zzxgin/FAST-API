"""
API Smoke Test Script for SkyrisReward Backend
Usage: python api_smoke_test.py
This script tests all major API endpoints for basic availability and correctness.
No pytest required.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# --- Helper functions ---
def print_result(name, resp):
    print(f"[TEST] {name}: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)
    print("-" * 40)

def get_token(username, password):
    resp = requests.post(f"{BASE_URL}/api/user/login", json={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# --- Test Data ---
USER = {"username": "testuser", "email": "testuser@example.com", "password": "testpass", "role": "user"}
ADMIN = {"username": "admin", "email": "admin@example.com", "password": "adminpass", "role": "admin"}
PUBLISHER = {"username": "publisher", "email": "publisher@example.com", "password": "pubpass", "role": "publisher"}

# --- 1. Register Users ---
print("Registering users...")
for u in [USER, ADMIN, PUBLISHER]:
    resp = requests.post(f"{BASE_URL}/api/user/register", json=u)
    print_result(f"Register {u['username']}", resp)

# --- 2. Login Users ---
print("Logging in...")
user_token = get_token(USER["username"], USER["password"])
admin_token = get_token(ADMIN["username"], ADMIN["password"])
pub_token = get_token(PUBLISHER["username"], PUBLISHER["password"])

# --- 3. Publish Task (publisher) ---
print("Publishing task...")
task_data = {"title": "Test Task", "description": "A test task.", "reward_amount": 100}
resp = requests.post(f"{BASE_URL}/api/tasks/publish", json=task_data, headers=auth_header(pub_token))
print_result("Publish Task", resp)
task_id = resp.json().get("id")

# --- 4. Accept Task (user) ---
print("Accepting task...")
assignment_data = {"task_id": task_id, "submit_content": "My submission."}
resp = requests.post(f"{BASE_URL}/api/assignment/accept", json=assignment_data, headers=auth_header(user_token))
print_result("Accept Task", resp)
assignment_id = resp.json().get("id")

# --- 5. Submit Review (admin) ---
print("Submitting review...")
review_data = {"assignment_id": assignment_id, "review_result": "approved", "review_comment": "Looks good."}
resp = requests.post(f"{BASE_URL}/api/review/submit", json=review_data, headers=auth_header(admin_token))
print_result("Submit Review", resp)
review_id = resp.json().get("id")

# --- 6. Appeal (user) ---
print("Submitting appeal...")
resp = requests.post(f"{BASE_URL}/api/review/appeal/{assignment_id}", headers=auth_header(user_token))
print_result("Appeal Assignment", resp)

# --- 7. Get Assignment Detail ---
print("Getting assignment detail...")
resp = requests.get(f"{BASE_URL}/api/assignment/{assignment_id}")
print_result("Get Assignment Detail", resp)

# --- 8. Get Review Detail ---
print("Getting review detail...")
resp = requests.get(f"{BASE_URL}/api/review/{review_id}")
print_result("Get Review Detail", resp)

# --- 9. List Reviews by Assignment ---
print("Listing reviews by assignment...")
resp = requests.get(f"{BASE_URL}/api/review/assignment/{assignment_id}")
print_result("List Reviews by Assignment", resp)

# --- 10. List Assignments by User ---
print("Listing assignments by user...")
resp = requests.get(f"{BASE_URL}/api/assignment/user/{1}")  # Pass user_id as integer
print_result("List Assignments by User", resp)

print("Smoke test completed.")
