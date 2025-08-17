import asyncio


def create_group(
    self,
    message: str,
    writer: asyncio.StreamWriter,
    group: str | None,
    groups: dict[str, set[asyncio.StreamWriter]],
):
    groups[message[2:-1]] = {writer}
    setattr(self, "group", message[2:-1])

    if group:
        groups[group].remove(writer)

    writer.write(f"created group: {message[2:-1]}\n".encode())


def join_group(self, message, writer, group, groups):
    if message[2:-1] in groups:
        groups[message[2:-1]].add(writer)
        if group:
            groups[group].remove(writer)

        setattr(self, "group", message[2:-1])
        writer.write(f"joined group: {message[2:-1]}\n".encode())

    else:
        writer.write("no such group exists\n".encode())


def leave_group(message, writer, group, groups):
    message = f"left group: {message[2:-1]}\n"
    _clean_up(writer, group, groups, message)


def _clean_up(writer, group, groups, message=""):
    if group:
        groups[group].remove(writer)
        if not groups[group]:
            groups.pop(group)

        if message:
            writer.write(message.encode())
