### Memory and RAG
There are several use cases where it is valuable to maintain a *store* of useful facts that can be intelligently added to the context of the agent just before a specific step. The typical use case here is a RAG (Retrieval Augmented Generation) pattern where a query is used to retrieve relevant information from a database that is then added to the agent’s context.

AgentChat provides a Memory protocol that can be extended to provide this functionality. The key methods defined within this protocol are `query`, `update_context`, `add`, `clear`, and `close`.

*   `add`: add new entries to the memory store
*   `query`: retrieve relevant information from the memory store
*   `update_context`: mutate an agent’s internal `model_context` by adding the retrieved information (used in the `AssistantAgent` class)
*   `clear`: clear all entries from the memory store
*   `close`: clean up any resources used by the memory store

### ListMemory Example
`autogen_core.memory.ListMemory` is provided as an example implementation of the `autogen_core.memory.Memory` protocol. It is a simple list-based memory implementation that maintains memories in chronological order, appending the most recent memories to the model’s context. The implementation is designed to be straightforward and predictable, making it easy to understand and debug. In the following example, `ListMemory` will be used to maintain a memory bank of user preferences and demonstrate how it can provide consistent context for agent responses over time.

```python
from   autogen_agentchat.agents   import   AssistantAgent
from   autogen_agentchat.ui   import   Console
from   autogen_core.memory   import   ListMemory ,   MemoryContent ,   MemoryMimeType
from   autogen_ext.models.openai   import   OpenAIChatCompletionClient

# Initialize user memory
user_memory   =   ListMemory ()

# Add user preferences to memory
await   user_memory . add ( MemoryContent ( content = "The weather should be in metric units" ,   mime_type = MemoryMimeType . TEXT ))
await   user_memory . add ( MemoryContent ( content = "Meal recipe must be vegan" ,   mime_type = MemoryMimeType . TEXT ))

async   def   get_weather ( city :   str ,   units :   str   =   "imperial" )   ->   str :
    if   units   ==   "imperial" :
        return   f "The weather in  { city }  is 73 °F and Sunny."
    elif   units   ==   "metric" :
        return   f "The weather in  { city }  is 23 °C and Sunny."
    else :
        return   f "Sorry, I don't know the weather in  { city } ."

assistant_agent   =   AssistantAgent (
    name = "assistant_agent" ,
    model_client = OpenAIChatCompletionClient (
        model = "gpt-4o-2024-08-06" ,
    ),
    tools = [ get_weather ],
    memory = [ user_memory ],
)

# Run the agent with a task.
stream   =   assistant_agent . run_stream ( task = "What is the weather in New York?" )
await   Console ( stream )
```


We can inspect that the `assistant_agent` `model_context` is actually updated with the retrieved memory entries. The `transform` method is used to format the retrieved memory entries into a string that can be used by the agent. In this case, the content of each memory entry is simply concatenated into a single string.

```python
await   assistant_agent . _model_context . get_messages ()
```

We see above that the weather is returned in Centigrade as stated in the user preferences.

Similarly, assuming a separate question is asked about generating a meal plan, the agent is able to retrieve relevant information from the memory store and provide a personalized (vegan) response.

```python
stream   =   assistant_agent . run_stream ( task = "Write brief meal recipe with broth" )
await   Console ( stream )
```


### Custom Memory Stores (Vector DBs, etc.)
You can build on the `Memory` protocol to implement more complex memory stores. For example, a custom memory store could use a vector database to store and retrieve information, or employ a machine learning model to generate personalized responses based on user preferences.

Specifically, you will need to overload the `add`, `query`, and `update_context` methods to implement the desired functionality and pass the custom memory store to your agent.

Currently, the following example memory stores are available as part of the `autogen_ext` extensions package:
*   `autogen_ext.memory.chromadb.ChromaDBVectorMemory`: A memory store that uses a vector database to store and retrieve information.

