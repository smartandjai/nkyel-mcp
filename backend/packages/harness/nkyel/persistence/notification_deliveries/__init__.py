"""Scheduled-task notification delivery outbox persistence (issue #4254)."""

from nkyel.persistence.notification_deliveries.model import NotificationDeliveryRow
from nkyel.persistence.notification_deliveries.sql import NotificationDeliveryRepository

__all__ = [
    "NotificationDeliveryRepository",
    "NotificationDeliveryRow",
]
