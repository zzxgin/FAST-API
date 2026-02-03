"""
Notification templates for various business events.

This module provides centralized notification message templates for different events.
"""

NOTIFICATION_TEMPLATES = {
    "review_approved": "Your assignment '{task_title}' has been approved.",
    "review_rejected": "Your assignment '{task_title}' was rejected. Reason: {reason}",
    "appeal_submitted": "Your appeal for assignment '{task_title}' has been submitted.",
}
