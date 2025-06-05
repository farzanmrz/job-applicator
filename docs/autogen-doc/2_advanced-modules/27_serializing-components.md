### Serializing Components#

AutoGen provides a `Component` configuration class that defines behaviors to serialize and deserialize components into declarative specifications. This serialization and deserialization functionality is accomplished by calling the `.dump_component()` and `.load_component()` methods, respectively. The utility of this capability extends to debugging, visualizing component configurations, and facilitating the sharing of work. This documentation section will demonstrate how to serialize multiple components to a declarative specification, exemplified by a JSON file.

<div class="admonition warning">
<p class="admonition-title">Warning</p>
<p>ONLY LOAD COMPONENTS FROM TRUSTED SOURCES.</p>
</div>
It is imperative to understand that each serialized component implements its own logic for serialization and deserialization. This inherent logic governs how the declarative specification is generated and subsequently converted back into an object. A critical consideration is that, in certain scenarios, the process of creating an object from a serialized component may necessitate the execution of embedded code, such as a serialized function. Consequently, to mitigate security risks, it is an absolute requirement to **ONLY LOAD COMPONENTS FROM TRUSTED SOURCES**.

#### Termination Condition Example#

This example delineates the process of defining termination conditions, which are integral elements of an agent team, directly within Python. Furthermore, it demonstrates the export of these termination conditions to a dictionary or JSON format and the subsequent loading of the termination condition object from the generated declarative specification.

```python
from autogen_agentchat.conditions import MaxMessageTermination, StopMessageTermination

max_termination = MaxMessageTermination(5)
stop_termination = StopMessageTermination()
or_termination = max_termination | stop_termination

or_term_config = or_termination.dump_component()
print("Config: ", or_term_config.model_dump_json())

new_or_termination = or_termination.load_component(or_term_config)
```

```json
Config: {"provider":"autogen_agentchat.base.OrTerminationCondition","component_type":"termination","version":1,"component_version":1,"description":null,"config":{"conditions":[{"provider":"autogen_agentchat.conditions.MaxMessageTermination","component_type":"termination","version":1,"component_version":1,"config":{"max_messages":5}},{"provider":"autogen_agentchat.conditions.StopMessageTermination","component_type":"termination","version":1,"component_version":1,"config":{}}]}}
```

#### Agent Example#

This example illustrates the definition of an agent in Python, its export to a dictionary or JSON format, and the subsequent loading of the agent object from that dictionary or JSON representation.

```python
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create an agent that uses the OpenAI GPT-4o model.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    # tools=[], # serializing tools is not yet supported
    system_message="Use tools to solve tasks.",
)

user_proxy = UserProxyAgent(name="user")

user_proxy_config = user_proxy.dump_component() # dump component
print(user_proxy_config.model_dump_json())

up_new = user_proxy.load_component(user_proxy_config) # load component
```

```json
{"provider":"autogen_agentchat.agents.UserProxyAgent","component_type":"agent","version":1,"component_version":1,"description":null,"config":{"name":"user","description":"A human user"}}
```

```python
agent_config = agent.dump_component() # dump component
print(agent_config.model_dump_json())

agent_new = agent.load_component(agent_config) # load component
```

```json
{"provider":"autogen_agentchat.agents.AssistantAgent","component_type":"agent","version":1,"component_version":1,"description":null,"config":{"name":"assistant","model_client":{"provider":"autogen_ext.models.openai.OpenAIChatCompletionClient","component_type":"model","version":1,"component_version":1,"config":{"model":"gpt-4o"}},"handoffs":[{"target":"flights_refunder","description":"Handoff to flights_refunder.","name":"transfer_to_flights_refunder","message":"Transferred to flights_refunder, adopting the role of flights_refunder immediately."},{"target":"user","description":"Handoff to user.","name":"transfer_to_user","message":"Transferred to user, adopting the role of user immediately."}],"model_context":{"provider":"autogen_core.model_context.UnboundedChatCompletionContext","component_type":"chat_completion_context","version":1,"component_version":1,"config":{}},"description":"An agent that provides assistance with ability to use tools.","system_message":"Use tools to solve tasks.","reflect_on_tool_use":false,"tool_call_summary_format":"{result}"}}
```

A similar methodology can be applied for the serialization of the `MultiModalWebSurfer` agent.

```python
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

agent = MultimodalWebSurfer(
    name="web_surfer",
    model_client=model_client,
    headless=False,
)

web_surfer_config = agent.dump_component() # dump component
print(web_surfer_config.model_dump_json())
```

#### Team Example#

This example details the procedure for defining a team in Python, exporting it to a dictionary or JSON, and subsequently demonstrating the loading of the team object from the generated declarative specification.

```python
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create an agent that uses the OpenAI GPT-4o model.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    # tools=[], # serializing tools is not yet supported
    system_message="Use tools to solve tasks.",
)

team = RoundRobinGroupChat(
    participants=[agent],
    termination_condition=MaxMessageTermination(2)
)

team_config = team.dump_component() # dump component
print(team_config.model_dump_json())

await model_client.close()
```

```json
{"provider":"autogen_agentchat.teams.RoundRobinGroupChat","component_type":"team","version":1,"component_version":1,"description":null,"config":{"participants":[{"provider":"autogen_agentchat.agents.AssistantAgent","component_type":"agent","version":1,"component_version":1,"config":{"name":"assistant","model_client":{"provider":"autogen_ext.models.openai.OpenAIChatCompletionClient","component_type":"model","version":1,"component_version":1,"config":{"model":"gpt-4o"}},"handoffs":[{"target":"flights_refunder","description":"Handoff to flights_refunder.","name":"transfer_to_flights_refunder","message":"Transferred to flights_refunder, adopting the role of flights_refunder immediately."},{"target":"user","description":"Handoff to user.","name":"transfer_to_user","message":"Transferred to user, adopting the role of user immediately."}],"model_context":{"provider":"autogen_core.model_context.UnboundedChatCompletionContext","component_type":"chat_completion_context","version":1,"component_version":1,"config":{}},"description":"An agent that provides assistance with ability to use tools.","system_message":"Use tools to solve tasks.","reflect_on_tool_use":false,"tool_call_summary_format":"{result}"}}],"termination_condition":{"provider":"autogen_agentchat.conditions.MaxMessageTermination","component_type":"termination","version":1,"component_version":1,"config":{"max_messages":2}}}}
```