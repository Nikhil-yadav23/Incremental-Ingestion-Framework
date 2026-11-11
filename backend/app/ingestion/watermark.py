
def get_watermark(connection, pipeline_name="customer_ingestion"):
    """Read the last successfully processed watermark."""

    result = connection.execute(
        """
        SELECT last_updated_at, last_event_id
        FROM watermarks
        WHERE pipeline_name = ?
        """,
        (pipeline_name,)
    ).fetchone()

    if result is None:
        return None

    return (
        result["last_updated_at"],
        result["last_event_id"]
    )


def update_watermark(
    connection,
    updated_at,
    event_id,
    pipeline_name="customer_ingestion"
):
    """Save the latest successfully processed watermark."""

    connection.execute(
        """
        INSERT INTO watermarks (
            pipeline_name,
            last_updated_at,
            last_event_id
        )
        VALUES (?, ?, ?)
        ON CONFLICT(pipeline_name) DO UPDATE SET
            last_updated_at = excluded.last_updated_at,
            last_event_id = excluded.last_event_id
        """,
        (pipeline_name, updated_at, event_id)
    )
