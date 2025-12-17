from collections import defaultdict
from dataclasses import dataclass

from .database import FingerprintDatabase

MIN_MATCHES = 5


@dataclass
class MatchResult:
    """Result of a song identification."""
    song_id: int
    song_name: str
    confidence: float
    aligned_matches: int


def find_matches(query_hashes: list[tuple[str, int, int]], db: FingerprintDatabase) -> MatchResult | None:
    """Find best matching song using time-alignment voting.

    Args:
        query_hashes: List of (hash_string, query_time_offset, _) tuples.
        db: Fingerprint database to query.

    Returns:
        MatchResult if a match is found, None otherwise.
    """
    if not query_hashes:
        return None

    # Query all hashes from database
    matches = db.query(query_hashes)

    if not matches:
        return None

    # Group by (song_id, time_diff) where time_diff = db_offset - query_offset
    alignment_counts = defaultdict(int)
    for song_id, db_offset, query_offset in matches:
        time_diff = db_offset - query_offset
        alignment_counts[(song_id, time_diff)] += 1

    # Find best alignment
    best_key = max(alignment_counts, key=alignment_counts.get)
    best_count = alignment_counts[best_key]
    best_song_id = best_key[0]

    # Check minimum threshold
    if best_count < MIN_MATCHES:
        return None

    # Calculate confidence
    confidence = best_count / len(query_hashes)

    # Get song name
    song_name = db.get_song(best_song_id)

    return MatchResult(
        song_id=best_song_id,
        song_name=song_name,
        confidence=confidence,
        aligned_matches=best_count
    )
