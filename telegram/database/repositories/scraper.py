from database.connection import get_connection


def get_all():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    platform,
                    is_running,
                    last_error_at,
                    last_error_message,
                    updated_at
                FROM scrapers
                ORDER BY platform
                """
            )

            return cursor.fetchall()


def get(platform: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM scrapers
                WHERE platform = %s
                """,
                (platform,),
            )

            return cursor.fetchone()


def set_running(
    platform: str,
    is_running: bool,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE scrapers
                SET
                    is_running = %s,
                    updated_at = NOW()
                WHERE platform = %s
                """,
                (
                    is_running,
                    platform,
                ),
            )

        conn.commit()


def set_error(
    platform: str,
    message: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE scrapers
                SET
                    last_error_at = NOW(),
                    last_error_message = %s,
                    updated_at = NOW()
                WHERE platform = %s
                """,
                (
                    message,
                    platform,
                ),
            )

        conn.commit()


def clear_error(platform: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE scrapers
                SET
                    last_error_at = NULL,
                    last_error_message = NULL,
                    updated_at = NOW()
                WHERE platform = %s
                """,
                (platform,),
            )

        conn.commit()