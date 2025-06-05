# autogen_core.tools

### `autogen_core.tools`

*class* `BaseTool` ( `args_type` : `Type` `[ ArgsT ]` , `return_type` : `Type` `[ ReturnT ]` , `name` : `str`, `description` : `str`, `strict` : `bool` *= `False` )[source]#Bases: `ABC`, `Tool`, `Generic`[`ArgsT`, `ReturnT`], `ComponentBase`[`BaseModel`]

`args_type` ( ) → `Type`[`BaseModel`][source]#

`component_type` *: `ClassVar` [`ComponentType`]* *= `'tool'`* #The logical type of the component.

*property* `description`: `str`#

*async* `load_state_json` ( `state` : `Mapping`[`str`, `Any`*] ) → `None`[source]#

*property* `name`: `str`#

`return_type` ( ) → `Type`[`Any`][source]#

`return_value_as_string` ( `value` : `Any`) → `str`[source]#

*abstract async* `run` ( *`args` : `ArgsT`* , `cancellation_token` : `CancellationToken`) → `ReturnT`[source]#

*async* `run_json` ( `args` : `Mapping`[`str`, `Any`*] , `cancellation_token` : `CancellationToken`) → `Any`[source]#

*async* `save_state_json` ( ) → `Mapping`[`str`, `Any`][source]#

*property* `schema`: `ToolSchema`#

`state_type` ( ) → `Type`[`BaseModel`] | `None`[source]#

*class* `BaseToolWithState` ( `args_type` : `Type` `[ ArgsT ]` , `return_type` : `Type` `[ ReturnT ]` , `state_type` : `Type` `[ StateT ]` , `name` : `str`, `description` : `str`)[source]#Bases: `BaseTool`[`ArgsT`, `ReturnT`], `ABC`, `Generic`[`ArgsT`, `ReturnT`, `StateT`], `ComponentBase`[`BaseModel`]

`component_type` *: `ClassVar` [`ComponentType`]* *= `'tool'`* #The logical type of the component.

*abstract* `load_state` ( *`state` : `StateT`* ) → `None`[source]#

*async* `load_state_json` ( `state` : `Mapping`[`str`, `Any`*] ) → `None`[source]#

*abstract* `save_state` ( ) → `StateT`[source]#

*async* `save_state_json` ( ) → `Mapping`[`str`, `Any`][source]#

*class* `FunctionTool` ( `func` : `Callable`[ `[ ... ]` , `Any`*] , `description` : `str`, `name` : `str`| `None` *= `None`* , `global_imports` : `Sequence`[`str`| `ImportFromModule`| `Alias`*] `= []`* , `strict` : `bool` *= `False`* )[source]#Bases: `BaseTool`[`BaseModel`, `BaseModel`], `Component`[`FunctionToolConfig`]

`FunctionTool` provides an interface for executing Python functions, supporting both asynchronous and synchronous operations. To enable input validation, serialization, and to inform the Large Language Model (LLM) about expected parameters, each wrapped function must include type annotations for all its parameters and its return type. The LLM utilizes this schema when preparing a function call to generate arguments that conform to the function's specifications.

Note: It is the user’s responsibility to verify that the tool’s output type matches the expected type.

**Parameters**:

*   **`func`** (`Callable`[`...`, `ReturnT` | `Awaitable`[`ReturnT`]]): The Python function to be wrapped and exposed as a tool.
*   **`description`** (`str`): A descriptive string that informs the model about the function’s purpose, detailing what it does and the appropriate context for its invocation.
*   **`name`** (`str`, *optional*): An optional custom name for the tool. If not provided, the function’s original name will be used by default.
*   **`strict`** (`bool`, *optional*): If set to `True`, the tool schema will exclusively contain arguments explicitly defined in the function signature, disallowing default values. This parameter *must* be set to `True` when the tool is utilized with models operating in structured output mode. Defaults to `False`.

**Example**:

```python
import   random
from   autogen_core   import   CancellationToken
from   autogen_core.tools   import   FunctionTool
from   typing_extensions   import   Annotated
import   asyncio

async   def   get_stock_price ( ticker :   str ,   date :   Annotated [ str ,   "Date in YYYY/MM/DD" ])   ->   float :
    # Simulates a stock price retrieval by returning a random float within a specified range.
    return   random . uniform ( 10 ,   200 )

async   def   example ():
    # Initialize a FunctionTool instance for retrieving stock prices.
    stock_price_tool   =   FunctionTool ( get_stock_price ,   description = "Fetch the stock price for a given ticker." )

    # Execute the tool with cancellation support.
    cancellation_token   =   CancellationToken ()
    result   =   await   stock_price_tool . run_json ({ "ticker" :   "AAPL" ,   "date" :   "2021/01/01" },   cancellation_token )

    # Output the result as a formatted string.
    print ( stock_price_tool . return_value_as_string ( result ))

asyncio . run ( example ())
```

