# Pattern Catalog

This chapter gathers patterns that are widely documented across the literature,
not only the original *Design Patterns* (GoF) set.
It draws from *Pattern-Oriented Software Architecture* (POSA),
*Patterns of Enterprise Application Architecture* (Fowler),
*Enterprise Integration Patterns* (Hohpe and Woolf),
and the common distributed and cloud patterns that emerged later.

Each entry has a one-line intent so you can recognize a pattern by name and find it elsewhere.
Listing a pattern here is not a recommendation.
Many overlap, some compete,
and several exist only to work around limits of a particular language.
The body of this book argues that a number of them are unnecessary in Python.
When this book covers a pattern, its name links to that coverage.
An unlinked name means the pattern appears only in this catalog.

## Creational (GoF)

| Pattern | Intent |
|---------|--------|
| [Abstract Factory](27_Factory.md#abstract-factories) | Create families of related objects without naming concrete classes. |
| [Builder](27_Factory.md#builder) | Separate constructing a complex object from its representation, building it in steps. |
| [Factory Method](27_Factory.md) | Defer instantiation to a method so subclasses choose the concrete type. |
| [Prototype](27_Factory.md#prototype) | Create new objects by cloning an existing instance. |
| [Singleton](24_Singleton.md) | Ensure a class has one instance with a single point of access. |

## Structural (GoF)

| Pattern | Intent |
|---------|--------|
| [Adapter](29_Changing_the_Interface.md#adapter) | Convert one interface into another a client expects. |
| Bridge | Separate an abstraction from its implementation so both vary independently. |
| [Composite](34_Composite_and_Interpreter.md) | Treat individual objects and compositions of them uniformly through a tree. |
| [Decorator](14_Decorators.md#the-decorator-pattern) | Attach responsibilities to an object dynamically by wrapping it. |
| [Façade](29_Changing_the_Interface.md#façade) | Provide one simplified interface to a subsystem. |
| [Flyweight](35_Flyweight.md) | Share fine-grained objects to support large numbers of them efficiently. |
| [Proxy](26_Surrogate.md#proxy) | Provide a surrogate that controls access to another object. |

## Behavioral (GoF)

| Pattern | Intent |
|---------|--------|
| [Chain of Responsibility](28_Function_Objects.md#chain-of-responsibility) | Pass a request along a chain until a handler processes it. |
| [Command](28_Function_Objects.md#command-choosing-the-operation-at-runtime) | Encapsulate a request as an object, enabling queues, logging, and undo. |
| [Interpreter](34_Composite_and_Interpreter.md#interpreter) | Represent a grammar and evaluate sentences written in it. |
| [Iterator](23_Iterators.md) | Access the elements of a collection in order without exposing its structure. |
| Mediator | Route communication between objects through one place to reduce coupling. |
| [Memento](36_Memento.md) | Capture and restore an object's state without breaking encapsulation. |
| [Observer](30_Observer.md) | Notify dependents automatically when an object changes state. |
| [State](26_Surrogate.md#state) | Change an object's behavior when its internal state changes. |
| [Strategy](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) | Make a family of algorithms interchangeable at runtime. |
| [Template Method](25_Template_Method.md) | Define an algorithm's skeleton, letting subclasses fill in steps. |
| [Visitor](33_Visitor.md) | Add operations to an object structure without changing its classes. |

## Concurrency (POSA and others)

| Pattern | Intent |
|---------|--------|
| Active Object | Decouple a method call from its execution by giving the object its own thread. |
| Monitor Object | Serialize access so only one method runs on an object at a time. |
| Half-Sync/Half-Async | Separate synchronous and asynchronous work, joined by a queue. |
| Leader/Followers | Let a pool of threads take turns receiving and handling events. |
| [Thread Pool](19_Concurrency.md#the-gil-and-free-threading) | Reuse a fixed set of worker threads across many tasks. |
| Reactor | Dispatch incoming requests to handlers synchronously as they arrive. |
| Proactor | Dispatch the completion of asynchronous operations to handlers. |
| [Producer-Consumer](19_Concurrency.md#coordinating-threads-with-queues) | Decouple work creation from processing through a shared queue. |
| Read-Write Lock | Allow concurrent readers but exclusive writers. |
| Double-Checked Locking | Cut locking cost when lazily initializing a shared resource. |
| Guarded Suspension | Block a call until a precondition becomes true. |
| Balking | Refuse an action when the object is not in a suitable state. |
| [Future / Promise](19_Concurrency.md#parallelism) | Represent a result that will become available later. |
| Thread-Specific Storage | Give each thread its own copy of a value. |

## Architectural (POSA)

| Pattern | Intent |
|---------|--------|
| Layers | Stack responsibilities so each layer uses only the one beneath it. |
| [Pipes and Filters](23_Iterators.md#reusable-algorithms) | Process a stream through a chain of independent transforms. |
| [Blackboard](38_Simulation.md) | Let independent components cooperate through a shared data store. |
| Broker | Coordinate requests and replies between distributed components. |
| [Model-View-Controller](30_Observer.md#a-visual-example-of-observers) | Separate data, presentation, and input handling. |
| Presentation-Abstraction-Control | Build interactive systems from cooperating agents, each split three ways. |
| Microkernel | Keep a minimal core and add capability through plug-ins. |
| [Reflection](17_Metaprogramming.md) | Let a program inspect and adjust its own structure at runtime. |

## Enterprise Application (Fowler)

| Pattern | Intent |
|---------|--------|
| Domain Model | Model business logic as a graph of objects. |
| Transaction Script | Organize logic as one procedure per request. |
| Table Module | Let one class handle all rows of a table. |
| Active Record | Wrap a table row in an object that carries its own persistence. |
| Data Mapper | Move data between objects and the database, keeping each unaware of the other. |
| Repository | Mediate the domain and data with a collection-like query interface. |
| Unit of Work | Track changes in a transaction and commit them together. |
| Identity Map | Load each object only once per session. |
| Lazy Load | Defer loading data until it is actually needed. |
| [Data Transfer Object](22_Data_Transfer_Objects.md) | Carry data between processes in one batched object. |
| [Value Object](12_Data_Classes_as_Types.md#immutability) | A small immutable object compared by value, not identity. |
| Service Layer | Define an application boundary as a set of operations. |
| Gateway | Wrap access to an external system behind a simple interface. |
| Front Controller | Funnel all requests through a single handler. |
| Money | Represent monetary amounts together with their currency. |
| [Special Case](20_Rethinking_Objects.md#null-object) | Supply a subclass for a special case instead of scattering null checks. |
| [Registry](27_Factory.md#the-pythonic-factory-a-dictionary) | A well-known object others use to find services or data. |
| Plugin | Choose behavior with classes named at configuration time. |

## Integration and Messaging (Hohpe and Woolf)

| Pattern | Intent |
|---------|--------|
| Message Channel | Connect senders and receivers through a logical pipe. |
| Message | A packet of data sent over a channel. |
| [Publish-Subscribe Channel](28_Function_Objects.md#an-event-bus-handlers-keyed-by-type) | Broadcast a message to every interested subscriber. |
| Point-to-Point Channel | Deliver a message to exactly one receiver. |
| Message Router | Send a message to a destination chosen at runtime. |
| Content-Based Router | Route by inspecting the message content. |
| Message Translator | Convert a message from one format to another. |
| Message Endpoint | Connect an application to the messaging system. |
| Aggregator | Combine related messages into one. |
| Splitter | Break one message into several. |
| Dead Letter Channel | Hold messages that cannot be delivered or processed. |

## Distributed and Cloud

| Pattern | Intent |
|---------|--------|
| Circuit Breaker | Stop calling a failing service until it recovers. |
| Retry | Re-attempt a failed operation, often with backoff. |
| Bulkhead | Isolate resources so one failure does not sink the whole system. |
| Timeout | Bound how long to wait for a response. |
| Saga | Run a long transaction as a series of compensable steps. |
| Command Query Responsibility Segregation (CQRS) | Separate the read model from the write model. |
| Event Sourcing | Store state as a log of events instead of current values. |
| Sidecar | Attach helper functionality to a service as a separate process. |
| Ambassador | Proxy a service's outbound calls through a helper. |
| Strangler Fig | Replace a legacy system incrementally by routing around it. |
| Service Discovery | Locate service instances dynamically. |
| API Gateway | Offer one entry point in front of many services. |

## Foundational Idioms

| Pattern | Intent |
|---------|--------|
| [Null Object](20_Rethinking_Objects.md#null-object) | Use an object with neutral behavior in place of null. |
| [Object Pool](15_Context_Managers.md#an-object-pool) | Reuse expensive objects from a managed pool. |
| [Multiton](35_Flyweight.md#interning-in-the-constructor) | Manage a fixed set of named singletons. |
| [Dependency Injection](11_Testing.md#isolating-tests-from-the-world) | Supply an object's collaborators from outside it. |
| [Inversion of Control](25_Template_Method.md) | Let a framework call your code rather than the reverse. |
| Service Locator | Look up dependencies through a central registry. |
| [Resource Acquisition Is Initialization (RAII)](15_Context_Managers.md) | Tie a resource's lifetime to an object's scope. |
| Type Object | Represent a "kind of" thing as data rather than a subclass. |
| Specification | Encapsulate a rule as a predicate that combines with others. |
| [Fluent Interface](27_Factory.md#builder) | Chain method calls that return the receiver for readable APIs. |
| Mixin | Add reusable behavior through multiple inheritance. |
| [Monad](42_Functional_Error_Handling.md) | Sequence computations inside a context such as optionality, error, or async. |
| [Function Object](28_Function_Objects.md) | An object whose sole purpose is to wrap a single function. |
| [Memoization](41_Functional_Toolkits.md#the-functools-toolkit) | Cache a function's results keyed by its arguments. |
| [Lazy Initialization](07_Classes.md#properties) | Create a value on first use. |
| Marker Interface | Tag a class with an empty interface to signal a capability. |
| Curiously Recurring Template Pattern (CRTP) | A class inherits from a base parameterized by the class itself. |
| Pointer to Implementation (Pimpl) | Hide a class's implementation behind an indirection to cut compile coupling. |
