# Pattern Catalog

This chapter gathers patterns that are widely documented across the literature,
not only the original *Design Patterns* (GoF) set.
It draws from *Pattern-Oriented Software Architecture* (POSA, Buschmann et al.),
*Patterns of Enterprise Application Architecture* (Fowler),
*Enterprise Integration Patterns* (Hohpe and Woolf),
and the common distributed and cloud patterns that emerged later.

Each entry has a one-line intent so you can recognize a pattern by name and look it up in the literature that documents it.
Listing a pattern here is not a recommendation.
Many overlap, some compete,
and several exist only to work around limits of a particular language.
The body of this book argues that a number of them are unnecessary in Python
([The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves) says why).

The tables still follow each source's own grouping,
including the [*Creational*/*Structural*/*Behavioral* split](21_The_Pattern_Concept.md#pattern-taxonomy)
questioned there, so each name sits where its source puts it.
Rows are alphabetical within each table,
which for the classic patterns is also GoF's own order.
When this book covers a pattern, its name links to that coverage.
An unlinked name means the pattern appears only in this catalog.

## Finding a Pattern by Problem

The tables below are grouped by source.
This one is for when you know the problem but not the name.

| If the problem is | Look at |
|-------------------|---------|
| Creating objects without naming their classes | Abstract Factory, Builder, Factory Method, Prototype, Registry, Plugin |
| Making one object stand in for another | Proxy, Decorator, Adapter, Façade, Ambassador, Sidecar |
| Choosing behavior at runtime | Strategy, Command, Chain of Responsibility, State, Visitor, Double Dispatch |
| Structuring recursive or tree-shaped data | Composite, Interpreter, Visitor, Blackboard |
| Keeping the number of objects down | Flyweight, Multiton, Object Pool, Singleton |
| Saving and restoring state | Memento, Event Sourcing, Unit of Work, Identity Map |
| Reacting to change | Observer, Publish-Subscribe Channel, Model-View-Controller |
| Coordinating concurrent work | Thread Pool, Producer-Consumer, Future/Promise, Active Object, Reactor |
| Surviving a failing dependency | Circuit Breaker, Retry, Bulkhead, Timeout, Dead Letter Channel |
| Moving data across a boundary | Data Transfer Object, Message Translator, Gateway, Data Mapper |
| Supplying a collaborator from outside | Dependency Injection, Service Locator, Inversion of Control, Strategy |

## Creational (GoF)

| Pattern | Intent |
|---------|--------|
| [Abstract Factory](27_Factory.md#abstract-factories) | Create families of related objects without naming concrete classes. |
| [Builder](27_Factory.md#builder) | Separate constructing a complex object from its representation, building it in steps. |
| [Factory Method](27_Factory.md#polymorphic-factories) | Defer instantiation to a method so subclasses choose the concrete type. |
| [Prototype](27_Factory.md#prototype) | Create new objects by cloning an existing instance. |
| [Singleton](24_Singleton.md) | Ensure a class has one instance with a single point of access. |

## Structural (GoF)

| Pattern | Intent |
|---------|--------|
| [Adapter](29_Changing_the_Interface.md#adapter) | Convert one interface into another a client expects. |
| Bridge | Separate an abstraction from its implementation so both vary independently. |
| [Composite](34_Composite_and_Interpreter.md#the-classic-composite) | Treat individual objects and compositions of them uniformly through a tree. |
| [Decorator](14_Decorators.md#the-decorator-pattern) | Attach responsibilities to an object dynamically by wrapping it. |
| [Façade](29_Changing_the_Interface.md#façade) | Provide one simplified interface to a subsystem. |
| [Flyweight](35_Flyweight.md) | Share fine-grained objects to support large numbers of them efficiently. |
| [Proxy](26_Surrogate.md#proxy) | Provide a surrogate that controls access to another object. |

## Behavioral (GoF)

| Pattern | Intent |
|---------|--------|
| [Chain of Responsibility](28_Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime) | Pass a request along a chain until a handler processes it. |
| [Command](28_Function_Objects.md#command-choosing-the-operation-at-runtime) | Encapsulate a request as an object, enabling queues, logging, and undo. |
| [Interpreter](34_Composite_and_Interpreter.md#interpreter) | Represent a grammar and evaluate sentences written in it. |
| [Iterator](23_Iterators.md) | Access the elements of a collection in order without exposing its structure. |
| Mediator | Route communication between objects through one place to reduce coupling. |
| [Memento](36_Memento.md) | Capture and restore an object's state without breaking encapsulation. |
| [Observer](30_Observer.md) | Notify dependents automatically when an object changes state. |
| [State](26_Surrogate.md#state) | Change an object's behavior when its internal state changes. |
| [State Machine](31_State_Machines.md) | Drive an object through a fixed set of states from a transition table. |
| [Strategy](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) | Make a family of algorithms interchangeable at runtime. |
| [Template Method](25_Template_Method.md) | Define an algorithm's skeleton, letting subclasses fill in steps. |
| [Visitor](33_Visitor.md) | Add operations to an object structure without changing its classes. |

## Concurrency (POSA and others)

| Pattern | Intent |
|---------|--------|
| Active Object | Decouple a method call from its execution by giving the object its own thread. |
| Balking | Refuse an action when the object is not in a suitable state. |
| [Double-Checked Locking](24_Singleton.md#tests-threads-and-locks) | Cut locking cost when lazily initializing a shared resource. |
| [Future/Promise](19_Concurrency.md#one-task-many-backends) | Represent a result that will become available later. |
| Guarded Suspension | Block a call until a precondition becomes true. |
| Half-Sync/Half-Async | Separate synchronous and asynchronous work, joined by a queue. |
| Leader/Followers | Let a pool of threads take turns receiving and handling events. |
| Monitor Object | Serialize access so only one method runs on an object at a time. |
| Proactor | Dispatch the completion of asynchronous operations to handlers. |
| [Producer-Consumer](19_Concurrency.md#coordinating-threads-with-queues) | Decouple work creation from processing through a shared queue. |
| Reactor | Dispatch incoming requests to handlers synchronously as they arrive. |
| Read-Write Lock | Allow concurrent readers but exclusive writers. |
| [Thread Pool](19_Concurrency.md#one-task-many-backends) | Reuse a fixed set of worker threads across many tasks. |
| [Thread-Specific Storage](19_Concurrency.md#context-that-follows-the-call-chain) | Give each thread its own copy of a value. |

## Architectural (POSA)

| Pattern | Intent |
|---------|--------|
| [Blackboard](38_Simulation.md) | Let independent components cooperate through a shared data store. |
| Broker | Coordinate requests and replies between distributed components. |
| Layers | Stack responsibilities so each layer uses only the one beneath it. |
| Microkernel | Keep a minimal core and add capability through plug-ins. |
| [Model-View-Controller (MVC)](30_Observer.md#a-visual-example-of-observers) | Separate data, presentation, and input handling. |
| [Pipes and Filters](23_Iterators.md#reusable-algorithms) | Process a stream through a chain of independent transforms. |
| Presentation-Abstraction-Control (PAC) | Build interactive systems from cooperating agents, each split three ways. |
| [Reflection](17_Metaprogramming.md) | Let a program inspect and adjust its own structure at runtime. |

## Enterprise Application (Fowler)

| Pattern | Intent |
|---------|--------|
| Active Record | Wrap a table row in an object that carries its own persistence. |
| Data Mapper | Move data between objects and the database, keeping each unaware of the other. |
| [Data Transfer Object (DTO)](22_Data_Transfer_Objects.md) | Carry data between processes in one batched object. |
| Domain Model | Model business logic as a graph of objects. |
| Front Controller | Funnel all requests through a single handler. |
| Gateway | Wrap access to an external system behind a simple interface. |
| Identity Map | Load each object only once per session. |
| Lazy Load | Defer loading a persisted object until it is needed. |
| Money | Represent monetary amounts together with their currency. |
| Plugin | Choose behavior with classes named at configuration time. |
| [Registry](27_Factory.md#the-pythonic-factory-a-dictionary) | A well-known object others use to find services or data. |
| Repository | Mediate the domain and data with a collection-like query interface. |
| Service Layer | Define an application boundary as a set of operations. |
| [Special Case](20_Rethinking_Objects.md#null-object) | Supply a subclass for a special case instead of scattering null checks. |
| Table Module | Let one class handle all rows of a table. |
| Transaction Script | Organize logic as one procedure per request. |
| Unit of Work | Track changes in a transaction and commit them together. |
| [Value Object](12_Data_Classes_as_Types.md#immutability) | A small immutable object compared by value, not identity. |

## Integration and Messaging (Hohpe and Woolf)

| Pattern | Intent |
|---------|--------|
| Aggregator | Combine related messages into one. |
| Content-Based Router | Route by inspecting the message content. |
| Dead Letter Channel | Hold messages that cannot be delivered or processed. |
| Message | A packet of data sent over a channel. |
| Message Channel | Connect senders and receivers through a logical pipe. |
| Message Endpoint | Connect an application to the messaging system. |
| Message Router | Send a message to a destination chosen at runtime. |
| Message Translator | Convert a message from one format to another. |
| Point-to-Point Channel | Deliver a message to exactly one receiver. |
| [Publish-Subscribe Channel](28_Function_Objects.md#an-event-bus-handlers-keyed-by-type) | Broadcast a message to every interested subscriber. |
| Splitter | Break one message into several. |

## Distributed and Cloud

| Pattern | Intent |
|---------|--------|
| Ambassador | Proxy a service's outbound calls through a helper. |
| API Gateway | Offer one entry point in front of many services. |
| Bulkhead | Isolate resources so one failure does not sink the whole system. |
| Circuit Breaker | Stop calling a failing service until it recovers. |
| Command Query Responsibility Segregation (CQRS) | Separate the read model from the write model. |
| Event Sourcing | Store state as a log of events instead of current values. |
| [Retry](47_Stateless_in_Practice.md#adding-behavior-to-an-existing-effect) | Re-attempt a failed operation, often with backoff. |
| Saga | Run a long transaction as a series of compensable steps. |
| Service Discovery | Locate service instances dynamically. |
| Sidecar | Attach helper functionality to a service as a separate process. |
| Strangler Fig | Replace a legacy system incrementally by routing around it. |
| Timeout | Bound how long to wait for a response. |

## Other Patterns and Idioms

| Pattern | Intent |
|---------|--------|
| [Borg (Monostate)](24_Singleton.md#borg-singleton-by-inheritance) | Let every instance share one set of state instead of sharing one instance. |
| Curiously Recurring Template Pattern (CRTP) | Parameterize a base class by the subclass that inherits from it. |
| [Dependency Injection](11_Testing.md#isolating-tests-from-the-world) | Supply an object's collaborators from outside it. |
| [Double Dispatch](32_Multiple_Dispatching.md) | Resolve behavior from the runtime types of two objects, through two calls. |
| [Fluent Interface](27_Factory.md#builder) | Chain method calls that return the receiver for readable APIs. |
| [Function Composition](40_Functional_Foundations.md#composing-functions) | Build a function by feeding one function's output into the next. |
| [Function Object](28_Function_Objects.md) | Decouple the choice of function to call from the place that calls it. |
| [Inversion of Control](25_Template_Method.md#the-fixed-algorithm) | Let a framework call your code rather than the reverse. |
| [Lazy Initialization](07_Classes.md#properties) | Create a value on first use. |
| Marker Interface | Tag a class with an empty interface to signal a capability. |
| [Memoization](41_Functional_Toolkits.md#the-functools-toolkit) | Cache a function's results keyed by its arguments. |
| Mixin | Add reusable behavior through multiple inheritance. |
| [Monad](42_Functional_Error_Handling.md) | Sequence computations inside a context such as optionality, error, or async. |
| [Multiton](35_Flyweight.md#interning-in-the-constructor) | Manage a fixed set of named singletons. |
| [Null Object](20_Rethinking_Objects.md#null-object) | Use an object with neutral behavior in place of null. |
| [Object Pool](15_Context_Managers.md#an-object-pool) | Reuse expensive objects from a managed pool. |
| [Partial Application](40_Functional_Foundations.md#partial-application) | Fix some of a function's arguments and get a function expecting the rest. |
| Pointer to Implementation (Pimpl) | Hide a class's implementation behind an indirection to cut compile coupling. |
| [Resource Acquisition Is Initialization (RAII)](15_Context_Managers.md) | Tie a resource's lifetime to an object's scope. |
| [Service Locator](46_Stateless.md#dependency-injection) | Look up dependencies through a central registry. |
| Specification | Encapsulate a rule as a predicate that combines with others. |
| Type Object | Represent a "kind of" thing as data rather than a subclass. |

## Patterns Python Absorbed

Several entries above are in the catalog because the literature documents them,
not because you need to write them.
Python already supplies the piece they were invented to supply.

| Pattern | What Python gives you instead |
|---------|------------------------------|
| [Iterator](23_Iterators.md#the-pattern-that-disappeared) | The iteration protocol, called for you by `for` |
| [Singleton](24_Singleton.md#a-module-is-already-a-singleton) | A module, imported once and cached |
| [Factory Method](27_Factory.md#the-pythonic-factory-a-dictionary) | A dictionary of classes, since a class is an object |
| [Strategy](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) | A function passed as an argument |
| [Command](28_Function_Objects.md#command-choosing-the-operation-at-runtime) | A function stored in a list |
| [Chain of Responsibility](28_Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime) | A list of functions, tried in order |
| [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch) | `functools.singledispatch` |
| [Flyweight](35_Flyweight.md#python-uses-flyweights) | Interned strings and cached small integers |
| [Prototype](27_Factory.md#prototype) | `copy.deepcopy()` and `dataclasses.replace()` |

What survives the subtraction is the intent, not the structure.
[The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves)
makes the general argument; each chapter above works one case.
