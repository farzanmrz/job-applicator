# autogen_core.code_executor

Skip to main contentCtrl + K

*   0.2 Docs
*   GitHub
*   Discord
*   Twitter
*   GitHub
*   Discord
*   Twitter

## Classes

### *class* Alias ( *name* : 'str', *alias* : 'str') [source]

Bases: `object`

*   `alias`: str#
*   `name`: str#

### *class* CodeBlock ( *code* : str, *language* : str) [source]

Bases: `object`

A code block extracted from an agent message.

*   `code`: str#
*   `language`: str#

### *class* CodeExecutor [source]

Bases: `ABC`, `ComponentBase[BaseModel]`

Executes code blocks and returns the result.

This is an abstract base class for code executors. It defines the interface for executing code blocks and returning the result. A concrete implementation of this class should be provided to execute code blocks in a specific environment. For example, `DockerCommandLineCodeExecutor` executes code blocks in a command line environment in a Docker container.

It is recommended for a subclass to be used as a context manager to ensure that resources are cleaned up properly. To do this, implement the `start()` and `stop()` methods that will be called when entering and exiting the context manager.

*   `component_type`: `ClassVar[ComponentType]` = `'code_executor'`
    The logical type of the component.

#### *abstract async* execute_code_blocks ( *code_blocks* : `List[CodeBlock]`, *cancellation_token* : `CancellationToken`) → `CodeResult` [source]

Execute code blocks and return the result.

This method should be implemented by the code executor.

**Parameters**:
*   **`code_blocks`** (`List[CodeBlock]`): The code blocks to execute.

**Returns**:
*   **`CodeResult`**: The result of the code execution.

**Raises**:
*   **`ValueError`**: Errors in user inputs
*   **`TimeoutError`**: Code execution timeouts
*   **`CancelledError`**: `CancellationToken` evoked during execution

#### *abstract async* restart ( ) → `None` [source]

Restart the code executor.

This method should be implemented by the code executor.
This method is called when the agent is reset.

#### *abstract async* start ( ) → `None` [source]

Start the code executor.

#### *abstract async* stop ( ) → `None` [source]

Stop the code executor and release any resources.

### *class* CodeResult ( *exit_code* : int, *output* : str) [source]

Bases: `object`

Result of a code execution.

*   `exit_code`: int#
*   `output`: str#

### *class* FunctionWithRequirements ( *func* : `Callable[P, T]`, *python_packages* : `Sequence[str]` = `<factory>`, *global_imports* : `Sequence[Import]` = `<factory>`) [source]

Bases: `Generic[T, P]`

*   `func`: `Callable[[P], T]`
*   `global_imports`: `Sequence[str | ImportFromModule | Alias]`
*   `python_packages`: `Sequence[str]`

#### *classmethod* from_callable ( *func* : `Callable[[P], T]`, *python_packages* : `Sequence[str]` = `[]`, *global_imports* : `Sequence[str | ImportFromModule | Alias]` = `[]`) → `FunctionWithRequirements[T, P]` [source]

#### *static* from_str ( *func* : str, *python_packages* : `Sequence[str]` = `[]`, *global_imports* : `Sequence[str | ImportFromModule | Alias]` = `[]`) → `FunctionWithRequirementsStr` [source]

### *class* FunctionWithRequirementsStr ( *func* : 'str', *python_packages* : `Sequence[str]` = `[]`, *global_imports* : `Sequence[Import]` = `[]`) [source]

Bases: `object`

*   `compiled_func`: `Callable[[...], Any]`
*   `func`: str#
*   `global_imports`: `Sequence[str | ImportFromModule | Alias]`
*   `python_packages`: `Sequence[str]`

### *class* ImportFromModule ( *module* : 'str', *imports* : `Union[Tuple[Union[str, Alias], ...], List[Union[str, Alias]]]` ) [source]

Bases: `object`

*   `imports`: `Tuple[str | Alias, ...]`
*   `module`: str#

## Functions

### `with_requirements` ( *python_packages* : `Sequence[str]` = `[]`, *global_imports* : `Sequence[str | ImportFromModule | Alias]` = `[]`) → `Callable[[Callable[[P], T]], FunctionWithRequirements[T, P]]` [source]

Decorate a function with package and import requirements for code execution environments.

This decorator makes a function available for reference in dynamically executed code blocks by wrapping it in a `FunctionWithRequirements` object that tracks its dependencies. When the decorated function is passed to a code executor, it can be imported by name in the executed code, with all dependencies automatically handled.

**Parameters**:
*   **`python_packages`** (`Sequence[str]`, *optional*): Python packages required by the function. Can include version specifications (e.g., `["pandas>=1.0.0"]`). Defaults to `[]`.
*   **`global_imports`** (`Sequence[Import]`, *optional*): Import statements required by the function. Can be strings (`"numpy"`), `ImportFromModule` objects, or `Alias` objects. Defaults to `[]`.

**Returns**:
*   `Callable[[Callable[P, T]], FunctionWithRequirements[T, P]]`: A decorator that wraps the target function, preserving its functionality while registering its dependencies.

**Example**

```python
import tempfile
import asyncio
from autogen_core import CancellationToken
from autogen_core.code_executor import with_requirements, CodeBlock
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
import pandas

@with_requirements(python_packages=["pandas"], global_imports=["pandas"])
def load_data() -> pandas.DataFrame:
    """Load some sample data.
    Returns:
        pandas.DataFrame: A DataFrame with sample data
    """
    data = {
        "name": ["John", "Anna", "Peter", "Linda"],
        "location": ["New York", "Paris", "Berlin", "London"],
        "age": ,
    }
    return pandas.DataFrame(data)

async def run_example():
    # The decorated function can be used in executed code
    with tempfile.TemporaryDirectory() as temp_dir:
        executor = LocalCommandLineCodeExecutor(work_dir=temp_dir, functions=[load_data])
        code = f"""from {executor.functions_module} import load_data
# Use the imported function
data = load_data()
print(data['name'])"""
        result = await executor.execute_code_blocks(
            code_blocks=[CodeBlock(language="python", code=code)],
            cancellation_token=CancellationToken(),
        )
        print(result.output)

# Output: John
# Run the async example
asyncio.run(run_example())
```