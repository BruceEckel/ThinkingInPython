// ts/greet.ts
import { Context, Effect, Layer } from "effect"
import * as readline from "node:readline/promises"
import { stdin, stdout } from "node:process"

// The Effects' interfaces, as services
class Ask extends Context.Service<
  Ask,
  { ask: (prompt: string) => Effect.Effect<string> }
>()("Ask") {}

class Tell extends Context.Service<
  Tell,
  { tell: (message: string) => Effect.Effect<void> }
>()("Tell") {}

// Core logic: still just a description
const greet = Effect.gen(function* () {
  // Fetch each service object the layer supplies
  const ask = yield* Ask
  const tell = yield* Tell
  // Each call builds a description; yield* runs it
  const name = yield* ask.ask("What is your name? ")
  yield* tell.tell(`Hello, ${name}!`)
})

// The implementations, packaged for delayed binding
const ConsoleAsk = Layer.succeed(Ask, {
  ask: (prompt) =>
    Effect.promise(async () => {
      const rl = readline.createInterface({
        input: stdin,
        output: stdout,
      })
      const answer = await rl.question(prompt)
      rl.close()
      return answer
    }),
})

const ConsoleTell = Layer.succeed(Tell, {
  tell: (message) => Effect.sync(() => console.log(message)),
})

// The boundary: descriptions above, execution here
const Console = Layer.merge(ConsoleAsk, ConsoleTell)
Effect.runPromise(greet.pipe(Effect.provide(Console)))
