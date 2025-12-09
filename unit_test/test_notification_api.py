"""Unit tests for Notification API endpoints."""

import pytest
from app.models.notification import Notification


class TestNotificationSend:
    """Test sending notifications."""

    def test_send_notification_success(self, client, admin_headers, test_user):
        """Test successfully sending a notification."""
        response = client.post("/api/notifications/send", json={
            "user_id": test_user.id,
            "content": "Test notification message"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["content"] == "Test notification message"

    def test_send_notification_unauthorized(self, client, auth_headers, test_user):
        """Test sending notification without admin privileges."""
        response = client.post("/api/notifications/send", json={
            "user_id": test_user.id,
            "content": "Test notification"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_send_notification_nonexistent_user(self, client, admin_headers):
        """Test sending notification to non-existent user."""
        response = client.post("/api/notifications/send", json={
            "user_id": 99999,
            "content": "Test notification"
        }, headers=admin_headers)
        assert response.status_code == 404


class TestNotificationList:
    """Test listing notifications."""

    def test_list_user_notifications(self, client, auth_headers, db_session, test_user):
        """Test listing notifications for a user."""
        notification = Notification(
            user_id=test_user.id,
            content="Test notification",
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()

        response = client.get(f"/api/notifications/user/{test_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) > 0

    def test_list_notifications_unauthorized(self, client):
        """Test listing notifications without authentication."""
        response = client.get("/api/notifications/user/1")
        assert response.status_code == 401


class TestNotificationRead:
    """Test marking notifications as read."""

    def test_mark_notification_read(self, client, auth_headers, db_session, test_user):
        """Test marking a notification as read."""
        notification = Notification(
            user_id=test_user.id,
            content="Test notification",
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)

        response = client.patch(
            f"/api/notifications/{notification.id}/read",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["is_read"] is True

    def test_mark_nonexistent_notification_read(self, client, auth_headers):
        """Test marking non-existent notification as read."""
        response = client.patch(
            "/api/notifications/99999/read",
            headers=auth_headers
        )
        assert response.status_code == 404
