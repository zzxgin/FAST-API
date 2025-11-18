"""
API Smoke Test Script with Response Format Validation for SkyrisReward Backend
增强版API烟测脚本 - 包含统一响应格式验证功能

Usage: python api_smoke_test_enhanced.py

特性:
- 全面的API功能测试
- 自动验证响应格式是否符合 {code, message, data} 标准
- 详细的统计报告
- 彩色终端输出
"""
import requests
import json
import sys, os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8000"

# --- Response Format Validation ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

# 统计信息
format_stats = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'failed_tests': []
}

def validate_response_format(resp, test_name):
    """验证响应是否符合统一格式: {code, message, data}"""
    format_stats['total'] += 1
    
    try:
        data = resp.json()
    except Exception as e:
        print(f"{Colors.RED}✗ [{test_name}] 响应不是有效的JSON{Colors.END}")
        format_stats['failed'] += 1
        format_stats['failed_tests'].append(f"{test_name} - Invalid JSON")
        return False
    
    errors = []
    
    # 检查必需字段
    if 'code' not in data:
        errors.append("缺少 'code' 字段")
    if 'message' not in data:
        errors.append("缺少 'message' 字段")
    if 'data' not in data:
        errors.append("缺少 'data' 字段")
    
    # 检查字段类型
    if 'code' in data and not isinstance(data['code'], int):
        errors.append(f"'code' 应该是整数,实际是 {type(data['code']).__name__}")
    if 'message' in data and not isinstance(data['message'], str):
        errors.append(f"'message' 应该是字符串,实际是 {type(data['message']).__name__}")
    
    if errors:
        print(f"{Colors.RED}✗ [{test_name}] 响应格式错误:{Colors.END}")
        for error in errors:
            print(f"  {Colors.RED}- {error}{Colors.END}")
        format_stats['failed'] += 1
        format_stats['failed_tests'].append(f"{test_name} - {', '.join(errors)}")
        return False
    else:
        code = data['code']
        message = data['message']
        status_color = Colors.GREEN if resp.status_code < 400 else Colors.YELLOW
        print(f"{Colors.GREEN}✓ [{test_name}] 响应格式正确{Colors.END} - {status_color}Status: {resp.status_code}, Code: {code}, Message: '{message}'{Colors.END}")
        format_stats['passed'] += 1
        return True

# --- Helper functions ---
def print_result(name, resp, validate_format=True):
    """打印测试结果并验证响应格式"""
    print(f"\n{Colors.BLUE}[TEST] {name}{Colors.END}")
    
    # 验证响应格式
    if validate_format:
        validate_response_format(resp, name)
    
    # 打印详细响应
    try:
        response_data = resp.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)
    print("-" * 60)

def get_token(username, password):
    resp = requests.post(f"{BASE_URL}/api/user/login", json={"username": username, "password": password})
    
    # 验证登录响应格式
    validate_response_format(resp, f"Login {username}")
    
    if resp.status_code == 200:
        data = resp.json()
        # 成功响应中,token在data字段中
        if 'data' in data and isinstance(data['data'], dict):
            return data['data'].get('access_token')
    return None

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# ============================================================
# 开始测试
# ============================================================
print("=" * 60)
print(f"{Colors.BLUE}SkyrisReward API 烟测 + 响应格式验证{Colors.END}")
print("=" * 60)
print(f"测试服务器: {BASE_URL}")
print(f"测试内容: API功能 + 统一响应格式验证")
print("=" * 60)

# 检查服务器连接
print(f"\n{Colors.YELLOW}检查服务器连接...{Colors.END}")
try:
    resp = requests.get(f"{BASE_URL}/docs", timeout=5)
    if resp.status_code == 200:
        print(f"{Colors.GREEN}✓ 服务器正在运行{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ 服务器响应异常 (status: {resp.status_code}){Colors.END}")
