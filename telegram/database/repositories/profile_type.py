from database.connection import get_connection


def get_all():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description
                FROM profile_types
                ORDER BY id
                """
            )

            return cursor.fetchall()