```python
import   os
from   pathlib   import   Path
from   autogen_agentchat.agents   import   AssistantAgent
from   autogen_agentchat.ui   import   Console
from   autogen_core.memory   import   MemoryContent ,   MemoryMimeType
from   autogen_ext.memory.chromadb   import   ChromaDBVectorMemory ,   PersistentChromaDBVectorMemoryConfig
from   autogen_ext.models.openai   import   OpenAIChatCompletionClient

# Initialize ChromaDB memory with custom config
chroma_user_memory   =   ChromaDBVectorMemory (
    config = PersistentChromaDBVectorMemoryConfig (
        collection_name = "preferences" ,
        persistence_path = os . path . join ( str ( Path . home ()),   ".chromadb_autogen" ),
        k = 2 ,   # Return top k results
        score_threshold = 0.4 ,   # Minimum similarity score
    )
)
# a HttpChromaDBVectorMemoryConfig is also supported for connecting to a remote ChromaDB server
# Add user preferences to memory
await   chroma_user_memory . add (
    MemoryContent (
        content = "The weather should be in metric units" ,
        mime_type = MemoryMimeType . TEXT ,
        metadata = { "category" :   "preferences" ,   "type" :   "units" },
    )
)
await   chroma_user_memory . add (
    MemoryContent (
        content = "Meal recipe must be vegan" ,
        mime_type = MemoryMimeType . TEXT ,
        metadata = { "category" :   "preferences" ,   "type" :   "dietary" },
    )
)

model_client   =   OpenAIChatCompletionClient (
    model = "gpt-4o" ,
)

# Create assistant agent with ChromaDB memory
assistant_agent   =   AssistantAgent (
    name = "assistant_agent" ,
    model_client = model_client ,
    tools = [ get_weather ],
    memory = [ chroma_user_memory ],
)

stream   =   assistant_agent . run_stream ( task = "What is the weather in New York?" )
await   Console ( stream )

await   model_client . close ()
await   chroma_user_memory . close ()
```

Note that you can also serialize the `ChromaDBVectorMemory` and save it to disk.
```python
chroma_user_memory . dump_component () . model_dump_json ()
```


### RAG Agent: Putting It All Together
The RAG (Retrieval Augmented Generation) pattern, which is common in building AI systems, encompasses two distinct phases:
*   **Indexing**: Loading documents, chunking them, and storing them in a vector database
*   **Retrieval**: Finding and using relevant chunks during conversation runtime

In the previous examples, items were manually added to memory and passed to agents. In practice, the indexing process is usually automated and based on much larger document sources like product documentation, internal files, or knowledge bases.

Note: The quality of a RAG system is dependent on the quality of the chunking and retrieval process (models, embeddings, etc.). You may need to experiment with more advanced chunking and retrieval models to get the best results.

#### Building a Simple RAG Agent
To begin, let’s create a simple document indexer that will be used to load documents, chunk them, and store them in a `ChromaDBVectorMemory` memory store.

```python
import   re
from   typing   import   List
import   aiofiles
import   aiohttp
from   autogen_core.memory   import   Memory ,   MemoryContent ,   MemoryMimeType

class   SimpleDocumentIndexer :
    """Basic document indexer for AutoGen Memory."""
    def   __init__ ( self ,   memory :   Memory ,   chunk_size :   int   =   1500 )   ->   None :
        self . memory   =   memory
        self . chunk_size   =   chunk_size

    async   def   _fetch_content ( self ,   source :   str )   ->   str :
        """Fetch content from URL or file."""
        if   source . startswith (( "http://" ,   "https://" )):
            async   with   aiohttp . ClientSession ()   as   session :
                async   with   session . get ( source )   as   response :
                    return   await   response . text ()
        else :
            async   with   aiofiles . open ( source ,   "r" ,   encoding = "utf-8" )   as   f :
                return   await   f . read ()

    def   _strip_html ( self ,   text :   str )   ->   str :
        """Remove HTML tags and normalize whitespace."""
        text   =   re . sub ( r "<[^>]*>" ,   " " ,   text )
        text   =   re . sub ( r "\s+" ,   " " ,   text )
        return   text . strip ()

    def   _split_text ( self ,   text :   str )   ->   List [ str ]:
        """Split text into fixed-size chunks."""
        chunks :   list [ str ]   =   []
        # Just split text into fixed-size chunks
        for   i   in   range ( 0 ,   len ( text ),   self . chunk_size ):
            chunk   =   text [ i   :   i   +   self . chunk_size ]
            chunks . append ( chunk . strip ())
        return   chunks

    async   def   index_documents ( self ,   sources :   List [ str ])   ->   int :
        """Index documents into memory."""
        total_chunks   =   0
        for   source   in   sources :
            try :
                content   =   await   self . _fetch_content ( source )
                # Strip HTML if content appears to be HTML
                if   "<"   in   content   and   ">"   in   content :
                    content   =   self . _strip_html ( content )
                chunks   =   self . _split_text ( content )
                for   i ,   chunk   in   enumerate ( chunks ):
                    await   self . memory . add (
                        MemoryContent (
                            content = chunk ,
                            mime_type = MemoryMimeType . TEXT ,
                            metadata = { "source" :   source ,   "chunk_index" :   i }
                        )
                    )
                total_chunks   +=   len ( chunks )
            except   Exception   as   e :
                print ( f "Error indexing  { source } :  { str ( e ) } " )
        return   total_chunks
```


