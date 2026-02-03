"""Unit tests for User Center API endpoints."""

import pytest
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus


class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_user_profile(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/user/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "testuser"

    def test_update_user_profile(self, client, auth_headers):
        """Test updating user profile."""
        response = client.put("/api/user/profile", json={
            "email": "newemail@example.com"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["email"] == "newemail@example.com"

    def test_update_unvalidate_profile(self, client, auth_headers):
        """Test unvalidate user email."""
        response = client.put("/api/user/profile", json={
            "email": "newemail"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication."""
        response = client.get("/api/user/profile")
        assert response.status_code == 401


class TestUserTasks:
    """Test user task records."""

    def test_get_user_tasks(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test getting user's task records."""
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
            status=AssignmentStatus.assignment_submission_pending
        )
        db_session.add(assignment)
        db_session.commit()

        response = client.get("/api/user/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    def test_get_user_tasks_with_status_filter(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test filtering user tasks by status."""
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
            status=AssignmentStatus.task_completed
        )
        db_session.add(assignment)
        db_session.commit()

        response = client.get("/api/user/tasks?status=approved", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_get_user_tasks_with_pagination(self, client, auth_headers):
        """Test paginating user tasks."""
        response = client.get("/api/user/tasks?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestUserPublishedTasks:
    """Test user published tasks."""

    def test_get_published_tasks(self, client, publisher_headers, db_session, test_publisher):
        """Test getting user's published tasks."""
        task = Task(
            title="Published Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()

        response = client.get("/api/user/published-tasks", headers=publisher_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0


class TestUserRewards:
    """Test user reward records."""

    def test_get_user_rewards(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test getting user's reward records."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.completed
        )
        db_session.add(task)
        db_session.commit()
        
        assignment = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed
        )
        db_session.add(assignment)
        db_session.commit()

        reward = Reward(
            assignment_id=assignment.id,
            amount=100.0,
            status=RewardStatus.issued
        )
        db_session.add(reward)
        db_session.commit()

        response = client.get("/api/user/rewards", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    def test_get_user_rewards_with_filter(self, client, auth_headers):
        """Test filtering user rewards by status."""
        response = client.get("/api/user/rewards?status=issued", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestUserStatistics:
    """Test user statistics."""

    def test_get_user_statistics(self, client, auth_headers):
        """Test getting user statistics."""
        response = client.get("/api/user/statistics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total_tasks_taken" in data["data"]
        assert "total_rewards_earned" in data["data"]

    def test_get_user_task_stats(self, client, auth_headers):
        """Test getting detailed user task statistics."""
        response = client.get("/api/user/task-stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "taken_tasks" in data["data"]
        assert "completed_tasks" in data["data"]
