from database.connection import get_connection

def get_all():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.id,
                    w.name AS worker_name,
                    c.name,
                    c.is_valid,
                    c.last_checked_at
                FROM cookies c
                JOIN workers w
                    ON w.id = c.worker_id
                ORDER BY
                    w.name,
                    c.name
                """
            )

            return cursor.fetchall()


def get(
    worker_id: int,
    name: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM cookies
                WHERE
                    worker_id = %s
                AND name = %s
                """,
                (
                    worker_id,
                    name,
                ),
            )

            return cursor.fetchone()


def add(
    worker_id: int,
    name: str,
    content: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cookies (
                    worker_id,
                    name,
                    content
                )
                VALUES (
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    worker_id,
                    name,
                    content,
                ),
            )

            cookie_id = cursor.fetchone()["id"]

        conn.commit()

        return cookie_id

def exists(
    worker_id: int,
    name: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM cookies
                WHERE worker_id = %s
                  AND name = %s
                """,
                (
                    worker_id,
                    name,
                ),
            )

            return cursor.fetchone() is not None
        
def get_by_worker_and_name(
    worker_id: int,
    name: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM cookies
                WHERE worker_id = %s
                  AND name = %s
                """,
                (
                    worker_id,
                    name,
                ),
            )

            return cursor.fetchone()

def update_content(
    cookie_id: int,
    content: str,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE cookies
                SET
                    content = %s,
                    is_valid = FALSE,
                    last_checked_at = NULL,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    content,
                    cookie_id,
                ),
            )

            updated = cursor.rowcount > 0

        conn.commit()

        return updated


def delete(
    cookie_id: int,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM cookies
                WHERE id = %s
                """,
                (cookie_id,),
            )

            deleted = cursor.rowcount > 0

        conn.commit()

        return deleted


def update_validation(
    cookie_id: int,
    is_valid: bool,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE cookies
                SET
                    is_valid = %s,
                    last_checked_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    is_valid,
                    cookie_id,
                ),
            )

            updated = cursor.rowcount > 0

        conn.commit()

        return updated