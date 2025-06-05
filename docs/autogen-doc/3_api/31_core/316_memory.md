# `autogen_core.memory`

### `class ListMemory`

`ListMemory` is a straightforward, chronological list-based memory implementation designed for managing conversational context. This component stores memory contents within a list and retrieves them in the order they were added. A core functionality is its `update_context` method, which appends all stored memories to model contexts, thereby enriching the information available to the model.

The contents of this memory can be directly accessed and modified via its `content` property, providing external applications direct control over the memory state.

**Definition**:
```python
class ListMemory (name : str| None = None , memory_contents : List[MemoryContent] | None = None )[source]
```
Bases: `Memory`, `Component[ ListMemoryConfig ]`

**Example**:
```python
import asyncio
from autogen_core.memory import ListMemory, MemoryContent
from autogen_core.model_context import BufferedChatCompletionContext

async def main() -> None:
    # Initialize memory
    memory = ListMemory(name="chat_history")

    # Add memory content
    content = MemoryContent(content="User prefers formal language", mime_type="text/plain")
    await memory.add(content)

    # Directly modify memory contents
    memory.content = [MemoryContent(content="New preference", mime_type="text/plain")]

    # Create a model context
    model_context = BufferedChatCompletionContext(buffer_size=10)

    # Update a model context with memory
    await memory.update_context(model_context)

    # See the updated model context
    print(await model_context.get_messages())

asyncio.run(main())
```

**Parameters**:
*   **`name`** (`str` | `None`) – An optional identifier for this specific memory instance.

#### `classmethod _from_config`

This class method is responsible for instantiating a new component from a configuration object.

**Definition**:
```python
classmethod _from_config (config : T) → Self[source]
```

**Parameters**:
*   **`config`** (`T`) – The configuration object from which to create the instance.

**Returns**:
*   **`Self`** – The newly created instance of the component.

#### `_to_config`

This method facilitates dumping the configuration required to create a new instance that matches the current instance's configuration.

**Definition**:
```python
_to_config ( ) → ListMemoryConfig[source]
```

**Returns**:
*   **`T`** – The configuration object representing the component's current state.

#### `async add`

Adds new content to the memory store.

**Definition**:
```python
async add (content : MemoryContent, cancellation_token : CancellationToken | None = None ) → None[source]
```

**Parameters**:
*   **`content`** (`MemoryContent`) – The memory content item to be stored.
*   **`cancellation_token`** (`CancellationToken` | `None`) – An optional token that can be used to cancel the operation.

#### `async clear`

Removes all content entries from memory.

**Definition**:
```python
async clear ( ) → None[source]
```

#### `async close`

Performs any necessary cleanup of resources utilized by the memory instance.

**Definition**:
```python
async close ( ) → None[source]
```

#### `component_config_schema`

Alias of `ListMemoryConfig`.

#### `component_provider_override`

`ClassVar[str | None] = 'autogen_core.memory.ListMemory'`
Overrides the provider string for the component, preventing internal module names from becoming part of the module name.

#### `component_type`

`ClassVar[ComponentType] = 'memory'`
Indicates the logical type of the component.

#### `property content`

Provides access to the current list of stored memory contents.

**Definition**:
```python
property content: List[MemoryContent]
```

**Returns**:
*   **`List[MemoryContent]`** – A list containing all stored memory contents.

#### `property name`

Retrieves the identifier assigned to this memory instance.

**Definition**:
```python
property name: str
```

**Returns**:
*   **`str`** – The name of the memory instance.

#### `async query`

Returns all memories without applying any filtering mechanisms. In this specific `ListMemory` implementation, the `query` and `kwargs` parameters are ignored.

**Definition**:
```python
async query (query : str | MemoryContent = '', cancellation_token : CancellationToken | None = None , ** kwargs : Any) → MemoryQueryResult[source]
```

**Parameters**:
*   **`query`** (`str` | `MemoryContent`) – This parameter is ignored in the `ListMemory` implementation.
*   **`cancellation_token`** (`CancellationToken` | `None`) – An optional token for canceling the operation.
*   **`**kwargs`** (`Any`) – Additional parameters; these are also ignored in this implementation.

**Returns**:
*   **`MemoryQueryResult containing all stored memories`**.

#### `async update_context`

Modifies the provided `model_context` by appending all stored memories as `SystemMessage` instances.

**Definition**:
```python
async update_context (model_context : ChatCompletionContext) → UpdateContextResult[source]
```

**Parameters**:
*   **`model_context`** (`ChatCompletionContext`) – The context object to be updated. This object will be mutated if memories are present.

**Returns**:
*   **`UpdateContextResult containing the memories that were added to the context`**.

