### Logging#

AutoGen utilizes Python’s built-in `logging` module for its logging capabilities.

To effectively enable logging specifically for AgentChat interactions, the following Python code snippet can be employed:

```python
import logging
from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)

# For trace logging.
trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

# For structured message logging, such as low-level messages between agents.
event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)
```
This configuration sets a basic logging level to `WARNING` by default. It then specifically configures two distinct loggers: `trace_logger` and `event_logger`. The `trace_logger` is intended for general trace logging and is set to a `DEBUG` level, indicating it will capture very detailed trace information. Similarly, the `event_logger` is dedicated to structured message logging, including low-level communications that occur between agents, and is also configured to `DEBUG` level to ensure comprehensive capture of these events. Both loggers utilize `StreamHandler` to output log messages, typically to the console.

For the purpose of enabling additional logging categories, such as detailed model client calls or specific agent runtime events, users are directed to consult the Core Logging Guide.

---