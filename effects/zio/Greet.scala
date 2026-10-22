// zio/Greet.scala
import zio.*
import zio.Console.{print, printLine, readLine}

// The Effects' interfaces
trait Ask:
  def ask(prompt: String): UIO[String]

trait Tell:
  def tell(message: String): UIO[Unit]

// Accessors: lift each method into a ZIO description
object Ask:
  def ask(prompt: String): ZIO[Ask, Nothing, String] =
    ZIO.serviceWithZIO[Ask](_.ask(prompt))

object Tell:
  def tell(message: String): ZIO[Tell, Nothing, Unit] =
    ZIO.serviceWithZIO[Tell](_.tell(message))

// Core logic: a value, not an action; nothing runs here
val greet: ZIO[Ask & Tell, Nothing, Unit] =
  for
    name <- Ask.ask("What is your name? ")
    _ <- Tell.tell(s"Hello, $name!")
  yield ()

// The implementations, packaged for delayed binding
val consoleAsk: ULayer[Ask] = ZLayer.succeed(new Ask:
  def ask(prompt: String): UIO[String] =
    (print(prompt) *> readLine).orDie)

val consoleTell: ULayer[Tell] = ZLayer.succeed(new Tell:
  def tell(message: String): UIO[Unit] =
    printLine(message).orDie)

// Entry point: bind the implementations, then execute
object Main extends ZIOAppDefault:
  def run = greet.provide(consoleAsk, consoleTell)
