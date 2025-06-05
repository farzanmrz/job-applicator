# autogen_core.exceptions

*exception* **CantHandleException**[source]#
Bases: `Exception`
Raised when a handler can’t handle the exception [i].

*exception* **MessageDroppedException**[source]#
Bases: `Exception`
Raised when a message is dropped [i].

*exception* **NotAccessibleError**[source]#
Bases: `Exception`
Tried to access a value that is not accessible. For example if it is remote cannot be accessed locally [i].

*exception* **UndeliverableException**[source]#
Bases: `Exception`
Raised when a message can’t be delivered [j].
