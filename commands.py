async def create_group(
    self,
    message: str,
    client,
    group: str | None,
    groups: dict[str, set],
):
    groups[message[2:-1]] = {client}
    setattr(self, "group", message[2:-1])

    if group:
        groups[group].remove(client)

    await client.send(f"created group: {message[2:-1]}\n".encode())


async def join_group(self, message, client, group, groups):
    if message[2:-1] in groups:
        groups[message[2:-1]].add(client)
        if group:
            groups[group].remove(client)

        setattr(self, "group", message[2:-1])
        await client.send(f"joined group: {message[2:-1]}\n".encode())

    else:
        await client.send("no such group exists\n".encode())


async def leave_group(message, client, group, groups):
    message = f"left group: {message[2:-1]}\n"
    await _clean_up(client, group, groups, message)


async def _clean_up(client, group, groups, message=""):
    if group:
        groups[group].remove(client)
        if not groups[group]:
            groups.pop(group)

        if message:
            await client.send(message.encode())
        else:
            await client.send_eof()