Now let’s use our indexer with `ChromaDBVectorMemory` to build a complete RAG agent:

```python
import   os
from   pathlib   import   Path
from   autogen_agentchat.agents   import   AssistantAgent
from   autogen_agentchat.ui   import   Console
from   autogen_ext.memory.chromadb   import   ChromaDBVectorMemory ,   PersistentChromaDBVectorMemoryConfig
from   autogen_ext.models.openai   import   OpenAIChatCompletionClient

# Initialize vector memory
rag_memory   =   ChromaDBVectorMemory (
    config = PersistentChromaDBVectorMemoryConfig (
        collection_name = "autogen_docs" ,
        persistence_path = os . path . join ( str ( Path . home ()),   ".chromadb_autogen" ),
        k = 3 ,   # Return top 3 results
        score_threshold = 0.4 ,   # Minimum similarity score
    )
)
await   rag_memory . clear ()   # Clear existing memory

# Index AutoGen documentation
async   def   index_autogen_docs ()   ->   None :
    indexer   =   SimpleDocumentIndexer ( memory = rag_memory )
    sources   =   [
        "https://raw.githubusercontent.com/microsoft/autogen/main/README.md" ,
        "https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/agents.html" ,
        "https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/teams.html" ,
        "https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/termination.html" ,
    ]
    chunks :   int   =   await   indexer . index_documents ( sources )
    print ( f "Indexed  { chunks }  chunks from  { len ( sources ) }  AutoGen documents" )

await   index_autogen_docs ()
```


```
Indexed 72 chunks from 4 AutoGen documents
```


# Create our RAG assistant agent
```python
rag_assistant   =   AssistantAgent (
    name = "rag_assistant" ,
    model_client = OpenAIChatCompletionClient ( model = "gpt-4o" ),
    memory = [ rag_memory ]
)

# Ask questions about AutoGen
stream   =   rag_assistant . run_stream ( task = "What is AgentChat?" )
await   Console ( stream )

# Remember to close the memory when done
await   rag_memory . close ()
```


```
---------- user ----------
What is AgentChat?
Query results: results=[MemoryContent(content='ng OpenAI\'s GPT-4o model. See [other supported models](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html).
```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    agent = AssistantAgent("assistant", model_client=model_client)
    print(await agent.run(task="Say \'Hello World!\'"))
    await model_client.close()

