import asyncio
import sys

writers = set()


async def socket_server(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    writers.add(writer)
    async for data in reader:
        message = data.decode()
        addr = writer.get_extra_info("peername")

        print(f"Received {message!r} from {addr!r}")
        for w in writers:
            if w != writer:
                w.write(data)

    await writer.drain()
    writers.remove(writer)


async def main():
    server = await asyncio.start_server(socket_server, "127.0.0.1", 8888)
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nbye bye")
    sys.exit()
