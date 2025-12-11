"""Unit tests for Assignment API endpoints."""

import pytest
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus


class TestAssignmentAccept:
    """Test accepting task assignments."""

    def test_accept_task_success(self, client, auth_headers, db_session, test_publisher):
        """Test successfully accepting a task."""
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

        response = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "I want to accept this task"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["task_id"] == task.id
        
        # Verify task status remains open (until review pproved)
        db_session.refresh(task)
        assert task.status == TaskStatus.open
        
        # Verify assignment status is task_pending
        assert data["data"]["status"] == "task_pending"

    def test_accept_task_duplicate(self, client, auth_headers, db_session, test_publisher):
        """Test accepting the same task twice (should fail)."""
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

        # First acceptance - should succeed
        response1 = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "First acceptance"
        }, headers=auth_headers)
        assert response1.status_code == 200

        # Second acceptance - should fail with 409
        response2 = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "Second acceptance"
        }, headers=auth_headers)
        assert response2.status_code == 409
        assert "already accepted" in response2.json()["message"].lower()

    def test_accept_own_task(self, client, db_session, test_publisher):
        """Test accepting own published task (should fail)."""
        from app.core.security import create_access_token
        
        task = Task(
            title="My Own Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Use publisher's token
        publisher_token = create_access_token({"sub": test_publisher.username})
        publisher_headers = {"Authorization": f"Bearer {publisher_token}"}

        response = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "Trying to accept my own task"
        }, headers=publisher_headers)
        assert response.status_code == 409
        assert "cannot accept your own" in response.json()["message"].lower()

    def test_accept_closed_task(self, client, auth_headers, db_session, test_publisher):
        """Test accepting a closed task (should fail)."""
        task = Task(
            title="Closed Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.closed
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "Trying to accept closed task"
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "not available" in response.json()["message"].lower()

    def test_accept_in_progress_task(self, client, auth_headers, db_session, test_publisher):
        """Test accepting a task that is already in progress (should fail)."""
        task = Task(
            title="In Progress Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.in_progress
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "Trying to accept in-progress task"
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "not available" in response.json()["message"].lower()

    def test_accept_nonexistent_task(self, client, auth_headers):
        """Test accepting non-existent task."""
        response = client.post("/api/assignment/accept", json={
            "task_id": 99999,
            "submit_content": "Test"
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_accept_task_unauthorized(self, client, db_session, test_publisher):
        """Test accepting task without authentication."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()

        response = client.post("/api/assignment/accept", json={
            "task_id": task.id,
            "submit_content": "Test"
        })
        assert response.status_code == 401


class TestAssignmentSubmit:
    """Test submitting assignment content."""

    def test_submit_assignment_text(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test submitting assignment with text content."""
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
            status=AssignmentStatus.task_receive
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post(
            f"/api/assignment/submit/{assignment.id}",
            data={"submit_content": "My submission content"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_submit_nonexistent_assignment(self, client, auth_headers):
        """Test submitting non-existent assignment."""
        response = client.post(
            "/api/assignment/submit/99999",
            data={"submit_content": "Test"},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestAssignmentProgress:
    """Test updating assignment progress."""

    def test_update_progress(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test updating assignment progress."""
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
            status=AssignmentStatus.task_receive
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.patch(
            f"/api/assignment/{assignment.id}/progress",
            json={"status": "task_completed"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestAssignmentDetail:
    """Test getting assignment details."""

    def test_get_assignment_detail(self, client, db_session, test_user, test_publisher):
        """Test getting assignment detail."""
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
            submit_content="Test submission",
            status=AssignmentStatus.task_receive
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.get(f"/api/assignment/{assignment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == assignment.id

    def test_get_nonexistent_assignment(self, client):
        """Test getting non-existent assignment."""
        response = client.get("/api/assignment/99999")
        assert response.status_code == 404


class TestAssignmentList:
    """Test listing user assignments."""

    def test_list_user_assignments(self, client, db_session, test_user, test_publisher):
        """Test listing assignments by user."""
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
            status=AssignmentStatus.task_receive
        )
        db_session.add(assignment)
        db_session.commit()

        response = client.get(f"/api/assignment/user/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0