*classmethod* `_from_config` ( *`config` : `FunctionToolConfig`* ) → `Self`[source]#Create a new instance of the component from a configuration object.

**Parameters**:

*   **`config`** (`T`): The configuration object.

**Returns**:

*   **`Self`**: The new instance of the component.

`_to_config` ( ) → `FunctionToolConfig`[source]#Dump the configuration that would be requite to create a new instance of a component matching the configuration of this instance.

**Returns**:

*   **`T`**: The configuration of the component.

`component_config_schema`#alias of `FunctionToolConfig`

`component_provider_override`: `ClassVar`[`str`| `None`*] *= `'autogen_core.tools.FunctionTool'`* #Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

*async* `run` ( *`args` : `BaseModel`* , `cancellation_token` : `CancellationToken`) → `Any`[source]#

*pydantic model* `ImageResultContent`[source]#Bases: `BaseModel`

`ImageResultContent` represents the image content resulting from a tool execution.

Show JSON schema:
```json
{
   "title" :   "ImageResultContent" ,
   "description" :   "Image result content of a tool execution." ,
   "type" :   "object" ,
   "properties" :   {
      "type" :   {
         "const" :   "ImageResultContent" ,
         "default" :   "ImageResultContent" ,
         "title" :   "Type" ,
         "type" :   "string"
      },
      "content" :   {
         "title" :   "Content"
      }
   },
   "required" :   [   "content"   ]
}
```

**Fields**:

*   `content` (`autogen_core._image.Image`)
*   `type` (`Literal['ImageResultContent']`)

*field* `content`: `Image` *[Required]* #The image content of the result.

*field* `type`: `Literal`[`'ImageResultContent'`] *= `'ImageResultContent'`* #

*class* `ParametersSchema`[source]#Bases: `TypedDict`

`additionalProperties`: `NotRequired`[`bool`*] #

`properties`: `Dict`[`str`, `Any`*] #

`required`: `NotRequired`[`Sequence`[`str`*]]* #

`type`: `str`#

*class* `StaticWorkbench` ( `tools` : `List`[`BaseTool`[`Any`, `Any`*] ]* )[source]#Bases: `Workbench`, `Component`[`StaticWorkbenchConfig`]

`StaticWorkbench` is a workbench implementation that provides a fixed set of tools, meaning the tools do not change after each execution.

**Parameters**:

*   **`tools`** (`List`[`BaseTool`[`Any`, `Any`]]): A list of tools to be included in the workbench. These tools must be subclasses of `BaseTool`.

*classmethod* `_from_config` ( *`config` : `StaticWorkbenchConfig`* ) → `Self`[source]#Create a new instance of the component from a configuration object.

**Parameters**:

*   **`config`** (`T`): The configuration object.

**Returns**:

*   **`Self`**: The new instance of the component.

`_to_config` ( ) → `StaticWorkbenchConfig`[source]#Dump the configuration that would be requite to create a new instance of a component matching the configuration of this instance.

**Returns**:

*   **`T`**: The configuration of the component.

*async* `call_tool` ( `name` : `str`, `arguments` : `Mapping`[`str`, `Any`] | `None` *= `None`* , `cancellation_token` : `CancellationToken`| `None` *= `None`* ) → `ToolResult`[source]#Call a tool in the workbench.

**Parameters**:

*   **`name`** (`str`): The name of the tool to call.
*   **`arguments`** (`Mapping`[`str`, `Any`] | `None`): The arguments to pass to the tool. If `None`, the tool will be called with no arguments.
*   **`cancellation_token`** (`CancellationToken` | `None`): An optional cancellation token to cancel the tool execution.

**Returns**:

*   **`ToolResult`**: The result of the tool execution.

`component_config_schema`#alias of `StaticWorkbenchConfig`

`component_provider_override`: `ClassVar`[`str`| `None`*] *= `'autogen_core.tools.StaticWorkbench'`* #Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

