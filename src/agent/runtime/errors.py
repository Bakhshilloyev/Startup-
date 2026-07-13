"""Runtime errors used across the agent."""

from typing import Optional


class AgentError(Exception):
    """Base class for all agent errors."""


class ConfigError(AgentError):
    """Raised when configuration is missing or invalid."""


class PlatformError(AgentError):
    """Raised when an operation is unsupported on the current platform."""


class ToolError(AgentError):
    """Raised when a tool fails to execute."""


class LLMError(AgentError):
    """Raised when an LLM provider call fails."""

    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class SafetyError(AgentError):
    """Raised when an action is blocked by the policy guard."""


class MemoryError_(AgentError):
    """Raised when the memory store fails."""


class StepFailed(AgentError):
    """Raised when a planned step cannot be completed."""

    def __init__(self, step_id: int, message: str):
        super().__init__(f"step {step_id} failed: {message}")
        self.step_id = step_id
