# Effect Management: A High-Level View

Some functions do the same thing every time you call them.
Others depend on the world outside your program, and that world keeps changing.
An *Effect Management System* tracks the second kind of function and gives you control over what each one does.

## Predictable and Unpredictable Functions

Here is a function you can predict:

```python
def add(a: int, b: int) -> int:
    return a + b
```

`add(2, 3)` returns `5` today, tomorrow, and on every computer.
The arguments decide the result,
and the function leaves everything else as it was.
Programmers call such a function *pure*.

Many functions work with things outside the program: the keyboard, the screen,
the clock, the disk, the network.
All of those things are outside your program's control,
so you cannot predict what such a function will do.
A function can be unpredictable in three ways:

- It reads from the outside world.
  `input()` returns the words a person types,
  and a function that reads the clock returns a new time on each call.
- It changes the outside world.
  `print()` changes what the screen shows,
  and a function that saves a file changes the disk.
  The change outlasts the call, so the next call can find a different world.
- It fails for a reason outside the program.
  A function that opens a file fails when the file is missing.

An unpredictable function has a name: an *Effect*.

## An Effect Spreads to Its Callers

This function calls two Effects:

```python
def greet() -> None:
    name = input("What is your name? ")
    print(f"Hello, {name}!")
```

`greet()` reads the keyboard and writes to the screen,
so `greet()` is unpredictable too.
If `welcome()` calls `greet()`, and `main()` calls `welcome()`,
both of those functions become unpredictable,
because each one waits for a person to type.
An Effect spreads to its caller, then to that function's caller,
and on to the top of the program.

The Effects also stay hidden.
The first line of a function is its *signature*,
which lists what the function takes and what it returns.
The signature of `welcome()` is `def welcome() -> None:`.
That signature says that `welcome()` returns `None`.
The keyboard and the screen appear one call away, in the body of `greet()`.
To find the Effects of `welcome()`, you must read its body,
then the body of each function it calls, and so on down.

Hidden Effects make a program hard to test.
A test calls a function and checks the result.
A test of `add()` passes every time.
A test of `welcome()` needs someone to type a name on every run.
A test of a function that fetches a web page passes on most days and fails on the day the network is slow.

## A Program Needs Its Effects

You might try to remove every Effect.
A program built from pure functions alone computes an answer,
but the answer stays in the computer's memory until the program ends.
Showing the answer on a screen is an Effect.
So is saving the answer to a file or sending it over a network.
Effects are the reason to run a program.

The goal, then, is to manage Effects, not to remove them.
An Effect Management System does three jobs:

1. It separates asking from doing.
   A function says what it needs, while code in another place does the work.
2. It leaves the choice of that code for later.
   One function can run with the real keyboard today and with a stand-in during a test.
3. It tracks Effects.
   Each signature lists the Effects its function uses,
   and a tool checks the list.

## Asking Instead of Doing

`greet()` holds the calls to `input()` and `print()` in its body.
Such a call is *embedded*.
The function that uses the Effect also decides which code runs the Effect.
`greet()` names `input()`, so `greet()` reads the keyboard for every caller,
on every run, a test included.

An Effect Management System takes the Effects out of the function.
`greet()` makes a *request* at the line where it needs a name.
This overview calls that request `Ask`.
An `Ask` says what `greet()` needs, the answer to a question.
Other code decides how to get that answer.
Then four steps follow:

1. `greet()` pauses.
   It keeps its place and its variables.
2. The computer starts running a *handler*,
   a piece of code in another part of the program that answers this kind of request.
3. The handler does the work and produces an answer.
4. The computer goes back to `greet()` with the answer,
   and `greet()` continues from the line where it paused.

To put its message on the screen, `greet()` makes a second request, `Tell`.
The four steps run again for `Tell`.

Programmers call the running of a program its *execution*.
In those four steps, execution transfers from `greet()` to a handler and back.
`greet()` asks for the Effect.
The handler, in another part of the program, runs the Effect.
The call to `input()` is now in the handler,
while `greet()` holds a request where the call was.

A restaurant works the same way.
You give your order to a waiter and stay at your table.
The order goes to the kitchen, the kitchen cooks,
and the food comes back to you.
You are the function, the order is the request, and the kitchen is the handler.
When the restaurant changes cooks, you order as before.
An embedded call is a diner who walks into the kitchen to cook.
That diner must know where the pans are and how the stove works.

A request moves the unpredictable work into the handler.
`greet()` now does the same thing on every run: it asks a question, waits,
and builds a greeting from the answer.
The handler does the unpredictable part, reading what a person types.

