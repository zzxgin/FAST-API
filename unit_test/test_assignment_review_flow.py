"""Integration tests for Assignment and Review flows."""

import pytest
import threading
from concurrent.futures import ThreadPoolExecutor
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.review import Review, ReviewResult, ReviewType
from app.models.user import UserRole

class TestAcceptanceFlow:
    """Test flow: Accept Task -> Review Acceptance."""

    def test_accept_and_approve(self, client, auth_headers, admin_headers, db_session, test_publisher, test_user):
        """Test accepting a task and having it approved."""
        # 1. Create Task
        task = Task(
            title="Flow Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 2. User accepts task
        response = client.post("/api/assignment/accept", json={
            "task_id": task.id
        }, headers=auth_headers)
        assert response.status_code == 200
        assignment_id = response.json()["data"]["id"]

        # Verify initial state
        db_session.refresh(task)
        assignment = db_session.query(TaskAssignment).get(assignment_id)
        assert assignment.status == AssignmentStatus.task_pending
        
        # Verify pending review created
        review = db_session.query(Review).filter_by(assignment_id=assignment_id).first()
        assert review is not None
        assert review.review_type == ReviewType.acceptance_review
        assert review.review_result == ReviewResult.pending

        # 3. Admin approves review
        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "approved",
            "review_comment": "Go ahead"
        }, headers=admin_headers)
        assert response.status_code == 200

        # 4. Verify final state
        db_session.refresh(assignment)
        db_session.refresh(task)
        assert assignment.status == AssignmentStatus.task_receive
        assert task.status == TaskStatus.in_progress

    def test_accept_and_reject(self, client, auth_headers, admin_headers, db_session, test_publisher):
        """Test accepting a task and having it rejected."""
        # 1. Create Task
        task = Task(
            title="Flow Test Task 2",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 2. User accepts task
        response = client.post("/api/assignment/accept", json={
            "task_id": task.id
        }, headers=auth_headers)
        assignment_id = response.json()["data"]["id"]

        # Get review
        review = db_session.query(Review).filter_by(assignment_id=assignment_id).first()

        # 3. Admin rejects review
        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "rejected",
            "review_comment": "Not qualified"
        }, headers=admin_headers)
        assert response.status_code == 200

        # 4. Verify final state
        db_session.expire_all()
        assignment = db_session.query(TaskAssignment).get(assignment_id)
        task = db_session.query(Task).get(task.id)
        
        assert assignment.status == AssignmentStatus.task_receivement_rejected
        # Task should remain open or revert to open? 
        # Logic says: if task.status == TaskStatus.open: update_task(..., in_progress) ONLY ON APPROVE.
        # So on reject, it stays open?
        # Actually, accept_task doesn't change task status immediately?
        # Let's check accept_task logic again. It just creates assignment.
        # apply_review_action(approved) -> task.status = in_progress.
        # So initially it is open.
        assert task.status == TaskStatus.open


class TestSubmissionFlow:
    """Test flow: Submit Assignment -> Review Submission."""

    def test_submit_and_approve(self, client, auth_headers, admin_headers, db_session, test_publisher, test_user):
        """Test submitting an assignment and having it approved."""
        # Setup: Task and Assignment in 'task_receive' state (after acceptance approved)
        task = Task(
            title="Submission Flow Task",
            description="Desc",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.in_progress
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

        # 1. User submits assignment
        response = client.post(f"/api/assignment/submit/{assignment.id}", data={
            "submit_content": "Here is my work"
        }, headers=auth_headers)
        assert response.status_code == 200

        # Verify state
        db_session.refresh(assignment)
        assert assignment.status == AssignmentStatus.assignment_submission_pending
        
        # Verify review created
        review = db_session.query(Review).filter_by(
            assignment_id=assignment.id, 
            review_type=ReviewType.submission_review
        ).first()
        assert review is not None
        assert review.review_result == ReviewResult.pending

        # 2. Admin approves
        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "approved",
            "review_comment": "Great job"
        }, headers=admin_headers)
        assert response.status_code == 200

        # 3. Verify final state
        db_session.refresh(assignment)
        db_session.refresh(task)
        assert assignment.status == AssignmentStatus.task_completed
        assert task.status == TaskStatus.completed

    def test_submit_and_reject(self, client, auth_headers, admin_headers, db_session, test_publisher, test_user):
        """Test submitting an assignment and having it rejected."""
        # Setup
        task = Task(
            title="Submission Flow Task 2",
            description="Desc",
            publisher_id=test_publisher.id,
            reward_amount=100.0,
            status=TaskStatus.in_progress # Assuming single assignee for now
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

        # 1. User submits
        client.post(f"/api/assignment/submit/{assignment.id}", data={
            "submit_content": "Bad work"
        }, headers=auth_headers)

        # Get review
        review = db_session.query(Review).filter_by(
            assignment_id=assignment.id, 
            review_type=ReviewType.submission_review
        ).first()

        # 2. Admin rejects
        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "rejected",
            "review_comment": "Redo it"
        }, headers=admin_headers)
        assert response.status_code == 200

        # 3. Verify final state
        db_session.refresh(assignment)
        db_session.refresh(task)
        assert assignment.status == AssignmentStatus.task_reject
        # Logic: if task.status == TaskStatus.completed: update_task(..., in_progress)
        # Here task was in_progress, so it stays in_progress?
        # Wait, if assignment is rejected, the task is still "in progress" because the user failed?
        # Or does it open up for others?
        # The logic says: "管理员只会将任务给一个人，因此作业审核拒绝后任务应回到 in_progress"
        # But it only updates if task.status == completed.
        # Since task was in_progress, it remains in_progress.
        assert task.status == TaskStatus.in_progress


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_review_invalid_status_transition(self, client, admin_headers, db_session, test_publisher, test_user, test_admin):
        """Test trying to approve an assignment that is not in pending state."""
        task = Task(title="T", description="D", publisher_id=test_publisher.id, reward_amount=10, status=TaskStatus.open)
        db_session.add(task)
        db_session.commit()

        # Assignment is already completed
        assignment = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed,
            submit_content="Done"
        )
        db_session.add(assignment)
        db_session.commit()

        # Create a pending review manually (simulating inconsistency or old review)
        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.pending
        )
        db_session.add(review)
        db_session.commit()

        # Try to approve
        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "approved"
        }, headers=admin_headers)
        
        assert response.status_code == 400
        assert "Only assignment_submission_pending" in response.json()["message"]

    def test_review_permission_denied(self, client, auth_headers, db_session, test_publisher, test_user, test_admin):
        """Test non-admin trying to review."""
        task = Task(title="T", description="D", publisher_id=test_publisher.id, reward_amount=10, status=TaskStatus.open)
        db_session.add(task)
        db_session.commit()

        assignment = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.assignment_submission_pending,
            submit_content="Done"
        )
        db_session.add(assignment)
        db_session.commit()

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.pending
        )
        db_session.add(review)
        db_session.commit()

        # User tries to review
        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "approved"
        }, headers=auth_headers)
        
        assert response.status_code == 403


