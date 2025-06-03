# `autogen_agentchat.ui`

*   `0.2` Docs
*   GitHub
*   Discord
*   Twitter

This module implements utility classes for formatting/printing agent messages.

<br/>

`async` **Console** (
&nbsp;&nbsp;&nbsp;&nbsp;`stream` : `AsyncGenerator`[`BaseAgentEvent` | `BaseChatMessage` | `T`, `None`],
&nbsp;&nbsp;&nbsp;&nbsp`***`,
&nbsp;&nbsp;&nbsp;&nbsp;`no_inline_images` : `bool` = `False`,
&nbsp;&nbsp;&nbsp;&nbsp;`output_stats` : `bool` = `False`,
&nbsp;&nbsp;&nbsp;&nbsp;`user_input_manager` : `UserInputManager` | `None` = `None`
) &rarr; `T`[source]#

Consumes the message stream from `run_stream()` or `on_messages_stream()` and renders the messages to the console. It returns the last processed `TaskResult` or `Response`.

<br/>

> **Note**
> `output_stats` is experimental and the stats may not be accurate. It will be improved in future releases.

**Parameters** :
*   **`stream`** (`AsyncGenerator`[`BaseAgentEvent` | `BaseChatMessage` | `TaskResult`, `None`] | `AsyncGenerator`[`BaseAgentEvent` | `BaseChatMessage` | `Response`, `None`]) –
    The message stream to render. This stream can originate from either `run_stream()` or `on_messages_stream()`.
*   **`no_inline_images`** (`bool`, *optional*) –
    If the terminal environment is iTerm2, this option allows for inline rendering of images. Setting this parameter to `True` will disable this specific behavior. The default value is `False`.
*   **`output_stats`** (`bool`, *optional*) –
    (Experimental) When set to `True`, this parameter enables the output of a summary of the messages processed, along with inline token usage information. The default value is `False`.

**Returns** :
*   **`last_processed`** –
    The return value is a `TaskResult` if the consumed stream originates from `run_stream()`. Alternatively, it is a `Response` if the stream is provided by `on_messages_stream()`.

<br/>

`class` **UserInputManager** (
&nbsp;&nbsp;&nbsp;&nbsp;`callback` : `Callable`[[`str`], `str`] | `Callable`[[`str`, `CancellationToken` | `None`], `Awaitable`[`str`]]
)[source]#
Bases: `object`

`get_wrapped_callback` ( ) &rarr; `Callable`[[`str`, `CancellationToken` | `None`], `Awaitable`[`str`]] [source]#

`notify_event_received` (`request_id` : `str`) &rarr; `None` [source]#

<br/>
