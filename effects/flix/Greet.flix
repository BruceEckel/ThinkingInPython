// flix/Greet.flix
use Sys.Console

// Effect declarations: the interface, not the implementation
eff Ask {
    def ask(prompt: String): String
}

eff Tell {
    def tell(message: String): Unit
}

// Core logic: the Effect row appears after the backslash
def greet(): Unit \ {Ask, Tell} =
    let name = Ask.ask("What is your name? ");
    Tell.tell("Hello, ${name}!")

// Main binds each Effect to an implementation
def main(): Unit \ Console =
    run {
        greet()
    } with handler Ask {
        def ask(prompt, resume) = {
            Console.print(prompt);
            let line = Console.readln();
            resume(Option.getWithDefault("", line))
        }
    } with handler Tell {
        def tell(message, resume) =
            resume(Console.println(message))
    }
