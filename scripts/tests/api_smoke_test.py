"""
API Smoke Test Script for SkyrisReward Backend
Usage: python api_smoke_test.py
This script tests all major API endpoints for basic availability and correctness.
No pytest required.
"""
import requests
import json
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

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
        return resp.json()["data"]["access_token"]
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

# --- 4.1 Submit Assignment (user, text) ---
print("Submitting assignment (text)...")
submit_data = {"submit_content": "This is my assignment result."}
resp = requests.post(f"{BASE_URL}/api/assignment/submit/{assignment_id}", data=submit_data, headers=auth_header(user_token))
print_result("Submit Assignment (text)", resp)

# --- 4.2 Submit Assignment (user, file) ---
print("Submitting assignment (file)...")
file_path = os.path.join(os.path.dirname(__file__), "api_smoke_test.py")
with open(file_path, "rb") as f:
    files = {"file": ("api_smoke_test.py", f, "text/x-python")}
    resp = requests.post(f"{BASE_URL}/api/assignment/submit/{assignment_id}", files=files, headers=auth_header(user_token))
    print_result("Submit Assignment (file)", resp)

# --- 4.3 Update Assignment Progress (user) ---
print("Updating assignment progress...")
progress_data = {"status": "pending_review"}
resp = requests.patch(f"{BASE_URL}/api/assignment/{assignment_id}/progress", json=progress_data, headers=auth_header(user_token))
print_result("Update Assignment Progress", resp)

# --- 5. Submit Review (admin) ---
print("Submitting review...")
review_data = {"assignment_id": assignment_id, "review_result": "approved", "review_comment": "Looks good."}
resp = requests.post(f"{BASE_URL}/api/review/submit", json=review_data, headers=auth_header(admin_token))
print_result("Submit Review", resp)
review_id = resp.json().get("id")

# --- F3-T3: Notification API Tests ---
print("Testing notification send (admin)...")
notification_data = {"user_id": 1, "content": "Manual notification test."}
resp = requests.post(f"{BASE_URL}/api/notifications/send", json=notification_data, headers=auth_header(admin_token))
print_result("Send Notification (admin)", resp)

print("Testing notification list (user)...")
resp = requests.get(f"{BASE_URL}/api/notifications/user/1", headers=auth_header(user_token))
print_result("List Notifications (user)", resp)

if resp.status_code == 200 and resp.json():
    notification_id = resp.json()[0]["id"]
    print("Marking notification as read...")
    resp2 = requests.patch(f"{BASE_URL}/api/notifications/{notification_id}/read", headers=auth_header(user_token))
    print_result("Mark Notification Read", resp2)

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

# --- 11. Issue Reward (admin) ---
print("Issuing reward...")
reward_data = {"assignment_id": assignment_id, "user_id": 1, "amount": 100}
resp = requests.post(f"{BASE_URL}/api/reward/issue", json=reward_data, headers=auth_header(admin_token))
print_result("Issue Reward", resp)
reward_id = None
try:
    reward_id = resp.json().get("id")
except Exception:
    pass

# --- 12. Get Reward Detail ---
if reward_id:
    print("Getting reward detail...")
    resp = requests.get(f"{BASE_URL}/api/reward/{reward_id}")
    print_result("Get Reward Detail", resp)

# --- 13. List Rewards by User ---
print("Listing rewards by user...")
resp = requests.get(f"{BASE_URL}/api/reward/user/{1}")
print_result("List Rewards by User", resp)

print("Smoke test completed.")

# --- F3-T1: Task List API 测试 ---
print("Testing task list (分页/筛选/排序)...")
resp = requests.get(f"{BASE_URL}/api/tasks/?skip=0&limit=5")
print_result("Task List (first 5)", resp)
resp = requests.get(f"{BASE_URL}/api/tasks/?status=open")
print_result("Task List (status=open)", resp)
resp = requests.get(f"{BASE_URL}/api/tasks/?order_by=created_at")
print_result("Task List (order_by=created_at)", resp)

# --- F3-T1: Task Search API 测试 ---
print("Testing task search...")
resp = requests.get(f"{BASE_URL}/api/tasks/search/?keyword=Test")
print_result("Task Search (keyword=Test)", resp)

# --- F3-T1: Task Detail API 测试 ---
print("Testing task detail...")
if task_id:
    resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    print_result("Task Detail", resp)

# --- F2-T5: config.py 测试 ---
print("Testing config.py...")
try:
    from app.core import config
    print("[CONFIG] DB URL:", config.SQLALCHEMY_DATABASE_URL)
except Exception as e:
    print("[CONFIG] Import/config test failed:", e)
print("-" * 40)

