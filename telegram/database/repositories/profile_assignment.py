def rebuild(conn):

    cursor = conn.execute(
        """
        SELECT id
        FROM workers
        WHERE is_active = TRUE
        ORDER BY id
        """
    )

    workers = cursor.fetchall()

    if not workers:
        raise ValueError(
            "Tidak ada worker aktif."
        )

    cursor = conn.execute(
        """
        SELECT id
        FROM profiles
        ORDER BY id
        """
    )

    profiles = cursor.fetchall()

    conn.execute(
        """
        DELETE FROM profile_assignments
        """
    )

    worker_count = len(workers)

    for index, profile in enumerate(profiles):

        worker = workers[
            index % worker_count
        ]

        conn.execute(
            """
            INSERT INTO profile_assignments (
                profile_id,
                worker_id
            )
            VALUES (
                %s,
                %s
            )
            """,
            (
                profile["id"],
                worker["id"],
            ),
        )