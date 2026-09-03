# network_io.py
import asyncio

async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    line = await reader.readline()
    writer.write(b"echo: " + line)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def request(port: int, message: str) -> str:
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", port)
    writer.write(message.encode() + b"\n")
    await writer.drain()
    reply = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return reply.decode().strip()

async def main() -> None:
    server = await asyncio.start_server(
        handle_client, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    async with server:
        replies = await asyncio.gather(
            request(port, "a"), request(port, "b"))
    print(replies)

asyncio.run(main())
#: ['echo: a', 'echo: b']
