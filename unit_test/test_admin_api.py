"""Unit tests for Admin API endpoints."""

import pytest
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus


class TestAdminUsers:
    """Test admin user management endpoints."""

    def test_create_user(self, client, admin_headers):
        """Test creating a new user."""
        response = client.post(
            "/api/admin/users",
            json={
                "username": "newuser123",
                "email": "newuser@test.com",
                "password": "password123",
                "role": "user"
            },
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "newuser123"
        assert data["data"]["email"] == "newuser@test.com"
        assert data["data"]["role"] == "user"

    def test_create_user_duplicate_username(self, client, admin_headers, test_user):
        """Test creating user with duplicate username."""
        response = client.post(
            "/api/admin/users",
            json={
                "username": test_user.username,
                "email": "different@test.com",
                "password": "password123",
                "role": "user"
            },
            headers=admin_headers
        )
        assert response.status_code == 400

    def test_create_user_unauthorized(self, client, auth_headers):
        """Test creating user without admin privileges."""
        response = client.post(
            "/api/admin/users",
            json={
                "username": "newuser456",
                "email": "newuser@test.com",
                "password": "password123"
            },
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_list_users(self, client, admin_headers):
        """Test listing all users."""
        response = client.get("/api/admin/users?skip=0&limit=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    def test_list_users_with_order_by(self, client, admin_headers):
        """Test listing users with sorting."""
        # Test ascending order by username
        response = client.get("/api/admin/users?order_by=username", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        # Test descending order by created_at
        response = client.get("/api/admin/users?order_by=-created_at", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_list_users_with_pagination(self, client, admin_headers):
        """Test listing users with pagination."""
        response = client.get("/api/admin/users?skip=0&limit=2", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) <= 2

    def test_list_users_unauthorized(self, client, auth_headers):
        """Test listing users without admin privileges."""
        response = client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403

    def test_get_user_detail(self, client, admin_headers, test_user):
        """Test getting user details."""
        response = client.get(f"/api/admin/users/{test_user.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == test_user.id
        assert data["data"]["username"] == test_user.username

    def test_get_nonexistent_user(self, client, admin_headers):
        """Test getting non-existent user."""
        response = client.get("/api/admin/users/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_user_role(self, client, admin_headers, test_user):
        """Test updating user role."""
        response = client.put(
            f"/api/admin/users/{test_user.id}",
            json={"role": "publisher"},
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["role"] == "publisher"

    def test_update_user_email(self, client, admin_headers, test_user):
        """Test updating user email."""
        response = client.put(
            f"/api/admin/users/{test_user.id}",
            json={"email": "newemail@test.com"},
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["email"] == "newemail@test.com"

    def test_update_user_unauthorized(self, client, auth_headers, test_user):
        """Test updating user without admin privileges."""
        response = client.put(
            f"/api/admin/users/{test_user.id}",
            json={"role": "admin"},
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_update_nonexistent_user(self, client, admin_headers):
        """Test updating non-existent user."""
        response = client.put(
            "/api/admin/users/99999",
            json={"role": "publisher"},
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_delete_user(self, client, admin_headers, db_session):
        """Test deleting a user."""
        from app.models.user import User, UserRole
        # Create a user to delete
        user = User(
            username="usertodelete",
            email="delete@test.com",
            password_hash="hashed",
            role=UserRole.user
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = client.delete(f"/api/admin/users/{user.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["deleted"] == True

    def test_delete_nonexistent_user(self, client, admin_headers):
        """Test deleting non-existent user."""
        response = client.delete("/api/admin/users/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_delete_user_unauthorized(self, client, auth_headers, test_user):
        """Test deleting user without admin privileges."""
        response = client.delete(f"/api/admin/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == 403


class TestAdminTasks:
    """Test admin task management endpoints."""

    def test_create_task(self, client, admin_headers):
        """Test creating a new task."""
        response = client.post(
            "/api/admin/tasks",
            json={
                "title": "New Admin Task",
                "description": "Task created by admin",
                "reward_amount": 100.0,
                "status": "open"
            },
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "New Admin Task"
        assert data["data"]["reward_amount"] == 100.0

    def test_create_task_invalid_amount(self, client, admin_headers):
        """Test creating task with invalid amount."""
        response = client.post(
            "/api/admin/tasks",
            json={
                "title": "Invalid Task",
                "description": "Task with negative amount",
                "reward_amount": -10.0
            },
            headers=admin_headers
        )
        assert response.status_code == 422

    def test_create_task_unauthorized(self, client, auth_headers):
        """Test creating task without admin privileges."""
        response = client.post(
            "/api/admin/tasks",
            json={
                "title": "Unauthorized Task",
                "reward_amount": 50.0
            },
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_list_tasks(self, client, admin_headers, db_session, test_publisher):
        """Test listing all tasks."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()

        response = client.get("/api/admin/tasks?skip=0&limit=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0

    def test_list_tasks_with_status_filter(self, client, admin_headers, db_session, test_publisher):
        """Test listing tasks filtered by status."""
        task1 = Task(
            title="Open Task",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        task2 = Task(
            title="Completed Task",
            publisher_id=test_publisher.id,
            reward_amount=60.0,
            status=TaskStatus.completed
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        response = client.get("/api/admin/tasks?status=open", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_list_tasks_with_order_by(self, client, admin_headers, db_session, test_publisher):
        """Test listing tasks with sorting."""
        task1 = Task(
            title="High Reward Task",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.open
        )
        task2 = Task(
            title="Low Reward Task",
            publisher_id=test_publisher.id,
            reward_amount=20.0,
            status=TaskStatus.open
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        # Test ascending order by reward_amount
        response = client.get("/api/admin/tasks?order_by=reward_amount", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        # Test descending order by created_at
        response = client.get("/api/admin/tasks?order_by=-created_at", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_list_tasks_with_pagination(self, client, admin_headers, db_session, test_publisher):
        """Test listing tasks with pagination."""
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                publisher_id=test_publisher.id,
                reward_amount=50.0 + i,
                status=TaskStatus.open
            )
            db_session.add(task)
        db_session.commit()

        response = client.get("/api/admin/tasks?skip=0&limit=2", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) <= 2

    def test_list_tasks_unauthorized(self, client, auth_headers):
        """Test listing tasks without admin privileges."""
        response = client.get("/api/admin/tasks", headers=auth_headers)
        assert response.status_code == 403

    def test_get_task_detail(self, client, admin_headers, db_session, test_publisher):
        """Test getting task details."""
        task = Task(
            title="Detail Task",
            description="Task for detail test",
            publisher_id=test_publisher.id,
            reward_amount=75.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.get(f"/api/admin/tasks/{task.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == task.id
        assert data["data"]["title"] == "Detail Task"

    def test_get_nonexistent_task(self, client, admin_headers):
        """Test getting non-existent task."""
        response = client.get("/api/admin/tasks/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_task_status(self, client, admin_headers, db_session, test_publisher):
        """Test updating task status."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(
            f"/api/admin/tasks/{task.id}",
            json={"status": "completed"},
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "completed"

    def test_update_task_title(self, client, admin_headers, db_session, test_publisher):
        """Test updating task title."""
        task = Task(
            title="Original Title",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(
            f"/api/admin/tasks/{task.id}",
            json={"title": "Updated Title"},
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Updated Title"

    def test_update_task_reward_amount(self, client, admin_headers, db_session, test_publisher):
        """Test updating task reward amount."""
        task = Task(
            title="Task",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(
            f"/api/admin/tasks/{task.id}",
            json={"reward_amount": 100.0},
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["reward_amount"] == 100.0

    def test_update_task_multiple_fields(self, client, admin_headers, db_session, test_publisher):
        """Test updating multiple task fields."""
        task = Task(
            title="Original",
            description="Original Desc",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(
            f"/api/admin/tasks/{task.id}",
            json={
                "title": "Updated",
                "description": "Updated Desc",
                "reward_amount": 80.0,
                "status": "in_progress"
            },
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Updated"
        assert data["data"]["description"] == "Updated Desc"
        assert data["data"]["reward_amount"] == 80.0
        assert data["data"]["status"] == "in_progress"

    def test_update_task_no_fields(self, client, admin_headers, db_session, test_publisher):
        """Test updating task with no fields provided."""
        task = Task(
            title="Task",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(
            f"/api/admin/tasks/{task.id}",
            json={},
            headers=admin_headers
        )
        assert response.status_code == 400

    def test_update_task_unauthorized(self, client, auth_headers, db_session, test_publisher):
        """Test updating task without admin privileges."""
        task = Task(
            title="Task",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(
            f"/api/admin/tasks/{task.id}",
            json={"status": "completed"},
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_update_nonexistent_task(self, client, admin_headers):
        """Test updating non-existent task."""
        response = client.put(
            "/api/admin/tasks/99999",
            json={"status": "completed"},
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_delete_task(self, client, admin_headers, db_session, test_publisher):
        """Test deleting a task."""
        task = Task(
            title="Task to Delete",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.delete(f"/api/admin/tasks/{task.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["deleted"] == True

    def test_delete_nonexistent_task(self, client, admin_headers):
        """Test deleting non-existent task."""
        response = client.delete("/api/admin/tasks/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_delete_task_unauthorized(self, client, auth_headers, db_session, test_publisher):
        """Test deleting task without admin privileges."""
        task = Task(
            title="Task",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.delete(f"/api/admin/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_flag_task(self, client, admin_headers, db_session, test_publisher):
        """Test flagging a task as risky."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.post(
            f"/api/admin/tasks/{task.id}/flag",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_flag_nonexistent_task(self, client, admin_headers):
        """Test flagging non-existent task."""
        response = client.post(
            "/api/admin/tasks/99999/flag",
            headers=admin_headers
        )
        assert response.status_code == 404


class TestAdminStatistics:
    """Test admin statistics endpoint."""

    def test_get_site_statistics(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test getting site statistics."""
        # Create some test data
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()

        assignment = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.pending_review
        )
        db_session.add(assignment)
        db_session.commit()

        response = client.get("/api/admin/statistics", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total_users" in data["data"]
        assert "total_tasks" in data["data"]
        assert "total_assignments" in data["data"]
        assert data["data"]["total_users"] >= 2
        assert data["data"]["total_tasks"] >= 1
        assert data["data"]["total_assignments"] >= 1

    def test_get_statistics_unauthorized(self, client, auth_headers):
        """Test getting statistics without admin privileges."""
        response = client.get("/api/admin/statistics", headers=auth_headers)
        assert response.status_code == 403