class TestConcurrency:
    """Test concurrency scenarios."""

    # @pytest.mark.skip(reason="SQLite concurrency issues in test environment")
    def test_concurrent_accept_task(self, client, db_session, test_publisher, test_user, test_admin):
        """
        Test multiple users trying to accept the same task simultaneously.
        Note: SQLite might lock, but we want to ensure logic holds.
        """
        from app.core.security import create_access_token
        from app.main import app
        from app.core.database import get_db
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker

        # Setup separate sessions for threads
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
        # Increase timeout to handle locking
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30})
        
        # Enable WAL mode for better concurrency
        with engine.connect() as connection:
            connection.execute(text("PRAGMA journal_mode=WAL"))

        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db_new_session():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        # Override dependency for this test
        app.dependency_overrides[get_db] = override_get_db_new_session

        try:
            task = Task(
                title="Concurrent Task",
                description="Desc",
                publisher_id=test_publisher.id,
                reward_amount=100.0,
                status=TaskStatus.open
            )
            db_session.add(task)
            db_session.commit()
            
            # Create another user
            from app.models.user import User
            user2 = User(username="user2", email="user2@example.com", password_hash="pw", role=UserRole.user)
            db_session.add(user2)
            db_session.commit()

            token1 = create_access_token({"sub": test_user.username})
            token2 = create_access_token({"sub": user2.username})
            
            headers1 = {"Authorization": f"Bearer {token1}"}
            headers2 = {"Authorization": f"Bearer {token2}"}

            def accept_task(headers):
                return client.post("/api/assignment/accept", json={
                    "task_id": task.id
                }, headers=headers)

            # Run in threads
            with ThreadPoolExecutor(max_workers=2) as executor:
                future1 = executor.submit(accept_task, headers1)
                future2 = executor.submit(accept_task, headers2)
                
                resp1 = future1.result()
                resp2 = future2.result()

            assert resp1.status_code == 200
            assert resp2.status_code == 200
            
            # Verify 2 assignments created
            assignments = db_session.query(TaskAssignment).filter_by(task_id=task.id).all()
            assert len(assignments) == 2
        finally:
            # Restore dependency
            app.dependency_overrides = {}


    # @pytest.mark.skip(reason="SQLite concurrency issues in test environment")
    def test_concurrent_review_same_assignment(self, client, admin_headers, db_session, test_publisher, test_user, test_admin):
        """Test concurrent reviews on the same assignment."""
        from app.main import app
        from app.core.database import get_db
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker

        # Setup separate sessions for threads
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30})
        
        # Enable WAL mode
        with engine.connect() as connection:
            connection.execute(text("PRAGMA journal_mode=WAL"))

        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db_new_session():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        # Override dependency for this test
        app.dependency_overrides[get_db] = override_get_db_new_session

        try:
            task = Task(title="T", description="D", publisher_id=test_publisher.id, reward_amount=10, status=TaskStatus.open)
            db_session.add(task)
            db_session.commit()

            assignment = TaskAssignment(
                task_id=task.id,
                user_id=test_user.id,
                status=AssignmentStatus.task_pending
            )
            db_session.add(assignment)
            db_session.commit()

            review = Review(
                assignment_id=assignment.id,
                reviewer_id=test_admin.id,
                review_type=ReviewType.acceptance_review,
                review_result=ReviewResult.pending
            )
            db_session.add(review)
            db_session.commit()

            def submit_review(result):
                return client.post(f"/api/review/{review.id}", json={
                    "review_result": result,
                    "review_comment": "Concurrent"
                }, headers=admin_headers)

            # Run in threads - one approves, one rejects
            with ThreadPoolExecutor(max_workers=2) as executor:
                future1 = executor.submit(submit_review, "approved")
                future2 = executor.submit(submit_review, "rejected")
                
                resp1 = future1.result()
                resp2 = future2.result()

            statuses = [resp1.status_code, resp2.status_code]
            assert 200 in statuses
            # We expect at least one success
            assert statuses.count(200) >= 1
        finally:
            app.dependency_overrides = {}