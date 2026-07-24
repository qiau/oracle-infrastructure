def parse_netscape_cookie(
    text: str,
) -> tuple[str, dict[str, str]]:

    lines = []
    cookies = {}

    for line in text.splitlines():

        line = line.rstrip()

        if not line:
            continue

        if line.startswith("#"):
            lines.append(line)
            continue

        parts = line.split(maxsplit=6)

        if len(parts) != 7:
            raise ValueError(
                f"Format cookie tidak valid:\n{line}"
            )

        normalized = "\t".join(parts)

        lines.append(normalized)

        cookies[parts[5]] = parts[6]

    if not cookies:
        raise ValueError(
            "Cookie kosong."
        )

    return (
        "\n".join(lines),
        cookies,
    )