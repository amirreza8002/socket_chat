from anyio import create_tcp_listener, run


async def handle(client):
    async for data in client:
        await client.send(b"Hello, %s\n" % data)


async def main():
    listener = await create_tcp_listener(local_port=8888)
    await listener.serve(handle)


run(main)