except Exception as e:
    print(f"{Colors.RED}✗ 无法连接到服务器: {e}{Colors.END}")
    print(f"{Colors.RED}请先启动服务器: uvicorn app.main:app --reload{Colors.END}")
    sys.exit(1)

# --- Test Data ---
USER = {"username": "testuser", "email": "testuser@example.com", "password": "testpass", "role": "user"}
ADMIN = {"username": "admin", "email": "admin@example.com", "password": "adminpass", "role": "admin"}
PUBLISHER = {"username": "publisher", "email": "publisher@example.com", "password": "pubpass", "role": "publisher"}

print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
print(f"{Colors.BLUE}开始API测试{Colors.END}")
print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")

# --- 1. Register Users ---
print("\n" + "=" * 60)
print("1. 用户注册测试")
print("=" * 60)
for u in [USER, ADMIN, PUBLISHER]:
    resp = requests.post(f"{BASE_URL}/api/user/register", json=u)
    print_result(f"Register {u['username']}", resp)

# --- 2. Login Users ---
print("\n" + "=" * 60)
print("2. 用户登录测试")
print("=" * 60)
user_token = get_token(USER["username"], USER["password"])
admin_token = get_token(ADMIN["username"], ADMIN["password"])
pub_token = get_token(PUBLISHER["username"], PUBLISHER["password"])

# --- 3. Publish Task (publisher) ---
print("\n" + "=" * 60)
print("3. 任务发布测试")
print("=" * 60)
task_data = {"title": "Test Task", "description": "A test task.", "reward_amount": 100}
resp = requests.post(f"{BASE_URL}/api/tasks/publish", json=task_data, headers=auth_header(pub_token))
print_result("Publish Task", resp)
task_id = resp.json().get("data", {}).get("id") if resp.status_code == 200 else None

# --- 4. Accept Task (user) ---
print("\n" + "=" * 60)
print("4. 任务接取和提交测试")
print("=" * 60)
assignment_data = {"task_id": task_id, "submit_content": "My submission."}
resp = requests.post(f"{BASE_URL}/api/assignment/accept", json=assignment_data, headers=auth_header(user_token))
print_result("Accept Task", resp)
assignment_id = resp.json().get("data", {}).get("id") if resp.status_code == 200 else None

# --- 4.1 Submit Assignment (user, text) ---
print("Submitting assignment (text)...")
submit_data = {"submit_content": "This is my assignment result."}
resp = requests.post(f"{BASE_URL}/api/assignment/submit/{assignment_id}", data=submit_data, headers=auth_header(user_token))
print_result("Submit Assignment (text)", resp)

# --- 4.2 Submit Assignment (user, file) ---
print("Submitting assignment (file)...")
file_path = os.path.join(os.path.dirname(__file__), "api_smoke_test_enhanced.py")
with open(file_path, "rb") as f:
    files = {"file": ("test_script.py", f, "text/x-python")}
    resp = requests.post(f"{BASE_URL}/api/assignment/submit/{assignment_id}", files=files, headers=auth_header(user_token))
    print_result("Submit Assignment (file)", resp)

# --- 4.3 Update Assignment Progress (user) ---
print("Updating assignment progress...")
progress_data = {"status": "pending_review"}
resp = requests.patch(f"{BASE_URL}/api/assignment/{assignment_id}/progress", json=progress_data, headers=auth_header(user_token))
print_result("Update Assignment Progress", resp)

# --- 5. Submit Review (admin) ---
print("\n" + "=" * 60)
print("5. 审核测试")
print("=" * 60)
review_data = {"assignment_id": assignment_id, "review_result": "approved", "review_comment": "Looks good."}
resp = requests.post(f"{BASE_URL}/api/review/submit", json=review_data, headers=auth_header(admin_token))
print_result("Submit Review", resp)
review_id = resp.json().get("data", {}).get("id") if resp.status_code == 200 else None

