from database.connection import get_connection


def get_all():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    is_active
                FROM workers
                ORDER BY id
                """
            )

            return cursor.fetchall()


def get(
    worker_id: int,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM workers
                WHERE id = %s
                """,
                (worker_id,),
            )

            return cursor.fetchone()


def get_by_name(
    name: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM workers
                WHERE name = %s
                """,
                (name,),
            )

            return cursor.fetchone()