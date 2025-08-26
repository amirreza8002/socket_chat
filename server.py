import asyncio
import sys

import anyio
from anyio._backends._asyncio import SocketStream

from commands import create_group, join_group, leave_group, _clean_up

groups: dict[str, set[asyncio.StreamWriter]] = {}


class Server:
    async def __call__(self, client: SocketStream):
        await self.socket_server(client)

    async def socket_server(self, client: SocketStream):
        data: bytes
        group = None
        async for data in client:
            message, group = self._info(client, data)

            if await self._check_message_is_command(client, message, group):
                continue

            elif message == "q\n":
                await client.send("goodbye\n".encode())
                break

            if not group:
                await client.send(
                    "please join a group before sending messages, or send h for help\n".encode()
                )
                continue

            await self._write(client, data, group)

        await _clean_up(client, group, groups)

    def _info(self, client, data: bytes) -> tuple[str, str]:
        message = data.decode()
        group = getattr(self, "group", None)

        return message, group

    async def _write(self, client, data: bytes, group: str):
        for c in groups[group]:
            if c != client:
                await c.send(data)

    async def _check_message_is_command(self, client, message: str, group: str) -> bool:
        if message == "h\n":
            await client.send(
                "send c <group> to create a group, j <group> to join a group, l to leave a group, q to exit\n".encode()
            )

        elif message.startswith("c "):
            await create_group(self, message, client, group, groups)

        elif message.startswith("j "):
            await join_group(self, message, client, group, groups)

        elif message == "l\n":
            await leave_group(message, client, group, groups)

        else:
            return False

        return True


async def make_server(client):
    return await Server()(client)


async def main():
    server = await anyio.create_tcp_listener(local_port=8888)
    print("starting server")

    await server.serve(make_server)


try:
    anyio.run(main)
except KeyboardInterrupt:
    print("\nbye bye")
    sys.exit()
