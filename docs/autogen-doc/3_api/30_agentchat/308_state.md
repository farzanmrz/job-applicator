# autogen_agentchat.state

State management for agents, teams and termination conditions.

---

### pydantic model AssistantAgentState
Bases: BaseState

State for an assistant agent.

**Show JSON schema**
```json
{
  "title": "AssistantAgentState",
  "description": "State for an assistant agent.",
  "type": "object",
  "properties": {
    "type": {
      "default": "AssistantAgentState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "llm_context": {
      "title": "Llm Context",
      "type": "object"
    }
  }
}
```

**Fields**:
*   `llm_context` (Mapping[str, Any])
    *field* `llm_context`: Mapping[str, Any] [*Optional*]
*   `type` (str)
    *field* `type`: str *= 'AssistantAgentState'*

---

### pydantic model BaseGroupChatManagerState
Bases: BaseState

Base state for all group chat managers.

**Show JSON schema**
```json
{
  "title": "BaseGroupChatManagerState",
  "description": "Base state for all group chat managers.",
  "type": "object",
  "properties": {
    "type": {
      "default": "BaseGroupChatManagerState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "message_thread": {
      "items": {
        "type": "object"
      },
      "title": "Message Thread",
      "type": "array"
    },
    "current_turn": {
      "default": 0,
      "title": "Current Turn",
      "type": "integer"
    }
  }
}
```

**Fields**:
*   `current_turn` (int)
    *field* `current_turn`: int *= 0*
*   `message_thread` (List[Mapping[str, Any]])
    *field* `message_thread`: List[Mapping[str, Any]] [*Optional*]
*   `type` (str)
    *field* `type`: str *= 'BaseGroupChatManagerState'*

---

### pydantic model BaseState
Bases: BaseModel

Base class for all saveable state

**Show JSON schema**
```json
{
  "title": "BaseState",
  "description": "Base class for all saveable state",
  "type": "object",
  "properties": {
    "type": {
      "default": "BaseState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    }
  }
}
```

**Fields**:
*   `type` (str)
    *field* `type`: str *= 'BaseState'*
*   `version` (str)
    *field* `version`: str *= '1.0.0'*

---

### pydantic model ChatAgentContainerState
Bases: BaseState

State for a container of chat agents.

**Show JSON schema**
```json
{
  "title": "ChatAgentContainerState",
  "description": "State for a container of chat agents.",
  "type": "object",
  "properties": {
    "type": {
      "default": "ChatAgentContainerState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "agent_state": {
      "title": "Agent State",
      "type": "object"
    },
    "message_buffer": {
      "items": {
        "type": "object"
      },
      "title": "Message Buffer",
      "type": "array"
    }
  }
}
```

**Fields**:
*   `agent_state` (Mapping[str, Any])
    *field* `agent_state`: Mapping[str, Any] [*Optional*]
*   `message_buffer` (List[Mapping[str, Any]])
    *field* `message_buffer`: List[Mapping[str, Any]] [*Optional*]
*   `type` (str)
    *field* `type`: str *= 'ChatAgentContainerState'*

---

### pydantic model MagenticOneOrchestratorState
Bases: BaseGroupChatManagerState

State for MagneticOneGroupChat orchestrator.

**Show JSON schema**
```json
{
  "title": "MagenticOneOrchestratorState",
  "description": "State for :class:`~autogen_agentchat.teams.MagneticOneGroupChat` orchestrator.",
  "type": "object",
  "properties": {
    "type": {
      "default": "MagenticOneOrchestratorState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "message_thread": {
      "items": {
        "type": "object"
      },
      "title": "Message Thread",
      "type": "array"
    },
    "current_turn": {
      "default": 0,
      "title": "Current Turn",
      "type": "integer"
    },
    "task": {
      "default": "",
      "title": "Task",
      "type": "string"
    },
    "facts": {
      "default": "",
      "title": "Facts",
      "type": "string"
    },
    "plan": {
      "default": "",
      "title": "Plan",
      "type": "string"
    },
    "n_rounds": {
      "default": 0,
      "title": "N Rounds",
      "type": "integer"
    },
    "n_stalls": {
      "default": 0,
      "title": "N Stalls",
      "type": "integer"
    }
  }
}
```

**Fields**:
*   `facts` (str)
    *field* `facts`: str *= ''*
*   `n_rounds` (int)
    *field* `n_rounds`: int *= 0*
