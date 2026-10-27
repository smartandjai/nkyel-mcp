"""Per-user read state of threads (server-created threads stay unread until opened)."""

from nkyel.persistence.thread_reads.model import ThreadReadMarkerRow, ThreadReadVersionRow
from nkyel.persistence.thread_reads.sql import ThreadReadRepository

__all__ = [
    "ThreadReadMarkerRow",
    "ThreadReadRepository",
    "ThreadReadVersionRow",
]