asyncio.run(main())
```
### Web Browsing Agent Team
Create a group chat team with a web surfer agent and a user proxy agent for web browsing tasks. You need to install [playwright](https://playwright.dev/python/docs/library).
```python
# pip install -U autogen-agentchat autogen-ext[openai,web-surfer]
# playwright install
import asyncio
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    # The web surfer will open a Chromium browser window to perform web browsing tasks.
    web_surfer = MultimodalWebSurfer("web_surfer", model_client, headless=False, animate_actions=True)
    # The user proxy agent is used to ge', mime_type='MemoryMimeType.TEXT', metadata={'chunk_index': 1, 'mime_type': 'MemoryMimeType.TEXT', 'source': 'https://raw.githubusercontent.com/microsoft/autogen/main/README.md', 'score': 0.48810458183288574, 'id': '16088e03-0153-4da3-9dec-643b39c549f5'}), MemoryContent(content='els_usage=None content=&#39;AutoGen is a programming framework for building multi-agent applications.&#39; type=&#39;ToolCallSummaryMessage&#39; The call to the on_messages() method returns a Response that contains the agent’s final response in the chat_message attribute, as well as a list of inner messages in the inner_messages attribute, which stores the agent’s “thought process” that led to the final response. Note It is important to note that on_messages() will update the internal state of the agent – it will add the messages to the agent’s history. So you should call this method with new messages.

You should not repeatedly call this method with the same messages or the complete history. Note Unlike in v0.2 AgentChat, the tools are executed by the same agent directly within the same call to on_messages() . By default, the agent will return the result of the tool call as the final response. You can also call the run() method, which is a convenience method that calls on_messages() . It follows the same interface as Teams and returns a TaskResult object. Multi-Modal Input # The AssistantAgent can handle multi-modal input by providing the input as a MultiModalMessage . from io import BytesIO import PIL import requests from autogen_agentchat.messages import MultiModalMessage from autogen_core import Image # Create a multi-modal message with random image and text. pil_image = PIL . Image . open ( BytesIO ( requests . get ( &quot;https://picsum.photos/300/200&quot; ) . content )', mime_type='MemoryMimeType.TEXT', metadata={'chunk_index': 3, 'mime_type': 'MemoryMimeType.TEXT', 'source': 'https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/agents.html', 'score': 0.4665141701698303, 'id': '3d603b62-7cab-4f74-b671-586fe36306f2'}), MemoryContent(content='AgentChat Termination Termination # In the previous section, we explored how to define agents, and organize them into teams that can solve tasks. However, a run can go on forever, and in many cases, we need to know when to stop them. This is the role of the termination condition. AgentChat supports several termination condition by providing a base TerminationCondition class and several implementations that inherit from it. A termination condition is a callable that takes a sequence of BaseAgentEvent or BaseChatMessage objects since the last time the condition was called , and returns a StopMessage if the conversation should be terminated, or None otherwise. Once a termination condition has been reached, it must be reset by calling reset() before it can be used again. Some important things to note about termination conditions: They are stateful but reset automatically after each run ( run() or run_stream() ) is finished. They can be combined using the AND and OR operators.

Note For group chat teams (i.e., RoundRobinGroupChat , SelectorGroupChat , and Swarm ), the termination condition is called after each agent responds. While a response may contain multiple inner messages, the team calls its termination condition just once for all the messages from a single response. So the condition is called with the “delta sequence” of messages since the last time it was called. Built-In Termination Conditions: MaxMessageTermination : Stops after a specified number of messages have been produced,', mime_type='MemoryMimeType.TEXT', metadata={'chunk_index': 1, 'mime_type': 'MemoryMimeType.TEXT', 'source': 'https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/termination.html', 'score': 0.461774212772051, 'id': '699ef490-d108-4cd3-b629-c1198d6b78ba'})]
---------- rag_assistant ----------
AgentChat is part of the AutoGen framework, a programming environment for building multi-agent applications. In AgentChat, agents can interact with each other and with users to perform various tasks, including web browsing and engaging in dialogue. It utilizes models from OpenAI for chat completions and supports multi-modal input, which means agents can handle inputs that include both text and images. Additionally, AgentChat provides mechanisms to define termination conditions to control when a conversation or task should be concluded, ensuring that the agent interactions are efficient and goal-oriented. TERMINATE
```


This implementation provides a RAG agent that can answer questions based on AutoGen documentation. When a question is asked, the Memory system retrieves relevant chunks and adds them to the context, enabling the assistant to generate informed responses.

For production systems, you might want to:
*   Implement more sophisticated chunking strategies
*   Add metadata filtering capabilities
*   Customize the retrieval scoring
*   Optimize embedding models for your specific domain

---

This section appears to be a general example of using `AssistantAgent` from the broader documentation:

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    agent = AssistantAgent("assistant", model_client=model_client)
    print(await agent.run(task="Say 'Hello World!'"))
    await model_client.close()

asyncio.run(main())
```

