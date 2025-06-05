# autogen_agentchat documentation

## `autogen_agentchat` Module Documentation

This module serves as the primary entry point for the `autogen_agentchat` package. Its scope encompasses the definition of logger names for both trace and event logs, alongside the retrieval of the package version.

### Logger Names

The module explicitly defines constants for specifying the names of loggers used for different logging purposes within the `autogen_agentchat` system.

*   **`EVENT_LOGGER_NAME`**
    ```python
    EVENT_LOGGER_NAME = 'autogen_agentchat.events'
    ```
    This constant holds the designated logger name for event logs. Event logs capture significant occurrences or actions within the application, providing a chronological record of system events.

*   **`TRACE_LOGGER_NAME`**
    ```python
    TRACE_LOGGER_NAME = 'autogen_agentchat'
    ```
    This constant specifies the logger name for trace logs. Trace logs are typically more granular, detailing the flow of execution and internal states, which is invaluable for debugging and in-depth analysis.
