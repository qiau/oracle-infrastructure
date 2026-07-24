import httpx

from utils.cookies_parser import parse_netscape_cookie


USER_AGENT = (
    "Instagram 275.0.0.27.98 Android "
    "(33/13; 420dpi; 1080x2400; samsung; "
    "SM-G991B; o1s; exynos2100)"
)


def check_instagram_cookie(
    content: str,
) -> tuple[bool, str]:

    try:
        _, cookies = parse_netscape_cookie(
            content
        )

    except ValueError as e:
        return (
            False,
            str(e),
        )

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": "936619743392459",
    }

    try:
        with httpx.Client(
            headers=headers,
            cookies=cookies,
            timeout=15,
            follow_redirects=True,
        ) as client:

            response = client.get(
                "https://www.instagram.com/api/v1/feed/user/25025320/?count=1"
            )

    except httpx.TimeoutException:
        return (
            False,
            "Request timeout.",
        )

    except httpx.RequestError as e:
        return (
            False,
            str(e),
        )

    if response.status_code == 401:
        return (
            False,
            "Unauthorized.",
        )

    if response.status_code == 403:
        return (
            False,
            "Forbidden.",
        )

    if response.status_code == 429:
        return (
            False,
            "Rate limit.",
        )

    if response.status_code != 200:
        return (
            False,
            f"HTTP {response.status_code}",
        )

    try:
        data = response.json()

    except Exception:
        return (
            False,
            "Response bukan JSON.",
        )

    items = data.get("items")

    if not isinstance(items, list):
        return (
            False,
            "Format response tidak valid.",
        )

    return (
        True,
        "OK",
    )