### Web Browsing Agent Team
Create a group chat team with a web surfer agent and a user proxy agent for web browsing tasks. You need to install `playwright`.

```python
# pip install -U autogen-agentchat autogen-ext[openai,web-surfer]
# playwright install
import asyncio
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    # The web surfer will open a Chromium browser window to perform web browsing tasks.
    web_surfer = MultimodalWebSurfer("web_surfer", model_client, headless=False, animate_actions=True)
    # The user proxy agent is used to ge', mime_type='MemoryMimeType.TEXT', metadata={'chunk_index': 1, 'mime_type': 'MemoryMimeType.TEXT', 'source': 'https://raw.githubusercontent.com/microsoft/autogen/main/README.md', 'score': 0.48810458183288574, 'id': '16088e03-0153-4da3-9dec-643b39c549f5'}), MemoryContent(content='els_usage=None content=&#39;AutoGen is a programming framework for building multi-agent applications.&#39; type=&#39;ToolCallSummaryMessage&#39; The call to the on_messages() method returns a Response that contains the agent’s final response in the chat_message attribute, as well as a list of inner messages in the inner_messages attribute, which stores the agent’s “thought process” that led to the final response. Note It is important to note that on_messages() will update the internal state of the agent – it will add the messages to the agent’s history. So you should call this method with new messages.

You should not repeatedly call this method with the same messages or the complete history. Note Unlike in v0.2 AgentChat, the tools are executed by the same agent directly within the same call to on_messages() . By default, the agent will return the result of the tool call as the final response. You can also call the run() method, which is a convenience method that calls on_messages() . It follows the same interface as Teams and returns a TaskResult object. Multi-Modal Input # The AssistantAgent can handle multi-modal input by providing the input as a MultiModalMessage . from io import BytesIO import PIL import requests from autogen_agentchat.messages import MultiModalMessage from autogen_core import Image # Create a multi-modal message with random image and text. pil_image = PIL . Image . open ( BytesIO ( requests . get ( &quot;https://picsum.photos/300/200&quot; ) . content )', mime_type='MemoryMimeType.TEXT', metadata={'chunk_index': 3, 'mime_type': 'MemoryMimeType.TEXT', 'source': 'https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/agents.html', 'score': 0.4665141701698303, 'id': '3d603b62-7cab-4f74-b671-586fe36306f2'}), MemoryContent(content='AgentChat Termination Termination # In the previous section, we explored how to define agents, and organize them into teams that can solve tasks. However, a run can go on forever, and in many cases, we need to know when to stop them. This is the role of the termination condition. AgentChat supports several termination condition by providing a base TerminationCondition class and several implementations that inherit from it. A termination condition is a callable that takes a sequence of BaseAgentEvent or BaseChatMessage objects since the last time the condition was called , and returns a StopMessage if the conversation should be terminated, or None otherwise. Once a termination condition has been reached, it must be reset by calling reset() before it can be used again. Some important things to note about termination conditions: They are stateful but reset automatically after each run ( run() or run_stream() ) is finished. They can be combined using the AND and OR operators.

Note For group chat teams (i.e., RoundRobinGroupChat , SelectorGroupChat , and Swarm ), the termination condition is called after each agent responds. While a response may contain multiple inner messages, the team calls its termination condition just once for all the messages from a single response. So the condition is called with the “delta sequence” of messages since the last time it was called. Built-In Termination Conditions: MaxMessageTermination : Stops after a specified number of messages have been produced,', mime_type='MemoryMimeType.TEXT', metadata={'chunk_index': 1, 'mime_type': 'MemoryMimeType.TEXT', 'source': 'https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/termination.html', 'score': 0.461774212772051, 'id': '699ef490-d108-4cd3-b629-c1198d6b78ba'})]
```

```python
web_surfer = MultimodalWebSurfer("web_surfer", model_client, headless=False, animate_actions=True) # The user proxy agent is used to ge
```