*async* `list_tools` ( ) → `List`[`ToolSchema`][source]#List the currently available tools in the workbench as `ToolSchema` objects.

The list of tools may be dynamic, and their content may change after tool execution.

*async* `load_state` ( `state` : `Mapping`[`str`, `Any`*] ) → `None`[source]#Load the state of the workbench.

**Parameters**:

*   **`state`** (`Mapping`[`str`, `Any`]): The state to load into the workbench.

*async* `reset` ( ) → `None`[source]#Reset the workbench to its initialized, started state.

*async* `save_state` ( ) → `Mapping`[`str`, `Any`][source]#Save the state of the workbench.

This method should be called to persist the state of the workbench.

*async* `start` ( ) → `None`[source]#Start the workbench and initialize any resources.

This method should be called before using the workbench.

*async* `stop` ( ) → `None`[source]#Stop the workbench and release any resources.

This method should be called when the workbench is no longer needed.

*pydantic model* `TextResultContent`[source]#Bases: `BaseModel`

`TextResultContent` represents the text content resulting from a tool execution.

Show JSON schema:
```json
{
   "title" :   "TextResultContent" ,
   "description" :   "Text result content of a tool execution." ,
   "type" :   "object" ,
   "properties" :   {
      "type" :   {
         "const" :   "TextResultContent" ,
         "default" :   "TextResultContent" ,
         "title" :   "Type" ,
         "type" :   "string"
      },
      "content" :   {
         "title" :   "Content" ,
         "type" :   "string"
      }
   },
   "required" :   [   "content"   ]
}
```

**Fields**:

*   `content` (`str`)
*   `type` (`Literal['TextResultContent']`)

*field* `content`: `str` *[Required]* #The text content of the result.

*field* `type`: `Literal`[`'TextResultContent'`] *= `'TextResultContent'`* #

*class* `Tool` ( **`args`*, ***`kwargs`* )[source]#Bases: `Protocol`

`args_type` ( ) → `Type`[`BaseModel`][source]#

*property* `description`: `str`#

*async* `load_state_json` ( `state` : `Mapping`[`str`, `Any`*] ) → `None`[source]#

*property* `name`: `str`#

`return_type` ( ) → `Type`[`Any`][source]#

`return_value_as_string` ( `value` : `Any`) → `str`[source]#

*async* `run_json` ( `args` : `Mapping`[`str`, `Any`*] , `cancellation_token` : `CancellationToken`) → `Any`[source]#

*async* `save_state_json` ( ) → `Mapping`[`str`, `Any`][source]#

*property* `schema`: `ToolSchema`#

`state_type` ( ) → `Type`[`BaseModel`] | `None`[source]#

*pydantic model* `ToolResult`[source]#Bases: `BaseModel`

`ToolResult` encapsulates the outcome of a tool execution performed by a workbench.

Show JSON schema:
```json
{
   "title" :   "ToolResult" ,
   "description" :   "A result of a tool execution by a workbench." ,
   "type" :   "object" ,
   "properties" :   {
      "type" :   {
         "const" :   "ToolResult" ,
         "default" :   "ToolResult" ,
         "title" :   "Type" ,
         "type" :   "string"
      },
      "name" :   {
         "title" :   "Name" ,
         "type" :   "string"
      },
      "result" :   {
         "items" :   {
            "discriminator" :   {
               "mapping" :   {
                  "ImageResultContent" :   "#/$defs/ImageResultContent" ,
                  "TextResultContent" :   "#/$defs/TextResultContent"
               },
               "propertyName" :   "type"
            },
            "oneOf" :   [
               {
                  "$ref" :   "#/$defs/TextResultContent"
               },
               {
                  "$ref" :   "#/$defs/ImageResultContent"
               }
            ]
         },
         "title" :   "Result" ,
         "type" :   "array"
      },
      "is_error" :   {
         "default" :   false ,
         "title" :   "Is Error" ,
         "type" :   "boolean"
      }
   },
   "$defs" :   {
      "ImageResultContent" :   {
         "description" :   "Image result content of a tool execution." ,
         "properties" :   {
            "type" :   {
               "const" :   "ImageResultContent" ,
               "default" :   "ImageResultContent" ,
               "title" :   "Type" ,
               "type" :   "string"
            },
            "content" :   {
               "title" :   "Content"
            }
         },
         "required" :   [   "content"   ],
         "title" :   "ImageResultContent" ,
         "type" :   "object"
      },
      "TextResultContent" :   {
         "description" :   "Text result content of a tool execution." ,
         "properties" :   {
            "type" :   {
               "const" :   "TextResultContent" ,
               "default" :   "TextResultContent" ,
               "title" :   "Type" ,
               "type" :   "string"
            },
            "content" :   {
               "title" :   "Content" ,
               "type" :   "string"
            }
         },
         "required" :   [   "content"   ],
         "title" :   "TextResultContent" ,
         "type" :   "object"
      }
   },
   "required" :   [   "name" ,   "result"   ]
}
```

