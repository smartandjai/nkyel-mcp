"""OpenAI Decisions memory pre-screen: the same cost gate over ``/v1/decisions``.

The gate's meaning is unchanged and lives in the base class: it answers "is this batch worth
paying an extraction call for?", it gates no execution and no write, and every failure direction
still extracts. Only the endpoint differs, so this subclass overrides the three things that
cannot be shared — which service the connection resolves against, which client carries it, and
what the provider is handed to judge — and inherits the rubric, the threshold, the cache and the
audit policy.

Because the answers keep the shared ``NoulAnswer`` / ``AnswerSet`` shape, a deployment can move a
side from Jev to Decisions by editing its ``use:`` path alone, and the coordinator's combining,
cache-bucket and ``request_failed`` behaviour is untouched.

Configuration::

    memory:
      backend_config:
        prescreen:
          mode: shadow
          use: nkyel.agents.memory.prescreen.openai_decisions:OpenAIDecisionsMemoryPrescreen
          config:
            api_key_env: OPENAI_API_KEY
            model: <the decision model this deployment names>
"""

from __future__ import annotations

from nkyel.agents.memory.prescreen.contract import CONFIGURATION_SOURCE
from nkyel.agents.memory.prescreen.typesafe import TypeSafeMemoryPrescreen
from nkyel.openai_decisions.client import OpenAIDecisionsClient, resolve_decisions_connection
from nkyel.typesafe.client import TransportFactory, TypeSafeClient
from nkyel.typesafe.connection import TypeSafeConnection


class OpenAIDecisionsMemoryPrescreen(TypeSafeMemoryPrescreen):
    """Skip the extraction call on a Decisions ``predicate`` probability below ``skip_threshold``."""

    name = "openai_decisions"
    policy_id = "nkyel.memory.prescreen.openai_decisions"
    policy_version = "1.0.0"

    def _resolve_connection(self, settings: dict[str, object]) -> TypeSafeConnection:
        return resolve_decisions_connection(settings=settings, configuration_source=CONFIGURATION_SOURCE)

    def _build_client(self, connection: TypeSafeConnection, *, transport_factory: TransportFactory | None) -> TypeSafeClient:
        return OpenAIDecisionsClient(connection, transport_factory=transport_factory)

    def _judge_state(self, batch_text: str) -> str:
        """The batch text itself: this endpoint's ``input`` is text, not a state object.

        What is judged stays what the Jev side judges — the same
        ``format_conversation_for_update`` output, bounded by the same ``max_state_chars``
        character count — only the envelope around it differs.
        """
        return batch_text


__all__ = ["OpenAIDecisionsMemoryPrescreen"]
