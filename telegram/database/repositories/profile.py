from database.connection import get_connection

def get_all():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    pt.name AS profile_type,
                    p.generation,
                    p.birth_date
                FROM profiles p
                JOIN profile_types pt
                    ON pt.id = p.profile_type_id
                ORDER BY
                    p.generation NULLS FIRST,
                    p.name
                """
            )

            return cursor.fetchall()
        
def get(
    profile_id: int,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM profiles
                WHERE id = %s
                """,
                (profile_id,),
            )

            return cursor.fetchone()
        
def search(
    keyword: str,
    limit: int = 10,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    pt.name AS profile_type,
                    p.generation
                FROM profiles p
                JOIN profile_types pt
                    ON pt.id = p.profile_type_id
                WHERE p.name ILIKE %s
                ORDER BY p.name
                LIMIT %s
                """,
                (
                    f"%{keyword.strip()}%",
                    limit,
                ),
            )

            return cursor.fetchall()
        
def add(
    conn,
    name: str,
    profile_type_id: int,
    generation: int | None = None,
    birth_date: str | None = None,
    x_username: str | None = None,
    instagram_username: str | None = None,
    instagram_user_id: str | None = None,
    tiktok_username: str | None = None,
) -> int:

    cursor = conn.execute(
        """
        INSERT INTO profiles (
            name,
            profile_type_id,
            generation,
            birth_date,
            x_username,
            instagram_username,
            instagram_user_id,
            tiktok_username
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id
        """,
        (
            name,
            profile_type_id,
            generation,
            birth_date,
            x_username,
            instagram_username,
            instagram_user_id,
            tiktok_username,
        ),
    )

    return cursor.fetchone()["id"]
    
    
def update_field(
    profile_id: int,
    field: str,
    value,
):
    allowed_fields = {
        "name",
        "profile_type_id",
        "generation",
        "birth_date",
        "x_username",
        "instagram_username",
        "instagram_user_id",
        "tiktok_username",
    }

    if field not in allowed_fields:
        raise ValueError("Invalid field.")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE profiles
                SET
                    {field} = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    value,
                    profile_id,
                ),
            )

            updated = cursor.rowcount > 0

        conn.commit()

        return updated

def delete(profile_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM profiles
                WHERE id = %s
                """,
                (profile_id,),
            )

            deleted = cursor.rowcount > 0

        conn.commit()

        return deleted