**Fields**:

*   `is_error` (`bool`)
*   `name` (`str`)
*   `result` (`List`[`autogen_core.tools._workbench.TextResultContent` | `autogen_core.tools._workbench.ImageResultContent`])
*   `type` (`Literal['ToolResult']`)

*field* `is_error`: `bool` *= `False`* #Indicates whether the tool execution resulted in an error.

*field* `name`: `str` *[Required]* #The name of the tool that was executed.

*field* `result`: `List`[`Annotated`[`TextResultContent`| `ImageResultContent` *, `FieldInfo` (`annotation` = `NoneType`, `required` = `True`, `discriminator` = `'type'` ) ] ]* *[Required]* #The result of the tool execution.

*field* `type`: `Literal`[`'ToolResult'`] *= `'ToolResult'`* #

`to_text` ( `replace_image` : `str`| `None` *= `None`* ) → `str`[source]#Converts the result to a text string.

**Parameters**:

*   **`replace_image`** (`str` | `None`): The string to substitute for image content. If `None`, the image content will be included in the text as a base64 string.

**Returns**:

*   **`str`**: The text representation of the result.

*class* `ToolSchema`[source]#Bases: `TypedDict`

`description`: `NotRequired`[`str`*] #

`name`: `str`#

`parameters`: `NotRequired`[`ParametersSchema`*] #

`strict`: `NotRequired`[`bool`*] #

*class* `Workbench`[source]#Bases: `ABC`, `ComponentBase`[`BaseModel`]

A `Workbench` is a fundamental component designed to provide a collection of tools that may share resources and state. It assumes the responsibility of managing the lifecycle of these tools and offering a unified interface for their invocation. The set of tools accessible through a workbench can be dynamic, with their availability potentially changing after each tool execution.

A workbench requires explicit lifecycle management: it must be started by calling the `start()` method and stopped by invoking the `stop()` method. Additionally, it can be seamlessly integrated as an asynchronous context manager, which automatically handles the `start()` and `stop()` operations upon entering and exiting the context, respectively.

*abstract async* `call_tool` ( `name` : `str`, `arguments` : `Mapping`[`str`, `Any`] | `None` *= `None`* , `cancellation_token` : `CancellationToken`| `None` *= `None`* ) → `ToolResult`[source]#Invokes a specified tool within the workbench.

**Parameters**:

*   **`name`** (`str`): The identifier for the tool to be called.
*   **`arguments`** (`Mapping`[`str`, `Any`] | `None`): The arguments to be passed to the tool. If `None`, the tool will be executed without any arguments.
*   **`cancellation_token`** (`CancellationToken` | `None`): An optional token that can be used to cancel the ongoing tool execution.

**Returns**:

*   **`ToolResult`**: The outcome generated by the tool's execution.

`component_type` *: `ClassVar` [`ComponentType`]* *= `'workbench'`* #The logical type of the component.

*abstract async* `list_tools` ( ) → `List`[`ToolSchema`][source]#Retrieves a list of currently available tools within the workbench, presented as `ToolSchema` objects.

The collection of tools may be dynamic, and their content or availability might undergo changes following each tool execution.

*abstract async* `load_state` ( `state` : `Mapping`[`str`, `Any`*] ) → `None`[source]#Loads the operational state into the workbench.

**Parameters**:

*   **`state`** (`Mapping`[`str`, `Any`]): The state data to be loaded into the workbench.

*abstract async* `reset` ( ) → `None`[source]#Resets the workbench to its initial, started state.

*abstract async* `save_state` ( ) → `Mapping`[`str`, `Any`][source]#Persists the current state of the workbench.

This method is crucial for saving the workbench's state.

*abstract async* `start` ( ) → `None`[source]#Initiates the workbench and allocates any necessary resources.

This method must be called before the workbench can be utilized.

*abstract async* `stop` ( ) → `None`[source]#Halts the workbench operation and releases any held resources.

This method should be invoked when the workbench is no longer required.