---

### `class Memory`

The `Memory` class defines a protocol, serving as an abstract interface for various memory implementations. Its primary purpose is to act as a storage mechanism for data that can subsequently be utilized to enrich or modify the model context.

Memory implementations possess the flexibility to employ any underlying storage mechanism, such as a simple list, a database, or a file system. Similarly, they can leverage diverse retrieval mechanisms, including vector search or traditional text search. The specific choice of storage and retrieval mechanisms is left to the discretion of the individual memory implementation.

Furthermore, it is a fundamental responsibility of any memory implementation to dynamically update the model context with pertinent memory content, guided by the current model context and by querying its internal memory store. The `ListMemory` class serves as a concrete example of such an implementation.

**Definition**:
```python
class Memory[source]
```
Bases: `ABC`, `ComponentBase[ BaseModel ]`

#### `abstract async add`

Abstract method to add a new content item to memory.

**Definition**:
```python
abstract async add (content : MemoryContent, cancellation_token : CancellationToken | None = None ) → None[source]
```

**Parameters**:
*   **`content`** (`MemoryContent`) – The memory content to be added.
*   **`cancellation_token`** (`CancellationToken` | `None`) – An optional token to cancel the operation.

#### `abstract async clear`

Abstract method to clear all entries from memory.

**Definition**:
```python
abstract async clear ( ) → None[source]
```

#### `abstract async close`

Abstract method to clean up any resources used by the memory implementation.

**Definition**:
```python
abstract async close ( ) → None[source]
```

#### `component_type`

`ClassVar[ComponentType] = 'memory'`
Signifies the logical type of the component.

#### `abstract async query`

Abstract method to query the memory store and retrieve relevant entries.

**Definition**:
```python
abstract async query (query : str | MemoryContent, cancellation_token : CancellationToken | None = None , ** kwargs : Any) → MemoryQueryResult[source]
```

**Parameters**:
*   **`query`** (`str` | `MemoryContent`) – The content item used for the query.
*   **`cancellation_token`** (`CancellationToken` | `None`) – An optional token for canceling the operation.
*   **`**kwargs`** (`Any`) – Additional implementation-specific parameters.

**Returns**:
*   **`MemoryQueryResult containing memory entries with relevance scores`**.

#### `abstract async update_context`

Abstract method to update the provided model context using relevant memory content.

**Definition**:
```python
abstract async update_context (model_context : ChatCompletionContext) → UpdateContextResult[source]
```

**Parameters**:
*   **`model_context`** (`ChatCompletionContext`) – The context object to be updated.

**Returns**:
*   **`UpdateContextResult containing relevant memories`**.

---

### `pydantic model MemoryContent`

A pydantic model representing a single memory content item.

**Definition**:
```python
pydantic model MemoryContent[source]
```
Bases: `BaseModel`

**JSON Schema**:
```json
{
  "title": "MemoryContent",
  "description": "A memory content item.",
  "type": "object",
  "properties": {
    "content": {
      "anyOf": [
        { "type": "string" },
        { "format": "binary", "type": "string" },
        { "type": "object" },
        {}
      ],
      "title": "Content"
    },
    "mime_type": {
      "anyOf": [
        { "$ref": "#/$defs/MemoryMimeType" },
        { "type": "string" }
      ],
      "title": "Mime Type"
    },
    "metadata": {
      "anyOf": [
        { "type": "object" },
        { "type": "null" }
      ],
      "default": null,
      "title": "Metadata"
    }
  },
  "$defs": {
    "MemoryMimeType": {
      "description": "Supported MIME types for memory content.",
      "enum": [
        "text/plain",
        "application/json",
        "text/markdown",
        "image/*",
        "application/octet-stream"
      ],
      "title": "MemoryMimeType",
      "type": "string"
    }
  },
  "required": [ "content", "mime_type" ]
}
```

**Fields**:
*   `content` (`str` | `bytes` | `Dict[str, Any]` | `autogen_core._image.Image`)
*   `metadata` (`Dict[str, Any]` | `None`)
*   `mime_type` (`autogen_core.memory._base_memory.MemoryMimeType` | `str`)

#### `field content`

**`str` | `bytes` | `Dict[str, Any]` | `Image` `[Required]`**
The actual content of the memory item. This can be a string, bytes, a dictionary, or an Image object.

#### `field metadata`

**`Dict[str, Any]` | `None` `= None`**
Optional metadata associated with the memory item.

#### `field mime_type`

**`MemoryMimeType` | `str` `[Required]`**
The MIME type that describes the memory content.

#### `serialize_mime_type`

Serializes the MIME type, whether it's a `MemoryMimeType` enum or a string, into its string representation.

