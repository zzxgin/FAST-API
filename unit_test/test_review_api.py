"""Unit tests for Review API endpoints."""

import pytest
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.review import Review, ReviewResult, ReviewType


class TestReviewSubmit:
    """Test submitting reviews."""

    def test_submit_review_success(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test successfully submitting a review."""
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
            submit_content="My submission",
            status=AssignmentStatus.assignment_submission_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post("/api/review/submit", json={
            "assignment_id": assignment.id,
            "review_type": "submission_review",
            "review_result": "approved",
            "review_comment": "Good work!"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["review_result"] == "approved"

    def test_submit_review_rejected(self, client, admin_headers, db_session, test_user, test_publisher):
        """Test submitting a rejected review."""
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
            submit_content="Poor submission",
            status=AssignmentStatus.assignment_submission_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post("/api/review/submit", json={
            "assignment_id": assignment.id,
            "review_type": "submission_review",
            "review_result": "rejected",
            "review_comment": "Does not meet requirements"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["review_result"] == "rejected"
        assert "requirements" in data["data"]["review_comment"]

    def test_submit_review_unauthorized(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test submitting review without admin privileges."""
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
            status=AssignmentStatus.task_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post("/api/review/submit", json={
            "assignment_id": assignment.id,
            "review_type": "acceptance_review",
            "review_result": "approved",
            "review_comment": "Good work!"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_submit_review_nonexistent_assignment(self, client, admin_headers):
        """Test submitting review for non-existent assignment."""
        response = client.post("/api/review/submit", json={
            "assignment_id": 99999,
            "review_type": "acceptance_review",
            "review_result": "approved",
            "review_comment": "Good work!"
        }, headers=admin_headers)
        assert response.status_code == 404

    def test_submit_review_without_auth(self, client, db_session, test_user, test_publisher):
        """Test submitting review without authentication."""
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
            status=AssignmentStatus.task_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post("/api/review/submit", json={
            "assignment_id": assignment.id,
            "review_type": "acceptance_review",
            "review_result": "approved",
            "review_comment": "Good work!"
        })
        assert response.status_code == 401

    def test_submit_review_duplicate(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test submitting duplicate review."""
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
            status=AssignmentStatus.task_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        # First review
        client.post("/api/review/submit", json={
            "assignment_id": assignment.id,
            "review_type": "acceptance_review",
            "review_result": "approved",
            "review_comment": "Good work!"
        }, headers=admin_headers)

        # Duplicate review
        response = client.post("/api/review/submit", json={
            "assignment_id": assignment.id,
            "review_type": "acceptance_review",
            "review_result": "approved",
            "review_comment": "Good work again!"
        }, headers=admin_headers)
        assert response.status_code == 400


class TestReviewAppeal:
    """Test appealing reviews."""

    def test_appeal_review(self, client, auth_headers, db_session, test_user, test_publisher, test_admin):
        """Test appealing a rejected assignment."""
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
            status=AssignmentStatus.task_reject
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.rejected,
            review_comment="Needs improvement"
        )
        db_session.add(review)
        db_session.commit()

        response = client.post(f"/api/assignment/appeal/{assignment.id}", headers=auth_headers, data={"appeal_reason": "I disagree"})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_appeal_approved_assignment(self, client, auth_headers, db_session, test_user, test_publisher, test_admin):
        """Test appealing an approved assignment."""
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
        db_session.refresh(assignment)

        response = client.post(f"/api/assignment/appeal/{assignment.id}", headers=auth_headers, data={"appeal_reason": "I want to redo"})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_appeal_nonexistent_assignment(self, client, auth_headers):
        """Test appealing non-existent assignment."""
        response = client.post("/api/assignment/appeal/99999", headers=auth_headers, data={"appeal_reason": "test"})
        assert response.status_code == 404

    def test_appeal_not_owner(self, client, publisher_headers, db_session, test_user, test_publisher):
        """Test appealing assignment not owned by user."""
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
            status=AssignmentStatus.task_reject
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post(f"/api/assignment/appeal/{assignment.id}", headers=publisher_headers, data={"appeal_reason": "test"})
        assert response.status_code == 403

    def test_appeal_without_auth(self, client, db_session, test_user, test_publisher):
        """Test appealing without authentication."""
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
            status=AssignmentStatus.task_reject
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post(f"/api/assignment/appeal/{assignment.id}", data={"appeal_reason": "test"})
        assert response.status_code == 401

    def test_appeal_pending_assignment(self, client, auth_headers, db_session, test_user, test_publisher):
        """Test appealing pending assignment (should fail)."""
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
            status=AssignmentStatus.task_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.post(f"/api/assignment/appeal/{assignment.id}", headers=auth_headers, data={"appeal_reason": "test"})
        assert response.status_code == 400


class TestReviewDetail:
    """Test getting review details."""

    def test_get_review_detail(self, client, db_session, test_user, test_publisher, test_admin):
        """Test getting review detail."""
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

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.get(f"/api/review/{review.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == review.id

    def test_get_nonexistent_review(self, client):
        """Test getting non-existent review."""
        response = client.get("/api/review/99999")
        assert response.status_code == 404


class TestReviewList:
    """Test listing reviews."""

    def test_list_reviews_by_assignment(self, client, db_session, test_user, test_publisher, test_admin):
        """Test listing reviews for an assignment."""
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
        db_session.refresh(assignment)

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review)
        db_session.commit()

        response = client.get(f"/api/review/assignment/{assignment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0

    def test_list_reviews_empty(self, client, db_session, test_user, test_publisher):
        """Test listing reviews for assignment with no reviews."""
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
            status=AssignmentStatus.task_pending
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        response = client.get(f"/api/review/assignment/{assignment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 0

    def test_list_reviews_multiple(self, client, db_session, test_user, test_publisher, test_admin):
        """Test listing multiple reviews for assignment."""
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
            status=AssignmentStatus.appealing
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        review1 = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.rejected,
            review_comment="First rejection"
        )
        review2 = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.appeal_review,
            review_result=ReviewResult.pending,
            review_comment="Appeal submitted"
        )
        db_session.add_all([review1, review2])
        db_session.commit()

        response = client.get(f"/api/review/assignment/{assignment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 2


class TestReviewListAll:
    """Test listing all reviews (admin/publisher)."""

    def test_list_reviews_admin(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test admin listing all reviews."""
        # Create a task and review
        task = Task(
            title="Admin List Task",
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

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review)
        db_session.commit()

        response = client.get("/api/review/list", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 1
        # Verify the created review is in the list
        found = False
        for r in data["data"]:
            if r["id"] == review.id:
                found = True
                break
        assert found

    def test_list_reviews_publisher(self, client, db_session, test_user, test_publisher, test_admin):
        """Test publisher listing reviews for their tasks."""
        from app.core.security import create_access_token
        
        # Task 1: Published by test_publisher
        task1 = Task(
            title="Publisher Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task1)
        db_session.commit()
        
        assignment1 = TaskAssignment(
            task_id=task1.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed
        )
        db_session.add(assignment1)
        db_session.commit()

        review1 = Review(
            assignment_id=assignment1.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review1)
        db_session.commit()

        # Task 2: Published by admin (another user)
        task2 = Task(
            title="Admin Task",
            description="Test Description",
            publisher_id=test_admin.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task2)
        db_session.commit()
        
        assignment2 = TaskAssignment(
            task_id=task2.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed
        )
        db_session.add(assignment2)
        db_session.commit()

        review2 = Review(
            assignment_id=assignment2.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review2)
        db_session.commit()

        # Use publisher's token
        publisher_token = create_access_token({"sub": test_publisher.username})
        publisher_headers = {"Authorization": f"Bearer {publisher_token}"}

        response = client.get("/api/review/list", headers=publisher_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        # Should find review1 but NOT review2
        found1 = False
        found2 = False
        for r in data["data"]:
            if r["id"] == review1.id:
                found1 = True
            if r["id"] == review2.id:
                found2 = True
        
        assert found1
        assert not found2

    def test_list_reviews_user_forbidden(self, client, auth_headers):
        """Test normal user cannot list reviews."""
        response = client.get("/api/review/list", headers=auth_headers)
        assert response.status_code == 403

    def test_list_reviews_filter_type(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test filtering reviews by type."""
        task = Task(
            title="Filter Task",
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

        # Review 1: Submission Review
        review1 = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        # Review 2: Acceptance Review
        review2 = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.acceptance_review,
            review_result=ReviewResult.approved,
            review_comment="Accepted"
        )
        db_session.add_all([review1, review2])
        db_session.commit()

        # Filter by submission_review
        response = client.get("/api/review/list?review_type=submission_review", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        for r in data["data"]:
            assert r["review_type"] == "submission_review"
            
        # Verify we found at least one
        assert len(data["data"]) >= 1

    def test_list_reviews_filter_result(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test filtering reviews by result."""
        task = Task(
            title="Filter Result Task",
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

        # Review 1: Approved
        review1 = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        # Review 2: Rejected
        review2 = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.rejected,
            review_comment="Bad work"
        )
        db_session.add_all([review1, review2])
        db_session.commit()

        # Filter by rejected
        response = client.get("/api/review/list?review_result=rejected", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        for r in data["data"]:
            assert r["review_result"] == "rejected"
            
        # Verify we found at least one
        assert len(data["data"]) >= 1


class TestReviewUpdate:
    """Test updating reviews."""

    def test_update_review_success(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test updating review comment."""
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
            status=AssignmentStatus.task_completed,
            submit_content="http://example.com/submission"
        )
        db_session.add(assignment)
        db_session.commit()

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.post(f"/api/review/{review.id}", json={
            "review_comment": "Updated comment: Excellent work!"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "Excellent" in data["data"]["review_comment"]

    def test_update_review_result(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test updating review result."""
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
            status=AssignmentStatus.task_pending
        )
        db_session.add(assignment)
        db_session.commit()

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.acceptance_review,
            review_result=ReviewResult.pending,
            review_comment="Under review"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "approved"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["review_result"] == "approved"

    def test_update_review_unauthorized(self, client, auth_headers, db_session, test_user, test_publisher, test_admin):
        """Test updating review without admin privileges."""
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
            status=AssignmentStatus.task_completed,
            submit_content="http://example.com/submission"
        )
        db_session.add(assignment)
        db_session.commit()

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.post(f"/api/review/{review.id}", json={
            "review_comment": "Hacked comment"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_update_nonexistent_review(self, client, admin_headers):
        """Test updating non-existent review."""
        response = client.post("/api/review/99999", json={
            "review_comment": "Updated comment"
        }, headers=admin_headers)
        assert response.status_code == 404

    def test_update_review_without_auth(self, client, db_session, test_user, test_publisher, test_admin):
        """Test updating review without authentication."""
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
            status=AssignmentStatus.task_completed,
            submit_content="http://example.com/submission"
        )
        db_session.add(assignment)
        db_session.commit()

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.submission_review,
            review_result=ReviewResult.approved,
            review_comment="Good work!"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.post(f"/api/review/{review.id}", json={
            "review_comment": "Updated comment"
        })
        assert response.status_code == 401

    def test_update_review_invalid_status(self, client, admin_headers, db_session, test_user, test_publisher, test_admin):
        """Test updating review when assignment status is invalid."""
        task = Task(
            title="Test Task",
            description="Test Description",
            publisher_id=test_publisher.id,
            reward_amount=50.0,
            status=TaskStatus.open
        )
        db_session.add(task)
        db_session.commit()
        
        # Assignment is already completed, so acceptance review should fail
        assignment = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            status=AssignmentStatus.task_completed
        )
        db_session.add(assignment)
        db_session.commit()

        review = Review(
            assignment_id=assignment.id,
            reviewer_id=test_admin.id,
            review_type=ReviewType.acceptance_review,
            review_result=ReviewResult.pending,
            review_comment="Under review"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.post(f"/api/review/{review.id}", json={
            "review_result": "approved"
        }, headers=admin_headers)
        assert response.status_code == 400
        assert "Only task_pending assignments can be reviewed" in response.json()["message"]
