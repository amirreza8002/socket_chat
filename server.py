import asyncio
import sys

import aioftp

from commands import create_group, join_group, leave_group, _clean_up

groups: dict[str, set[asyncio.StreamWriter]] = {}


class Server:
    async def __call__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        await self.socket_server(reader, writer)

    async def socket_server(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        data: bytes
        async for data in reader:
            message, group = self._info(writer, data)

            if await self._check_message_is_command(writer, message, group):
                continue

            elif message == "q\n":
                writer.write("goodbye\n".encode())
                break

            if not group:
                writer.write(
                    "please join a group before sending messages, or send h for help\n".encode()
                )
                continue

            self._write(writer, data, group)

            await writer.drain()

        _clean_up(writer, group, groups)

        if hasattr(self, "ftp_server"):
            self.ftp_server.close()

    def _info(self, writer: asyncio.StreamWriter, data: bytes) -> tuple[str, str]:
        print(writer)
        message = data.decode()
        addr = writer.get_extra_info("peername")
        group = getattr(self, "group", None)

        print(f"Received {message!r} from {addr!r}")
        return message, group

    def _write(self, writer: asyncio.StreamWriter, data: bytes, group: str):
        for w in groups[group]:
            if w != writer:
                w.write(data)

    async def _check_message_is_command(
        self, writer: asyncio.StreamWriter, message: str, group: str
    ) -> bool:
        if message == "h\n":
            writer.write(
                "send c <group> to create a group, j <group> to join a group, l to leave a group, q to exit\n".encode()
            )

        elif message.startswith("c "):
            create_group(self, message, writer, group, groups)

        elif message.startswith("j "):
            join_group(self, message, writer, group, groups)

        elif message == "l\n":
            leave_group(message, writer, group, groups)

        else:
            return False

        await writer.drain()
        return True


async def make_server(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    return await Server()(reader, writer)


async def main():
    server = await asyncio.start_server(make_server, "127.0.0.1", 8888)
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nbye bye")
    sys.exit()
