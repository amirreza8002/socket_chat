import asyncio
import aioftp


async def main():
    server = aioftp.Server()
    await server.start()
    addr = server.address
    print(f"Serving on {addr}")
    try:
        await server.serve_forever()
    finally:
        await server.close()


asyncio.run(main())