**Definition**:
```python
serialize_mime_type (mime_type : MemoryMimeType | str) → str[source]
```

---

### `class MemoryMimeType`

An Enum class defining the supported MIME types for memory content.

**Definition**:
```python
class MemoryMimeType (value, names = None, *, module = None, qualname = None, type = None, start = 1, boundary = None)[source]
```
Bases: `Enum`

**Supported MIME Types**:
*   `BINARY = 'application/octet-stream'`
*   `IMAGE = 'image/*'`
*   `JSON = 'application/json'`
*   `MARKDOWN = 'text/markdown'`
*   `TEXT = 'text/plain'`

---

### `pydantic model MemoryQueryResult`

A pydantic model encapsulating the result returned from a memory `query()` operation.

**Definition**:
```python
pydantic model MemoryQueryResult[source]
```
Bases: `BaseModel`

**JSON Schema**:
```json
{
  "title": "MemoryQueryResult",
  "description": "Result of a memory :meth:`~autogen_core.memory.Memory.query` operation.",
  "type": "object",
  "properties": {
    "results": {
      "items": {
        "$ref": "#/$defs/MemoryContent"
      },
      "title": "Results",
      "type": "array"
    }
  },
  "$defs": {
    "MemoryContent": {
      "description": "A memory content item.",
      "properties": {
        "content": {
          "anyOf": [
            { "type": "string" },
            { "format": "binary", "type": "string" },
            { "type": "object" },
            {}
          ],
          "title": "Content"
        },
        "mime_type": {
          "anyOf": [
            { "$ref": "#/$defs/MemoryMimeType" },
            { "type": "string" }
          ],
          "title": "Mime Type"
        },
        "metadata": {
          "anyOf": [
            { "type": "object" },
            { "type": "null" }
          ],
          "default": null,
          "title": "Metadata"
        }
      },
      "required": [ "content", "mime_type" ],
      "title": "MemoryContent",
      "type": "object"
    },
    "MemoryMimeType": {
      "description": "Supported MIME types for memory content.",
      "enum": [
        "text/plain",
        "application/json",
        "text/markdown",
        "image/*",
        "application/octet-stream"
      ],
      "title": "MemoryMimeType",
      "type": "string"
    }
  },
  "required": [ "results" ]
}
```

**Fields**:
*   `results` (`List[autogen_core.memory._base_memory.MemoryContent]`)

#### `field results`

**`List[MemoryContent]` `[Required]`**

---

### `pydantic model UpdateContextResult`

A pydantic model representing the result obtained from a memory `update_context()` operation.

**Definition**:
```python
pydantic model UpdateContextResult[source]
```
Bases: `BaseModel`

**JSON Schema**:
```json
{
  "title": "UpdateContextResult",
  "description": "Result of a memory :meth:`~autogen_core.memory.Memory.update_context` operation.",
  "type": "object",
  "properties": {
    "memories": {
      "$ref": "#/$defs/MemoryQueryResult"
    }
  },
  "$defs": {
    "MemoryContent": {
      "description": "A memory content item.",
      "properties": {
        "content": {
          "anyOf": [
            { "type": "string" },
            { "format": "binary", "type": "string" },
            { "type": "object" },
            {}
          ],
          "title": "Content"
        },
        "mime_type": {
          "anyOf": [
            { "$ref": "#/$defs/MemoryMimeType" },
            { "type": "string" }
          ],
          "title": "Mime Type"
        },
        "metadata": {
          "anyOf": [
            { "type": "object" },
            { "type": "null" }
          ],
          "default": null,
          "title": "Metadata"
        }
      },
      "required": [ "content", "mime_type" ],
      "title": "MemoryContent",
      "type": "object"
    },
    "MemoryMimeType": {
      "description": "Supported MIME types for memory content.",
      "enum": [
        "text/plain",
        "application/json",
        "text/markdown",
        "image/*",
        "application/octet-stream"
      ],
      "title": "MemoryMimeType",
      "type": "string"
    },
    "MemoryQueryResult": {
      "description": "Result of a memory :meth:`~autogen_core.memory.Memory.query` operation.",
      "properties": {
        "results": {
          "items": {
            "$ref": "#/$defs/MemoryContent"
          },
          "title": "Results",
          "type": "array"
        }
      },
      "required": [ "results" ],
      "title": "MemoryQueryResult",
      "type": "object"
    }
  },
  "required": [ "memories" ]
}
```

**Fields**:
*   `memories` (`autogen_core.memory._base_memory.MemoryQueryResult`)

#### `field memories`

**`MemoryQueryResult` `[Required]`**

---