# --- F2-T5: logger.py 测试 ---
print("Testing logger.py...")
try:
    from app.core.logger import logger
    logger.info("Smoke test logger info")
    logger.error("Smoke test logger error")
    print("[LOGGER] Logger test messages should appear in backend logs.")
except Exception as e:
    print("[LOGGER] Import/logger test failed:", e)
print("-" * 40)

# --- F2-T5: exception_handler.py 测试 ---
print("Testing exception handler...")
resp = requests.post(f"{BASE_URL}/api/user/login", json={"username": "notexist", "password": "wrong"})
print_result("Login with wrong credentials (should trigger exception handler)", resp)
resp = requests.get(f"{BASE_URL}/api/assignment/999999")  # 不存在的ID
print_result("Get non-existent assignment (should trigger exception handler)", resp)

# --- F2-T5: utils.py 测试 ---
print("Testing utils.py...")
try:
    from app.core import utils
    print("[UTILS] random_str(8):", utils.random_str(8))
except Exception as e:
    print("[UTILS] Import/utils test failed:", e)
print("-" * 40)

# --- F3-T4: User Center API Tests ---
print("Testing user center - get user profile...")
resp = requests.get(f"{BASE_URL}/api/user/profile", headers=auth_header(user_token))
print_result("Get User Profile", resp)

print("Testing user center - update user profile...")
profile_update = {"email": "updated_testuser@example.com", "bio": "Updated bio for testing"}
resp = requests.put(f"{BASE_URL}/api/user/profile", json=profile_update, headers=auth_header(user_token))
print_result("Update User Profile", resp)

print("Testing user center - get user task records...")
resp = requests.get(f"{BASE_URL}/api/user/tasks", headers=auth_header(user_token))
print_result("Get User Task Records", resp)

print("Testing user center - get user task records with status filter...")
resp = requests.get(f"{BASE_URL}/api/user/tasks?status=pending_review", headers=auth_header(user_token))
print_result("Get User Task Records (status=pending_review)", resp)

print("Testing user center - get user published tasks (publisher)...")
resp = requests.get(f"{BASE_URL}/api/user/published-tasks", headers=auth_header(pub_token))
print_result("Get User Published Tasks", resp)

print("Testing user center - get user reward records...")
resp = requests.get(f"{BASE_URL}/api/user/rewards", headers=auth_header(user_token))
print_result("Get User Reward Records", resp)

print("Testing user center - get user statistics...")
resp = requests.get(f"{BASE_URL}/api/user/statistics", headers=auth_header(user_token))
print_result("Get User Statistics", resp)

print("Testing user center - get user task statistics...")
resp = requests.get(f"{BASE_URL}/api/user/task-stats", headers=auth_header(user_token))
print_result("Get User Task Statistics", resp)

print("Testing user center - pagination test...")
resp = requests.get(f"{BASE_URL}/api/user/tasks?skip=0&limit=5", headers=auth_header(user_token))
print_result("Get User Task Records (pagination)", resp)

print("Testing user center - admin access to user center...")
resp = requests.get(f"{BASE_URL}/api/user/statistics", headers=auth_header(admin_token))
print_result("Admin Get User Statistics", resp)

# --- Admin API Tests ---
print("\n=== Testing Admin APIs ===")

print("Testing admin - get users list...")
resp = requests.get(f"{BASE_URL}/api/admin/users?skip=0&limit=10", headers=auth_header(admin_token))
print_result("Admin Get Users List", resp)

print("Testing admin - update user role...")
user_update = {"role": "publisher"}
resp = requests.put(f"{BASE_URL}/api/admin/users/1", json=user_update, headers=auth_header(admin_token))
print_result("Admin Update User Role", resp)

print("Testing admin - get tasks list...")
resp = requests.get(f"{BASE_URL}/api/admin/tasks?skip=0&limit=10", headers=auth_header(admin_token))
print_result("Admin Get Tasks List", resp)

if task_id:
    print("Testing admin - update task status...")
    task_update = {"status": "completed"}
    resp = requests.put(f"{BASE_URL}/api/admin/tasks/{task_id}", json=task_update, headers=auth_header(admin_token))
    print_result("Admin Update Task Status", resp)

    print("Testing admin - flag task as risky...")
    resp = requests.post(f"{BASE_URL}/api/admin/tasks/{task_id}/flag", headers=auth_header(admin_token))
    print_result("Admin Flag Task", resp)

print("Testing admin - get site statistics...")
resp = requests.get(f"{BASE_URL}/api/admin/statistics", headers=auth_header(admin_token))
print_result("Admin Get Site Statistics", resp)

print("Testing admin - non-admin access (should fail)...")
resp = requests.get(f"{BASE_URL}/api/admin/users", headers=auth_header(user_token))
print_result("Non-admin Access to Admin API (should be 403)", resp)
