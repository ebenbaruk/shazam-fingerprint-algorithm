from pathlib import Path

from .audio import load_audio
from .spectrogram import compute_spectrogram
from .peaks import find_peaks
from .fingerprint import generate_hashes
from .database import FingerprintDatabase
from .matcher import find_matches, MatchResult


class Shazam:
    """Main interface for audio fingerprinting and identification."""

    def __init__(self, db_path: str = "fingerprints.db"):
        """Initialize Shazam with database path."""
        self.db = FingerprintDatabase(db_path)

    def fingerprint(self, filepath: str) -> list[tuple[str, int, int]]:
        """Generate fingerprints for an audio file.

        Args:
            filepath: Path to audio file.

        Returns:
            List of (hash_string, time_offset, None) tuples.
        """
        audio, sr = load_audio(filepath)
        spectrogram = compute_spectrogram(audio, sr)
        peaks = find_peaks(spectrogram)
        hashes = generate_hashes(peaks)
        return hashes

    def add_song(self, filepath: str, name: str = None) -> int:
        """Add a song to the database.

        Args:
            filepath: Path to audio file.
            name: Song name. If None, uses filename.

        Returns:
            The song_id of the added song.
        """
        if name is None:
            name = Path(filepath).stem

        hashes = self.fingerprint(filepath)
        song_id = self.db.insert_song(name, hashes)
        return song_id

    def identify(self, filepath: str) -> MatchResult | None:
        """Identify a song from an audio sample.

        Args:
            filepath: Path to audio sample.

        Returns:
            MatchResult if identified, None otherwise.
        """
        hashes = self.fingerprint(filepath)
        return find_matches(hashes, self.db)

    def list_songs(self) -> list[tuple[int, str]]:
        """List all songs in database."""
        return self.db.list_songs()

    def stats(self) -> dict:
        """Get database statistics."""
        return {
            "songs": self.db.song_count(),
            "fingerprints": self.db.fingerprint_count()
        }
