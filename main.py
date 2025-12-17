#!/usr/bin/env python3
import argparse
from pathlib import Path

from shazam import Shazam


def add_song(args):
    """Add a single song to the database."""
    shazam = Shazam(args.db)
    song_id = shazam.add_song(args.filepath, args.name)
    print(f"Added: {args.name or Path(args.filepath).stem} (id={song_id})")


def add_dir(args):
    """Add all audio files in a directory."""
    shazam = Shazam(args.db)
    extensions = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

    path = Path(args.directory)
    files = [f for f in path.iterdir() if f.suffix.lower() in extensions]

    if not files:
        print(f"No audio files found in {args.directory}")
        return

    for filepath in files:
        song_id = shazam.add_song(str(filepath))
        print(f"Added: {filepath.stem} (id={song_id})")

    print(f"\nAdded {len(files)} songs")


def identify(args):
    """Identify a song from an audio sample."""
    shazam = Shazam(args.db)
    result = shazam.identify(args.filepath)

    if result:
        print(f"Match: {result.song_name}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Aligned matches: {result.aligned_matches}")
    else:
        print("No match found")


def list_songs(args):
    """List all songs in the database."""
    shazam = Shazam(args.db)
    songs = shazam.list_songs()

    if not songs:
        print("No songs in database")
        return

    for song_id, name in songs:
        print(f"  {song_id}: {name}")

    stats = shazam.stats()
    print(f"\nTotal: {stats['songs']} songs, {stats['fingerprints']} fingerprints")


def main():
    parser = argparse.ArgumentParser(description="Shazam-style audio fingerprinting")
    parser.add_argument("--db", default="fingerprints.db", help="Database file path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a song to the database")
    add_parser.add_argument("filepath", help="Path to audio file")
    add_parser.add_argument("--name", help="Song name (default: filename)")
    add_parser.set_defaults(func=add_song)

    # add-dir command
    adddir_parser = subparsers.add_parser("add-dir", help="Add all songs in a directory")
    adddir_parser.add_argument("directory", help="Path to directory")
    adddir_parser.set_defaults(func=add_dir)

    # identify command
    id_parser = subparsers.add_parser("identify", help="Identify a song")
    id_parser.add_argument("filepath", help="Path to audio sample")
    id_parser.set_defaults(func=identify)

    # list command
    list_parser = subparsers.add_parser("list", help="List all songs in database")
    list_parser.set_defaults(func=list_songs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