## The Handler Decides

`greet()` asks and a handler answers,
so you can change the handler and leave `greet()` as written.
The real program uses a handler that reads the keyboard.
A test uses a handler that answers `"Alice"` every time.
With the test handler, `greet()` is predictable,
so the test passes on every run.

You choose the handlers at the outer edge of the program,
in the code that starts everything.
The functions in the middle make requests.
Each request passes outward, from caller to caller,
until it reaches a handler for its kind.
One choice at the edge serves every function in the program.

A handler is also a single place to change every request of one kind.
Suppose a hundred functions ask for web pages.
A handler that tries a failed fetch again gives that second try to all hundred,
while their code stays as it was.

In a language with Effects built in, a handler can do more than answer.
The requesting function pauses and waits,
so the handler chooses what that function does next:

- The handler sends back an answer, and the function continues.
  The request then acts like an ordinary call.
- The handler drops the paused function and skips the rest of that function's work.
  The request then acts like an error that stops the work.
- In some languages, the handler continues the function several times,
  to try a different answer each time.

The paused function still has the rest of its work ahead of it.
Programmers call it a *continuation*.

## Signatures That List Effects

Tracking adds a third part to a signature.
Along with what the function takes and what it returns,
the signature lists the Effects the function requests.
The signature of `greet()` lists `Ask` and `Tell`.

A tool then checks every function against a rule.
The tool is the compiler or the type checker,
which reads your code before the program runs.
The rule says that a function takes on every request made by the functions it calls.
For each of those requests,
the function installs a handler or lists the request in its own signature.
If `welcome()` calls `greet()` and does neither for `Ask`,
the checker reports an error before the program runs.

A request still spreads from a function to its callers.
Now each signature records the spread, and a tool checks every signature.
One signature tells you whether a function is pure.
When the function is not pure,
that signature tells you which Effects make it unpredictable.

Handling a request also takes it off the list.
A function that installs a handler for `Ask` settles that request,
so its signature leaves `Ask` out.
By the top of the program, every request needs a handler.
The checker reports a missing handler before the program runs.

Tracking covers failures as well as requests.
A signature lists the errors its function can report,
and each caller handles an error or lists it.

## Native Systems and Library Systems

A few languages have Effects built in, Koka and Flix among them.
These languages have *native* Effect systems.
The compiler reads the body of each function and works out which requests the function makes.
Koka's compiler fills in the list, so you rarely write one.
A request looks like an ordinary call,
and the language makes the jump to the handler and back.

In most languages, Python among them,
an Effect system is a *library* that programmers add: ZIO for Scala,
a library named Effect for TypeScript, and Stateless for Python.

A library cannot change the way its language runs a call.
An ordinary call runs right away, at the place where you wrote it.
So a library changes what a call returns.
Calling a function that uses Effects builds a *description*,
a plan of the steps with a request at each Effect.
The work waits until a loop inside the library, the *driver*,
carries out the plan.
At each request, the driver hands the request to its handler and then continues the plan with the answer.

In Python, the pause is the keyword `yield`:

```python
def greet():
    name = yield Ask("What is your name? ")
    yield Tell(f"Hello, {name}!")
```

Each request is a small object.
An `Ask` carries the question, and a `Tell` carries the message.
Calling `greet()` builds the description.
When the driver starts the body, `greet()` runs as far as `yield Ask(...)`,
pauses there, and hands the `Ask` to the driver.
The driver gets an answer from the handler and sends that answer into `greet()`.
`greet()` continues from that `yield` with the answer stored in `name`.

A library cannot add a third part to a signature.
In Stateless, the return type of `greet()` lists `Ask` and `Tell`,
and Python's type checker reads the list there.

Native or library, a request follows one path: the function asks,
execution transfers to a handler, and the answer comes back.

A native system also checks more.
Its compiler reads every call,
so it catches an Effect that your list leaves out.
A library tracks the requests you make through it.
An embedded `print()` in the middle of a function still runs,
and the checker accepts it.

## A Predictable Middle, Effects at the Edge

These ideas give a program two parts.
The middle holds functions that compute and ask.
The edge holds the handlers, where the program meets the world.
The signatures say which function asks for what,
and a checker confirms that every request has a handler.

The world outside stays as unpredictable as before.
Clocks move, networks fail, and people type strange things.
Your program now meets that world in a few handlers that you choose.
If you replace those handlers with ones that give known answers,
the whole program does the same thing on every run.
