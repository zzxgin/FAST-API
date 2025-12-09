"""Unit tests for Task API endpoints."""

import pytest
from app.models.task import Task, TaskStatus


class TestTaskPublish:
    """Test task publishing endpoint."""

    def test_publish_task_success(self, client, publisher_headers):
        """Test successful task publishing."""
        response = client.post("/api/tasks/publish", json={
            "title": "Test Task",
            "description": "This is a test task",
            "reward_amount": 100.0
        }, headers=publisher_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Test Task"
        assert data["data"]["reward_amount"] == 100.0
        assert data["data"]["status"] == "open"

    def test_publish_task_unauthorized(self, client):
        """Test publishing task without authentication."""
        response = client.post("/api/tasks/publish", json={
            "title": "Test Task",
            "description": "This is a test task",
            "reward_amount": 100.0
        })
        assert response.status_code == 401

    def test_publish_task_invalid_amount(self, client, publisher_headers):
        """Test publishing task with negative reward amount."""
        response = client.post("/api/tasks/publish", json={
            "title": "Test Task",
            "description": "This is a test task",
            "reward_amount": -10.0
        }, headers=publisher_headers)
        assert response.status_code == 422


class TestTaskList:
    """Test task listing endpoints."""

    def test_list_tasks(self, client, db_session, test_publisher):
        """Test listing all tasks."""
        # Create test tasks
        task1 = Task(
            title="Task 1",
            description="Description 1",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        task2 = Task(
            title="Task 2",
            description="Description 2",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.open
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        response = client.get("/api/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 2

    def test_list_tasks_with_pagination(self, client, db_session, test_publisher):
        """Test task listing with pagination."""
        # Create multiple tasks
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                description=f"Description {i}",
                publisher_id=test_publisher.id,
                reward_amount=50.0,
                status=TaskStatus.open
            )
            db_session.add(task)
        db_session.commit()

        response = client.get("/api/tasks/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 3

    def test_list_tasks_by_status(self, client, db_session, test_publisher):
        """Test filtering tasks by status."""
        task = Task(
            title="Open Task",
            description="Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()

        response = client.get("/api/tasks/?status=open")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert all(t["status"] == "open" for t in data["data"])

    def test_list_tasks_with_order_by(self, client, db_session, test_publisher):
        """Test ordering tasks by reward_amount and created_at."""
        # Create tasks with different reward amounts
        task1 = Task(
            title="Low Reward Task",
            description="Description 1",
            publisher_id=test_publisher.id,
            reward_amount=30.0,
            status=TaskStatus.open
        )
        task2 = Task(
            title="High Reward Task",
            description="Description 2",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.open
        )
        task3 = Task(
            title="Medium Reward Task",
            description="Description 3",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add_all([task1, task2, task3])
        db_session.commit()

        # Test order by reward_amount ascending
        response = client.get("/api/tasks/?order_by=reward_amount")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        rewards = [t["reward_amount"] for t in data["data"]]
        assert rewards == sorted(rewards)

        # Test order by created_at descending (newest first)
        response = client.get("/api/tasks/?order_by=created_at")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 3


class TestTaskDetail:
    """Test task detail endpoint."""

    def test_get_task_detail(self, client, db_session, test_publisher):
        """Test getting task detail."""
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

        response = client.get(f"/api/tasks/{task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Test Task"

    def test_get_nonexistent_task(self, client):
        """Test getting non-existent task."""
        response = client.get("/api/tasks/99999")
        assert response.status_code == 404


class TestTaskSearch:
    """Test task search endpoint."""

    def test_search_tasks(self, client, db_session, test_publisher):
        """Test searching tasks by keyword."""
        task = Task(
            title="Python Development Task",
            description="Need a Python developer",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()

        response = client.get("/api/tasks/search/?keyword=Python")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0
        assert "Python" in data["data"][0]["title"]

    def test_search_tasks_no_results(self, client):
        """Test searching tasks with no matching results."""
        response = client.get("/api/tasks/search/?keyword=NonExistentKeyword12345")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 0

    def test_search_tasks_with_pagination(self, client, db_session, test_publisher):
        """Test searching tasks with pagination."""
        # Create multiple tasks with same keyword
        for i in range(5):
            task = Task(
                title=f"JavaScript Task {i}",
                description="JS development",
                publisher_id=test_publisher.id,
                reward_amount=50.0,
                status=TaskStatus.open
            )
            db_session.add(task)
        db_session.commit()

        response = client.get("/api/tasks/search/?keyword=JavaScript&skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) <= 3


class TestTaskUpdate:
    """Test task update endpoint."""

    def test_update_task_as_publisher(self, client, db_session, test_publisher, publisher_headers):
        """Test updating task as the publisher."""
        task = Task(
            title="Original Task",
            description="Original description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(f"/api/tasks/{task.id}", json={
            "title": "Updated Task",
            "reward_amount": 150.0
        }, headers=publisher_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Updated Task"
        assert data["data"]["reward_amount"] == 150.0

    def test_update_task_status(self, client, db_session, test_publisher, publisher_headers):
        """Test updating task status."""
        task = Task(
            title="Test Task",
            description="Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(f"/api/tasks/{task.id}", json={
            "status": "in_progress"
        }, headers=publisher_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "in_progress"

    def test_update_task_unauthorized(self, client, db_session, test_publisher, auth_headers):
        """Test updating task as non-publisher/admin."""
        task = Task(
            title="Test Task",
            description="Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.put(f"/api/tasks/{task.id}", json={
            "title": "Hacked Title"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_update_nonexistent_task(self, client, publisher_headers):
        """Test updating non-existent task."""
        response = client.put("/api/tasks/99999", json={
            "title": "New Title"
        }, headers=publisher_headers)
        assert response.status_code == 404


class TestTaskAccept:
    """Test task acceptance endpoint."""

    def test_accept_task_success(self, client, db_session, test_publisher,auth_headers):
        """Test successful task acceptance."""
        task = Task(
            title="Acceptable Task",
            description="Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.post(f"/api/tasks/accept/{task.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "in_progress"

    def test_accept_task_unauthorized(self, client, db_session, test_publisher):
        """Test accepting task without authentication."""
        task = Task(
            title="Test Task",
            description="Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.post(f"/api/tasks/accept/{task.id}")
        assert response.status_code == 401

    def test_accept_nonexistent_task(self, client, auth_headers):
        """Test accepting non-existent task."""
        response = client.post("/api/tasks/accept/99999", headers=auth_headers)
        assert response.status_code == 400

    def test_accept_task_already_accepted(self, client, db_session, test_publisher, auth_headers):
        """Test accepting a task that is not open."""
        task = Task(
            title="InProgress Task",
            description="Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.in_progress
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        response = client.post(f"/api/tasks/accept/{task.id}", headers=auth_headers)
        assert response.status_code == 400
