"""Feedback persistence — ORM and SQL repository."""

from nkyel.persistence.feedback.model import FeedbackRow
from nkyel.persistence.feedback.sql import FeedbackRepository

__all__ = ["FeedbackRepository", "FeedbackRow"]