# --- F3-T3: Notification API Tests ---
print("\n" + "=" * 60)
print("6. 通知系统测试")
print("=" * 60)
notification_data = {"user_id": 1, "content": "Manual notification test."}
resp = requests.post(f"{BASE_URL}/api/notifications/send", json=notification_data, headers=auth_header(admin_token))
print_result("Send Notification (admin)", resp)

print("Testing notification list (user)...")
resp = requests.get(f"{BASE_URL}/api/notifications/user/1", headers=auth_header(user_token))
print_result("List Notifications (user)", resp)

if resp.status_code == 200:
    data = resp.json().get("data", [])
    if data and len(data) > 0:
        notification_id = data[0]["id"]
        print("Marking notification as read...")
        resp2 = requests.patch(f"{BASE_URL}/api/notifications/{notification_id}/read", headers=auth_header(user_token))
        print_result("Mark Notification Read", resp2)

# --- 6. Appeal (user) ---
print("\n" + "=" * 60)
print("7. 申诉测试")
print("=" * 60)
resp = requests.post(f"{BASE_URL}/api/review/appeal/{assignment_id}", headers=auth_header(user_token))
print_result("Appeal Assignment", resp)

# --- 7. Get Assignment Detail ---
print("\n" + "=" * 60)
print("8. 详情查询测试")
print("=" * 60)
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
resp = requests.get(f"{BASE_URL}/api/assignment/user/{1}")
print_result("List Assignments by User", resp)

# --- 11. Issue Reward (admin) ---
print("\n" + "=" * 60)
print("9. 奖励发放测试")
print("=" * 60)
reward_data = {"assignment_id": assignment_id, "user_id": 1, "amount": 100}
resp = requests.post(f"{BASE_URL}/api/reward/issue", json=reward_data, headers=auth_header(admin_token))
print_result("Issue Reward", resp)
reward_id = None
try:
    if resp.status_code == 200:
        reward_id = resp.json().get("data", {}).get("id")
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

# --- F3-T1: Task List API 测试 ---
print("\n" + "=" * 60)
print("10. 任务列表和搜索测试")
print("=" * 60)
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
print("\n" + "=" * 60)
print("11. 核心模块测试 (config, logger, utils)")
print("=" * 60)
try:
    from app.core import config
    print(f"{Colors.GREEN}✓ [CONFIG] DB URL: {config.SQLALCHEMY_DATABASE_URL}{Colors.END}")
except Exception as e:
    print(f"{Colors.RED}✗ [CONFIG] Import/config test failed: {e}{Colors.END}")
print("-" * 60)

# --- F2-T5: logger.py 测试 ---
try:
    from app.core.logger import logger
    logger.info("Smoke test logger info")
    logger.error("Smoke test logger error")
    print(f"{Colors.GREEN}✓ [LOGGER] Logger test messages sent{Colors.END}")
except Exception as e:
    print(f"{Colors.RED}✗ [LOGGER] Import/logger test failed: {e}{Colors.END}")
print("-" * 60)

# --- F2-T5: exception_handler.py 测试 ---
print("\n" + "=" * 60)
print("12. 异常处理测试")
print("=" * 60)
resp = requests.post(f"{BASE_URL}/api/user/login", json={"username": "notexist", "password": "wrong"})
print_result("Login with wrong credentials (should trigger exception handler)", resp)
resp = requests.get(f"{BASE_URL}/api/assignment/999999")
print_result("Get non-existent assignment (should trigger exception handler)", resp)

# --- F2-T5: utils.py 测试 ---
try:
    from app.core import utils
    print(f"{Colors.GREEN}✓ [UTILS] random_str(8): {utils.random_str(8)}{Colors.END}")
except Exception as e:
    print(f"{Colors.RED}✗ [UTILS] Import/utils test failed: {e}{Colors.END}")
print("-" * 60)

# --- F3-T4: User Center API Tests ---
print("\n" + "=" * 60)
print("13. 用户中心API测试")
print("=" * 60)
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

