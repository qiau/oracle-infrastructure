def rebuild(conn):

    checks = [
        ("x", "post", "x_username"),
        ("instagram", "post", "instagram_user_id"),
        ("instagram", "story", "instagram_user_id"),
        ("tiktok", "post", "tiktok_username"),
        ("tiktok", "story", "tiktok_username"),
    ]

    for platform, content_type, column in checks:

        conn.execute(
            f"""
            DELETE FROM profile_checks
            WHERE

                platform = %s

                AND profile_id IN (

                    SELECT id
                    FROM profiles

                    WHERE {column} IS NULL

                )
            """,
            (platform,),
        )

        conn.execute(
            f"""
            INSERT INTO profile_checks (
                profile_id,
                platform,
                content_type
            )

            SELECT
                id,
                %s,
                %s
            FROM profiles

            WHERE {column} IS NOT NULL

            ON CONFLICT (
                profile_id,
                platform,
                content_type
            ) DO NOTHING
            """,
            (
                platform,
                content_type,
            ),
        )