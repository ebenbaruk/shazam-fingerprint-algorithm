import sqlite3
from pathlib import Path


class FingerprintDatabase:
    """SQLite database for storing and querying audio fingerprints."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fingerprints (
                    hash TEXT NOT NULL,
                    song_id INTEGER NOT NULL,
                    time_offset INTEGER NOT NULL,
                    FOREIGN KEY (song_id) REFERENCES songs(id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash)")
            conn.commit()

    def insert_song(self, name: str, hashes: list[tuple[str, int, int]]) -> int:
        """Insert a song and its fingerprints.

        Args:
            name: Song name/title.
            hashes: List of (hash_string, time_offset, _) tuples.

        Returns:
            The song_id of the inserted song.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("INSERT INTO songs (name) VALUES (?)", (name,))
            song_id = cursor.lastrowid

            # Insert fingerprints
            fingerprint_data = [(h, song_id, t) for h, t, _ in hashes]
            conn.executemany(
                "INSERT INTO fingerprints (hash, song_id, time_offset) VALUES (?, ?, ?)",
                fingerprint_data
            )
            conn.commit()
            return song_id

    def query(self, hashes: list[tuple[str, int, int]]) -> list[tuple[int, int, int]]:
        """Query database for matching hashes.

        Args:
            hashes: List of (hash_string, query_time_offset, _) tuples.

        Returns:
            List of (song_id, db_time_offset, query_time_offset) for matches.
        """
        matches = []
        with sqlite3.connect(self.db_path) as conn:
            for hash_val, query_offset, _ in hashes:
                cursor = conn.execute(
                    "SELECT song_id, time_offset FROM fingerprints WHERE hash = ?",
                    (hash_val,)
                )
                for song_id, db_offset in cursor.fetchall():
                    matches.append((song_id, db_offset, query_offset))
        return matches

    def get_song(self, song_id: int) -> str | None:
        """Get song name by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM songs WHERE id = ?", (song_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def list_songs(self) -> list[tuple[int, str]]:
        """List all songs in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, name FROM songs ORDER BY id")
            return cursor.fetchall()

    def song_count(self) -> int:
        """Get number of songs in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM songs")
            return cursor.fetchone()[0]

    def fingerprint_count(self) -> int:
        """Get total number of fingerprints in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM fingerprints")
            return cursor.fetchone()[0]