# --- F3-T5: Admin API Tests ---
print("\n" + "=" * 60)
print("14. 管理员API测试")
print("=" * 60)

# --- Admin: List Users ---
print("Testing admin - list users...")
resp = requests.get(f"{BASE_URL}/api/admin/users?skip=0&limit=10", headers=auth_header(admin_token))
print_result("Admin List Users", resp)

# --- Admin: Update User (change role) ---
print("Testing admin - update user role...")
user_update = {"role": "publisher"}
resp = requests.put(f"{BASE_URL}/api/admin/users/1", json=user_update, headers=auth_header(admin_token))
print_result("Admin Update User Role", resp)

# --- Admin: Update User (deactivate user) ---
print("Testing admin - deactivate user...")
user_update = {"is_active": False}
resp = requests.put(f"{BASE_URL}/api/admin/users/2", json=user_update, headers=auth_header(admin_token))
print_result("Admin Deactivate User", resp)

# --- Admin: Reactivate User ---
print("Testing admin - reactivate user...")
user_update = {"is_active": True}
resp = requests.put(f"{BASE_URL}/api/admin/users/2", json=user_update, headers=auth_header(admin_token))
print_result("Admin Reactivate User", resp)

# --- Admin: List Tasks ---
print("Testing admin - list tasks...")
resp = requests.get(f"{BASE_URL}/api/admin/tasks?skip=0&limit=10", headers=auth_header(admin_token))
print_result("Admin List Tasks", resp)

# --- Admin: Update Task Status ---
print("Testing admin - update task status...")
if task_id:
    task_update = {"status": "in_progress"}
    resp = requests.put(f"{BASE_URL}/api/admin/tasks/{task_id}", json=task_update, headers=auth_header(admin_token))
    print_result("Admin Update Task Status", resp)

# --- Admin: Flag Task ---
print("Testing admin - flag task (close)...")
if task_id:
    flag_update = {"status": "closed"}
    resp = requests.post(f"{BASE_URL}/api/admin/tasks/{task_id}/flag", json=flag_update, headers=auth_header(admin_token))
    print_result("Admin Flag Task", resp)

# --- Admin: Get Site Statistics ---
print("Testing admin - get site statistics...")
resp = requests.get(f"{BASE_URL}/api/admin/statistics", headers=auth_header(admin_token))
print_result("Admin Get Site Statistics", resp)

# --- Admin: Test Permission Denied (non-admin user) ---
print("Testing admin - permission denied for non-admin...")
resp = requests.get(f"{BASE_URL}/api/admin/users", headers=auth_header(user_token))
print_result("Non-Admin Access Admin API (should fail)", resp)

# ============================================================
# 响应格式验证统计报告
# ============================================================
print("\n" + "=" * 60)
print(f"{Colors.BLUE}响应格式验证统计报告{Colors.END}")
print("=" * 60)

print(f"\n总测试端点数: {format_stats['total']}")
print(f"{Colors.GREEN}✓ 格式正确: {format_stats['passed']}{Colors.END}")

if format_stats['failed'] > 0:
    print(f"{Colors.RED}✗ 格式错误: {format_stats['failed']}{Colors.END}")
    print(f"\n{Colors.RED}失败的测试:{Colors.END}")
    for failed_test in format_stats['failed_tests']:
        print(f"  {Colors.RED}- {failed_test}{Colors.END}")
else:
    print(f"{Colors.GREEN}✗ 格式错误: 0{Colors.END}")

pass_rate = (format_stats['passed'] / format_stats['total'] * 100) if format_stats['total'] > 0 else 0
print(f"\n通过率: {pass_rate:.1f}%")

if format_stats['failed'] == 0:
    print(f"\n{Colors.GREEN}🎉 所有API响应格式均符合统一标准!{Colors.END}")
else:
    print(f"\n{Colors.YELLOW}⚠ 部分API响应格式需要修复{Colors.END}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
