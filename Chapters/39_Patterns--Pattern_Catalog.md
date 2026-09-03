# Pattern Catalog

This chapter gathers patterns that the literature documents widely,
not only the original *Design Patterns* (GoF) set.
It draws from *Pattern-Oriented Software Architecture* (POSA, Buschmann et al.),
*Patterns of Enterprise Application Architecture* (Fowler),
*Enterprise Integration Patterns* (Hohpe and Woolf),
and the common distributed and cloud patterns that emerged later.

Each entry has a one-line intent so you can recognize a pattern by name and look it up in the literature that documents it.
Listing a pattern here does not recommend it.
Many overlap, some compete,
and several exist only to work around limits of a particular language.
[State](26_Patterns--Surrogate.md#state)
and [State Machine](31_Patterns--State_Machines.md) are one such pair.
State changes an object's behavior when its internal state changes.
State Machine drives an object through a fixed set of states in response to inputs.
A design rarely needs both at once.
The body of this book argues that a number of them are unnecessary in Python
([Design Patterns](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves) says why).

The tables follow each source's own grouping,
so each name sits where its source puts it.
That includes GoF's [*Creational*/*Structural*/*Behavioral* split](21_Patterns--Design_Patterns.md#pattern-taxonomy),
which [Design Patterns](21_Patterns--Design_Patterns.md)
accepts for *Creational* and questions for the other two.
A few idioms below belong to no single source.
This chapter groups them by what they share instead:
language idioms tied to C++ or Java's limits, functional idioms,
and the patterns that supply a collaborator from outside.
What that grouping leaves over sits in Other Patterns and Idioms,
the catalog's remaining grab-bag.
Each table lists its rows alphabetically,
and for the classic patterns that is also GoF's own order.
When this book covers a pattern, its name links to that coverage.
An unlinked name means the book has no section on that pattern.

## Finding a Pattern by Problem

The tables below group by source.
Use this one when you know the problem but not the name.

| If the problem is | Look at |
|-------------------|---------|
| Creating objects without naming their classes | Abstract Factory, Builder, Factory Method, Prototype, Registry, Plugin |
| Controlling access to another object | Proxy |
| Adding behavior to an object without changing its class | Decorator |
| Converting one interface into another a client expects | Adapter |
| Simplifying access to a subsystem | Façade |
| Proxying a service's calls from a helper process | Ambassador, Sidecar |
| Swapping an algorithm at runtime | Strategy |
| Encapsulating a request as an object | Command |
| Passing a request along a chain until something handles it | Chain of Responsibility |
| Changing behavior when an object's internal state changes | State |
| Driving an object through a fixed set of states | State Machine |
| Adding an operation without changing the classes it visits | Visitor |
| Resolving behavior from the runtime types of two objects | Double Dispatch |
| Structuring recursive or tree-shaped data | Composite, Interpreter, Visitor, Blackboard |
| Keeping the number of objects down | Flyweight, Multiton, Object Pool, Singleton |
| Saving and restoring state | Memento, Event Sourcing, Unit of Work, Identity Map |
| Reacting to change | Observer, Publish-Subscribe Channel, Model-View-Controller |
| Coordinating concurrent work | Thread Pool, Producer-Consumer, Future/Promise, Active Object, Reactor |
| Surviving a failing dependency | Circuit Breaker, Retry, Bulkhead, Timeout, Dead Letter Channel |
| Moving data across a boundary | Data Transfer Object, Message Translator, Gateway, Data Mapper |
| Persisting domain objects to a database | Active Record, Repository, Table Module, Lazy Load |
| Organizing application logic by request or use case | Transaction Script, Domain Model, Service Layer, Front Controller |
| Modeling a value, amount, or special case instead of null | Value Object, Money, Special Case |
| Routing or transforming a message | Content-Based Router, Message Router, Splitter, Aggregator |
| Connecting an application to a messaging system | Message, Message Channel, Message Endpoint, Point-to-Point Channel |
| Supplying a collaborator from outside, an application of Inversion of Control | Dependency Injection, Service Locator, Strategy |

## Creational (GoF)

| Pattern | Intent |
|---------|--------|
| [Abstract Factory](27_Patterns--Factory.md#abstract-factories) | Create families of related objects without naming concrete classes. |
| [Builder](27_Patterns--Factory.md#builder) | Build a complex object in steps, keeping the step-by-step assembly separate from the finished object. |
| [Factory Method](27_Patterns--Factory.md#subclasses-choose-the-type) | Defer instantiation to a method so subclasses choose the concrete type. |
| [Prototype](27_Patterns--Factory.md#prototype) | Create new objects by cloning an existing instance. |
| [Singleton](24_Patterns--Singleton.md) | Ensure a class has one instance with a single point of access. |

## Structural (GoF)

| Pattern | Intent |
|---------|--------|
| [Adapter](29_Patterns--Changing_the_Interface.md#adapter) | Convert one interface into another a client expects. |
| Bridge | Separate an abstraction from its implementation so both vary independently. |
| [Composite](34_Patterns--Composite_and_Interpreter.md#the-classic-composite) | Treat individual objects and compositions of them uniformly through a tree. |
| [Decorator](14_Techniques--Decorators.md#the-decorator-pattern) | Attach responsibilities to an object dynamically by wrapping it. |
| [Façade](29_Patterns--Changing_the_Interface.md#façade) | Provide one simplified interface to a subsystem. |
| [Flyweight](35_Patterns--Flyweight.md) | Share fine-grained objects to support large numbers of them efficiently. |
| [Proxy](26_Patterns--Surrogate.md#proxy) | Provide a surrogate that controls access to another object. |

## Behavioral (GoF)

| Pattern | Intent |
|---------|--------|
| [Chain of Responsibility](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime) | Pass a request along a chain until a handler processes it. |
| [Command](28_Patterns--Function_Objects.md#command-choosing-the-operation-at-runtime) | Encapsulate a request as an object, enabling queues, logging, and undo. |
| [Interpreter](34_Patterns--Composite_and_Interpreter.md#interpreter) | Represent a grammar and evaluate sentences written in it. |
| [Iterator](23_Patterns--Iterators.md) | Access the elements of a collection in order without exposing its structure. |
| Mediator | Route communication between objects through one place to reduce coupling. |
| [Memento](36_Patterns--Memento.md) | Capture and restore an object's state without breaking encapsulation. |
| [Observer](30_Patterns--Observer.md) | Notify dependents automatically when an object changes state. |
| [State](26_Patterns--Surrogate.md#state) | Change an object's behavior when its internal state changes. |
| [Strategy](28_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) | Make a family of algorithms interchangeable at runtime. |
| [Template Method](25_Patterns--Template_Method.md) | Define an algorithm's skeleton, letting subclasses fill in steps. |
| [Visitor](33_Patterns--Visitor.md) | Add operations to an object structure without changing its classes. |

## Concurrency (POSA and others)

| Pattern | Intent |
|---------|--------|
| Active Object | Decouple a method call from its execution by giving the object its own thread. |
| Balking | Refuse an action when the object is in an unsuitable state. |
| [Double-Checked Locking](24_Patterns--Singleton.md#tests-threads-and-locks) | Cut locking cost when lazily initializing a shared resource. |
| [Future/Promise](19_Techniques--Concurrency.md#one-task-many-backends) | Represent a result that becomes available later. |
| Guarded Suspension | Block a call until a precondition becomes true. |
| Half-Sync/Half-Async | Separate synchronous and asynchronous work, joined by a queue. |
| Leader/Followers | Let a pool of threads take turns receiving and handling events. |
| Monitor Object | Serialize access so only one method runs on an object at a time. |
| Proactor | Dispatch the completion of asynchronous operations to handlers. |
| [Producer-Consumer](19_Techniques--Concurrency.md#coordinating-threads-with-queues) | Decouple work creation from processing through a shared queue. |
| Reactor | Dispatch incoming requests to handlers synchronously as they arrive. |
| Read-Write Lock | Allow concurrent readers but exclusive writers. |
| [Thread Pool](19_Techniques--Concurrency.md#one-task-many-backends) | Reuse a fixed set of worker threads across many tasks. |
| [Thread-Specific Storage](19_Techniques--Concurrency.md#context-that-follows-the-call-chain) | Give each thread its own copy of a value. |

## Architectural (POSA)

| Pattern | Intent |
|---------|--------|
| [Blackboard](38_Patterns--Simulation.md) | Let independent components cooperate through a shared data store. |
| Broker | Coordinate requests and replies between distributed components. |
| Layers | Stack responsibilities so each layer uses only the one beneath it. |
| Microkernel | Keep a minimal core and add capability through plug-ins. |
| [Model-View-Controller (MVC)](30_Patterns--Observer.md) | Separate data, presentation, and input handling. |
| [Pipes and Filters](23_Patterns--Iterators.md#reusable-algorithms) | Process a stream through a chain of independent transforms. |
| Presentation-Abstraction-Control (PAC) | Build interactive systems from cooperating agents, each split three ways. |
| [Reflection](17_Techniques--Metaprogramming.md) | Let a program inspect and adjust its own structure at runtime. |

## Enterprise Application (Fowler)

| Pattern | Intent |
|---------|--------|
| Active Record | Wrap a table row in an object that carries its own persistence. |
| Data Mapper | Move data between objects and the database, keeping each unaware of the other. |
| [Data Transfer Object (DTO)](22_Patterns--Data_Transfer_Objects.md) | Carry data between processes in one batched object. |
| Domain Model | Model business logic as a graph of objects. |
| Front Controller | Funnel all requests through a single handler. |
| Gateway | Wrap access to an external system behind a simple interface. |
| Identity Map | Load each object only once per session. |
| Lazy Load | Defer loading a persisted object until something needs it. |
| Money | Represent monetary amounts together with their currency. |
| Plugin | Select an implementation by naming its class in configuration rather than in code. |
| [Registry](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary) | Keep one well-known object where the rest of the program looks up services or data. |
| Repository | Stand between the domain and the data store, presenting stored objects as a queryable collection. |
| Service Layer | Define an application boundary as a set of operations. |
| [Special Case](20_Patterns--Rethinking_Objects.md#null-object) | Supply a subclass for a special case instead of scattering null checks. |
| Table Module | Let one class handle all rows of a table. |
| Transaction Script | Organize logic as one procedure per request. |
| Unit of Work | Track changes in a transaction and commit them together. |
| [Value Object](12_Techniques--Data_Classes_as_Types.md#immutability) | Model a small value as an immutable object compared by value, not identity. |

## Integration and Messaging (Hohpe and Woolf)

| Pattern | Intent |
|---------|--------|
| Aggregator | Combine related messages into one. |
| Content-Based Router | Route by inspecting the message content. |
| Dead Letter Channel | Hold messages that no one can deliver or process. |
| Message | Package data to send over a channel. |
| Message Channel | Connect senders and receivers through a logical pipe. |
| Message Endpoint | Connect an application to the messaging system. |
| Message Router | Send a message to a destination chosen at runtime. |
| Message Translator | Convert a message from one format to another. |
| Point-to-Point Channel | Deliver a message to exactly one receiver. |
| [Publish-Subscribe Channel](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type) | Broadcast a message to every interested subscriber. |
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
| [Retry](47_Effects--Stateless_in_Practice.md#adding-behavior-to-an-existing-effect) | Re-attempt a failed operation, often with backoff. |
| Saga | Run a long transaction as a series of compensable steps. |
| Service Discovery | Locate service instances dynamically. |
| Sidecar | Attach helper functionality to a service as a separate process. |
| Strangler Fig | Replace a legacy system incrementally by routing around it. |
| Timeout | Bound how long to wait for a response. |

## Language and Implementation Idioms

| Pattern | Intent |
|---------|--------|
| Curiously Recurring Template Pattern (CRTP) | Parameterize a base class by the subclass that inherits from it. |
| Marker Interface | Tag a class with an empty interface to signal a capability. |
| Mixin | Add reusable behavior through multiple inheritance. |
| Pointer to Implementation (Pimpl) | Hide a class's implementation behind a pointer so changing it recompiles less. |
| [Resource Acquisition Is Initialization (RAII)](15_Techniques--Context_Managers.md) | Acquire a resource in a constructor and release it in the destructor. |

## Functional Idioms

| Pattern | Intent |
|---------|--------|
| [Function Composition](40_Functional--Foundations.md#composing-functions) | Build a function by feeding one function's output into the next. |
| [Memoization](41_Functional--Toolkits.md#cache) | Cache a function's results keyed by its arguments. |
| [Monad](42_Functional--Error_Handling.md) | Sequence computations inside a context such as optionality, error, or async. |
| [Partial Application](40_Functional--Foundations.md#partial-application) | Fix some of a function's arguments and get a function expecting the rest. |

## Dependency Supply

| Pattern | Intent |
|---------|--------|
| [Dependency Injection](11_Techniques--Testing.md#isolating-tests-from-the-world) | Supply an object's collaborators from outside it. |
| [Inversion of Control](25_Patterns--Template_Method.md#the-anchored-algorithm) | Let a framework call your code rather than the reverse. Dependency Injection and Service Locator each implement it. |
| [Service Locator](46_Effects--Stateless.md#dependency-injection) | Look up dependencies through a central registry. |

## Other Patterns and Idioms

| Pattern | Intent |
|---------|--------|
| [Borg (Monostate)](24_Patterns--Singleton.md#borg-singleton-by-inheritance) | Let every instance share one set of state instead of sharing one instance. |
| [Double Dispatch](32_Patterns--Multiple_Dispatching.md) | Resolve behavior from the runtime types of two objects, through two calls. |
| [Fluent Interface](27_Patterns--Factory.md#builder) | Chain method calls that return the receiver for readable APIs. |
| [Function Object](28_Patterns--Function_Objects.md) | Decouple the choice of function to call from the place that calls it. |
| [Lazy Initialization](07_Foundations--Classes.md#properties) | Create a value on first use. |
| [Multiton](35_Patterns--Flyweight.md#interning-in-the-constructor) | Manage a pool of singletons, one per key. |
| [Null Object](20_Patterns--Rethinking_Objects.md#null-object) | Use an object with neutral behavior in place of null. |
| [Object Pool](15_Techniques--Context_Managers.md#an-object-pool) | Reuse expensive objects from a managed pool. |
| Specification | Encapsulate a rule as a predicate that combines with others. |
| [State Machine](31_Patterns--State_Machines.md) | Drive an object through a fixed set of states in response to inputs. |
| Type Object | Represent a "kind of" thing as data rather than a subclass. |

## Patterns Python Absorbed

Several entries above are in the catalog because the literature documents them,
not because you need to write them.
Python includes the piece their inventors set out to supply.

| Pattern | What Python gives you instead |
|---------|------------------------------|
| [Iterator](23_Patterns--Iterators.md#the-pattern-that-disappeared) | The iteration protocol, called for you by `for` |
| [Singleton](24_Patterns--Singleton.md#a-module-is-already-a-singleton) | A module, imported once and cached |
| [Factory Method](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary) | A dictionary of classes, since a class is an object |
| [Prototype](27_Patterns--Factory.md#prototype) | `copy.deepcopy()` and `dataclasses.replace()` |
| [Strategy](28_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) | A function passed as an argument |
| [Command](28_Patterns--Function_Objects.md#command-choosing-the-operation-at-runtime) | A function stored in a list |
| [Chain of Responsibility](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime) | A list of functions, tried in order |
| [Visitor](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch) | `functools.singledispatch` |
| [Flyweight](35_Patterns--Flyweight.md#python-uses-flyweights) | Interned strings and cached small integers |

What survives the subtraction is the intent, not the structure.
[Reading the Chapters Ahead](21_Patterns--Design_Patterns.md#reading-the-chapters-ahead)
argues this in general.
Each linked chapter shows one case.
