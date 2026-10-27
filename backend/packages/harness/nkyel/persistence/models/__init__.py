"""ORM model registration entry point.

Importing this module ensures all ORM models are registered with
``Base.metadata`` so Alembic autogenerate detects every table.

The actual ORM classes have moved to entity-specific subpackages:
- ``nkyel.persistence.thread_meta``
- ``nkyel.persistence.run``
- ``nkyel.persistence.feedback``
- ``nkyel.persistence.user``

``RunEventRow`` remains in ``nkyel.persistence.models.run_event`` because
its storage implementation lives in ``nkyel.runtime.events.store.db`` and
there is no matching entity directory.
"""

from nkyel.persistence.agents.model import AgentRow
from nkyel.persistence.channel_connections.model import (
    ChannelConnectionRow,
    ChannelConversationRow,
    ChannelCredentialRow,
    ChannelOAuthStateRow,
)
from nkyel.persistence.channel_leases.model import ChannelLeaseRow
from nkyel.persistence.channel_runtime_configs.model import ChannelRuntimeConfigRow
from nkyel.persistence.channel_thread_bindings.model import ChannelThreadBindingRow
from nkyel.persistence.extension_leases.model import ExtensionExecutionLeaseRow
from nkyel.persistence.feedback.model import FeedbackRow
from nkyel.persistence.login_throttle.model import LoginThrottleRow
from nkyel.persistence.managed_subagents.model import ManagedSubagentRow
from nkyel.persistence.mcp_oauth_tokens.model import McpOAuthTokenRow
from nkyel.persistence.mcp_tasks.model import McpTaskRow
from nkyel.persistence.models.run_event import RunEventRow, RunEventThreadSeqRow
from nkyel.persistence.notification_deliveries.model import NotificationDeliveryRow
from nkyel.persistence.personal_access_tokens.model import PersonalAccessTokenRow
from nkyel.persistence.projects.model import ProjectDocumentRow, ProjectRow
from nkyel.persistence.run.model import RunChangeClockRow, RunRow
from nkyel.persistence.scheduled_task_events.model import ScheduledTaskEventRow
from nkyel.persistence.scheduled_task_runs.model import ScheduledTaskRunRow
from nkyel.persistence.scheduled_tasks.model import ScheduledTaskRow
from nkyel.persistence.skill_mutations.model import SkillAssetRow, SkillOperationRow, SkillOwnerRow, SkillProposalRow
from nkyel.persistence.subagent_batches.model import SubagentBatchItemRow, SubagentBatchRow
from nkyel.persistence.thread_meta.model import ThreadMetaRow
from nkyel.persistence.thread_reads.model import ThreadReadMarkerRow, ThreadReadVersionRow
from nkyel.persistence.user.im_notifications import ImNotificationPreferenceRow
from nkyel.persistence.user.model import UserPreferenceRow, UserRow
from nkyel.persistence.user_mcp_connections.model import UserMcpConnectionRow
from nkyel.persistence.webhook_delivery.model import WebhookDeliveryRow

__all__ = [
    "ExtensionExecutionLeaseRow",
    "AgentRow",
    "ChannelConnectionRow",
    "ChannelConversationRow",
    "ChannelCredentialRow",
    "ChannelLeaseRow",
    "ChannelOAuthStateRow",
    "ChannelRuntimeConfigRow",
    "ChannelThreadBindingRow",
    "FeedbackRow",
    "LoginThrottleRow",
    "McpOAuthTokenRow",
    "McpTaskRow",
    "ManagedSubagentRow",
    "NotificationDeliveryRow",
    "PersonalAccessTokenRow",
    "ProjectDocumentRow",
    "ProjectRow",
    "RunEventRow",
    "RunEventThreadSeqRow",
    "RunChangeClockRow",
    "RunRow",
    "SkillAssetRow",
    "SkillOperationRow",
    "SkillOwnerRow",
    "SkillProposalRow",
    "ScheduledTaskEventRow",
    "ScheduledTaskRow",
    "ScheduledTaskRunRow",
    "SubagentBatchRow",
    "SubagentBatchItemRow",
    "ThreadMetaRow",
    "ThreadReadMarkerRow",
    "ThreadReadVersionRow",
    "UserPreferenceRow",
    "ImNotificationPreferenceRow",
    "UserRow",
    "UserMcpConnectionRow",
    "WebhookDeliveryRow",
]
