"""UI-entered IM channel runtime configuration shared by every Gateway instance (``channel_runtime_configs``)."""

from nkyel.persistence.channel_runtime_configs.model import (
    CHANNEL_RUNTIME_CONFIG_PROVIDER_LENGTH,
    ChannelRuntimeConfigRow,
    StoredChannelRuntimeConfig,
)
from nkyel.persistence.channel_runtime_configs.sql import SqlChannelRuntimeConfigRepository

__all__ = [
    "CHANNEL_RUNTIME_CONFIG_PROVIDER_LENGTH",
    "ChannelRuntimeConfigRow",
    "SqlChannelRuntimeConfigRepository",
    "StoredChannelRuntimeConfig",
]