*   `n_stalls` (int)
    *field* `n_stalls`: int *= 0*
*   `plan` (str)
    *field* `plan`: str *= ''*
*   `task` (str)
    *field* `task`: str *= ''*
*   `type` (str)
    *field* `type`: str *= 'MagenticOneOrchestratorState'*

---

### pydantic model RoundRobinManagerState
Bases: BaseGroupChatManagerState

State for RoundRobinGroupChat manager.

**Show JSON schema**
```json
{
  "title": "RoundRobinManagerState",
  "description": "State for :class:`~autogen_agentchat.teams.RoundRobinGroupChat` manager.",
  "type": "object",
  "properties": {
    "type": {
      "default": "RoundRobinManagerState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "message_thread": {
      "items": {
        "type": "object"
      },
      "title": "Message Thread",
      "type": "array"
    },
    "current_turn": {
      "default": 0,
      "title": "Current Turn",
      "type": "integer"
    },
    "next_speaker_index": {
      "default": 0,
      "title": "Next Speaker Index",
      "type": "integer"
    }
  }
}
```

**Fields**:
*   `next_speaker_index` (int)
    *field* `next_speaker_index`: int *= 0*
*   `type` (str)
    *field* `type`: str *= 'RoundRobinManagerState'*

---

### pydantic model SelectorManagerState
Bases: BaseGroupChatManagerState

State for SelectorGroupChat manager.

**Show JSON schema**
```json
{
  "title": "SelectorManagerState",
  "description": "State for :class:`~autogen_agentchat.teams.SelectorGroupChat` manager.",
  "type": "object",
  "properties": {
    "type": {
      "default": "SelectorManagerState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "message_thread": {
      "items": {
        "type": "object"
      },
      "title": "Message Thread",
      "type": "array"
    },
    "current_turn": {
      "default": 0,
      "title": "Current Turn",
      "type": "integer"
    },
    "previous_speaker": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Previous Speaker"
    }
  }
}
```

**Fields**:
*   `previous_speaker` (str | None)
    *field* `previous_speaker`: str| None *= None*
*   `type` (str)
    *field* `type`: str *= 'SelectorManagerState'*

---

### pydantic model SocietyOfMindAgentState
Bases: BaseState

State for a Society of Mind agent.

**Show JSON schema**
```json
{
  "title": "SocietyOfMindAgentState",
  "description": "State for a Society of Mind agent.",
  "type": "object",
  "properties": {
    "type": {
      "default": "SocietyOfMindAgentState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "inner_team_state": {
      "title": "Inner Team State",
      "type": "object"
    }
  }
}
```

**Fields**:
*   `inner_team_state` (Mapping[str, Any])
    *field* `inner_team_state`: Mapping[str, Any] [*Optional*]
*   `type` (str)
    *field* `type`: str *= 'SocietyOfMindAgentState'*

---

### pydantic model SwarmManagerState
Bases: BaseGroupChatManagerState

State for Swarm manager.

**Show JSON schema**
```json
{
  "title": "SwarmManagerState",
  "description": "State for :class:`~autogen_agentchat.teams.Swarm` manager.",
  "type": "object",
  "properties": {
    "type": {
      "default": "SwarmManagerState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "message_thread": {
      "items": {
        "type": "object"
      },
      "title": "Message Thread",
      "type": "array"
    },
    "current_turn": {
      "default": 0,
      "title": "Current Turn",
      "type": "integer"
    },
    "current_speaker": {
      "default": "",
      "title": "Current Speaker",
      "type": "string"
    }
  }
}
```

**Fields**:
*   `current_speaker` (str)
    *field* `current_speaker`: str *= ''*
*   `type` (str)
    *field* `type`: str *= 'SwarmManagerState'*

---

### pydantic model TeamState
Bases: BaseState

State for a team of agents.

**Show JSON schema**
```json
{
  "title": "TeamState",
  "description": "State for a team of agents.",
  "type": "object",
  "properties": {
    "type": {
      "default": "TeamState",
      "title": "Type",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "title": "Version",
      "type": "string"
    },
    "agent_states": {
      "title": "Agent States",
      "type": "object"
    }
  }
}
```

**Fields**:
*   `agent_states` (Mapping[str, Any])
    *field* `agent_states`: Mapping[str, Any] [*Optional*]
*   `type` (str)
    *field* `type`: str *= 'TeamState'*
