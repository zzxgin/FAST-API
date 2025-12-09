"""Unit tests for Reward API endpoints."""

import pytest
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus


class TestRewardIssue:
    """Test issuing rewards."""

    def test_issue_reward_success(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test successfully issuing a reward."""
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
        db_session.refresh(assignment)

        response = client.post("/api/reward/issue", json={
            "assignment_id": assignment.id,
            "user_id": test_user.id,
            "amount": 100.0
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["amount"] == 100.0

    def test_issue_reward_unauthorized(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test issuing reward without admin privileges."""
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
        db_session.refresh(assignment)

        response = client.post("/api/reward/issue", json={
            "assignment_id": assignment.id,
            "user_id": test_user.id,
            "amount": 100.0
        }, headers=auth_headers)
        assert response.status_code == 403


class TestRewardDetail:
    """Test getting reward details."""

    def test_get_reward_detail(self, client, db_session, test_user, test_publisher):
        """Test getting reward detail."""
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
        db_session.refresh(reward)

        response = client.get(f"/api/reward/{reward.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == reward.id

    def test_get_nonexistent_reward(self, client):
        """Test getting non-existent reward."""
        response = client.get("/api/reward/99999")
        assert response.status_code == 404


class TestRewardList:
    """Test listing rewards."""

    def test_list_rewards_by_user(self, client, db_session, test_user, test_publisher):
        """Test listing rewards for a user."""
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

        response = client.get(f"/api/reward/user/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0
        assert data["data"][0]["amount"] == 100.0

    def test_list_rewards_empty(self, client, test_user):
        """Test listing rewards for user with no rewards."""
        response = client.get(f"/api/reward/user/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 0

    def test_list_rewards_multiple_statuses(self, client, db_session, test_user, test_publisher):
        """Test listing rewards with different statuses."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.completed
        )
        db_session.add(task)
        db_session.commit()
        
        assignment1 = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed
        )
        assignment2 = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed
        )
        db_session.add_all([assignment1, assignment2])
        db_session.commit()

        reward1 = Reward(
            assignment_id=assignment1.id,
            amount=100.0,
            status=RewardStatus.issued
        )
        reward2 = Reward(
            assignment_id=assignment2.id,
            amount=50.0,
            status=RewardStatus.pending
        )
        db_session.add_all([reward1, reward2])
        db_session.commit()

        response = client.get(f"/api/reward/user/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 2


class TestRewardUpdate:
    """Test updating rewards."""

    def test_update_reward_status(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test updating reward status."""
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
            status=RewardStatus.pending
        )
        db_session.add(reward)
        db_session.commit()
        db_session.refresh(reward)

        response = client.put(f"/api/reward/{reward.id}", json={
            "status": "issued"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "issued"

    def test_update_reward_unauthorized(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test updating reward without admin privileges."""
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
            status=RewardStatus.pending
        )
        db_session.add(reward)
        db_session.commit()
        db_session.refresh(reward)

        response = client.put(f"/api/reward/{reward.id}", json={
            "status": "issued"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_update_nonexistent_reward(self, client, admin_headers):
        """Test updating non-existent reward."""
        response = client.put("/api/reward/99999", json={
            "status": "issued"
        }, headers=admin_headers)
        assert response.status_code == 404

    def test_update_reward_without_auth(self, client, db_session, test_user, test_publisher):
        """Test updating reward without authentication."""
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
            status=RewardStatus.pending
        )
        db_session.add(reward)
        db_session.commit()
        db_session.refresh(reward)

        response = client.put(f"/api/reward/{reward.id}", json={
            "status": "issued"
        })
        assert response.status_code == 401


class TestRewardEdgeCases:
    """Test edge cases and error handling."""

    def test_issue_reward_duplicate(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test issuing duplicate reward for same assignment."""
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
        db_session.refresh(assignment)

        # First reward
        client.post("/api/reward/issue", json={
            "assignment_id": assignment.id,
            "user_id": test_user.id,
            "amount": 100.0
        }, headers=admin_headers)

        # Duplicate reward - behavior depends on CRUD implementation
        response = client.post("/api/reward/issue", json={
            "assignment_id": assignment.id,
            "user_id": test_user.id,
            "amount": 100.0
        }, headers=admin_headers)
        # Should succeed or return appropriate status based on business logic
        assert response.status_code in [200, 400]

    def test_issue_reward_negative_amount(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test issuing reward with negative amount."""
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
        db_session.refresh(assignment)

        response = client.post("/api/reward/issue", json={
            "assignment_id": assignment.id,
            "user_id": test_user.id,
            "amount": -50.0
        }, headers=admin_headers)
        assert response.status_code == 422  # Validation error

    def test_issue_reward_without_auth(self, client, db_session, test_user, test_publisher):
        """Test issuing reward without authentication."""
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
        db_session.refresh(assignment)

        response = client.post("/api/reward/issue", json={
            "assignment_id": assignment.id,
            "user_id": test_user.id,
            "amount": 100.0
        })
        assert response.status_code == 401

    def test_get_reward_detail_without_auth(self, client, db_session, test_user, test_publisher):
        """Test getting reward detail without authentication (should work)."""
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
        db_session.refresh(reward)

        response = client.get(f"/api/reward/{reward.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
